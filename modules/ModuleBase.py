import pymel.core as pm

from ..rig import utils
from .. import user


# ----------------------------------------------------------------------------------------------------------------------
"""

	MODULEBASE.PY
	contains base class for creating rig modules

"""


# ----------------------------------------------------------------------------------------------------------------------
class ModuleBaseException(Exception):
	pass


class ModuleBase(object):

	# TODO: add extra prefs dict for modules? eg; ctrl shapes, ctrl colours ? anything 'hard coded'

	def __init__(self, scaffold_obj):

		# get attributes from scaffold object
		self.chain = scaffold_obj.chain
		self.name = scaffold_obj.name
		self.socket = scaffold_obj.socket

		# rig globals
		self.rigBase = self.jointsGrp = self.modulesGrp = None

		self.getRigGlobals()

		# module globals
		self.moduleInputs = self.moduleOutputs = self.moduleControls = self.transformGrp = self.noTransformGrp = None

		self.registerModule()

		# rig attributes
		self.controllers = None

		pm.parent(user.prefs['root-joint'], self.jointsGrp)

	# end def __init__():

	# 	def __str__(self):
	# 		return 'rb.{}({})'.format(self.__class__.__name__, self.name)
	# 	# end def __str__():

	# 	def __repr__(self):
	# 		return self.__str__()
	# 	# end def __repr__():

	def registerModule(self):
		self.moduleInputs = pm.group(n=self.name + '_inputs', em=True)
		self.moduleOutputs = pm.group(n=self.name + '_outputs', em=True)
		self.moduleControls = pm.group(n=self.name + '_controls', em=True)
		self.transformGrp = pm.group(n=self.name + '_transform', em=True)
		self.noTransformGrp = pm.group(n=self.name + '_noTransform', em=True)
		mod_grp = pm.group(self.moduleInputs, self.moduleOutputs, self.moduleControls, n=self.name + '_cmpnt')
		rig_dag_grp = pm.group(self.transformGrp, self.noTransformGrp, n=self.name + '_rigDag')
		pm.parent(rig_dag_grp, mod_grp)
		pm.parent(mod_grp, self.modulesGrp)
	# make connections
	# end registerModule():

	def preBuild(self):
		pass

	# ------------------------------------------------------------------------------------------------------------------
	# probably don't want to call build() in the init but from builder after class initialized
	def build(self):
		raise ModuleBaseException('Invalid subclass-- build() function not implemented.')

	# 	# ------------------------------------------------------------------------------------------------------------------
	# 	def buildCleanup(self):
	# 		# eg; transfers custom attrs from module root jnt
	# 		pass
	# 	#end def buildCleanup():

	# ------------------------------------------------------------------------------------------------------------------
	def getRigGlobals(self):

		def validateExists(item):
			if pm.objExists(item):
				return pm.PyNode(item)
			else:
				utils.initiateRig()
				return pm.PyNode(item)

		# TODO: get rigBase decomposeMatrix not node ?
		# TODO: actually all of the globals should probably hook through module inputs node ahh fuck
		self.rigBase = validateExists(user.prefs['root2-ctrl-name'] + '_' + user.prefs['ctrl-suffix'])
		self.jointsGrp = validateExists(user.prefs['joint-group-name'])
		self.modulesGrp = validateExists('modules')
	# end def getRigGlobals():
# end class ModuleBase():
