import pymel.core as pm

import os
import copy

from .. import user

from . import controls

# ----------------------------------------------------------------------------------------------------------------------
"""

	UTILS.PY
	Common utility functions

"""
# ----------------------------------------------------------------------------------------------------------------------


class UtilsException(Exception):
	pass


class Colours:

	_colourRGB = {
		"yellow":		[1.0, 	1.0, 	0.0],
		"green":		[0.0, 	1.0, 	0.0],
		"blue":			[0.0, 	0.0, 	1.0],
		"dark-blue":	[0.0,	0.117,	0.117],  # default
		"red":			[1.0, 	0.0, 	0.0],
		"orange":		[1.0, 	0.17, 	0.0],
		"pale-orange":	[1.0, 	0.25, 	0.1],
		"grey-blue":	[0.03,	0.03,	0.06],
		"grey":			[0.038, 0.038, 	0.038],
		"white":		[1.0,	1.0,	1.0],
		"purple":		[0.25,	0.0,	0.80],
	}

	@staticmethod
	def get_rgb_value(colour):
		"""
		Used to look up rgb colour in _colourRGB dictionary

		:param colour: string name of colour
		:return: rgb 0-1 of colour
		"""
		for item in Colours._colourRGB:
			if item == colour:
				return Colours._colourRGB[item]
		raise ValueError('%s is not an available colour!' % colour)
	# end def get_rgb_value():

	@staticmethod
	def get_linear_value(colour):
		"""
		Look up rgb colour in _colourRGB dictionary and convert to linear colour space

		:param colour: string name of colour
		:return: rgb 0-1 of colour converted to linear space
		"""
		rgb_colour = copy.copy(Colours.get_rgb_value(colour))
		for index, clr in enumerate(rgb_colour):
			shifted_value = (1.055 * (clr ** (1.0 / 2.4)) - 0.055)
			if 0 > shifted_value:
				rgb_colour[ index ] = 0.0
			elif 1 < shifted_value:
				rgb_colour[ index ] = 1.0
			else:
				rgb_colour[ index ] = shifted_value
		return rgb_colour
	# end def get_linear_value():

	@staticmethod
	def list():
		print('Available colours are:')
		for key in Colours._colourRGB:
			print key
	# end def list():
# end class Colours:


# ----------------------------------------------------------------------------------------------------------------------
# 												MAYA UTILITY FUNCTIONS
# ----------------------------------------------------------------------------------------------------------------------

def makeJointChain(length, name, suffix='jnt', rad=1):
	"""
	Used to make a chain of joints

	:param length: length of joint chain
	:param name: prefix naming convention
	:param suffix: suffix naming convention
	:param rad: radius of joints
	:return: list of joints in chain
	"""

	# First run deselect so joints are made on origin
	pm.select(deselect=True)

	joint_list = []

	for i in range(length):
		joint_list.append(pm.joint(p=[(10*i), 0, 0 ], n='{}_{:02d}_{}'.format(name, (i+1), suffix), radius=rad))

	return joint_list
# end def makeJointChain():


# ----------------------------------------------------------------------------------------------------------------------
def setOverrideColour(colour, *args):
	"""
	Set DAG node override colour

	:param colour: `str or RGB` colour to set override colour
	:param args: `node or string` nodes to apply change
	"""

	item_ls = makePynodeList(args, type=['transform', 'joint', 'nurbsCurve', 'locator'])

	if isinstance(colour, basestring):
		colour = Colours.get_rgb_value(colour)

	for item in item_ls:
		try:
			shapes = item.getShapes()

			# check to see if getShapes returned empty list
			if shapes:
				print(shapes)
				for shape in shapes:
					shape.overrideEnabled.set(1)
					shape.drawOverride.overrideRGBColors.set(1)
					shape.drawOverride.overrideColorRGB.set(*colour)

		except AttributeError:
			pass

		# currently just blanket colour every transform and shape
		item.overrideEnabled.set(1)
		item.drawOverride.overrideRGBColors.set(1)
		item.drawOverride.overrideColorRGB.set(*colour)
# end def setOverrideColour():


# ----------------------------------------------------------------------------------------------------------------------
def setOutlinerColour(colour, *args):
	"""
	Set node outliner colour

	:param colour: colour to set outliner colour
	:param args: nodes to apply change
	"""

	item_ls = makePynodeList(args, type=['transform', 'joint', 'nurbsCurve', 'locator'])

	if isinstance(colour, basestring):
		colour = Colours.get_linear_value(colour)

	for item in item_ls:
		item.useOutlinerColor.set(1)
		item.outlinerColor.set(*colour)
# end def setOutlinerColour():


