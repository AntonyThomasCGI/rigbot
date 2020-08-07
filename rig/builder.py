import pymel.core as pm

from .. import user, utils, data

from .. import modules as mod


# ----------------------------------------------------------------------------------------------------------------------
"""

	BUILDER.PY
	Manage and build scaffold/rig classes

"""
# ----------------------------------------------------------------------------------------------------------------------


class ScaffoldException(Exception):
	pass


class Scaffold(object):

	# Specify what modules can build from this scaffold
	_availableModules = utils.getFilteredDir('modules')
	_availableModules.append(' ')

	# ------------------------------------------------------------------------------------------------------------------
	def __init__(self, module_root):
		"""
		:param module_root: PyNode, valid module root to populate
							scaffold class attributes from.
		"""

		if not module_root.hasAttr('RB_MODULE_ROOT'):
			raise TypeError('--"{}" is not a module root.'.format(module_root))

		self.chain = utils.getModuleChildren(module_root)

		self._moduleType = module_root.getAttr('RB_module_type', asString=True)
		if self._moduleType not in self._availableModules:
			raise ScaffoldException('Module type: {} is not in list of available modules.'.format(self._moduleType))

		self._name = self.getModName(module_root)
		self._length = set()
		self.socket = module_root.listRelatives(parent=True)[0]
	# end def __init__():

	def __str__(self):
		return 'rb.{}({})'.format(self.__class__.__name__, self.name)
	# end def __str__():

	def __repr__(self):
		return self.__str__()
	# end def __repr__():

	# ------------------------------------------------------------------------------------------------------------------
	# . 												properties
	# ------------------------------------------------------------------------------------------------------------------
	@property
	def socket(self):
		return self._socket

	# end def socket():

	@socket.setter
	def socket(self, new_parent):
		pm.parent(self.root, new_parent)
		self._socket = new_parent

	# end def socket():

	@property
	def name(self):
		return self._name

	# end def name():

	@name.setter
	def name(self, new_name):
		if self.chain:
			for jnt in self.chain:
				pm.rename(jnt, jnt.replace(self._name, new_name))
		self._name = new_name

	# end def name():

	@property
	def moduleType(self):
		return self._moduleType

	# end def module():

	@moduleType.setter
	def moduleType(self, new_module):
		if self.root.hasAttr('RB_module_type'):
			try:
				self.root.RB_module_type.set(new_module)
			except pm.MayaAttributeEnumError:
				raise ScaffoldException("--This scaffold does not support module type: {}".format(new_module))

		self._moduleType = new_module
	# end def moduleType():

	@property
	def root(self):
		if self.chain:
			return self.chain[0]
		else:
			return None
	# end def root():

	@property
	def length(self):
		if self.chain:
			return len(self.chain)
		else:
			return self._length
	# end def length():

	# ------------------------------------------------------------------------------------------------------------------
	# .											static utility functions
	# ------------------------------------------------------------------------------------------------------------------
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
	# end def getModName():
# end class Scaffold():


# ----------------------------------------------------------------------------------------------------------------------
def makeScaffold(module_type=' ', length=1, name='untitled', socket='root'):
	"""
	Makes new scaffold and reloads modules

	:param module_type: (string) type of module chain will build into
	:param kwargs: builder kwargs, see: rigbot.scaffolds.ScaffoldBase
	:return:
	Builder kwargs: 		length (int) 	= joint chain length
							module (string) = module type to tag module root with
							name (string) 	= naming convention prefix
							socket (PyNode or string) = parent for module, default=root
	"""

	chain = utils.makeJointChain(length, name, user.prefs['bind-skeleton-suffix'])

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
	# end def returnValidParent():

	socket = returnValidParent(socket)

	pm.matchTransform(chain[0], socket)
	pm.parent(chain[0], socket)

	curv = pm.curve(d=1, p=data.controllerShapes['locator'], n=(name + '_display'))
	utils.scaleCtrlShape(curv, scale_mult=0.5, line_width=3)

	shape = curv.getChildren()[0]
	pm.parent(shape, chain[0], r=True, s=True)
	pm.delete(curv)

	# setting colours
	utils.setOverrideColour(user.prefs['default-jnt-colour'], chain)
	utils.setOverrideColour(user.prefs['module-root-colour'], chain[0])
	utils.setOutlinerColour(user.prefs['module-root-colour'], chain[0])
	utils.setOverrideColour(user.prefs['default-jnt-colour'], shape)

	all_modules = utils.getFilteredDir('modules')
	all_modules.append(' ')

	default_tags = [
		{'name': 'RB_MODULE_ROOT', 'at': 'enum', 'en': ' ', 'k': 0, 'l': 1},
		{'name': 'RB_module_type', 'k': 0, 'at': 'enum', 'en': (':'.join(all_modules)),
			'dv': (all_modules.index(module_type))},
		{'name': 'RB_include_end_joint', 'k': 0, 'at': 'bool', 'dv': 1},
	]
	for attr_dict in default_tags:
		utils.makeAttrFromDict(chain[0], attr_dict)

	return Scaffold(chain[0])
# end def addScaffold(self):


# ----------------------------------------------------------------------------------------------------------------------
def batchBuild(modules=None):
	"""
	Batch rig all modules or pass modules to rig

	:param modules: modules to rig
	:return: list of module classes?? ##TODO
	"""
	utils.initiateRig()

	if not modules:
		modules = getModules()

	for module in modules:
		if module.moduleType in utils.getFilteredDir('modules'):
			mod_class = getattr(mod, module.moduleType)
			mod_class(module)
# end def batchBuild():


# ----------------------------------------------------------------------------------------------------------------------
def getModules():
	"""
	Get all of the current modules under the root joint
	:return: List of rigbot module/scaffold objects
	"""
	if user.debug:
		print('>>Fetching modules.')

	if pm.objExists(user.prefs['root-joint']):
		root_jnt = pm.PyNode(user.prefs['root-joint'])
	else:
		return []

	flattened_jnts = root_jnt.getChildren(ad=True, type='joint')

	def isModRoot(jnt):
		return jnt.hasAttr('RB_MODULE_ROOT')
	# end def isModRoot(jnt):

	module_roots = filter(isModRoot, flattened_jnts)

	modules_ls = map(lambda mod_root: Scaffold(module_root=mod_root), module_roots)

	return modules_ls
# end def getModules():
