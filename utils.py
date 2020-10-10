# ----------------------------------------------------------------------------------------------------------------------
"""

	UTILS.PY
	Common utility functions

"""
# ----------------------------------------------------------------------------------------------------------------------

import pymel.core as pm
import math
import os

from . import user, data


class UtilsException(Exception):
	pass


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
# TODO: flag to use linear colour, same with setOutLinerColour()
def setOverrideColour(colour, *args):
	"""
	Set DAG node override colour

	:param colour: `str or RGB` colour to set override colour
	:param args: `node or string` nodes to apply change
	"""

	item_ls = makePyNodeList(args, type=['transform', 'joint', 'nurbsCurve', 'locator'])

	if isinstance(colour, basestring):
		colour = data.Colours.get_rgb_value(colour)

	for item in item_ls:
		try:
			shapes = item.getShapes()

			# check to see if getShapes returned empty list
			if shapes:
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
	Set node outliner colour, uses linear colour value always as outliner applies no colour LUTs.

	:param colour: colour to set outliner colour
	:param args: nodes to apply change
	"""

	item_ls = makePyNodeList(args, type=['transform', 'joint', 'nurbsCurve', 'locator'])

	if isinstance(colour, basestring):
		colour = data.Colours.get_linear_value(colour)

	for item in item_ls:
		item.useOutlinerColor.set(1)
		item.outlinerColor.set(*colour)
# end def setOutlinerColour():


# ----------------------------------------------------------------------------------------------------------------------
def makePyNodeList(*args, **kwargs):
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
	# end def makeListRecursive():

	# only attempt PyNodes at this point, after the above list has been filtered
	objects = [pm.PyNode(x) for x in makeListRecursive(args) if pm.objExists(x)]

	# filter by type
	if obType:
		objects = pm.ls(objects, type=obType)

	return objects
# end def makePyNodeList():


# ----------------------------------------------------------------------------------------------------------------------
def makeAttrFromDict(ob, attr_data):
	"""
	Creates attribute from dictionary - sets keyable=True and channelBox=True by default

	:param ob: single PyNode to add attribute to
	:param attr_data: dictionary of flags for addAttr/setAttr command
	:return: attribute
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
		print('//Warning: Attribute already exists, overriding.')
		pm.setAttr('{}.{}'.format(ob, attr_name), l=False)
		ob.deleteAttr(attr_name)

	ob.addAttr(attr_name, **attr_data)
	ob.setAttr(attr_name, l=lock)

	# channel box flag is ignored if attr is keyable so this:
	if 'keyable' in attr_data:
		if not attr_data['keyable']:
			ob.setAttr(attr_name, cb=channel_box)
	else:
		if not attr_data['k']:
			ob.setAttr(attr_name, cb=channel_box)

	return ob.attr(attr_name)
# end def makeAttrFromDict():


# ----------------------------------------------------------------------------------------------------------------------
def scaleCtrlShapes(*args, **kwargs):
	"""
	Scale ctrl shapes and set line width

	:param args: list of transform nodes to change
	:param kwargs:  scale_mult: amount to scale ctrl curve, default 1
					line_width: line width thickness, ignores if not specified
	"""
	scale_mult = kwargs.pop('scale_mult', 1)
	line_width = kwargs.pop('line_width', None)

	ctrl_ls = makePyNodeList(args)

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
# end def scaleCtrlShapes():


# ----------------------------------------------------------------------------------------------------------------------
def lockHide(attr_data, *args):
	"""
	Lock and hide attributes from dictionary

	:param attr_data: 	(dictionary) attrs to lock hide eg: {'r':1, 's':'xy', 't':'z', 'v':1, 'custom_attr':1}
						also accepts 'all' to lock/hide all default channels
	:param args:		list of nodes to lockHide
	"""

	objs = makePyNodeList(args)

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
def parentByList(node_list):
	"""
	Parent nodes in hierarchy dictated by list order.
	:param node_list: list of nodes, or node string names
	:return: None
	"""
	node_list = makePyNodeList(node_list)
	for i in range(len(node_list)-1):
		pm.parent(node_list[i], node_list[i+1])
# end def parentByList():


# ----------------------------------------------------------------------------------------------------------------------
def cleanJointOrients(jnts):
	"""
	Converts joint orient values to rotations only.
	:param jnts: list of joints
	:return: None
	"""
	jnts = makePyNodeList(jnts, type='joint')

	for jnt in jnts:
		jnt_mtx = jnt.matrix.get()
		jnt.jointOrient.set(0, 0, 0)
		pm.xform(jnt, m=jnt_mtx)
