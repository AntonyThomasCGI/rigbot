from .ModuleBase import ModuleBase

# ----------------------------------------------------------------------------------------------------------------------
"""

	SIMPLEFK.PY
	simple fk chain

"""
# ----------------------------------------------------------------------------------------------------------------------


class SimpleFk(ModuleBase):

	def __init__(self, *args):
		super(SimpleFk, self).__init__(*args)

	def build(self):

		print('>> Building')
		print self.chain
		print self.name
		print('|| Done')
	# end def makeBind(self):
# end class SingleChain(RBModule):