# ----------------------------------------------------------------------------------------------------------------------
def makePynodeList(*args, **kwargs):
	"""
	Return list of PyNodes

	:param args: list, tuple, nested list of string or PyNodes to return
	:param kwargs: node 'type' filter
	:return:
	"""

	obType = kwargs.get('type', None)

	def makeListRecursive(passed_args, actual_list=None):
		if actual_list is None:
			actual_list = []

		for item in passed_args:
			if isinstance(item, list) or isinstance(item, tuple):
				makeListRecursive(item, actual_list)
			else:
				actual_list.append(item)

		return actual_list
	# end def makeListRecursive(passed_args, actual_list=None):

	# only attempt PyNodes at this point, after the above list has been filtered
	objects = [pm.PyNode(x) for x in makeListRecursive(args) if pm.objExists(x)]

	# filter by type
	if obType is not None:
		objects = pm.ls(objects, type=obType)

	return objects
# end def makePynodeList():


# ----------------------------------------------------------------------------------------------------------------------
def safeMakeChildGroups(path_ls, query=False):
	"""
	Make hierarchy of groups or get list of PyNodes if they already exist

	:param path_ls: list of dag paths eg; ['Rig|joints', 'Rig|ctrls|etc.']
	:param query: can run in query mode to return if groups exist
	:return: list of PyNodes
	"""

	def permutatePath(node_path):
		# node_path (string) = full dag path to be split into individual dag paths
		split_ls = node_path.split('|')
		path_ls = []
		for i in range(len(split_ls)):
			path_ls.append('|'.join(split_ls[slice(i+1)]))

		return path_ls
	# end permutatePath():

	pynode_ls = []
	node = None

	for path in path_ls:
		dag_path_ls = permutatePath(path)

		for dag_path in dag_path_ls:

			if pm.objExists(dag_path):
				node = pm.PyNode(dag_path)

			elif query:
				return node

			else:
				split_dag = dag_path.split('|')
				node = pm.group(n=split_dag[-1], em=True)
				if len(split_dag) >= 2:
					pm.parent(node, split_dag[-2])
		pynode_ls.append(node)

	if query:
		return True
	else:
		return pynode_ls
# end def safeMakeChildGroups():


# ----------------------------------------------------------------------------------------------------------------------
def makeAttrFromDict(ob, attr_data):
	"""
	Creates attribute from dictionary - sets keyable=True and channelBox=True by default

	:param ob: node to add attribute to
	:param attr_data: flags for addAttr/setAttr command
	:return:
	"""

	try:
		attr_name = attr_data.pop('name')
	except NameError:
		raise NameError('"name" was not specified in dictionary but is required to make attribute.')

	# if keyable not specified set keyable by default
	if not any(key in attr_data for key in ['keyable', 'k']):
		attr_data['keyable'] = 1

	# pops lock and channelbox settings as they are not addAttr flags
	if 'lock' in attr_data:
		lock = attr_data.pop('lock')
	elif 'l' in attr_data:
		lock = attr_data.pop('l')
	else:
		lock = 0
	if 'channelBox' in attr_data:
		channel_box = attr_data.pop('channelBox')
	elif 'cb' in attr_data:
		channel_box = attr_data.pop('cb')
	else:
		channel_box = 1

	# if already has attr then delete
	if ob.hasAttr(attr_name):
		ob.deleteAttr(attr_name)

	ob.addAttr(attr_name, **attr_data)
	ob.setAttr(attr_name, l=lock)

	# channel box flag is ignored if attr is keyable so this:
	if 'keyable' in attr_data:
		if not attr_data[ 'keyable' ]:
			ob.setAttr(attr_name, cb=channel_box)
	else:
		if not attr_data[ 'k' ]:
			ob.setAttr(attr_name, cb=channel_box)
# end def makeAttrFromDict():


# ----------------------------------------------------------------------------------------------------------------------
def scaleCtrlShape(*args, **kwargs):
	"""
	Scale ctrl shapes and set line width

	:param args: list of transform nodes to change
	:param kwargs:  scale_mult: amount to scale ctrl curve, default 1
					line_width: line width thickness, ignores if not specified
	"""
	scale_mult = kwargs.pop('scale_mult', 1)
	line_width = kwargs.pop('line_width', None)

	ctrl_ls = makePynodeList(args)

	for ctrl in ctrl_ls:
		shapes = ctrl.getChildren()
		for shape in shapes:
			if 'nurbsCurve' in shape.nodeType():
				curv_type = pm.getAttr('%s.form' % shape)
				# if curve open get curve points
				if curv_type == 0:
					num_cv = pm.getAttr('%s.cp' % shape, s=1)
				# else curve must be closed so get spans
				else:
					num_cv = pm.getAttr('%s.spans' % shape)
				for i in xrange(num_cv):
					cv_ws = pm.xform('{}.cv[{}]'.format(shape, i), t=True, q=True)
					pm.xform(
						'{}.cv[{}]'.format(shape, i),
						t=[(cv_ws[0] * scale_mult), (cv_ws[1] * scale_mult), (cv_ws[2] * scale_mult)]
					)
				if line_width:
					shape.lineWidth.set(line_width)
