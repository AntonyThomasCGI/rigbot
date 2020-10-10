# ----------------------------------------------------------------------------------------------------------------------
"""

	_ROOT.PY
	Special module for creating root and base rig hierarchy. This module is required to be built before every
	other module so they have access to rig globals such has module group and root controllers.

"""
# ----------------------------------------------------------------------------------------------------------------------

from .ModuleBase import ModuleBase

from ..rig import controls as ctrl
from .. import utils, user, data

import pymel.core as pm


class _Root(ModuleBase):

	def __init__(self, *args):
		super(_Root, self).__init__(*args)
	# end def __init__():

	# ------------------------------------------------------------------------------------------------------------------
	def registerModule(self):
		self.safeCreateRigTree(user.RigTree)
	# end def registerModule():

	# ------------------------------------------------------------------------------------------------------------------
	def preBuild(self):
		self.controllers.append(ctrl.control(name='cog', shape='cog', colour='pink', size=5))

		pm.matchTransform(self.controllers[2].null, self.chain[1])  # match to the cog placement joint
		self.controllers[2].null.setParent(self.controllers[1])
	# end def preBuild():

	# ------------------------------------------------------------------------------------------------------------------
	def build(self):
		root2_world_outputs = self.controllers[1].worldMatrix[0].outputs()

		root2_dcmp = next(  # get node if node exists in outputs else createNode
			(o for o in root2_world_outputs if o.nodeType() == 'decomposeMatrix'),
			pm.createNode('decomposeMatrix', n='{}_dcmpM'.format(self.controllers[1]))
		)
		if not self.controllers[1].worldMatrix[0].isConnectedTo(root2_dcmp.inputMatrix):
			self.controllers[1].worldMatrix[0] >> root2_dcmp.inputMatrix

		for node in self.modGlobals.values():

			if not node.inheritsTransform.get(l=True):
				node.inheritsTransform.set(0, lock=True)

		root2_dcmp.outputTranslate >> self.root.translate
		root2_dcmp.outputRotate >> self.root.rotate
		root2_dcmp.outputScale >> self.root.scale
	# end def build():

	# ------------------------------------------------------------------------------------------------------------------
	def postBuild(self):
		super(_Root, self).postBuild()

		utils.setOverrideColour('grey', self.controllers[0])
		utils.scaleCtrlShapes(self.controllers[0], scale_mult=45, line_width=-1)

		utils.scaleCtrlShapes(self.controllers[1], scale_mult=10.2, line_width=2)
		utils.setOverrideColour('light-orange', self.controllers[1])

		for c in self.chain[2:]:
			pm.delete(c)
	# end def postBuild():

	# ------------------------------------------------------------------------------------------------------------------
	def encapsulate(self):
		pass  # TODO
	# end def encapsulate():

	# ------------------------------------------------------------------------------------------------------------------
	def safeCreateRigTree(self, tree, socket='World'):
		"""
		Recursively builds rig hierarchy from tree.  For any existing nodes, gets PyNode and continues.
		:param tree:  Rig tree containing component and children (see user file).
		:param socket:  `string World` or `PyNode` Current parent.
		:return:  None
		"""
		if tree.component == user.prefs['root-ctrl-name']:
			if pm.objExists('{0}_{1}'.format(user.prefs['root-ctrl-name'], user.prefs['ctrl-suffix'])):

				self.controllers.append(
					pm.PyNode('{0}_{1}'.format(user.prefs['root-ctrl-name'], user.prefs['ctrl-suffix'])))
				self.controllers.append(
					pm.PyNode('{0}_{1}'.format(user.prefs['root2-ctrl-name'], user.prefs['ctrl-suffix'])))

			else:
				self.controllers.append(
					pm.circle(
						n=(tree.component + '_' + user.prefs['ctrl-suffix']),
						nry=1,
						nrz=0,
						ch=False)[0])

				# utils.setOverrideColour('grey', god_ctrl)
				# utils.scaleCtrlShapes(god_ctrl, scale_mult=45, line_width=-1)
				for axis in ['X', 'Z']:
					pm.connectAttr(
						'{}.scaleY'.format(self.controllers[0]),
						'{}.scale{}'.format(self.controllers[0], axis))
					pm.setAttr('{}.scale{}'.format(self.controllers[0], axis), lock=True)

				self.controllers.append(
					pm.curve(
						d=1,
						p=data.controllerShapes['omni-circle'],
						n=user.prefs['root2-ctrl-name'] + '_' + user.prefs['ctrl-suffix']))

				self.controllers[1].setParent(self.controllers[0])

			if socket != 'World':
				pm.parent(self.controllers[0], socket)

			next_socket = self.controllers[0]

		else:  # component must be null at this point
			if pm.objExists(tree.component):
				grp = pm.PyNode(tree.component)
			else:
				grp = pm.group(n=tree.component, em=True)
				if tree.component == user.prefs['module-group-name']:
					utils.makeAttrFromDict(grp, {'name': 'RB_MODULES', 'at': 'enum', 'en': ' ', 'l': 1})

			self.modGlobals[tree.component] = grp
			next_socket = grp

			if socket != 'World':
				pm.parent(grp, socket)

		if not tree.children:
			return

		for child in tree.children:
			self.safeCreateRigTree(child, next_socket)
	# end def safeCreateRigTree():
# end class SingleChain():