# end def cleanJointOrients():


# ----------------------------------------------------------------------------------------------------------------------
def cleanScaleCompensate(jnts):
	"""
	Breaks inverse scale connections and sets segments scale compensate off.
	:param jnts: List of joints.
	:return: None
	"""
	jnts = makePyNodeList(jnts, type='joint')

	for jnt in jnts:
		if not jnt.segmentScaleCompensate.get(lock=True):
			jnt.segmentScaleCompensate.set(0, lock=True)
		inv_scale_input = jnt.inverseScale.inputs(p=True)
		if inv_scale_input:
			inv_scale_input[0] // jnt.inverseScale
# end def cleanScaleCompensate():


# ----------------------------------------------------------------------------------------------------------------------
def roundRotation(nodes, round_val=90):
	"""
	Rounds rotation to nearest multiple of given value
	:param nodes:  Transform nodes to round rotation value.
	:param round_val:  Value to round to.
	:return:  None
	"""
	nodes = makePyNodeList(nodes)

	for node in nodes:
		if node.rotate.get(settable=True):
			for rotAxis in node.rotate.iterDescendants():
				rotAxis.set(round(rotAxis.get() / round_val) * round_val)
# end def roundRotation():


# ----------------------------------------------------------------------------------------------------------------------
def iterDgNodes(root, up_stream=False, down_stream=False, end=None):
	"""
	Simplified version of MItDependencyGraph from api.
	:param root:  `PyNode` None to start iteration from.
	:param up_stream:  `bool` Traverse the graph upstream.
	:param down_stream:  `bool` Traverse the graph downstream.
	:param end:  `PyNode` Don't iterate past this node.
	:yield:  Pynode
	"""
	dirty = []
	stack = root.listConnections(source=up_stream, destination=down_stream)

	while stack:
		this_node = stack.pop()
		if this_node in dirty or this_node == end:
			continue
		dirty.append(this_node)

		stack = stack + this_node.listConnections(source=up_stream, destination=down_stream)

		yield this_node
# end def iterDgNodes():


# ----------------------------------------------------------------------------------------------------------------------
# 											BIND POSE UTILITY FUNCTIONS
# ----------------------------------------------------------------------------------------------------------------------
def getBindJoints(skin_clusters=None):
	"""
	Get joints connected to a skin cluster.
	:param skin_clusters: Pass a list of skin cluster PyNodes, if None will use all in scene.
	:return: list of bind joints
	"""
	if not skin_clusters:
		skin_clusters = pm.ls(type='skinCluster')

	bind_jnts = set()
	for skin_node in skin_clusters:
		bind_jnts |= set(skin_node.matrix.inputs())

	return list(bind_jnts)


# ----------------------------------------------------------------------------------------------------------------------
def setSceneToBindPose():
	"""
	Sets the scene to bind pose.
	:return: None
	"""
	bind_jnts = getBindJoints()

	input_nodes = set()
	for jnt in bind_jnts:
		input_nodes |= set(jnt.inputs())

	# set nodes to blocking
	for node in input_nodes:
		node.nodeState.set(2)

	pm.dagPose(bind_jnts, bindPose=True, restore=True)
# end def setSceneToBindPose():


# ----------------------------------------------------------------------------------------------------------------------
def undoSetSceneToBindPose():
	"""
	Unblock nodes connected to bind joints, enabling constraints to work as normal.
	:return: None
	"""
	bind_jnts = getBindJoints()

	input_nodes = set()
	for jnt in bind_jnts:
		input_nodes |= set(jnt.inputs())

	# set nodes to blocking
	for node in input_nodes:
		node.nodeState.set(0)
# end def undoSetSceneToBindPose():