# end def scaleCtrlShape():


# ----------------------------------------------------------------------------------------------------------------------
def lockHide(attr_data, *args):
	"""
	Lock and hide attributes from dictionary

	:param attr_data: 	(dictionary) attrs to lock hide eg: {'r':1, 's':'xy', 't':'z', 'v':1, 'custom_attr':1}
						also accepts 'all' to lock/hide all default channels
	:param args:		list of nodes to lockHide
	"""

	objs = makePynodeList(args)

	to_lock = []

	for item, axis in attr_data.items():
		if any([ s == item for s in ['t', 'r', 's', 'translate', 'rotate', 'scale'] ]):
			# as well as 'xyz' axis can be 1 or 0 so:
			if isinstance(axis, int) and axis:
				for channel in ['x', 'y', 'z']:
					to_lock.append(item + channel)
			else:
				for i in range(len(axis)):
					to_lock.append(item + axis[i])

		# special case 'all'
		elif item == 'all':
			for default_attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']:
				to_lock.append(default_attr)

		# attrs with no xyz values eg; custom attrs or visibility
		else:
			if axis:
				to_lock.append(item)

	for ob in objs:
		for attr in to_lock:
			pm.setAttr('{}.{}'.format(ob, attr), lock=True, keyable=False, channelBox=False)
# end def lockHide():


# ----------------------------------------------------------------------------------------------------------------------
def parentByList(list):
	list = makePynodeList(list)
	for i in range(len(list)-1):
		pm.parent(list[i], list[i+1])
# end def parentByList():


# ----------------------------------------------------------------------------------------------------------------------
# 											RIG BOT UTILITY FUNCTIONS
# ----------------------------------------------------------------------------------------------------------------------

def getFilteredDir(folder):
	"""
	Return list of files in give folder

	:param folder: string name of folder within rigbot dir
	:return: string name of python files that are not __init__ or end with Base.py
	"""

	main_dir = os.path.dirname(os.path.dirname(os.path.abspath(os.path.realpath(__file__))))

	files = [
		x.split('.')[0] for x in os.listdir(main_dir+'\\{}'.format(folder))
		if x.endswith('.py')
		and not x.count('__init__')
		and not x.endswith('Base.py')
	]

	return files
# end def getFilteredDir():


# ----------------------------------------------------------------------------------------------------------------------
def makeRoot():
	"""
	Returns pynode of root joint or creates new one if none exists

	:return: root joint
	"""
	if pm.objExists(user.prefs['root-joint']):
		root_jnt = pm.PyNode(user.prefs['root-joint'])
	else:
		pm.select(deselect=True)
		root_jnt = pm.joint(n=user.prefs['root-joint'], radius=0.001)

		ctrl = pm.curve(d=1, p=controls.controllerShapes['locator'], n=(user.prefs['root-joint'] + '_display'))
		scaleCtrlShape(ctrl, scale_mult=1.43, line_width=3)

		ctrl_shape = ctrl.getChildren()[0]
		setOverrideColour(user.prefs['module-root-colour'], [root_jnt, ctrl_shape])
		setOutlinerColour(user.prefs['module-root-colour'], root_jnt)

		pm.parent(ctrl_shape, root_jnt, r=True, s=True)
		pm.delete(ctrl)

		tags = [
		{'name':'RB_MODULE_ROOT', 'at':'enum', 'en':' ', 'k':0, 'l':1},
		{'name':'RB_module_type', 'k':0, 'at':'enum', 'en':'root'},
		]
		for tag in tags:
			makeAttrFromDict(root_jnt, tag)

	return root_jnt
# end def makeRoot():


# ----------------------------------------------------------------------------------------------------------------------
def getModuleChildren(modroot):
	"""
	Find all the child joints within a module

	:param modroot: module root
	:return: list of modules joints including module root
	"""

	if pm.objExists(user.prefs['root-joint']):
		root_jnt = pm.PyNode(user.prefs['root-joint'])
	else:
		raise UtilsException('--{}: does not exist!'.format(user.prefs['root-joint']))

	flattened_jnts = root_jnt.getChildren(ad=True, type='joint')

	def isModRoot(jnt):
		return jnt.hasAttr('RB_MODULE_ROOT')
	# end def isModRoot():

	module_roots = filter(isModRoot, flattened_jnts)
	short_mod_roots = map(lambda mod_r: mod_r.shortName(), module_roots)

	modname = modroot.shortName()

	def filterChildren(jnt):

		path_dict = { k:v for k,v in enumerate(jnt.fullPath().split('|')) }

		mod_index = 0
		other_mod_index = []
		for n, node in path_dict.items():
			if modname == node:
				mod_index = n
			else:
				for s_modr in short_mod_roots:
					if s_modr == node:
						other_mod_index.append(n)

		if not other_mod_index:
			return True
		elif all(other_index < mod_index for other_index in other_mod_index):
			return True
		else:
			return False
	# end def filterChildren():

	mod_children = modroot.getChildren(ad=True, type='joint')

	children = filter(filterChildren, mod_children)
	children.append(modroot)
	children.reverse()

	return children
