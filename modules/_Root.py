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
		self.controllers['cog'] = \
			ctrl.control(
				name=user.prefs['cog-ctrl-name'],
				shape='circle',
				colour='pink',
				size=5.5)

		self.controllers['cogPivot'] = \
			ctrl.control(
				name=user.prefs['pivot-ctrl-name'],
				shape='cog',
				colour='purple',
				size=5)

		self.controllers['cog'].rotateCtrlShapes(rotate=90, axis=[0,0,1])

		self.controllers['cog'].makeAttr(name='Pivot_Visibility', at='bool', k=False) \
			>> self.controllers['cogPivot'].shape.visibility

		self.controllers['cogPivot'].null.setParent(self.controllers['cog'].ctrl)

		pm.matchTransform(self.controllers['cog'].null, self.chain[1], pos=True, rot=True)  # position on cog placement
		self.controllers['cog'].null.setParent(self.controllers['root2'])
	# end def preBuild():

	# ------------------------------------------------------------------------------------------------------------------
	def build(self):
		root2_world_outputs = self.controllers['root2'].worldMatrix[0].outputs()

		root2_dcmp = next(  # get node if node exists in outputs else createNode
			(o for o in root2_world_outputs if o.nodeType() == 'decomposeMatrix'),
			pm.createNode('decomposeMatrix', n='{}_dcmpM'.format(self.controllers['root2']))
		)
		if not self.controllers['root2'].worldMatrix[0].isConnectedTo(root2_dcmp.inputMatrix):
			self.controllers['root2'].worldMatrix[0] >> root2_dcmp.inputMatrix

		for node in self.modGlobals.values():

			if not node.inheritsTransform.get(l=True):
				node.inheritsTransform.set(0, lock=True)

		root2_dcmp.outputTranslate >> self.root.translate
		root2_dcmp.outputRotate >> self.root.rotate
		root2_dcmp.outputScale >> self.root.scale
	# end def build():

	# ------------------------------------------------------------------------------------------------------------------
	def postBuild(self):
		root_shape = self.root.getShape()
		if root_shape:
			pm.delete(root_shape)
		self.root.useOutlinerColor.set(0)

		utils.setOverrideColour('grey', self.controllers['root'])
		utils.scaleCtrlShapes(self.controllers['root'], scale_mult=45, line_width=-1)

		utils.scaleCtrlShapes(self.controllers['root2'], scale_mult=10.2, line_width=2)
		utils.setOverrideColour('light-orange', self.controllers['root2'])

		pm.delete(self.chain[1])
	# end def postBuild():

	# ------------------------------------------------------------------------------------------------------------------
	def encapsulate(self):
		pass  # TODO ?
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

				self.controllers['root'] = \
					pm.PyNode('{0}_{1}'.format(user.prefs['root-ctrl-name'], user.prefs['ctrl-suffix']))
				self.controllers['root2'] = \
					pm.PyNode('{0}_{1}'.format(user.prefs['root2-ctrl-name'], user.prefs['ctrl-suffix']))

			else:
				self.controllers['root'] = \
					pm.circle(
						n=(tree.component + '_' + user.prefs['ctrl-suffix']),
						nry=1,
						nrz=0,
						ch=False)[0]

				for axis in ['X', 'Z']:
					pm.connectAttr(
						'{}.scaleY'.format(self.controllers['root']),
						'{}.scale{}'.format(self.controllers['root'], axis))
					pm.setAttr('{}.scale{}'.format(self.controllers['root'], axis), lock=True)

				self.controllers['root2'] = \
					pm.curve(
						d=1,
						p=data.controllerShapes['omni-circle'],
						n=user.prefs['root2-ctrl-name'] + '_' + user.prefs['ctrl-suffix'])

				self.controllers['root2'].setParent(self.controllers['root'])

			if socket != 'World':
				pm.parent(self.controllers['root'], socket)

			next_socket = self.controllers['root']

		else:  # component must be null at this point
			if pm.objExists(tree.component):
				grp = pm.PyNode(tree.component)
			else:
				grp = pm.group(n=tree.component, em=True)
				if tree.component == user.prefs['module-group-name']:
					utils.makeAttr(grp, name='RB_MODULES', at='enum', en=' ', l=1)

			self.modGlobals[tree.component] = grp
			next_socket = grp

			if socket != 'World':
				pm.parent(grp, socket)

		if not tree.children:
			return

		for child in tree.children:
			self.safeCreateRigTree(child, next_socket)
	# end def safeCreateRigTree():
# end class _Root():