# ----------------------------------------------------------------------------------------------------------------------
def resetBindPose(jnts, selected=False):
	"""
	Resets the bind pose as if the skin was bound to the skeleton as it exists now it world space.
	:param jnts: List of joints to be reset. Use in conjunction with selected flag to get hierarchy.
	:param selected: By default will include all children of given jnts unless this is set to True.
	:return: None
	"""
	jnts = makePyNodeList(jnts)

	jnts_to_reset = set()
	if selected:
		jnts_to_reset |= set(jnts)
	else:
		for jnt in jnts:
			children = jnt.getChildren(ad=True, type='joint')
			jnts_to_reset |= set(children)

	pm.dagPose(jnts_to_reset, bindPose=True, reset=True)

	for jnt in jnts_to_reset:
		inv_world_mtx = jnt.worldInverseMatrix[0].get()

		skin_outputs = jnt.worldMatrix[0].outputs(p=True, type='skinCluster')
		for skin in skin_outputs:
			joint_index = skin.index()

			pre_mtx_attr = skin.node().attr('bindPreMatrix')

			jnt_pre_mtx = pre_mtx_attr.elementByLogicalIndex(joint_index)
			jnt_pre_mtx.set(inv_world_mtx)
# end def resetBindPose():


# ----------------------------------------------------------------------------------------------------------------------
# TODO: use are length vector not local end vect
def positionUpVectorFromPoints(point_start, point_mid, point_end, magnitude=1.2):
	"""
	Gets xyz world co-ordinates for a projected point that sits on the plane of the specified points.
	Useful for positioning pole vectors.
	:param point_start:		3d co-ordinates for start vector.
	:param point_mid:		3d co-ordinates for mid vector.
	:param point_end:		3d co-ordinates for end vector.
	:param magnitude:		Will project final vector by a scalar calculated from:
							(mid - start) + (end - start) multiplied by this value.
							Default = 1.2
	:return: 3d vector.
	"""
	start_vect = pm.datatypes.Vector(point_start)
	mid_vect = pm.datatypes.Vector(point_mid)
	end_vect = pm.datatypes.Vector(point_end)

	end_local_vect = end_vect - start_vect
	mid_local_vect = mid_vect - start_vect

	mid_vect_scalar = (end_local_vect * mid_local_vect) / (end_local_vect * end_local_vect)

	projected_mid_vect = end_local_vect * mid_vect_scalar

	mid_diff_vect = mid_local_vect - projected_mid_vect

	scaled_pv_local_vect = mid_diff_vect * math.sqrt(sum(map(lambda x: x ** 2, end_local_vect))) * magnitude

	return scaled_pv_local_vect + start_vect + projected_mid_vect
# end def positionUpVectorFromPoints():


# ----------------------------------------------------------------------------------------------------------------------
# 											MATRIX UTILITY FUNCTIONS
# ----------------------------------------------------------------------------------------------------------------------

