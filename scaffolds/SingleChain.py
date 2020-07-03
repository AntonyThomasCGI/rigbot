import pymel.core as pm

from .ScaffoldBase import Scaffold
from .. import utils
from ..userPrefs import user

## --------------------------------------------------------------------------------
'''

	SINGLECHAIN.PY
	simple fk chain scaffolding

'''
## --------------------------------------------------------------------------------


class SingleChain(Scaffold):

	_availableModules = [ ' ', 'SimpleFk' ]

	def __init__(self, **kwargs):
		super(SingleChain, self).__init__(**kwargs)

	def makeBind(self):

		self.chain = utils.makeJointChain(self.length, self.name, user.prefs(
													'bind-skeleton-suffix'))
	# end def makeBind(self):
# end class SingleChain(Scaffold):