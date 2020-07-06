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

		self.rigBase = self.jointsGrp = self.transformGrp = self.noTransformGrp = self.modulesGrp = None

		self.getRigGlobals()

		# rig attributes
		self.controllers = None

		pm.parent(user.prefs['root-joint'], self.jointsGrp)

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

# 	# ------------------------------------------------------------------------------------------------------------------
# 	def buildCleanup(self):
# 		# eg; transfers custom attrs from module root jnt
# 		pass
# 	#end def buildCleanup():

	# ------------------------------------------------------------------------------------------------------------------
	def getRigGlobals(self):

		def validateExists(item):
			if pm.objExists(item):
				return pm.PyNode(item)
			else:
				utils.initiateRig()
				return pm.PyNode(item)

		self.rigBase = validateExists(user.prefs['root2-ctrl-name'] + '_' + user.prefs['ctrl-suffix'])
		self.jointsGrp = validateExists(user.prefs['joint-group-name'])
		self.transformGrp = validateExists('transform')
		self.noTransformGrp = validateExists('no_transform')
		self.modulesGrp = validateExists('modules')
	# end def getRigGlobals():
# end class ModuleBase():
