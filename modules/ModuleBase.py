import pymel.core as pm

from .. import user, utils


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
	# maybe could add functor to also take selected objects and get scaffold_obj from that
	# TODO: lock inheritsTransform

	def __init__(self, scaffold_obj):

		# get attributes from scaffold object
		self.chain = scaffold_obj.chain
		self.name = scaffold_obj.name
		self.socket = scaffold_obj.socket
		self.socketDcmp = None

		# rig globals
		self.rigGlobals = {}
		self.getRigGlobals()

		# module globals
		self.modGlobals = {}
		self.registerModule()

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

	# ------------------------------------------------------------------------------------------------------------------
	def preBuild(self):
		# clean joint orients
		# generate ctrls
		raise ModuleBaseException('Invalid subclass-- preBuild() function not implemented.')
	# end def preBuild():

	# ------------------------------------------------------------------------------------------------------------------
	def build(self):
		raise ModuleBaseException('Invalid subclass-- build() function not implemented.')
	# end def build():

	# ------------------------------------------------------------------------------------------------------------------
	def postBuild(self):
		# eg; transfers custom attrs from module root jnt
		# also swaps the BIND jnt connection to socket with module output
		# containers? or maybe separate function
		# can probably implement this once and every module uses it
		pass
	# end def postBuild():

	@property
	def root(self):
		if self.chain:
			return self.chain[0]
		else:
			return None
	# end def root():

	# ------------------------------------------------------------------------------------------------------------------
	# .												utility functions
	# ------------------------------------------------------------------------------------------------------------------
	def getRigGlobals(self):

		def validateExists(item):
			if not pm.objExists(item):
				utils.initiateRig()

			return pm.PyNode(item)
		# end def validateExists():

		self.rigGlobals['rootCtrl'] = validateExists(user.prefs['root2-ctrl-name'] + '_' + user.prefs['ctrl-suffix'])
		self.rigGlobals['jointsGrp'] = validateExists(user.prefs['joint-group-name'])
		self.rigGlobals['modulesGrp'] = validateExists(user.prefs['module-group-name'])
	# end def getRigGlobals():

	# ------------------------------------------------------------------------------------------------------------------
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
# end class ModuleBase():