def matrixConstraint(parent_node, *args, **kwargs):
	"""
	Constrain a parent node to a child node or list of children nodes.

	:param parent_node:	(PyNode/string or PyNode attribute) Parent/constrainer node. Can not have more than one parent.
						Will use node's worldMatrix by default. Anything else pass the specific attribute.

	:param args:		Child or multiple children to be constrained.

	:param kwargs:		>maintainOffset / mo:	Maintains the offset between parent and child.
												Default = True.
						>skipTranslate / st: 	Possible arguments: 'xyz', will skip these channels.
												Default applies constraint to all channels.
						>skipRotate / sr:	 	Possible arguments: 'xyz', will skip these channels.
												Default applies constraint to all channels.
						>skipScale / ss:	 	Possible arguments: 'xyz', will skip these channels.
												Default applies constraint to all channels.
						>name / n:				Base name for nodes.
												Default uses node name of parent_node.
						>inverseParent / ip:	Add an additional connection to the mult matrix to counter a parent node.
												If passed node will use worldInverseMatrix of the node.
												If passed attribute will use that attribute.

	:return: None
	"""
	# Get name
	name = kwargs.pop('name', kwargs.pop('n', parent_node.node()))

	# Get parent as attribute plug
	if isinstance(parent_node, basestring):
		parent_node = pm.PyNode(parent_node)

	if type(parent_node).__name__ == 'Attribute':
		parent_matrix = parent_node
	else:
		parent_matrix = parent_node.attr('worldMatrix[0]')

	# If inverse parent specified get it as attribute plug
	inverse_parent = kwargs.pop('inverseParent', kwargs.pop('ip', None))
	if inverse_parent:
		if not type(inverse_parent).__name__ == 'Attribute':
			inverse_parent = inverse_parent.attr('worldInverseMatrix')

	children = makePyNodeList(args)
	if not children:
		raise UtilsException('--Failed to provide any valid child nodes to constrain.')

	# If maintain offset specified get it, else set to True by default.
	maintain_offset = kwargs.pop('maintainOffset', kwargs.pop('mo', True))

	target_axis = []
	for key_names in [('skipTranslate', 'st'), ('skipRotate', 'sr'), ('skipScale', 'ss')]:
		exclude_axis = (kwargs.pop(key_names[0], kwargs.pop(key_names[1], '')))

		target = 'xyz'
		for axis in exclude_axis:
			target = target.replace(axis, '')

		target_axis.append(target)

	# At this point if there are still kwargs there shouldn't be so raise error.
	if kwargs:
		s = 's' if len(kwargs) > 1 else ''
		raise TypeError('--Invalid flag{}: "{}"'.format(s, '", "'.join(kwargs.keys())))

	def connectDecomposeToNodes(decompose_node, child_nodes):
		"""
		Finalizes the constraint with connections into the child node(s).
		"""
		for target_node in child_nodes:
			for j, transform in enumerate(['translate', 'rotate', 'scale']):
				for single_axis in target_axis[j]:
					pm.connectAttr(
						'{}.output{}{}'.format(decompose_node, transform.title(), single_axis.capitalize()),
						'{}.{}{}'.format(target_node, transform, single_axis.capitalize())
					)
	# end connectDecomposeToNodes():

	# if not maintaining offset, no complicated set up required, just connect worldMatrix to all children.
	if not maintain_offset:
		dcmp_m = pm.createNode('decomposeMatrix', n='{}_const_dcmpM'.format(name))
		parent_matrix >> dcmp_m.inputMatrix
		connectDecomposeToNodes(dcmp_m, children)
		return

	# Categorize the list of children into nested lists of children with the same world space.
	children_categorized = []
	matrix_tracker = []
	for child in children:
		this_world_matrix = child.worldMatrix[0].get()

		if this_world_matrix in matrix_tracker:
			# Current child matrix already exists, so append to the nested list of children.
			child_index = matrix_tracker.index(this_world_matrix)
			children_categorized[child_index].append(child)
		else:
			# Add new matrix to matrix_tracker and create a new nested list for children with the same matrix.
			matrix_tracker.append(this_world_matrix)
			children_categorized.append([child])

	# Create matrix constraint node network for each nested child.
	for i, nested_children in enumerate(children_categorized):
		mult_m = pm.createNode('multMatrix', n='{}_{:02d}_const_multM'.format(name, i + 1))
		offset_dcmp_m = pm.createNode('decomposeMatrix', n='{}_{:02d}_const_dcmpM'.format(name, i + 1))

		# Can just get the local offset from first child in list as they should all have same world space.
		child_matrix = nested_children[0].worldMatrix[0].get()
		offset_matrix = child_matrix * parent_matrix.get().inverse()

		mult_m.matrixIn[0].set(offset_matrix)
		parent_matrix >> mult_m.matrixIn[1]
		if inverse_parent is not None:
			inverse_parent >> mult_m.matrixIn[2]

		mult_m.matrixSum >> offset_dcmp_m.inputMatrix

		connectDecomposeToNodes(offset_dcmp_m, nested_children)
# end matrixConstraint():


# ----------------------------------------------------------------------------------------------------------------------
# 											RIG BOT UTILITY FUNCTIONS
# ----------------------------------------------------------------------------------------------------------------------

def getFilteredDir(folder, ignore_private=True):
	"""
	Return list of files in give folder

	:param folder: `string` name of folder within rigbot dir
	:param ignore_private: `bool` ignore private modules unless specified not to.
	:return: string name of python files that are not __init__ or end with Base.py
	"""

	main_dir = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))

	files = [
		x.split('.')[0] for x in os.listdir(main_dir+'\\{}'.format(folder))
		if x.endswith('.py')
		and not x.count('__init__')
		and not x.endswith('Base.py')
		and not (x.startswith('_') if ignore_private else 0)
	]

	return files
# end def getFilteredDir():


