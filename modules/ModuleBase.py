import pymel.core as pm

from ..rig import utils
from .. import user

# ----------------------------------------------------------------------------------------------------------------------
"""

	MODULEBASE.PY
	contains base class for creating rig modules

"""


# ----------------------------------------------------------------------------------------------------------------------
class ModuleBaseException(Exception):
	pass


class ModuleBase(object):

	"""
	Inherit from this class ..blah blah

	"""
	# TODO: add extra prefs dict for modules? eg; ctrl shapes, ctrl colours ? anything 'hard coded'

	def __init__(self, scaffold_obj):

		# get attributes from scaffold object
		self.chain = scaffold_obj.chain
		self.name = scaffold_obj.name
		self.socket = scaffold_obj.socket

		# rig attributes
		self.controllers = None

		utils.safeMakeChildGroups(['%s|ctrl' % user.prefs['rig-group'], 'Rig|ctrls|etc.'])

		# probably don't want to call build() in the init but from builder after class initialized
		# self.build()
	# end def __init__():


# 	def __str__(self):
# 		return 'rb.{}({})'.format(self.__class__.__name__, self.name)
# 	# end def __str__():


# 	def __repr__(self):
# 		return self.__str__()
# 	# end def __repr__():


	def preBuild(self):
		pass
	# ------------------------------------------------------------------------------------------------------------------
	def build(self):
		raise ModuleBaseException('Invalid subclass-- build() function not implemented.')


# 	##-----------------------------------------------------------------------------
# 	def buildCleanup(self):
# 		## eg; transfers custom attrs from module root jnt
# 		pass
# 	#end def buildCleanup():

# # end class ModuleBase():
