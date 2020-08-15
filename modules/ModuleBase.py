# ----------------------------------------------------------------------------------------------------------------------
"""

	MODULEBASE.PY
	contains base class for creating rig modules

"""
# ----------------------------------------------------------------------------------------------------------------------

import pymel.core as pm

from .. import user, utils


# ----------------------------------------------------------------------------------------------------------------------
class ModuleBaseException(Exception):
	pass


class ModuleBase(object):

	# TODO: add extra prefs dict for modules? eg; ctrl shapes, ctrl colours ? anything 'hard coded'
	# maybe could add functor to also take selected objects and get scaffold_obj from that
	# TODO: lock inheritsTransform

	def __init__(self, scaffold_obj):

		# get attributes from scaffold object
		self.chain = scaffold_obj.chain
		self.name = scaffold_obj.name
		self.socket = scaffold_obj.socket
		self.includeEndJoint = scaffold_obj.includeEndJoint
		self.socketDcmp = None

		# get rig globals
		# TODO: maybe don't need rootCtrl or jointsGrp here? > would need cog_ctrl?
		try:
			self.rigGlobals = {
				'rootCtrl': pm.PyNode(user.prefs['root2-ctrl-name'] + '_' + user.prefs['ctrl-suffix']),
				'jointsGrp': pm.PyNode(user.prefs['joint-group-name']),
				'modulesGrp': pm.PyNode(user.prefs['module-group-name']),
			}
		except pm.MayaNodeError:
			raise ModuleBaseException('--Rig has not been initiated. try use utils.initiateRig().')

		# module globals
		self.modGlobals = {}

		# module attributes
		self.controllers = []
	# end def __init__():

	def __str__(self):
		return 'rb.{}({})'.format(self.__class__.__name__, self.name)
	# end def __str__():

	def __repr__(self):
		return self.__str__()
	# end def __repr__():

	def __len__(self):
		if self.chain:
			return len(self.chain)
		else:
			return 0
	# end def __len__():

	def registerModule(self):
		# make null hierarchy
		self.modGlobals['modInput'] = pm.group(n=self.name + '_input', em=True)
		self.modGlobals['modOutput'] = pm.group(n=self.name + '_output', em=True)
		self.modGlobals['modCtrls'] = pm.group(n=self.name + '_controls', em=True)
		self.modGlobals['transformGrp'] = pm.group(n=self.name + '_transform', em=True)
		self.modGlobals['noTransformGrp'] = pm.group(n=self.name + '_noTransform', em=True)

		mod_grp = pm.group(
			self.modGlobals['modInput'], self.modGlobals['modOutput'], self.modGlobals['modCtrls'], n=self.name + '_mod'
		)
		rig_dag_grp = pm.group(
			self.modGlobals['transformGrp'], self.modGlobals['noTransformGrp'], n=self.name + '_rigDag'
		)
		pm.parent(rig_dag_grp, mod_grp)
		pm.parent(mod_grp, self.rigGlobals['modulesGrp'])

		# make connections
		utils.makeAttrFromDict(self.modGlobals['modInput'], {'name': 'RB_Socket', 'at': 'matrix'})
		self.socket.worldMatrix[0] >> self.modGlobals['modInput'].RB_Socket

		self.socketDcmp = pm.createNode('decomposeMatrix', n=self.name + '_socket_dcmpM')
		self.modGlobals['modInput'].RB_Socket >> self.socketDcmp.inputMatrix

		for item in [self.modGlobals['modCtrls'], self.modGlobals['transformGrp']]:
			self.socketDcmp.outputTranslate >> item.translate
			self.socketDcmp.outputRotate >> item.rotate
			self.socketDcmp.outputScale >> item.scale
	# end registerModule():

	# ------------------------------------------------------------------------------------------------------------------
	def preBuild(self):
		# clean joint orients
		# generate ctrls
		# TODO: need to reset bind pose here if bind joints already connected to skin cluster
		utils.cleanJointOrients(self.chain)
		utils.cleanScaleCompensate(self.chain)
		# raise ModuleBaseException('Invalid subclass-- preBuild() function not implemented.')
	# end def preBuild():

	# ------------------------------------------------------------------------------------------------------------------
	def build(self):
		raise ModuleBaseException('Invalid subclass-- build() function not implemented.')
	# end def build():

	# ------------------------------------------------------------------------------------------------------------------
	def postBuild(self):
		# eg; transfers custom attrs from module root jnt
		# also swaps the BIND jnt connection to socket with module output
		# can probably implement this once and every module uses it
		pass
	# end def postBuild():

	def containerize(self):
		# can hopefully implement this once, similar to dismantle(), just get every node connected to module
		pass

	def dismantle(self):
		# deconstruct destroy, discombobulate.
		# can hopefully figure out a nice way to make this work for every module.
		pass
	# end def dismantle():

	@property
	def root(self):
		if self.chain:
			return self.chain[0]
		else:
			return None
	# end def root():

	# ------------------------------------------------------------------------------------------------------------------
	# 												utility functions
	# ------------------------------------------------------------------------------------------------------------------

# end class ModuleBase():
