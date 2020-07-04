import pymel.core as pm

from .. import user
import utils

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
	rig all un-rigged modules
	"""

	if not modules:
		modules = getModules()

	for module in modules:
		if module.moduleType in utils.getFilteredDir('modules'):
			mod_class = getattr(mod, module.moduleType)
			mod_class(module)
# end def batchBuild(self):


# ----------------------------------------------------------------------------------------------------------------------
def getModules():
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
	sel = pm.selected()
	mod_ls = []
	for item in sel:
		if item.hasAttr('RB_MODULE_ROOT'):
			mod_ls.append(scaf.Scaffold(module_root=item))
		else:
			print('// Warning: ignoring %s as it is not a module root' % item)
	return mod_ls
# end def selected():
