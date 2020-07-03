import pymel.core as pm

from .. import utils

## --------------------------------------------------------------------------------
'''

	MODULEBASE.PY
	contains base class for creating rig modules

'''

## --------------------------------------------------------------------------------

class ModuleException(Exception):
	pass

class Module(object):

	"""
	Inherrit from this class ..blah blah

	"""

	def __init__():
	pass
	# end def __init__(self):


# 	def __str__(self):
# 		return 'rb.{}({})'.format(self.__class__.__name__, self.name)
# 	# end def __str__(self):


# 	def __repr__(self):
# 		return self.__str__()
# 	# end def __repr__(self):


# 	##-----------------------------------------------------------------------------
# 	def build(self):
# 		raise ModuleBaseException('Invalid subclass-- build() function not '
# 			+'implemented.')


# 	##-----------------------------------------------------------------------------
# 	def buildCleanup(self):
# 		## eg; transfers custom attrs from module root jnt
# 		pass
# 	#end def buildCleanup(self):

# # end class ModuleBase(Object):
 