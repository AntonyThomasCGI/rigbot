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

		base_ctrl = ctrl.control(name='%s_base_ctrl' % self.name, shape='square', line_width=2)

		utils.matrixConstraint(self.modGlobals, )

		self.controllers.append(base_ctrl)
	# end def preBuild():
# end class SimpleIkArm():
