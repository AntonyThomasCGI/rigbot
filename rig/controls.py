# ----------------------------------------------------------------------------------------------------------------------
"""

	CONTROLS.PY
	Used to manage controller shapes

"""
# ----------------------------------------------------------------------------------------------------------------------

import pymel.core as pm

from .. import utils, user, data


# TODO: L / R auto colouring
# TODO: support for multiple shapes, shape = ['list', 'of', 'shapes']
class control(object):
	def __init__(
				self, name='control', shape='circle', size=1, line_width=user.prefs['default-line-width'],
				offsets=user.prefs['num-offset-ctrls'], colour='dark-blue'):
		"""
		Create controller and offset groups
		:param name: (string) Name of controller
		:param shape: (string) Controller shape
		:param size: (float, int) Scale factor of control
		:param line_width: (float, int) line width
		:param offsets: amount of offset locators to make
		"""

		self.name = utils.makeNameUnique(name, '_%s' % user.prefs['ctrl-suffix'])

		self.ctrl = \
			pm.curve(
				d=1,
				p=data.controllerShapes[shape],
				n=(self.name + '_' + user.prefs['ctrl-suffix']))

		utils.setOverrideColour(colour, self.ctrl)

		utils.scaleCtrlShapes(self.ctrl, scale_mult=size, line_width=line_width)

		self.null = pm.group(n=self.ctrl + '_null', em=True)

		self.offsets = []
		for i in range(offsets):
			num = '{:02d}'.format(i+1) if offsets > 1 else ''
			self.offsets.append(pm.spaceLocator(n=self.ctrl + '_offset%s_loc' % num))

			utils.setOverrideColour('purple', self.offsets)

		utils.parentByList([self.ctrl, self.offsets, self.null])
	# end def __init__():

	@property
	def shape(self):
		if self.ctrl:
			children = self.ctrl.getShape()
			return children
		else:
			return None
	# end def shape():

	def makeAttr(self, **kwargs):
		return utils.makeAttr(self.ctrl, **kwargs)
	# end def makeAttr():

	def scaleCtrlShapes(self, **kwargs):
		return utils.scaleCtrlShapes(self.ctrl, **kwargs)
	# end def scaleCtrlShapes():

	def rotateCtrlShapes(self, **kwargs):
		return utils.rotateCtrlShapes(self.ctrl, **kwargs)
	# end def rotateCtrlShapes():
# end class control():
