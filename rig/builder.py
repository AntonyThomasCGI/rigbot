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
	_availableModules = utils.getFilteredDir('modules', ignore_private=False)
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

		if module_root.hasAttr('RB_include_end_joint'):
			self._includeEndJoint = module_root.getAttr('RB_include_end_joint')
		else:
			self._includeEndJoint = 1

		self._name = self.getModName(module_root)
		self._length = set()

		if not self.moduleType == '_Root':
			self.socket = module_root.listRelatives(parent=True)[0]
		else:
			self.socket = None
	# end def __init__():

	def __str__(self):
		return 'rb.{}({})'.format(self.__class__.__name__, self.name)
	# end def __str__():

	def __repr__(self):
		return self.__str__()
	# end def __repr__():

	def __eq__(self, other):
		if isinstance(other, Scaffold):
			return self.moduleType == other.moduleType
		return False
	# end def __eq__():

	def __ne__(self, other):
		return not self.__eq__(other)
	# end def __ne__():

	# ------------------------------------------------------------------------------------------------------------------
	#  													properties
	# ------------------------------------------------------------------------------------------------------------------
	@property
	def socket(self):
		return self._socket
	# end def socket():

	@socket.setter
	def socket(self, new_parent):
		pm.parent(self.root, new_parent)
		self._socket = new_parent
	# end socket.setter

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
	# end name.setter

	# TODO: change moduleType and includeEndJoint getters to actually query the attribute? probably better.

	@property
	def moduleType(self):
		return self._moduleType
	# end def moduleType():

	@moduleType.setter
	def moduleType(self, new_module):
		if self.root.hasAttr('RB_module_type'):
			try:
				self.root.RB_module_type.set(new_module)
			except pm.MayaAttributeEnumError:
				raise ScaffoldException("--This scaffold does not support module type: {}".format(new_module))

		self._moduleType = new_module
	# end moduleType.setter

	@property
	def includeEndJoint(self):
		return self._includeEndJoint
	# end def includeEndJoint():

	@includeEndJoint.setter
	def includeEndJoint(self, new_bool):
		if not isinstance(new_bool, bool):
			raise ValueError('--includeEndJoint has to be set with a bool value')

		if self.root.hasAttr('RB_include_end_joint'):
			self.root.RB_module_type.set(new_module)

		self._includeEndJoint = new_bool
	# end includeEndJoint.setter

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
def makeScaffold(moduleType=' ', length=1, name='untitled', socket='root', includeEnd=1):
	"""
	Makes new scaffold for auto rigger to build from.

	:param moduleType: (string) Type of module chain will build into.
	:param length: (int) Joint chain length.
	:param name: (string) Naming convention prefix.
	:param socket: (PyNode or string) Parent for module.
	:param include_end: (bool) If auto rigger should generate controllers on end joint.
	:return: scaffold class object
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
	utils.scaleCtrlShapes(curv, scale_mult=0.5, line_width=3)

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
			'dv': (all_modules.index(moduleType))},
		{'name': 'RB_include_end_joint', 'k': 0, 'at': 'bool', 'dv': includeEnd},
	]
	for attr_dict in default_tags:
		utils.makeAttrFromDict(chain[0], attr_dict)

	return Scaffold(chain[0])
# end def addScaffold(self):


# ----------------------------------------------------------------------------------------------------------------------
def batchBuild(scaffolds=None):
	"""
	Batch rig all modules or pass modules to rig

	:param modules: list of scaffold objects to rig, if not specified attempts to batch rig every module in scene.
	:return: None
	"""
	if not scaffolds:
		scaffolds = getModules()

	root = next((s for s in scaffolds if s.moduleType == '_Root'), None)
	if root is not None:
		scaffolds.pop(scaffolds.index(root))
		root_module = getattr(mod, root.moduleType)
		root_class = getattr(root_module, root.moduleType)
		root_instance = root_class(root)
		root_instance.registerModule()
		root_instance.preBuild()
		root_instance.build()
		root_instance.postBuild()
		root_instance.encapsulate()

	print('>> Batch Build: Validating Scaffolds...')
	# TODO: something more concrete than just checking moduleType exists here?
	# TODO: potentially this should be implemented in in module classes as well eg;
	# TODO: 		validateJointChain()
	# TODO: 		if biped arm > 3 joints pass errors back, report, default to ' ' module type.

	modules = []
	for scaffold in scaffolds:
		if scaffold.moduleType in utils.getFilteredDir('modules', ignore_private=False):
			mod_module = getattr(mod, scaffold.moduleType)
			mod_class = getattr(mod_module, scaffold.moduleType)
			modules.append(mod_class(scaffold))
		elif scaffold.moduleType == ' ':
			modules.append(mod.ModuleBase(scaffold))
		else:
			print(
				'// Warning: Skipping {}, module type does not appear to be implemented or is missing source code.'.
					format(scaffold.moduleType)
			)

	print('>> Batch Build: Build Starting...')
	for module in modules:
		module.registerModule()

	print('>> Batch Build: Pre Building...')
	for module in modules:
		module.preBuild()

	print('>> Batch Build: Building...')
	for module in modules:
		module.build()

	print('>> Batch Build: Post Building...')
	for module in modules:
		module.postBuild()

	print('>> Batch Build: Encapsulating...')
	for module in modules:
		module.encapsulate()

	print('>> Batch Build: Completed.')
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
	flattened_jnts.append(root_jnt)

	def isModRoot(jnt):
		return jnt.hasAttr('RB_MODULE_ROOT')
	# end def isModRoot(jnt):

	module_roots = filter(isModRoot, flattened_jnts)

	modules_ls = map(lambda mod_root: Scaffold(module_root=mod_root), module_roots)

	return modules_ls
# end def getModules():
