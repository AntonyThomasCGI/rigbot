import pymel.core as pm

import os
import copy

from userPrefs import user

# ----------------------------------------------------------------------------------------------------------------------
'''

	UTILS.PY
	common utility functions

'''
# ----------------------------------------------------------------------------------------------------------------------


class UtilsException(Exception):
	pass


class Colours:
	"""
	Colour look up dict - has to be 0-1 because stupid maya only speaks computer
	Colour space: sRGB
	"""
	_colourRGB = {
		"yellow":		[1.0, 	1.0, 	0.0],
		"green":		[0.0, 	1.0, 	0.0],
		"blue":			[0.0, 	0.0, 	1.0],
		"red":			[1.0, 	0.0, 	0.0],
		"orange":		[1.0, 	0.17, 	0.0],
		"pale-orange":	[1.0, 	0.25, 	0.1],
		"grey-blue":	[0.03,	0.03,	0.06],
		"grey":			[0.038, 0.038, 	0.038],
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
	# end def get_rgb_value(colour):

	@staticmethod
	def get_linear_value(colour):
		"""
		Used to look up rgb colour in _colourRGB dictionary and convert to linear colour space
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
	# end def get_linear_value(colour):
# end class Colours:


controllerShapes = {
	'locator':	[
		[0.0, 0.0, 7.0], [0.0, 0.0, -7.0], 
		[0.0, 0.0, 0.0], [7.0, 0.0, 0.0], 
		[-7.0, 0.0, 0.0], [0.0, 0.0, 0.0], 
		[0.0, 7.0, 0.0], [0.0, -7.0, 0.0]
	],
	'box': [
		[0, -0.5, 0.5], [0, -0.5, -0.5], [0, 0.5, -0.5], [0, 0.5, 0.5], 
		[0, -0.5, 0.5]
	],
	'circle': [
		[1.874699728327322e-33, 0.5, -3.061616997868383e-17],
		[-1.1716301013315743e-17, 0.46193976625564337, 0.19134171618254486],
		[-2.1648901405887335e-17, 0.35355339059327373, 0.3535533905932738],
		[-2.8285652807192507e-17, 0.19134171618254486, 0.46193976625564337],
		[-3.061616997868383e-17, -2.4894981252573997e-17, 0.5],
		[-2.8285652807192507e-17, -0.19134171618254492, 0.46193976625564337],
		[-2.164890140588733e-17, -0.35355339059327384, 0.35355339059327373],
		[-1.1716301013315742e-17, -0.4619397662556434, 0.19134171618254484],
		[3.223916797098519e-33, -0.5, -5.265055686820291e-17],
		[1.171630101331575e-17, -0.4619397662556433, -0.19134171618254495],
		[2.1648901405887338e-17, -0.3535533905932737, -0.35355339059327384],
		[2.828565280719251e-17, -0.19134171618254478, -0.4619397662556434],
		[3.061616997868383e-17, 1.0816170809946073e-16, -0.5],
		[2.8285652807192507e-17, 0.191341716182545, -0.4619397662556433],
		[2.1648901405887323e-17, 0.35355339059327384, -0.3535533905932736],
		[1.1716301013315736e-17, 0.46193976625564337, -0.19134171618254472],
		[-1.0022072164332974e-32, 0.4999999999999999, 1.6367285933071856e-16]
	],
}


# ----------------------------------------------------------------------------------------------------------------------
# .												MAYA UTILITY FUNCTIONS
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
		joint_list.append(pm.joint(p=[ (10*i), 0, 0 ], n='{}_{:02d}_{}'.format(
									name, (i+1), suffix), radius=rad))

	return joint_list
# end def makeJointChain(length, name, suffix, rad=1):


# ----------------------------------------------------------------------------------------------------------------------
def setOverrideColour(colour, *args):
	"""
	Set DAG node override colour
	:param colour: colour to set override colour
	:param args: nodes to apply change
	"""

	item_ls = makePynodeList(args, type=['transform', 'joint', 'nurbsCurve', 'locator'])

	if isinstance(colour, basestring):
		colour = Colours.get_rgb_value(colour)

	for item in item_ls:
		item.overrideEnabled.set(1)
		item.drawOverride.overrideRGBColors.set(1)
		item.drawOverride.overrideColorRGB.set(*colour)
# end def setOverrideColour(colour, *args):


# ----------------------------------------------------------------------------------------------------------------------
def setOutlinerColour(colour, *args):
	"""
	Set DAG node outliner colour
	:param colour: colour to set outliner colour
	:param args: nodes to apply change
	"""

	item_ls = makePynodeList(args, type=['transform', 'joint', 'nurbsCurve', 'locator'])

	if isinstance(colour, basestring):
		colour = Colours.get_linear_value(colour)

	for item in item_ls:
		item.useOutlinerColor.set(1)
		item.outlinerColor.set(*colour)
# end def setOutlinerColour(colour, *args):


# ----------------------------------------------------------------------------------------------------------------------
# this function stolen from: https://github.com/kattkieru
def makePynodeList(*args, **kwargs):
	"""
	Return list of PyNodes
	:param args: list, tuple, nested list of string or PyNodes to return
	:param kwargs: node 'type' filter
	:return:
	"""
	
	obType = kwargs.get('type', None)

	def makeListRecursive(passedArgs, realList=None):
		if realList is None:
			realList = []

		for item in passedArgs:
			if isinstance(item, list) or isinstance(item, tuple):
				makeListRecursive(item, realList)
			else:
				realList.append(item)

		return realList
	# end def makeListRecursive(passedArgs, realList=None):

	# only attempt PyNodes at this point, after the above list has been filtered
	objects = [pm.PyNode(x) for x in makeListRecursive(args) if pm.objExists(x)]

	# filter by type
	if obType is not None:
		objects = pm.ls(objects, type=obType)

	return objects
# end def makePynodeList(*args, **kwargs):


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
			path_ls.append('|'.join(split_ls[ slice(i+1) ]))
	
		return path_ls
	# end permutatePath(node_path):
	
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
# end def safeMakeChildGroups(path_ls):


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

	## if already has attr then delete
	if ob.hasAttr(attr_name):
		ob.deleteAttr(attr_name)

	ob.addAttr(attr_name, **attr_data)
	ob.setAttr(attr_name, l=lock)

	## channel box flag is ignored if attr is keyable so this:
	if 'keyable' in attr_data:
		if not attr_data[ 'keyable' ]:
			ob.setAttr(attr_name, cb=channel_box)
	else:
		if not attr_data[ 'k' ]:
			ob.setAttr(attr_name, cb=channel_box)
# end def makeAttrFromDict(ob, attr_data):


## --------------------------------------------------------------------------------
def scaleCtrlShape(scle, line_width, *args):
	## scle (float, int) = how much to scale ctrl
	## line_width (float, int) = set ctrl line width

	ctrl_ls = makePynodeList(args)

	for ctrl in ctrl_ls:
		shapes = ctrl.getChildren()
		for shape in shapes:
			if 'nurbsCurve' in shape.nodeType():
				num_cv = pm.getAttr('{}.cp'.format(shape), s=1)
				for i in range(num_cv):
					cv_ws = pm.xform('{}.cv[{}]'.format(shape, i) , t=True,
						q=True)
					pm.xform('{}.cv[{}]'.format(shape, i) , t=[ (cv_ws[0]*scle),
												(cv_ws[1]*scle), (cv_ws[2]*scle) ])
				shape.lineWidth.set(line_width)
# end def scaleCtrlShape(scle, line_width, *args):


## --------------------------------------------------------------------------------
def lockHide(attr_data, *args):
	## attr_data (dictionary) = attrs to lock hide
	##		eg: {'r':1, 's':'xy', 't':'z', 'v':1, 'custom_attr':1}
	##		also accepts 'all' to lock/hide all default channels
	## hide (bool) = also hides the attr if True
	## args = list of nodes to lockHide
	
	objs = makePynodeList(args)
	
	to_lock = []
	
	for item, axis in attr_data.items():
		if any([ s == item for s in ['t', 'r', 's', 'translate', 'rotate', 
									'scale'] ]):
		    ## as well as 'xyz' axis can be 1 or 0 so:
			if isinstance(axis, int) and axis:
				for channel in ['x', 'y', 'z']:
					to_lock.append(item + channel)
			else:
				for i in range(len(axis)):
					to_lock.append(item + axis[i])
		## special case 'all'
		elif item == 'all':
			for default_attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 
								'sz', 'v']:
				to_lock.append(default_attr)
        ## attrs with no xyz values eg; custom attrs or visibility
		else:
			if axis:
				to_lock.append(item)
				
	for ob in objs:
	    for attr in to_lock:
	        pm.setAttr('{}.{}'.format(ob, attr), lock=True, keyable=False,
	        										channelBox=False)
# end def lockHide(attr_data, *args):




## --------------------------------------------------------------------------------
##							  RIG BOT UTILITY FUNCTIONS
## --------------------------------------------------------------------------------

def getFilteredDir(folder):

	main_dir = os.path.dirname(os.path.realpath(__file__))
	
	files = [x.split('.')[0] for x in os.listdir(main_dir+'\\{}'.format(folder))
					if x.endswith('.py') 
					and not x.count('__init__') 
					and not x.endswith('Base.py')]
					
	return files
# end def getFilteredDir(folder):


## --------------------------------------------------------------------------------
def makeRoot():
	if pm.objExists(user.prefs('root-joint')):
		root_jnt = pm.PyNode(user.prefs('root-joint'))
	else:
		pm.select(deselect=True)
		root_jnt = pm.joint(n=user.prefs('root-joint'), radius=0.001)

		ctrl = pm.curve(d=1, p=controllerShapes[ 'locator' ],
						n=(user.prefs('root-joint') + '_display'))
		scaleCtrlShape(1.43, 3, ctrl)

		ctrl_shape = ctrl.getChildren()[0]
		setOverrideColour(user.prefs('module-root-colour'),
								[root_jnt, ctrl_shape])
		setOutlinerColour(user.prefs('module-root-colour'),
								root_jnt)

		pm.parent(ctrl_shape, root_jnt, r=True, s=True)
		pm.delete(ctrl)

		tags = [
		{ 'name':'RB_MODULE_ROOT', 'at':'enum', 'en':' ', 'k':0, 'l':1 },
		{ 'name':'RB_module_type', 'k':0, 'at':'enum', 'en':'root' },
		]
		for tag in tags:
			makeAttrFromDict(root_jnt, tag)

	return root_jnt
# end def makeRoot():


## --------------------------------------------------------------------------------
def getModuleChildren(modroot):

	if pm.objExists(user.prefs('root-joint')):
		root_jnt = pm.PyNode(user.prefs('root-joint'))
	else:
		raise UtilsException('--{}: does not exist!'.format(user.prefs('root-joint')))

	flattened_jnts = root_jnt.getChildren(ad=True, type='joint')

	def isModRoot(jnt):
		return jnt.hasAttr('RB_MODULE_ROOT')
	# end def isModRoot(jnt):

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
	# end def filterChildren(jnt):

	mod_children = modroot.getChildren(ad=True, type='joint')
	
	children = filter(filterChildren, mod_children)
	children.append(modroot)
	children.reverse()

	return children
# end def getModuleChildren(modroot):