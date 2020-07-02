import pymel.core as pm

from .. import utils
from ..userPrefs import user

## --------------------------------------------------------------------------------
'''

	Scaffold.PY
	Base class for creating scaffold chains (Template joints for auto rigger to 
	build from).  Inherit from this class and override any functions required to 
	create new rig scaffolding.
	
	makeBind():		Creates the joints. This must be overridden when writing a new
					scaffolding module.
						> self.chain needs to be defined here.

	display():		Default sets colours on self.chain.  If a module needs additional 
					display information, consider overriding this.
						
	tag():		Handles tagging the joints with any module specific information. By
				default it will tag the root joint with the module type and the
				option to include end joint.

'''
## --------------------------------------------------------------------------------


class ScaffoldException( Exception ):
	pass


class Scaffold( object ):

	## Specify what modules can build from this scaffold
	## TODO: include all modules in Scaffold base class i guess..?
	_availableModules = utils.getFilteredDir( 'modules' )
	_availableModules.append( ' ' )
	
	
	##-----------------------------------------------------------------------------
	def __init__( self, moduleRoot=None, **kwargs ):
		'''
		moduleRoot (PyNode):	If moduleRoot=None will build a new scaffold from 
								builder args. Or pass valid module root to return
								scaffold class of module.
		
		Builder kwargs: length (int) 	= joint chain length
						module (string) = module type to tag module root with
						name (string) 	= naming convention prefix
						socket (pynode or string) = parent for module, default=root
		'''

		## if moduleRoot: module already exists so populate class attributes
		if moduleRoot:
			
			if not moduleRoot.hasAttr('RB_MODULE_ROOT'):
				raise TypeError( '--"{}" is not a module root.'.format( moduleRoot ))

			self.chain = utils.getModuleChildren( moduleRoot )
			self.moduleType = moduleRoot.getAttr( 'RB_module_type', asString=True )
			self.name = self.getModName( moduleRoot )
			self._length = set()
			self.socket = moduleRoot.listRelatives( parent=True )[0]

			for flag in kwargs:
				print( '// Warning: {} flag is ignored in non-build mode.'.format( flag ))

		else:

			self.chain = None
			self._length = kwargs.pop( 'length', 1 )
			self.name = self.makeNameUnique( kwargs.pop( 'name', 'joint' ))

			self.makeBind()
			
			self.socket = self.returnValidParent( kwargs.pop( 'socket', 'root'))
			pm.matchTransform( self.root, self.socket )
			
			self.moduleType = kwargs.pop( 'moduleType', ' ' )

			self.display()
			
			self.tag()

			## For convenience select chain root
			pm.select( self.root )
	# end def __init__( self, parent='root' ):


	def __str__( self ):
		return 'rb.{}( {} )'.format( self.__class__.__name__, self.name )
	# end def __str__( self ):

	def __repr__( self ):
		return self.__str__()
	# end def __repr__( self ):


	##-----------------------------------------------------------------------------
	def makeBind( self ):
		raise ScaffoldException( '--Invalid subclass: makeBind() function not '
									+'implemented.' )
	# end def makeBind( self ):


	##-----------------------------------------------------------------------------
	def display( self ):
		curv = pm.curve( d=1, p=utils.controllerShapes[ 'locator' ],
						n=(self.name + '_display') )
		utils.scaleCtrlShape( 0.5, 3, curv )

		shape = curv.getChildren()[0]
		utils.setOverrideColour( 'grey-blue', shape )
		pm.parent( shape, self.root, r=True, s=True )

		pm.delete( curv )
		utils.setOverrideColour( user.prefs('default-jnt-colour'), [self.chain, 
																		shape] )
		utils.setOverrideColour( user.prefs('module-root-colour'), self.root )
		utils.setOutlinerColour( user.prefs('module-root-colour'), self.root )
	# end def display( self ):


	##-----------------------------------------------------------------------------
	def tag( self ):
		default_tags = [
			{ 'name':'RB_MODULE_ROOT', 'at':'enum', 'en':' ', 'k':0, 'l':1 },
			{ 'name':'RB_module_type', 'k':0, 'at':'enum', 
				'en':( ':'.join( self._availableModules )), 
				'dv':( self._availableModules.index( self.moduleType )) },
			{ 'name':'RB_include_end_joint', 'k':0, 'at':'bool', 'dv':1 },
		]
		
		for attr_dict in default_tags:
			utils.makeAttrFromDict( self.root, attr_dict )
	# end def tag( self ):


	##-----------------------------------------------------------------------------
	## properties
	## ----------------------------------------------------------------------------

	@property
	def socket( self ):
		return self._socket
	# end def socket(self):

	@socket.setter
	def socket( self, new_parent ):
		pm.parent( self.root, new_parent )
		self._socket = new_parent
	# end def socket( self, parent ):


	@property
	def name( self ):
		return self._name
	# end def name( self ):
	
	@name.setter
	def name( self, new_name ):
		if self.chain:
			for jnt in self.chain:
				pm.rename( jnt, jnt.replace( self.getModName( jnt ), new_name ) )
		self._name = new_name
	# end def name( self, new_name ):


	@property
	def moduleType( self ):
		return self._moduleType
	# end def module( self ):

	@moduleType.setter
	def moduleType( self, new_module ):
		if new_module in self._availableModules:
			if self.root.hasAttr( 'RB_module_type' ):
				self.root.RB_module_type.set( new_module )
		else:
			raise ScaffoldException( 'Module type: {} '.format( new_module )
										+'is not in list of available modules.')
		self._moduleType = new_module
	# end def moduleType( self, new_module ):

	
	@property
	def root( self ):
		if self.chain:
			return( self.chain[0] )
		else:
			return( None )
	# end def root( self ):


	@property
	def length( self ):
		if self.chain:
			return len( self.chain )
		else:
			return self._length
	# end def length( self ):
	


	##-----------------------------------------------------------------------------
	## utility functions
	## ----------------------------------------------------------------------------
	
	def returnValidParent( self, node ):
		## node (string or pyNode) = 	Test if this node is a valid parent, if not
		## 								attempt to return root.

		try:
			if isinstance( node, basestring ):
				node = pm.PyNode( node )
		except:
			root_node = utils.makeRoot()
			return root_node

		if 'joint' == node.nodeType():
			return node
		else:
			root_node = utils.makeRoot()
			return root_node
	# end def returnValidParent( self, node ):


	##-----------------------------------------------------------------------------
	def makeNameUnique( self, name ):
		## name (string) = name to pad
		new_name = name
		i=1
		while pm.objExists( new_name+'_*' ):
		    new_name = '{}{}'.format( name, i )
		    i+=1
		    
		return new_name
	# end def makeNameUnique( self, name ):

	def getModName( self, node_name ):
		## node_name ( PyNode ) = node name to make into module nice name

		split_ls = node_name.split( '_' )
		mod_name = split_ls[0]

		## checks for L R prefixes
		if any( prefix for prefix in [user.prefs( 'left-prefix' ), 
			user.prefs( 'right-prefix' )] if prefix == split_ls[0] ):
				mod_name = ('_').join( split_ls[0:2] )

		return mod_name
	#end def getModName( node_name ):
# end class Scaffold( object ):