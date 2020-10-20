# ----------------------------------------------------------------------------------------------------------------------
"""

	SIMPLEFK.PY
	simple fk chain

"""
# ----------------------------------------------------------------------------------------------------------------------

from .ModuleBase import ModuleBase

from ..rig import controls as ctrl

import pymel.core as pm


class SimpleFk(ModuleBase):

	def __init__(self, *args):
		super(SimpleFk, self).__init__(*args)

	def preBuild(self):
		super(SimpleFk, self).preBuild()

		ctrl_num = len(self.chain) - (1 - self.includeEndJoint)
		for i in range(ctrl_num):
			self.controllers[i] = (ctrl.control(name='{}_{:02d}'.format(self.name, i+1), size=2))
			pm.matchTransform(self.controllers[i].null, self.chain[i])
			if i:
				pm.parent(self.controllers[i].null, self.controllers[i-1].ctrl)
		pm.parent(self.controllers[0].null, self.modGlobals['modCtrls'])
	# end def makeBind():

	def build(self):
		for i, this_ctrl in enumerate(self.controllers.values()):
			this_ctrl.ctrl.worldMatrix[0] >> self.outputPlug[i]
	# end def build():
# end class SingleChain():