# end def getModuleChildren():


# ----------------------------------------------------------------------------------------------------------------------
def makeNameUnique(name, suffix='_*'):
	"""
	Makes name unique in scene
	:param name: (string) name to pad with numeral
	:param suffix: (string) search suffix eg; _ctrl, _jnt, _*
	:return: string padded name
	"""

	new_name = name
	i = 1
	while pm.objExists(new_name+'%s' % suffix):
		new_name = '{}{}'.format(name, i)
		i += 1

	return new_name
# end makeNameUnique():


# ----------------------------------------------------------------------------------------------------------------------
def initiateRig():
	"""
	Creates default rig hierarchy to socket rig modules into
	:return: dict of global groups and ctrls
	"""

	rig_dict = {}

	def safeMakeNode(component, socket):

		if component == user.prefs['root-ctrl-name']:
			if pm.objExists(user.prefs['root-ctrl-name'] + '_' + user.prefs['ctrl-suffix']):
				god_ctrl = pm.PyNode(user.prefs['root-ctrl-name'] + '_' + user.prefs['ctrl-suffix'])
				god2_ctrl = pm.PyNode(user.prefs['root2-ctrl-name'] + '_' + user.prefs['ctrl-suffix'])

			else:
				god_ctrl = pm.circle(n=(component + '_' + user.prefs['ctrl-suffix']), nry=1, nrz=0, ch=False)[0]

				setOverrideColour('grey', god_ctrl)
				scaleCtrlShape(god_ctrl, scale_mult=45, line_width=-1)
				for axis in ['X', 'Z']:
					pm.connectAttr('{}.scaleY'.format(god_ctrl), '{}.scale{}'.format(god_ctrl, axis))
					pm.setAttr('{}.scale{}'.format(god_ctrl, axis), lock=True)

				god2_ctrl = pm.curve(
					d=1, p=controls.controllerShapes['omni-circle'], n=user.prefs['root2-ctrl-name'] + '_' +
																	   user.prefs['ctrl-suffix'])
				scaleCtrlShape(god2_ctrl, scale_mult=10.2, line_width=2)
				setOverrideColour('pale-orange', god2_ctrl)
				# god2_ctrl = controls.control(
				# 	name=user.prefs['root2-ctrl-name'], shape='omni-circle', size=10.2, colour='pale-orange')
				pm.parent(god2_ctrl, god_ctrl)

			rig_dict[component] = god_ctrl
			rig_dict['root2-ctrl-name'] = god2_ctrl

			if socket != 'World':
				pm.parent(god_ctrl, socket)

			return god_ctrl
		# component must be group at this point
		else:
			if pm.objExists(component):
				grp = pm.PyNode(component)
			else:
				grp = pm.group(n=component, em=True)

			rig_dict[component] = grp

			if socket != 'World':
				pm.parent(grp, socket)
			return grp
	# end def safeMakeNode():

	def walkTreeWithParent(tree, socket='World'):

		socket = safeMakeNode(tree.component, socket)

		if not tree.children:
			return

		for child in tree.children:
			walkTreeWithParent(child, socket)
	# end def walkTreeWithParent():

	walkTreeWithParent(user.RigTree)

	root2_world_outputs = rig_dict['root2-ctrl-name'].worldMatrix[0].outputs()

	#!FIXME: this errors if decompose Matrix plugin not loaded??
	if 'decomposeMatrix' not in map(lambda x: x.nodeType(), root2_world_outputs):
		root2_dcmp = pm.createNode('decomposeMatrix', n=rig_dict['root2-ctrl-name'] + '_dcmpM')
		rig_dict['root2-ctrl-name'].worldMatrix[0] >> root2_dcmp.inputMatrix
	else:
		for node in root2_world_outputs:
			if node.nodeType() == 'decomposeMatrix':
				root2_dcmp = node

	# make connections
	for item, node in rig_dict.items():

		# turn off inherit unless we have ctrl
		if not node.endswith('ctrl'):
			node.inheritsTransform.set(0)

		# these groups should follow god ctrls
		if item in ['transform', user.prefs['joint-group-name']]:
			root2_dcmp.outputTranslate >> node.translate
			root2_dcmp.outputRotate >> node.rotate
			root2_dcmp.outputScale >> node.scale

	return rig_dict
# end def initiateRig():
