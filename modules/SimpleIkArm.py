# ----------------------------------------------------------------------------------------------------------------------
"""

	SIMPLEIKARM.PY
	simple 3 chain ik

"""
# ----------------------------------------------------------------------------------------------------------------------

from .ModuleBase import ModuleBase

from ..rig import controls as ctrl
from .. import utils

import pymel.core as pm


class SimpleIkArm(ModuleBase):
	def __init__(self, *args):
		super(SimpleIkArm, self).__init__(*args)
	#  end def __init__():

	def preBuild(self):
		super(SimpleIkArm, self).preBuild()

		global_socket = self.makeGlobalSocket()

		base_ctrl = ctrl.control(name='%s_base_ctrl' % self.name, shape='square', colour='dark-cyan', size=1.2)
		ik_ctrl = ctrl.control(name='%s_ik_ctrl' % self.name, shape='cube', colour='light-orange')
		pv_ctrl = ctrl.control(name='%s_pv_ctrl' % self.name, shape='winged-pole', colour='cyan', size=0.5)

		self.controllers = [base_ctrl, pv_ctrl, ik_ctrl]
		for ctrl_item in self.controllers:
			pm.parent(ctrl_item.null, self.modGlobals['modCtrls'])

		ik_ctrl_param = [
			{'name': 'humerus', 'dv': self.chain[1].translateX.get()},
			{'name': 'radius', 'dv': self.chain[2].translateX.get()},
			{'name': 'stretch', 'at': 'bool'},
		]
		for param in ik_ctrl_param:
			utils.makeAttrFromDict(ik_ctrl.ctrl, param)

		pm.matchTransform(base_ctrl.null, self.chain[0])
		pm.matchTransform(ik_ctrl.null, self.chain[-1])

		joint_vectors = map(lambda x: pm.xform(x, q=True, t=True, ws=True), self.chain)

		pole_vector_position = utils.positionUpVectorFromPoints(*joint_vectors)

		pm.xform(pv_ctrl.null, t=pole_vector_position, ws=True)

		# TODO: space switches not constraints.
		utils.matrixConstraint(global_socket, ik_ctrl.null, pv_ctrl.null, ss='xyz', ip=self.modGlobals['modCtrls'])
	# end def preBuild():

	def build(self):

		#TODO: if negative x axis, extra mdl before output_02_compM.inputTranslateX
		#TODO: and also mdl -1 before output_03_fourM.30
		#TODO: also * -1 on expr :thinking: maybe better way


		stretchLimiter_clmp = pm.createNode('clamp', n='{}_stretchLimiter_clmp'.format(self.name))
		radiusStretch_mdl = pm.createNode('multDoubleLinear', n='{}_radiusStretch_mdl'.format(self.name))
		base_ctrl_dcmpM = pm.createNode('decomposeMatrix', n='{}_base_ctrl_dcmpM'.format(self.name))
		ik_rotations_compM = pm.createNode('composeMatrix', n='{}_ik_rotations_compM'.format(self.name))
		dist_scale_md = pm.createNode('multiplyDivide', n='{}_dist_scale_md'.format(self.name))
		stretch_blndA = pm.createNode('blendTwoAttr', n='{}_stretch_blndA'.format(self.name))
		base_aim_dcmpM = pm.createNode('decomposeMatrix', n='{}_base_aim_dcmpM'.format(self.name))
		stretchPercent_md = pm.createNode('multiplyDivide', n='{}_stretchPercent_md'.format(self.name))
		zVec_vecMtxProd = pm.createNode('vectorProduct', n='{}_03_zVec_vecMtxProd'.format(self.name))
		ctrl_distB = pm.createNode('distanceBetween', n='{}_ctrl_distB'.format(self.name))
		rot_inv_trnpM = pm.createNode('transposeMatrix', n='{}_02_trnpM'.format(self.name))
		output_03_fourM = pm.createNode('fourByFourMatrix', n='{}_03_result_fourM'.format(self.name))
		socket_invertM = pm.createNode('inverseMatrix', n='{}_socket_invertM'.format(self.name))
		baseLength_scale_mdl = pm.createNode('multDoubleLinear', n='{}_baseLength_scale_mdl'.format(self.name))
		output_02_compM = pm.createNode('composeMatrix', n='{}_02_BIND_compM'.format(self.name))
		pv_ctrl_dcmpM = pm.createNode('decomposeMatrix', n='{}_pv_ctrl_dcmpM'.format(self.name))
		ctrl_dcmpM = pm.createNode('decomposeMatrix', n='{}_ctrl_dcmpM'.format(self.name))
		baseLength_adl = pm.createNode('addDoubleLinear', n='{}_baseLength_adl'.format(self.name))
		base_aim_compM = pm.createNode('composeMatrix', n='{}_base_aim_compM'.format(self.name))
		world_02_multM = pm.createNode('multMatrix', n='{}_02_worldSpace_multM'.format(self.name))
		limited_vec_clmp = pm.createNode('clamp', n='{}_limited_vec_clmp'.format(self.name))
		xVec_vecMtxProd = pm.createNode('vectorProduct', n='{}_03_xVec_vecMtxProd'.format(self.name))
		output_01_multM = pm.createNode('multMatrix', n='{}_01_result_multM'.format(self.name))
		humerusStretch_mdl = pm.createNode('multDoubleLinear', n='{}_humerusStretch_mdl'.format(self.name))
		base_aim_matrix = pm.createNode('fourByFourMatrix', n='{}_base_aim_matrix'.format(self.name))
		localRot_03_multM = pm.createNode('multMatrix', n='{}_03_localRot_multM'.format(self.name))
		pv_localVec_pma = pm.createNode('plusMinusAverage', n='{}_pv_localVec_pma'.format(self.name))
		yVec_vecMtxProd = pm.createNode('vectorProduct', n='{}_03_yVec_vecMtxProd'.format(self.name))
		# ik_expr = pm.createNode('expression', n='{}_ik_expr'.format(self.name))
		base_aim_yVec_crsP = pm.createNode('vectorProduct', n='{}_base_aim_yVec_crsP'.format(self.name))
		localVec_pma = pm.createNode('plusMinusAverage', n='{}_localVec_pma'.format(self.name))

		# Make expression, set expression string.
		expr_string = """
float $a = {0}.radius;
float $b = {0}.humerus;
float $c = {1}.outputX;

float $a_sqr = `pow $a 2`;
float $b_sqr = `pow $b 2`;
float $c_sqr = `pow $c 2`;

{2}.inputRotateY = -(deg_to_rad(180) - (acos(($a_sqr + $b_sqr - $c_sqr)/(2 * $a * $b))));
{3}.inputRotateY = (acos(($b_sqr + $c_sqr - $a_sqr)/(2 * $b * $c)));
""".format(self.controllers[2].ctrl, dist_scale_md, output_02_compM, ik_rotations_compM)
		print('here1')
		ik_expr = pm.expression(s=expr_string, n='{}_ik_expr'.format(self.name))
		print('here2')
		print(ik_expr)
		pm.expression(ik_expr, e=True, unitConversion='none')

		stretch_blndA.setAttr('input[0]', 1)
		stretch_blndA.setAttr('input[1]', 100)
		stretchLimiter_clmp.setAttr('minR', 1.0)
		dist_scale_md.setAttr('operation', 2)
		stretchPercent_md.setAttr('operation', 2)
		zVec_vecMtxProd.setAttr('operation', 3)
		zVec_vecMtxProd.setAttr('input1Z', 1.0)
		limited_vec_clmp.setAttr('minR', 1.0)
		xVec_vecMtxProd.setAttr('input1X', 1.0)
		xVec_vecMtxProd.setAttr('operation', 3)
		pv_localVec_pma.setAttr('operation', 2)
		yVec_vecMtxProd.setAttr('input1Y', 1.0)
		yVec_vecMtxProd.setAttr('operation', 3)
		base_aim_yVec_crsP.setAttr('operation', 2)
		localVec_pma.setAttr('operation', 2)

		stretchPercent_md.outputX >> stretchLimiter_clmp.inputR
		stretch_blndA.output >> stretchLimiter_clmp.maxR
		self.controllers[2].ctrl.radius >> radiusStretch_mdl.input1
		stretchLimiter_clmp.outputR >> radiusStretch_mdl.input2
		self.controllers[0].ctrl.worldMatrix[0] >> base_ctrl_dcmpM.inputMatrix
		limited_vec_clmp.outputR >> dist_scale_md.input1X
		self.socketDcmp.outputScaleX >> dist_scale_md.input2X
		self.controllers[2].ctrl.stretch >> stretch_blndA.attributesBlender
		base_aim_matrix.output >> base_aim_dcmpM.inputMatrix
		baseLength_scale_mdl.output >> stretchPercent_md.input2X
		ctrl_distB.distance >> stretchPercent_md.input1X
		localRot_03_multM.matrixSum >> zVec_vecMtxProd.matrix
		base_ctrl_dcmpM.outputTranslate >> ctrl_distB.point1
		ctrl_dcmpM.outputTranslate >> ctrl_distB.point2
		world_02_multM.matrixSum >> rot_inv_trnpM.inputMatrix
		xVec_vecMtxProd.outputX >> output_03_fourM.in00
		xVec_vecMtxProd.outputY >> output_03_fourM.in01
		xVec_vecMtxProd.outputZ >> output_03_fourM.in02
		yVec_vecMtxProd.outputY >> output_03_fourM.in11
		yVec_vecMtxProd.outputZ >> output_03_fourM.in12
		zVec_vecMtxProd.outputX >> output_03_fourM.in20
		zVec_vecMtxProd.outputY >> output_03_fourM.in21
		zVec_vecMtxProd.outputZ >> output_03_fourM.in22
		yVec_vecMtxProd.outputX >> output_03_fourM.in10
		radiusStretch_mdl.output >> output_03_fourM.in30
		self.modGlobals['modInput'].RB_Socket >> socket_invertM.inputMatrix
		baseLength_adl.output >> baseLength_scale_mdl.input1
		self.socketDcmp.outputScaleX >> baseLength_scale_mdl.input2
		humerusStretch_mdl.output >> output_02_compM.inputTranslateX
		self.controllers[1].ctrl.worldMatrix[0] >> pv_ctrl_dcmpM.inputMatrix
		self.controllers[2].ctrl.worldMatrix[0] >> ctrl_dcmpM.inputMatrix
		self.controllers[2].ctrl.humerus >> baseLength_adl.input1
		self.controllers[2].ctrl.radius >> baseLength_adl.input2
		base_aim_dcmpM.outputRotate >> base_aim_compM.inputRotate
		base_ctrl_dcmpM.outputTranslate >> base_aim_compM.inputTranslate
		output_02_compM.outputMatrix >> world_02_multM.matrixIn[0]
		output_01_multM.matrixSum >> world_02_multM.matrixIn[1]
		self.modGlobals['modInput'].RB_Socket >> world_02_multM.matrixIn[2]
		ctrl_distB.distance >> limited_vec_clmp.inputR
		baseLength_scale_mdl.output >> limited_vec_clmp.maxR
		localRot_03_multM.matrixSum >> xVec_vecMtxProd.matrix
		ik_rotations_compM.outputMatrix >> output_01_multM.matrixIn[0]
		base_aim_compM.outputMatrix >> output_01_multM.matrixIn[1]
		socket_invertM.outputMatrix >> output_01_multM.matrixIn[2]
		stretchLimiter_clmp.outputR >> humerusStretch_mdl.input2
		self.controllers[2].ctrl.humerus >> humerusStretch_mdl.input1
		localVec_pma.output3Dx >> base_aim_matrix.in00
		localVec_pma.output3Dy >> base_aim_matrix.in01
		localVec_pma.output3Dz >> base_aim_matrix.in02
		base_aim_yVec_crsP.outputX >> base_aim_matrix.in10
		base_aim_yVec_crsP.outputY >> base_aim_matrix.in11
		base_aim_yVec_crsP.outputZ >> base_aim_matrix.in12
		pv_localVec_pma.output3Dz >> base_aim_matrix.in22
		pv_localVec_pma.output3Dy >> base_aim_matrix.in21
		pv_localVec_pma.output3Dx >> base_aim_matrix.in20
		self.controllers[2].ctrl.worldMatrix[0] >> localRot_03_multM.matrixIn[0]
		rot_inv_trnpM.outputMatrix >> localRot_03_multM.matrixIn[1]
		pv_ctrl_dcmpM.outputTranslate >> pv_localVec_pma.input3D[0]
		base_ctrl_dcmpM.outputTranslate >> pv_localVec_pma.input3D[1]
		localRot_03_multM.matrixSum >> yVec_vecMtxProd.matrix
		localVec_pma.output3D >> base_aim_yVec_crsP.input1
		pv_localVec_pma.output3D >> base_aim_yVec_crsP.input2
		ctrl_dcmpM.outputTranslate >> localVec_pma.input3D[0]
		base_ctrl_dcmpM.outputTranslate >> localVec_pma.input3D[1]

		# Handle outputs
		hold_outputs = [
			{'name': '%s_out' % self.chain[0], 'at': 'matrix'},
			{'name': '%s_out' % self.chain[1], 'at': 'matrix'},
			{'name': '%s_out' % self.chain[2], 'at': 'matrix'},
		]
		joint_outputs = []
		for output in hold_outputs:
			joint_outputs.append(utils.makeAttrFromDict(self.modGlobals['modOutput'], output))

		output_01_multM.matrixSum >> joint_outputs[0]
		output_02_compM.outputMatrix >> joint_outputs[1]
		output_03_fourM.output >> joint_outputs[2]

		chain_01_dcmpM = pm.createNode('decomposeMatrix', n='{}_dcmpM'.format(self.chain[0]))
		chain_02_dcmpM = pm.createNode('decomposeMatrix', n='{}_dcmpM'.format(self.chain[1]))
		chain_03_dcmpM = pm.createNode('decomposeMatrix', n='{}_dcmpM'.format(self.chain[2]))

		joint_outputs[0] >> chain_01_dcmpM.inputMatrix
		joint_outputs[1] >> chain_02_dcmpM.inputMatrix
		joint_outputs[2] >> chain_03_dcmpM.inputMatrix

		chain_01_dcmpM.outputTranslate >> self.chain[0].translate
		chain_02_dcmpM.outputTranslate >> self.chain[1].translate
		chain_03_dcmpM.outputTranslate >> self.chain[2].translate
		chain_01_dcmpM.outputRotate >> self.chain[0].rotate
		chain_02_dcmpM.outputRotate >> self.chain[1].rotate
		chain_03_dcmpM.outputRotate >> self.chain[2].rotate
	# end def build():
# end class SimpleIkArm():
