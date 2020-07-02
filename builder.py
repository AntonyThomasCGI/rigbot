import difflib

import pymel.core as pm

from userPrefs import user
import utils

import scaffolds as scaf
import modules as mod

## --------------------------------------------------------------------------------
'''

	BUILDER.PY
	batch builder for modules

'''


class RigException( Exception ):
	pass


class Rig( object ):
	def __init__( self ):

		self._modules = None
		self.getModules()
		
		self.module_classes = utils.getFilteredDir( 'modules' )
		# self.module_classes.append(' ')

		self.scaffold_classes = utils.getFilteredDir( 'scaffolds' )
	# end def __init__( self ):


	##-----------------------------------------------------------------------------
	def __str__( self ):
		s = 's' if len( self._modules ) > 1 else ''
		return 'Rig Instance: {}. (Module{}: {}).'.format( self.__class__, s, len( self._modules ))
	# end def __str__( self ):

	def __repr__( self ):
		return self.__str__()
	# end def __repr__( self ):


	##-----------------------------------------------------------------------------
	def scaffold( self, moduleType, **kwargs ):
		'''
		Makes new scaffold and reloads modules
		moduleType (string)	= module type
		kwargs = builder kwargs, see: rigbot.scaffolds.ScaffoldBase
		'''
		for scaf_class in self.scaffold_classes:
			scaffold_clss = getattr( scaf, scaf_class )
			if moduleType in scaffold_clss._availableModules:
				new_scaf = scaffold_clss( moduleType=moduleType, **kwargs )
				continue

		self._modules.append( new_scaf )

		return new_scaf
	# end def scaffold( self ):


	##-----------------------------------------------------------------------------
	def batchBuild( self ):
		'''
		rig all unrigged modules
		'''
		for module in self.modules:
			if module.moduleType in self.module_classes:
				mod_clss = getattr( mod, module )
	# end def batchBuild( self ):


	##-----------------------------------------------------------------------------
	@property
	def modules( self ):
		return self._modules
	# end def modules( self ):


	##-----------------------------------------------------------------------------
	def getModules( self ):
		print( '>>Fetching modules.' )

		if pm.objExists( user.prefs( 'root-joint' ) ):
			root_jnt = pm.PyNode( user.prefs( 'root-joint' ) )
		else:
			utils.makeRoot()
			self._modules = {}
			return

		flattened_jnts = root_jnt.getChildren( ad=True, type='joint' )

		def isModRoot( jnt ):
			return jnt.hasAttr( 'RB_MODULE_ROOT' )
		# end def isModRoot( jnt ):	

		module_roots = filter( isModRoot, flattened_jnts )

		modules_ls = map( lambda mod_root: scaf.Scaffold( moduleRoot=mod_root ), 
															module_roots )

		self._modules = modules_ls
	# end def getModules( self ):
# end class Rig( object ):