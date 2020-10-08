# ----------------------------------------------------------------------------------------------------------------------
"""

	SIMPLEFK.PY
	simple fk chain

"""
# ----------------------------------------------------------------------------------------------------------------------

from .ModuleBase import ModuleBase

from ..rig import controls as ctrl
from .. import utils

import pymel.core as pm


class SimpleFk(ModuleBase):

	def __init__(self, *args):
		super(SimpleFk, self).__init__(*args)

	def preBuild(self):
		super(SimpleFk, self).preBuild()

		ctrl_num = len(self.chain) - (1 - self.includeEndJoint)
		for i in range(ctrl_num):
			self.controllers.append(ctrl.control(name='{}_{:02d}'.format(self.name, i+1), size=2))
			pm.matchTransform(self.controllers[i].null, self.chain[i])
			if i:
				pm.parent(self.controllers[i].null, self.controllers[i-1].ctrl)
		pm.parent(self.controllers[0].null, self.modGlobals['modCtrls'])
	# end def makeBind(self):

	def build(self):

		#TODO: this set up pretty scuffed, just get null offset and drive matrix of joint not world and inv wrld
		for i, this_ctrl in enumerate(self.controllers):
			matrix_out = utils.makeAttrFromDict(
				self.modGlobals['modOutput'], {'name': '%s_out' % this_ctrl.ctrl, 'dt': 'matrix'}
			)

			multm = pm.createNode('multMatrix', n='%s_const_multM' % this_ctrl.ctrl)
			parent_inv_mtx = this_ctrl.null.getParent().attr('worldInverseMatrix[0]')

			this_ctrl.ctrl.worldMatrix[0] >> multm.matrixIn[0]
			parent_inv_mtx >> multm.matrixIn[1]
			multm.matrixSum >> matrix_out

			dcmpM = pm.createNode('decomposeMatrix', n='%s_const_dcmpM' % this_ctrl.ctrl)
			matrix_out >> dcmpM.inputMatrix
			dcmpM.outputTranslate >> self.chain[i].translate
			dcmpM.outputRotate >> self.chain[i].rotate
			dcmpM.outputScale >> self.chain[i].scale
	# end def build():
# end class SingleChain():
