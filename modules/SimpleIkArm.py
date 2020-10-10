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

		base_ctrl = ctrl.control(name='%s_base' % self.name, shape='square', colour='dark-cyan', size=1.2)
		ik_ctrl = ctrl.control(name='%s_ik' % self.name, shape='cube', colour='light-orange')
		pv_ctrl = ctrl.control(name='%s_pv' % self.name, shape='winged-pole', colour='cyan', size=0.5)

		self.controllers = [base_ctrl, pv_ctrl, ik_ctrl]
		for ctrl_item in self.controllers:
			pm.parent(ctrl_item.null, self.modGlobals['modCtrls'])

		ik_ctrl_param = [
			{'name': 'humerus', 'dv': abs(self.chain[1].translateX.get())},
			{'name': 'radius', 'dv': abs(self.chain[2].translateX.get())},
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


		# orientation down chain: mult for x axis in aim mat
		# check for maya math nodes,
		#  		use abs or use ** sqrt
		#  		use acos or use expression


		# option 1 for -x:
		#		-1 mult after distance clamp
		#		-1 mult animBlend after shoulder acos
		#		SWITCHED INPUTS:
		# 		===================
		#		_localVec_pma
		# 		_pv_localVec_pma
		# 		_base_aim_zVec_crsP

		# # get aim axis
		# vec_ls = zip(
		# 	(pm.xform(self.chain[0], q=True, t=True, ws=True)),
		# 	(pm.xform(self.chain[1], q=True, t=True, ws=True))
		# )
		#
		# local_vec = [(t[1] - t[0]) for t in vec_ls]
		# mtx = self.chain[0].worldMatrix[0].get()
		#
		# x_vec, y_vec, z_vec = [row[0:3] for row in mtx[0:3]]
		#
		# def dot(vec1, vec2):
		# 	return sum(x_i * y_i for x_i, y_i in zip(vec1, vec2))
		#
		# dot_data = {
		# 	'X': dot(x_vec, local_vec),
		# 	'Y': dot(y_vec, local_vec),
		# 	'Z': dot(z_vec, local_vec),
		# }
		# axis = 'X'
		# max_dot = max(dot_data, key=dot_data.get)
		axis = 'X'
		if self.chain[1].translateX.get() < 0:
			axis = '-X'

		stretchLimiter_clmp = pm.createNode('clamp', n='{}_stretchLimiter_clmp'.format(self.name))
		radiusStretch_mdl = pm.createNode('multDoubleLinear', n='{}_radiusStretch_mdl'.format(self.name))
		base_ctrl_dcmpM = pm.createNode('decomposeMatrix', n='{}_base_ctrl_dcmpM'.format(self.name))
		ik_rotations_compM = pm.createNode('composeMatrix', n='{}_ik_rotations_compM'.format(self.name))
		dist_scale_md = pm.createNode('multiplyDivide', n='{}_dist_scale_md'.format(self.name))
		stretch_blndA = pm.createNode('blendTwoAttr', n='{}_stretch_blndA'.format(self.name))
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
		localVec_norm = pm.createNode('vectorProduct', n='{}_localVec_normalize'.format(self.name))
		base_aim_zVec_crsP = pm.createNode('vectorProduct', n='{}_base_aim_zVec_crsP'.format(self.name))
		world_02_multM = pm.createNode('multMatrix', n='{}_02_worldSpace_multM'.format(self.name))
		limited_vec_clmp = pm.createNode('clamp', n='{}_limited_vec_clmp'.format(self.name))
		xVec_vecMtxProd = pm.createNode('vectorProduct', n='{}_03_xVec_vecMtxProd'.format(self.name))
		output_01_multM = pm.createNode('multMatrix', n='{}_01_result_multM'.format(self.name))
		humerusStretch_mdl = pm.createNode('multDoubleLinear', n='{}_humerusStretch_mdl'.format(self.name))
		base_aim_matrix = pm.createNode('fourByFourMatrix', n='{}_base_aim_matrix'.format(self.name))
		localRot_03_multM = pm.createNode('multMatrix', n='{}_03_localRot_multM'.format(self.name))
		pv_localVec_pma = pm.createNode('plusMinusAverage', n='{}_pv_localVec_pma'.format(self.name))
		yVec_vecMtxProd = pm.createNode('vectorProduct', n='{}_03_yVec_vecMtxProd'.format(self.name))
		base_aim_yVec_crsP = pm.createNode('vectorProduct', n='{}_base_aim_yVec_crsP'.format(self.name))
		localVec_pma = pm.createNode('plusMinusAverage', n='{}_localVec_pma'.format(self.name))
		elbow_rot_min180_animBlend = pm.createNode('animBlendNodeAdditiveDA', n='{}_elbow_min180_ab'.format(self.name))
		elbow_triAngle_acos = pm.createNode('math_Acos', n='{}_elbow_triAngle_acos'.format(self.name))
		elbow_incos_md = pm.createNode('multiplyDivide', n='{}_elbow_incos_md'.format(self.name))
		shoulder_incos_md = pm.createNode('multiplyDivide', n='{}_shoulder_incos_md'.format(self.name))
		add_b_c_sqr_adl = pm.createNode('addDoubleLinear', n='{}_add_b_c_sqr_adl'.format(self.name))
		minus_a_pma = pm.createNode('plusMinusAverage', n='{}_minus_a_pma'.format(self.name))
		shoulder_angle_acos = pm.createNode('math_Acos', n='{}_shoulder_angle_acos'.format(self.name))
		minus_c_pma = pm.createNode('plusMinusAverage', n='{}_minus_c_pma'.format(self.name))
		a_b_prod_mdl = pm.createNode('multDoubleLinear', n='{}_a_b_prod_mdl'.format(self.name))
		dist_c_sqr_mdl = pm.createNode('multDoubleLinear', n='{}_dist_c_sqr_mdl'.format(self.name))
		humerus_b_sqr_mdl = pm.createNode('multDoubleLinear', n='{}_humerus_b_sqr_mdl'.format(self.name))
		add_a_b_sqr_adl = pm.createNode('addDoubleLinear', n='{}_add_a_b_sqr_adl'.format(self.name))
		b_double_prod_mdl = pm.createNode('multDoubleLinear', n='{}_b_double_prod_mdl'.format(self.name))
		b_c_prod_mdl = pm.createNode('multDoubleLinear', n='{}_b_c_prod_mdl'.format(self.name))
		radius_a_sqr_mdl = pm.createNode('multDoubleLinear', n='{}_radius_a_sqr_mdl'.format(self.name))

		elbow_rot_min180_animBlend.setAttr('inputB', -180.0)
		elbow_incos_md.setAttr('operation', 2)
		shoulder_incos_md.setAttr('operation', 2)
		minus_a_pma.setAttr('operation', 2)
		minus_c_pma.setAttr('operation', 2)
		b_double_prod_mdl.setAttr('input2', 2.000001)
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
		base_aim_yVec_crsP.setAttr('normalizeOutput', 1)
		base_aim_zVec_crsP.setAttr('operation', 2)
		localVec_pma.setAttr('operation', 2)
		localVec_norm.setAttr('operation', 0)
		localVec_norm.setAttr('normalizeOutput', 1)

		elbow_triAngle_acos.output >> elbow_rot_min180_animBlend.inputA
		elbow_rot_min180_animBlend.output >> output_02_compM.inputRotateY
		elbow_incos_md.outputX >> elbow_triAngle_acos.input
		minus_c_pma.output1D >> elbow_incos_md.input1X
		a_b_prod_mdl.output >> elbow_incos_md.input2X
		minus_a_pma.output1D >> shoulder_incos_md.input1X
		b_c_prod_mdl.output >> shoulder_incos_md.input2X
		humerus_b_sqr_mdl.output >> add_b_c_sqr_adl.input1
		dist_c_sqr_mdl.output >> add_b_c_sqr_adl.input2
		add_b_c_sqr_adl.output >> minus_a_pma.input1D[0]
		radius_a_sqr_mdl.output >> minus_a_pma.input1D[1]
		shoulder_incos_md.outputX >> shoulder_angle_acos.input
		add_a_b_sqr_adl.output >> minus_c_pma.input1D[0]
		dist_c_sqr_mdl.output >> minus_c_pma.input1D[1]
		b_double_prod_mdl.output >> a_b_prod_mdl.input1
		self.controllers[2].ctrl.radius >> a_b_prod_mdl.input2
		dist_scale_md.outputX >> dist_c_sqr_mdl.input1
		dist_scale_md.outputX >> dist_c_sqr_mdl.input2
		self.controllers[2].ctrl.humerus >> humerus_b_sqr_mdl.input1
		self.controllers[2].ctrl.humerus >> humerus_b_sqr_mdl.input2
		radius_a_sqr_mdl.output >> add_a_b_sqr_adl.input1
		humerus_b_sqr_mdl.output >> add_a_b_sqr_adl.input2
		self.controllers[2].ctrl.humerus >> b_double_prod_mdl.input1
		dist_scale_md.outputX >> b_c_prod_mdl.input1
		b_double_prod_mdl.output >> b_c_prod_mdl.input2
		self.controllers[2].ctrl.radius >> radius_a_sqr_mdl.input1
		self.controllers[2].ctrl.radius >> radius_a_sqr_mdl.input2
		stretchPercent_md.outputX >> stretchLimiter_clmp.inputR
		stretch_blndA.output >> stretchLimiter_clmp.maxR
		self.controllers[2].ctrl.radius >> radiusStretch_mdl.input1
		self.controllers[0].ctrl.worldMatrix[0] >> base_ctrl_dcmpM.inputMatrix
		limited_vec_clmp.outputR >> dist_scale_md.input1X
		self.socketDcmp.outputScaleX >> dist_scale_md.input2X
		self.controllers[2].ctrl.stretch >> stretch_blndA.attributesBlender
		base_aim_matrix.output >> output_01_multM.matrixIn[1]
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
		output_02_compM.outputMatrix >> world_02_multM.matrixIn[0]
		output_01_multM.matrixSum >> world_02_multM.matrixIn[1]
		self.modGlobals['modInput'].RB_Socket >> world_02_multM.matrixIn[2]
		ctrl_distB.distance >> limited_vec_clmp.inputR
		baseLength_scale_mdl.output >> limited_vec_clmp.maxR
		localRot_03_multM.matrixSum >> xVec_vecMtxProd.matrix
		ik_rotations_compM.outputMatrix >> output_01_multM.matrixIn[0]
		socket_invertM.outputMatrix >> output_01_multM.matrixIn[2]
		self.controllers[2].ctrl.humerus >> humerusStretch_mdl.input1
		localVec_pma.output3D >> localVec_norm.input1
		localVec_norm.outputX >> base_aim_matrix.in00
		localVec_norm.outputY >> base_aim_matrix.in01
		localVec_norm.outputZ >> base_aim_matrix.in02
		base_aim_yVec_crsP.outputX >> base_aim_matrix.in10
		base_aim_yVec_crsP.outputY >> base_aim_matrix.in11
		base_aim_yVec_crsP.outputZ >> base_aim_matrix.in12
		base_aim_zVec_crsP.outputX >> base_aim_matrix.in20
		base_aim_zVec_crsP.outputY >> base_aim_matrix.in21
		base_aim_zVec_crsP.outputZ >> base_aim_matrix.in22
		base_ctrl_dcmpM.outputTranslateX >> base_aim_matrix.in30
		base_ctrl_dcmpM.outputTranslateY >> base_aim_matrix.in31
		base_ctrl_dcmpM.outputTranslateZ >> base_aim_matrix.in32
		self.controllers[2].ctrl.worldMatrix[0] >> localRot_03_multM.matrixIn[0]
		rot_inv_trnpM.outputMatrix >> localRot_03_multM.matrixIn[1]
		localRot_03_multM.matrixSum >> yVec_vecMtxProd.matrix
		shoulder_angle_acos.output >> ik_rotations_compM.inputRotateY
		pv_ctrl_dcmpM.outputTranslate >> pv_localVec_pma.input3D[0]
		base_ctrl_dcmpM.outputTranslate >> pv_localVec_pma.input3D[1]
		localVec_norm.output >> base_aim_zVec_crsP.input1
		base_aim_yVec_crsP.output >> base_aim_zVec_crsP.input2

		if axis == 'X':
			stretchLimiter_clmp.outputR >> radiusStretch_mdl.input2
			stretchLimiter_clmp.outputR >> humerusStretch_mdl.input2
			# pv_ctrl_dcmpM.outputTranslate >> pv_localVec_pma.input3D[0]
			# base_ctrl_dcmpM.outputTranslate >> pv_localVec_pma.input3D[1]
			ctrl_dcmpM.outputTranslate >> localVec_pma.input3D[0]
			base_ctrl_dcmpM.outputTranslate >> localVec_pma.input3D[1]
			# localVec_norm.output >> base_aim_zVec_crsP.input1
			# base_aim_yVec_crsP.output >> base_aim_zVec_crsP.input2
			localVec_pma.output3D >> base_aim_yVec_crsP.input1
			pv_localVec_pma.output3D >> base_aim_yVec_crsP.input2
		else:
			negate_stretch_mdl = pm.createNode('multDoubleLinear', n='{}_negateStretch_mdl'.format(self.name))
			negate_stretch_mdl.output >> radiusStretch_mdl.input2
			negate_stretch_mdl.output >> humerusStretch_mdl.input2
			stretchLimiter_clmp.outputR >> negate_stretch_mdl.input1
			negate_stretch_mdl.input2.set(-1)
			# negate_shoulder_ab = pm.createNode('animBlendNodeAdditiveDA', n='{}_negateShoulder_ab'.format(self.name))
			# shoulder_angle_acos.output >> ik_rotations_compM.inputRotateY
			# negate_shoulder_ab.output >> ik_rotations_compM.inputRotateY
			# negate_shoulder_ab.setAttr('weightB', 0.0)
			# negate_shoulder_ab.setAttr('weightA', -1.0)
			localVec_pma.output3D >> base_aim_yVec_crsP.input2
			pv_localVec_pma.output3D >> base_aim_yVec_crsP.input1

			# pv_ctrl_dcmpM.outputTranslate >> pv_localVec_pma.input3D[1]
			# base_ctrl_dcmpM.outputTranslate >> pv_localVec_pma.input3D[0]
			ctrl_dcmpM.outputTranslate >> localVec_pma.input3D[1]
			base_ctrl_dcmpM.outputTranslate >> localVec_pma.input3D[0]
			# localVec_norm.output >> base_aim_zVec_crsP.input2
			# base_aim_yVec_crsP.output >> base_aim_zVec_crsP.input1

		# Handle outputs
		hold_outputs = [
			{'name': '%s_out' % self.chain[0], 'at': 'matrix'},
			{'name': '%s_out' % self.chain[1], 'at': 'matrix'},
			{'name': '%s_out' % self.chain[2], 'at': 'matrix'},
		]
		joint_outputs = []
		for output in hold_outputs:
			joint_outputs.append(utils.makeAttrFromDict(self.modGlobals['modOutput'], output))

		chain_01_dcmpM = pm.createNode('decomposeMatrix', n='{}_dcmpM'.format(self.chain[0]))
		chain_02_dcmpM = pm.createNode('decomposeMatrix', n='{}_dcmpM'.format(self.chain[1]))
		chain_03_dcmpM = pm.createNode('decomposeMatrix', n='{}_dcmpM'.format(self.chain[2]))

		output_01_multM.matrixSum >> joint_outputs[0]
		output_02_compM.outputMatrix >> joint_outputs[1]
		output_03_fourM.output >> joint_outputs[2]
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
