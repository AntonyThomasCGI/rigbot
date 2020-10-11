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
		if pm.objExists(user.prefs['module-group-name']):
			self.rigModuleGrp = pm.PyNode(user.prefs['module-group-name'])
		else:
			self.rigModuleGrp = None

		# module globals
		self.modGlobals = {}

		# module attributes
		self.controllers = {}
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
		# TODO: output null matrix per joint created here?
		# make null hierarchy
		self.modGlobals['modInput'] = pm.group(n=self.name + '_input', em=True)
		self.modGlobals['modOutput'] = pm.group(n=self.name + '_output', em=True)
		self.modGlobals['modCtrls'] = pm.group(n=self.name + '_controls', em=True)
		self.modGlobals['transformGrp'] = pm.group(n=self.name + '_transform', em=True)
		self.modGlobals['noTransformGrp'] = pm.group(n=self.name + '_noTransform', em=True)

		self.modGlobals['modRoot'] = pm.group(
			self.modGlobals['modInput'], self.modGlobals['modOutput'], self.modGlobals['modCtrls'], n=self.name + '_mod'
		)
		rig_dag_grp = pm.group(
			self.modGlobals['transformGrp'], self.modGlobals['noTransformGrp'], n=self.name + '_rigDag'
		)
		pm.parent(rig_dag_grp, self.modGlobals['modRoot'])
		pm.parent(self.modGlobals['modRoot'], self.rigModuleGrp)

		utils.makeAttrFromDict(self.modGlobals['modOutput'], {'name': 'RB_Output', 'at': 'matrix', 'multi': True})

		# make connections
		utils.makeAttrFromDict(self.modGlobals['modInput'], {'name': 'RB_Socket', 'at': 'matrix'})

		if self.socket.shortName() == user.prefs['root-joint']:
			pivot_name = '{}_{}'.format(user.prefs['pivot-ctrl-name'], user.prefs['ctrl-suffix'])
			if pm.objExists(pivot_name):
				pm.PyNode(pivot_name).worldMatrix[0] >> self.modGlobals['modInput'].RB_Socket
			else:
				raise ModuleBaseException('--Pivot ctrl does not exist: {}'.format(pivot_name))
		else:
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
		utils.cleanJointOrients(self.chain)
		utils.cleanScaleCompensate(self.chain)
		# raise ModuleBaseException('Invalid subclass-- preBuild() function not implemented.')
	# end def preBuild():

	# ------------------------------------------------------------------------------------------------------------------
	def build(self):
		# raise ModuleBaseException('Invalid subclass-- build() function not implemented.')
		# maybe can send ' ' through this class if don't error for not implementing functions.
		pass
	# end def build():

	# ------------------------------------------------------------------------------------------------------------------
	def postBuild(self):
		# eg; transfers custom attrs from module root jnt
		# also swaps the BIND jnt connection to socket with module output
		# can probably implement this once and every module uses it
		root_shape = self.root.getShape()
		if root_shape:
			pm.delete(root_shape)
		self.root.useOutlinerColor.set(0)

		for i, jnt in enumerate(self.chain):
			multm = pm.createNode('multMatrix', n='{}_out_multM'.format(jnt))
			dcmp = pm.createNode('decomposeMatrix', n='{}_out_dcmpM'.format(jnt))

			self.outputPlug[i] >> multm.matrixIn[0]
			jnt.parentInverseMatrix >> multm.matrixIn[1]
			multm.matrixSum >> dcmp.inputMatrix

			dcmp.outputTranslate >> jnt.translate
			dcmp.outputRotate >> jnt.rotate
			# TODO: maybe, scale connection could be class global variable possible _connect_scale = False
	# end def postBuild():

	# ------------------------------------------------------------------------------------------------------------------
	def encapsulate(self):
		contain = pm.createNode('container', name=self.name)

		contain.addNode(utils.getModuleNodes(self.modGlobals['modRoot']))

		publish_count = 1
		for c in self.controllers.values():
			publish_plug = contain.attr('publishedNodeInfo')
			this_publish = publish_plug.elementByLogicalIndex(publish_count)

			c.ctrl.message >> this_publish.publishedNode

			publish_count += 1

			for o in c.offsets:  # publish ctrl offsets if any
				this_offset_publish = publish_plug.elementByLogicalIndex(publish_count)

				o.message >> this_offset_publish.publishedNode

				publish_count += 1

	# ------------------------------------------------------------------------------------------------------------------
	def dismantle(self):
		# deconstruct destroy, discombobulate, derig, delete.
		# can hopefully figure out a nice way to make this work for every module.
		# if containerized, decontainerize
		# uhh should this just be function somewhere.. hard to remake this class maybe?
		pass
	# end def dismantle():

	@property
	def root(self):
		if self.chain:
			return self.chain[0]
		else:
			return None
	# end def root():

	@property
	def socketPlug(self):
		return self.modGlobals['modInput'].attr('RB_Socket')
	# end def socketPlug():

	@property
	def outputPlug(self):
		return self.modGlobals['modOutput'].attr('RB_Output')
	# end def outputPlug():

	@property
	def globalPlug(self):
		if self.modGlobals['modInput'].hasAttr('RB_World'):
			return self.modGlobals['modInput'].attr('RB_World')
		else:
			return None
	# end def globalPlug():

	# ------------------------------------------------------------------------------------------------------------------
	# 												utility functions
	# ------------------------------------------------------------------------------------------------------------------
	def makeGlobalSocket(self):
		"""
		Add rig world space socket to module input null for modules that need world space ctrls such as ik handles.
		:return: PyNode attribute plug
		"""
		utils.makeAttrFromDict(self.modGlobals['modInput'], {'name': 'RB_World', 'at': 'matrix'})
		rig_global_ctrl = pm.PyNode('{}_{}'.format(user.prefs['root2-ctrl-name'], user.prefs['ctrl-suffix']))

		rig_global_ctrl.worldMatrix[0] >> self.modGlobals['modInput'].RB_World

		return self.globalPlug
	# end def makeGlobalSocket():
# end class ModuleBase():
