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

	def __init__(self, scaffold_obj):

		# get attributes from scaffold object
		self.chain = scaffold_obj.chain
		self.name = scaffold_obj.name
		self.socket = scaffold_obj.socket

		# rig attributes
		self.controllers = None

		self.build()
	# end def __init__(self):


# 	def __str__(self):
# 		return 'rb.{}({})'.format(self.__class__.__name__, self.name)
# 	# end def __str__(self):


# 	def __repr__(self):
# 		return self.__str__()
# 	# end def __repr__(self):


	def preBuild(self):
		pass
	# ------------------------------------------------------------------------------------------------------------------
	def build(self):
		raise ModuleBaseException('Invalid subclass-- build() function not implemented.')


# 	##-----------------------------------------------------------------------------
# 	def buildCleanup(self):
# 		## eg; transfers custom attrs from module root jnt
# 		pass
# 	#end def buildCleanup(self):

# # end class ModuleBase(Object):
