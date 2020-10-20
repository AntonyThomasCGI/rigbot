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
		self.controllers[-1].makeAttr(name='parentSpace', at='enum', en='GLOBAL:LOCAL', k=False)
	# end def preBuild():

	def build(self):
		pm.createNode('multMatrix')
	# end def build():
# end class SpaceSwitchChain():
