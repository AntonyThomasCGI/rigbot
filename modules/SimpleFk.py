import pymel.core as pm

from .ModuleBase import ModuleBase
from .. import utils
from .. import user

# --------------------------------------------------------------------------------
"""

	SIMPLEFK.PY
	simple fk chain

"""
# --------------------------------------------------------------------------------


# class SingleChain(ModuleBase):
#
# 	def __init__(self, length, **kwargs):
# 		super(SingleChain, self).__init__(length, **kwargs)
# 		pass
#
# 	def makeBind(self):
#
# 		self.chain = utils.makeJointChain(self.length, self.name, user.prefs(
# 													'bind-skeleton-suffix'))
# 	# end def makeBind(self):
# # end class SingleChain(RBModule):