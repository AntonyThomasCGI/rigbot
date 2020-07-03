import pymel.core as pm

from .. import utils
from .. import user

# ----------------------------------------------------------------------------------------------------------------------
"""

	SCAFFOLDBASE.PY
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

"""
# ----------------------------------------------------------------------------------------------------------------------


class ScaffoldException(Exception):
	pass


class Scaffold(object):

	# Specify what modules can build from this scaffold
	# TODO: include all modules in Scaffold base class i guess..?
	_availableModules = utils.getFilteredDir('modules')
	_availableModules.append(' ')
	
	# ------------------------------------------------------------------------------------------------------------------
	def __init__(self, module_root=None, **kwargs):
		"""
		module_root (PyNode):	If module_root=None will build a new scaffold from 
								builder args. Or pass valid module root to return
								scaffold class of module.
		
		Builder kwargs: 	length (int) 	= joint chain length
							module (string) = module type to tag module root with
							name (string) 	= naming convention prefix
							socket (PyNode or string) = parent for module, default=root
		"""

		# if module_root: module already exists so populate class attributes
		if module_root:
			
			if not module_root.hasAttr('RB_MODULE_ROOT'):
				raise TypeError('--"{}" is not a module root.'.format(module_root))

			self.chain = utils.getModuleChildren(module_root)

			self._moduleType = module_root.getAttr('RB_module_type', asString=True)
			if self._moduleType not in self._availableModules:
				raise ScaffoldException('Module type: {} is not in list of available modules.'.format(self._moduleType))

			self.name = self.getModName(module_root)
			self._length = set()
			self.socket = module_root.listRelatives(parent=True)[0]

			for flag in kwargs:
				print('// Warning: {} flag is ignored in non-build mode.'.format(flag))

		else:

			self.chain = None
			self._length = kwargs.pop('length', 1)
			self.name = self.makeNameUnique(kwargs.pop('name', 'joint'))

			self.makeBind()
			
			self.socket = self.returnValidParent(kwargs.pop('socket', 'root'))
			pm.matchTransform(self.root, self.socket)
			
			self._moduleType = kwargs.pop('moduleType', ' ')
			if self._moduleType not in self._availableModules:
				raise ScaffoldException('Module type: {} is not in list of available modules.'.format(self._moduleType))

			self.display()
			
			self.tag()

			# For convenience select chain root
			pm.select(self.root)
	# end def __init__(self, parent='root'):

	def __str__(self):
		return 'rb.{}({})'.format(self.__class__.__name__, self.name)
	# end def __str__(self):

	def __repr__(self):
		return self.__str__()
	# end def __repr__(self):

	# ------------------------------------------------------------------------------------------------------------------
	def makeBind(self):
		raise ScaffoldException('--Invalid subclass: makeBind() function not implemented.')
	# end def makeBind(self):

	# ------------------------------------------------------------------------------------------------------------------
	def display(self):
		curv = pm.curve(d=1, p=utils.controllerShapes['locator'],
						n=(self.name + '_display'))
		utils.scaleCtrlShape(0.5, 3, curv)

		shape = curv.getChildren()[0]
		utils.setOverrideColour('grey-blue', shape)
		pm.parent(shape, self.root, r=True, s=True)

		pm.delete(curv)
		utils.setOverrideColour(user.prefs['default-jnt-colour'], [self.chain,shape])
		utils.setOverrideColour(user.prefs['module-root-colour'], self.root)
		utils.setOutlinerColour(user.prefs['module-root-colour'], self.root)
	# end def display(self):

	# ------------------------------------------------------------------------------------------------------------------
	def tag(self):
		default_tags = [
			{ 'name':'RB_MODULE_ROOT', 'at':'enum', 'en':' ', 'k':0, 'l':1 },
			{ 'name':'RB_module_type', 'k':0, 'at':'enum', 
				'en':(':'.join(self._availableModules)),
				'dv':(self._availableModules.index(self.moduleType)) },
			{ 'name':'RB_include_end_joint', 'k':0, 'at':'bool', 'dv':1 },
		]
		
		for attr_dict in default_tags:
			utils.makeAttrFromDict(self.root, attr_dict)
	# end def tag(self):

	# ------------------------------------------------------------------------------------------------------------------
	# . 											properties
	# ------------------------------------------------------------------------------------------------------------------

	@property
	def socket(self):
		return self._socket
	# end def socket(self):

	@socket.setter
	def socket(self, new_parent):
		pm.parent(self.root, new_parent)
		self._socket = new_parent
	# end def socket(self, parent):

	@property
	def name(self):
		return self._name
	# end def name(self):
	
	@name.setter
	def name(self, new_name):
		if self.chain:
			for jnt in self.chain:
				pm.rename(jnt, jnt.replace(self.getModName(jnt), new_name))
		self._name = new_name
	# end def name(self, new_name):

	@property
	def moduleType(self):
		return self._moduleType
	# end def module(self):

	@moduleType.setter
	def moduleType(self, new_module):
		if self.root.hasAttr('RB_module_type'):
			self.root.RB_module_type.set(new_module)

		self._moduleType = new_module
	# end def moduleType(self, new_module):

	@property
	def root(self):
		if self.chain:
			return self.chain[0]
		else:
			return None
	# end def root(self):

	@property
	def length(self):
		if self.chain:
			return len(self.chain)
		else:
			return self._length
	# end def length(self):

	# ------------------------------------------------------------------------------------------------------------------
	# .											static utility functions
	# ------------------------------------------------------------------------------------------------------------------
	@staticmethod
	def returnValidParent(node):
		"""
		Get valid socket to parent module to
		:param node: (string or pyNode) Test if this node is a valid parent
		:return: node if node is a valid parent else return root joint
		"""

		try:
			if isinstance(node, basestring):
				node = pm.PyNode(node)
		except pm.MayaObjectError:
			root_node = utils.makeRoot()
			return root_node

		if 'joint' == node.nodeType():
			return node
		else:
			root_node = utils.makeRoot()
			return root_node
	# end def returnValidParent(self, node):

	@staticmethod
	def makeNameUnique(name):
		"""
		Makes name unique in scene
		:param name: (string) name to pad with numeral
		:return: string padded name
		"""

		new_name = name
		i = 1
		while pm.objExists(new_name+'_*'):
			new_name = '{}{}'.format(name, i)
			i += 1

		return new_name
	# end def makeNameUnique(name):

	@staticmethod
	def getModName(node_name):
		"""
		Get module nice name from a node name
		:param node_name: (PyNode) node name to make nice name
		:return: string stripped node nice name
		"""

		split_ls = node_name.split('_')
		mod_name = split_ls[0]

		# checks for L R prefixes
		if any(prefix for prefix in [user.prefs['left-prefix'], user.prefs['right-prefix']] if prefix == split_ls[0]):
			mod_name = '_'.join(split_ls[0:2])

		return mod_name
	# end def getModName(node_name):
# end class Scaffold(object):
