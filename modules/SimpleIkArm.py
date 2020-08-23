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

		pm.matchTransform(base_ctrl.null, self.chain[0])
		pm.matchTransform(ik_ctrl.null, self.chain[-1])

		joint_vectors = map(lambda x: pm.xform(x, q=True, t=True, ws=True), self.chain)

		pole_vector_position = utils.positionUpVectorFromPoints(*joint_vectors)

		pm.xform(pv_ctrl.null, t=pole_vector_position, ws=True)

		# TODO: space switches not constraints.
		utils.matrixConstraint(global_socket, ik_ctrl.null, pv_ctrl.null, ss='xyz', ip=self.modGlobals['modCtrls'])
	# end def preBuild():
# end class SimpleIkArm():
