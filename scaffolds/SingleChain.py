from .ScaffoldBase import Scaffold

from .. import user, utils

# ----------------------------------------------------------------------------------------------------------------------
"""

	SINGLECHAIN.PY
	Simple fk chain scaffolding inheriting from ScaffoldBase.Scaffold

"""
# ----------------------------------------------------------------------------------------------------------------------


class SingleChain(Scaffold):

	_availableModules = [' ', 'SimpleFk']

	def __init__(self, **kwargs):
		super(SingleChain, self).__init__(**kwargs)

	def makeBind(self):

		self.chain = utils.makeJointChain(self.length, self.name, user.prefs['bind-skeleton-suffix'])
	# end def makeBind():
# end class SingleChain():
