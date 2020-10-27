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

# TODO: blend between actual up vector somehow?
# TODO: actually this is just straight up broken euler rotation problem (rotate y on straight up chain breaks)


class SpaceSwitchChain(SimpleFk):

	_uses_global_plug = True

	def __init__(self, *args):
		super(SpaceSwitchChain, self).__init__(*args)
	# end def __init__():

	def preBuild(self):
		super(SpaceSwitchChain, self).preBuild()

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

		if len(self) > 2:
			inv_mm = pm.createNode('multMatrix', n='{}_invCtrl01_multM'.format(self.name))
			wt_add = pm.createNode('wtAddMatrix', n='{}_distributeSpace_wtAdM'.format(self.name))
			blend_two = pm.createNode('blendTwoAttr', n='{}_blend_two'.format(self.name))
			subtract = pm.createNode('plusMinusAverage', n='{}_min_pma'.format(self.name))

			inv_mm.matrixSum >> wt_add.wtMatrix[0].m
			blend_two.output >> wt_add.wtMatrix[0].w
			subtract.output1D >> wt_add.wtMatrix[1].w
			blend_two.output >> subtract.input1D[1]
			self.ctrlList[-1].ctrl.spaceBlend >> blend_two.attributesBlender
			self.globalPlug >> inv_mm.matrixIn[0]
			self.ctrlList[0].ctrl.worldInverseMatrix[0] >> inv_mm.matrixIn[1]

			inv_mm.matrixIn[2].set(self.ctrlList[0].wMatrix)
			subtract.setAttr('operation', 2)
			subtract.input1D[0].set(1)
			wt_add.wtMatrix[1].m.set(pm.dt.Matrix())
			blend_two.input[0].set(1.0 / (len(self) - 2.0))
			blend_two.input[1].set(0)

			for i in range(1, (len(self) - 1)):
				this_mm = pm.createNode('multMatrix', n='{0}_null{1:02d}_const_multM'.format(self.name, (i + 1)))
				this_dm = pm.createNode('decomposeMatrix', n='{0}_null{1:02d}_const_dcmpM'.format(self.name, (i + 1)))

				this_mm.matrixIn[0].set((
					pm.dt.TransformationMatrix(
						self.ctrlList[i].null.matrix.get())).asRotateMatrix()
				)

				wt_add.matrixSum >> this_mm.matrixIn[1]
				this_mm.matrixSum >> this_dm.inputMatrix
				# wt_add.matrixSum >> this_dm.inputMatrix
				this_dm.outputRotate >> self.ctrlList[i].null.rotate
	# end def build():
# end class SpaceSwitchChain():
