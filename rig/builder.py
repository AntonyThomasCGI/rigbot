import pymel.core as pm

from .. import user

from . import controls, utils

from .. import scaffolds as scaf
from .. import modules as mod


# ----------------------------------------------------------------------------------------------------------------------
"""

	BUILDER.PY
	Manage and build scaffold/rig classes

"""
# ----------------------------------------------------------------------------------------------------------------------


class BuilderException(Exception):
	pass


# ----------------------------------------------------------------------------------------------------------------------
# def addScaffold(self, module_type, **kwargs):
# 	"""
# 	Makes new scaffold and reloads modules
#
# 	:param module_type: (string) module type
# 	:param kwargs: builder kwargs, see: rigbot.scaffolds.ScaffoldBase
# 	:return:
# 	"""
#
# 	new_scaf = None
# 	for scaf_class in self.scaffold_classes:
# 		scaffold_class = getattr(scaf, scaf_class)
# 		if module_type in scaffold_class._availableModules:
# 			new_scaf = scaffold_class(moduleType=module_type, **kwargs)
# 			continue
#
# 	if not new_scaf:
# 		raise TypeError('No valid modules found for module type: %s' % module_type)
#
# 	self._modules.append(new_scaf)
#
# 	return new_scaf
# # end def addScaffold(self):


# ----------------------------------------------------------------------------------------------------------------------
def batchBuild(modules=None):
	"""
	Batch rig all modules or pass modules to rig

	:param modules: modules to rig
	:return: list of module classes?? ##TODO
	"""

	if not modules:
		modules = getModules()

	for module in modules:
		if module.moduleType in utils.getFilteredDir('modules'):
			mod_class = getattr(mod, module.moduleType)
			mod_class(module)
# end def batchBuild():


# ----------------------------------------------------------------------------------------------------------------------
def initiateRig():
	"""
	Creates default rig hierarchy to socket rig modules into
	:return: dict of groups and ctrls
	"""
	rig_dict = {}

	def safeMakeNode(component, socket):

		if component == user.prefs['root-ctrl-name']:
			if pm.objExists(user.prefs['root-ctrl-name'] + '_' + user.prefs['ctrl-suffix']):
				return pm.PyNode(user.prefs['root-ctrl-name'] + '_' + user.prefs['ctrl-suffix'])

			god_ctrl = pm.circle(n=(component + '_' + user.prefs['ctrl-suffix']), nry=1, nrz=0, ch=False)[0]

			utils.setOverrideColour('grey', god_ctrl)
			utils.scaleCtrlShape(god_ctrl, scale_mult=45, line_width=-1)
			for axis in ['X', 'Z']:
				pm.connectAttr('{}.scaleY'.format(god_ctrl), '{}.scale{}'.format(god_ctrl, axis))
				pm.setAttr('{}.scale{}'.format(god_ctrl, axis), lock=True)

			god2_ctrl = controls.control(
				name=user.prefs['root2-ctrl-name'], shape='omni-circle', size=10.2, colour='pale-orange')
			pm.parent(god2_ctrl.null, god_ctrl)

			if socket != 'World':
				pm.parent(god_ctrl, socket)

			return god_ctrl
		# component must be group at this point
		else:
			if pm.objExists(component):
				return pm.PyNode(component)

			grp = pm.group(n=component, em=True)
			if socket != 'World':
				pm.parent(grp, socket)
			return grp
	# end def safeMakeNode():

	def walkTreeWithParent(tree, socket='World'):

		socket = safeMakeNode(tree.component, socket)
		rig_dict[tree.component] = socket

		if not tree.children:
			return

		for child in tree.children:
			walkTreeWithParent(child, socket)
	# end def walkTreeWithParent():

	walkTreeWithParent(user.RigTree)

	# make connections
	for item in rig_dict:
		print item

	return rig_dict
# end def initiateRig():


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

	modules_ls = map(lambda mod_root: scaf.Scaffold(module_root=mod_root), module_roots)

	return modules_ls
# end def getModules():


# ----------------------------------------------------------------------------------------------------------------------
def selected():
	"""
	Convenience function for getting rigbot objects from selected
	:return: rigbot objects for currently selected module roots
	"""
	sel = pm.selected()
	mod_ls = []
	for item in sel:
		if item.hasAttr('RB_MODULE_ROOT'):
			mod_ls.append(scaf.Scaffold(module_root=item))
		else:
			print('// Warning: ignoring %s as it is not a module root' % item)
	return mod_ls
# end def selected():