# ----------------------------------------------------------------------------------------------------------------------
def makeRoot():
	"""
	Returns pynode of root joint or creates new one if none exists.  Also creates cog placement joint.

	:return: root joint
	"""
	if pm.objExists(user.prefs['root-joint']):
		root_jnt = pm.PyNode(user.prefs['root-joint'])
	else:
		pm.select(deselect=True)
		root_jnt = pm.joint(n=user.prefs['root-joint'], radius=0.001)

		ctrl = pm.curve(d=1, p=data.controllerShapes['locator'], n=(user.prefs['root-joint'] + '_display'))
		scaleCtrlShapes(ctrl, scale_mult=1.43, line_width=3)

		ctrl_shape = ctrl.getChildren()[0]
		setOverrideColour(user.prefs['module-root-colour'], [root_jnt, ctrl_shape])
		setOutlinerColour(user.prefs['module-root-colour'], root_jnt)

		pm.parent(ctrl_shape, root_jnt, r=True, s=True)
		pm.delete(ctrl)

		tags = [
			{'name': 'RB_MODULE_ROOT', 'at': 'enum', 'en': ' ', 'k': 0, 'l': 1},
			{'name': 'RB_module_type', 'k': 0, 'at': 'enum', 'en': '_Root'},
		]
		for tag in tags:
			makeAttrFromDict(root_jnt, tag)

		cog_place = pm.createNode('joint', n='cog_placement')

		cog_place.drawStyle.set(1)
		cog_place.radius.set(0.001)
		setOverrideColour('pink', cog_place)
		setOutlinerColour('pink', cog_place)

		display = [pm.createNode('joint', n='cog_display_{:02d}'.format(i)) for i in range(2)]

		display[0].translate.set([1.5, 1.5, 1.5])
		display[1].translate.set([-1.5, -1.5, -1.5])

		for jnt in display:
			jnt.radius.set(0.01)
			jnt.setParent(cog_place)
			jnt.visibility.set(0)
			jnt.hiddenInOutliner.set(1)

		cog_place.setParent(root_jnt)
		cleanScaleCompensate(display)
		cleanScaleCompensate(cog_place)
		lockHide({'r': 1, 's': 'xy', 't': 'z', 'v': 1}, *display)

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

	module_roots = filter(lambda jnt: jnt.hasAttr('RB_MODULE_ROOT'), flattened_jnts)
	short_mod_roots = map(lambda mod_r: mod_r.nodeName(), module_roots)

	modname = modroot.shortName()

	def filterChildren(jnt):
		flat_hierarchy = jnt.fullPath().split('|')

		mod_index = 0
		other_mod_index = []
		for parent in flat_hierarchy:
			if modname == parent:
				mod_index = flat_hierarchy.index(parent)
			else:
				for s_modr in short_mod_roots:
					if s_modr == parent:
						other_mod_index.append(flat_hierarchy.index(parent))

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
	while pm.objExists(new_name + suffix):
		new_name = '{}{}'.format(name, i)
		i += 1

	return new_name
# end makeNameUnique():


# ----------------------------------------------------------------------------------------------------------------------
def createRigBotMetadataNode():
	"""
	Creates or gets existing rigbot metadata node for storing information such as bind pose metadata.
	:return: PyNode of rigbot container.
	"""
	if pm.objExists('rigbot'):
		rb_node = pm.PyNode('rigbot')
	else:
		rb_node = pm.createNode('container', n='rigbot')
		# TODO:
		rb_node.iconName.set(r'C:\Users\iaman\Documents\maya\scripts\rigbot\icons\R50.png')
		pm.lockNode(rb_node, lock=True)

	return rb_node
# end def createRogBotMetadataNode():


# ----------------------------------------------------------------------------------------------------------------------
def deleteRigBotMetadataNode():
	"""
	Deletes if node has no existing metadata.
	:return: None
	"""
	if pm.objExists('rigbot'):
		rb_node = pm.PyNode('rigbot')

	metadata = rb_node.listAttr(ud=True)
	if not metadata:
		pm.lockNode(rb_node, lock=False)
		pm.delete(rb_node)
# end def deleteRigBotMetadataNode():


# ----------------------------------------------------------------------------------------------------------------------
def getModuleNodes(module_grp):
	"""
	Get all nodes associated with a module.  Requires correct module group structure.
	:param module_grp:  `PyNode` Root group of module.
	:return:  Set of all module PyNodes.
	"""
	module_dag = module_grp.getChildren(ad=True)

	input = next((x for x in module_dag if x.endswith('input')), None)
	output = next((y for y in module_dag if y.endswith('output')), None)

	if input is None or output is None:
		raise TypeError('--Failed to find input and/or ouput nodes in hierarchy.')

	module_nodes = {module_grp}
	module_nodes |= set([x for x in iterDgNodes(input, down_stream=True, end=output)])
	module_nodes |= set([x for x in iterDgNodes(output, up_stream=True, end=input)])

	for this_dag in module_dag:
		if this_dag in module_nodes:
			continue
		module_nodes.add(this_dag)

	return module_nodes
# end getModuleNodes():
