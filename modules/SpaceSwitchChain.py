# ----------------------------------------------------------------------------------------------------------------------
"""

	SPACESWITCHCHAIN.PY
	space switch that blends entire fk chain from local and global space

"""
# ----------------------------------------------------------------------------------------------------------------------

from .SimpleFk import SimpleFk

from ..rig import controls as ctrl
from .. import utils

import pymel.core as pm

# head component is:
# - chain of one or more joints
# - end jnt had global.local space
# - every other joint blends with space switch
# - fk functionality when head is in local


class SpaceSwitchChain(SimpleFk):

	def __init__(self, *args):
		super(SpaceSwitchChain, self).__init__(*args)
	# end def __init__():

	def preBuild(self):
		super(SpaceSwitchChain, self).preBuild()

		self.makeGlobalSocket()
		self.ctrlList[-1].makeAttr(name='spaceBlend', nn='Space Blend GLOBAL / LOCAL', max=0, min=1)
	# end def preBuild():

	def build(self):
		super(SpaceSwitchChain, self).build()

		global_mm = pm.createNode('multMatrix', n='{}_global_multM'.format(self.name))

		global_mm.matrixIn[0].set(self.ctrlList[-1].wMatrix)
		self.globalPlug >> global_mm.matrixIn[1]
		self.ctrlList[-2].ctrl.worldInverseMatrix[0] >> global_mm.matrixIn[2]

		local_offset_mtx = self.ctrlList[-1].wMatrix * self.ctrlList[-2].wInvMatrix

		wt_add = utils.matrixBlend(
							global_mm.matrixSum,
							local_offset_mtx,
							self.ctrlList[-1].ctrl.spaceBlend,
							name='{}_space'.format(self.name)
		)

		global_dm = pm.createNode('decomposeMatrix', n='{}_space_dcmpM'.format(self.name))
		wt_add.matrixSum >> global_dm.inputMatrix
		global_dm.outputRotate >> self.ctrlList[-1].null.rotate
	# end def build():
# end class SpaceSwitchChain():
