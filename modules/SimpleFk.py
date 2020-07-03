import pymel.core as pm

from .ModuleBase import RBModule
from .. import utils
from ..userPrefs import user

## --------------------------------------------------------------------------------
'''

	SIMPLEFK.PY
	simple fk chain

'''
## --------------------------------------------------------------------------------


class SingleChain(RBModule):

	def __init__(self, length, **kwargs):
		super(SingleChain, self).__init__(length, **kwargs)

	def makeBind(self):

		self.chain = utils.makeJointChain(self.length, self.name, user.prefs(
													'bind-skeleton-suffix'))
	# end def makeBind(self):
# end class SingleChain(RBModule):