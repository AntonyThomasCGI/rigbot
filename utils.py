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
def setOverrideColour(*args, **kwargs):
	"""
	Set node viewport override colour.

	:param args: `PyNode` or `str` Node(s) to apply change.

	:param kwargs:	colour | c: `str` or `[R,G,B]` Colour to set override.
					colourSpace | cs: `str` default = 'sRGB', Colour space to use.
	return None
	"""
	colour = kwargs.pop('colour', kwargs.pop('c', None))
	colour_space = kwargs.pop('colourSpace', kwargs.pop('cs', 'sRGB'))

	if colour is None:
		raise ValueError('--colour flag must be specified.')

	if kwargs:
		raise ValueError('--Unknown argument(s): {}'.format(kwargs))

	item_ls = makePyNodeList(args, type=['transform', 'joint', 'nurbsCurve', 'locator'])

	if isinstance(colour, basestring):
		colour = data.Colours.get_value(colour, space=colour_space)

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
def setOutlinerColour(*args, **kwargs):
	"""
	Set node outliner colour, uses linear colour value by default as outliner applies no colour LUTs.

	:param args: nodes to apply change

	:param kwargs:	colour | c: `str` or `[R,G,B]` Colour to set override.
					colourSpace | cs: `str` default = 'linear', Colour space to use.
	return None
	"""
	colour = kwargs.pop('colour', kwargs.pop('c', None))
	colour_space = kwargs.pop('colourSpace', kwargs.pop('cs', 'sRGB'))

	if colour is None:
		raise ValueError('--Keyword argument: colour must be specified.')

	if kwargs:
		raise ValueError('--Unknown argument(s): {}'.format(kwargs))

	item_ls = makePyNodeList(args, type=['transform', 'joint', 'nurbsCurve', 'locator'])

	if isinstance(colour, basestring):
		colour = data.Colours.get_value(colour, space=colour_space)

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
def makeAttr(ob, **kwargs):
	"""
	Convenience add attr wrapper to include channel box, lock and keyable flags in once function.

	:param ob:	`PyNode` to add attr to.

	:param kwargs:	name | n : `str`, Attribute long name.
					lock | l : `bool` default=0, If attr should be locked.
					channelBox | cb : `bool` default=1, If attr should appear in channel box.

					Also accepts any valid kwarg for addAttr command.

	:return: `Attribute`
	"""
	attr_name = kwargs.pop('name', kwargs.pop('n', None))
	lock = kwargs.pop('lock', kwargs.pop('l', 0))
	channel_box = kwargs.pop('channelBox', kwargs.pop('cb', 1))

	# if keyable not specified set keyable by default
	if not any(key in kwargs for key in ['keyable', 'k']):
		kwargs['keyable'] = 1

	if attr_name is None:
		raise NameError('--Name not specified but is required to make an Attribute.')

	# if already has attr then delete
	if ob.hasAttr(attr_name):
		print('//Warning: Attribute already exists, overriding.')
		pm.setAttr('{}.{}'.format(ob, attr_name), l=False)
		ob.deleteAttr(attr_name)

	ob.addAttr(attr_name, **kwargs)
	ob.setAttr(attr_name, l=lock)

	# channel box flag only set when attr is not keyable so this:
	keyable = kwargs.pop('keyable', kwargs.pop('k', 1))
	if not keyable and channel_box:
		ob.setAttr(attr_name, cb=channel_box)

	return ob.attr(attr_name)
# end def makeAttr():


# ----------------------------------------------------------------------------------------------------------------------
def scaleCtrlShapes(*args, **kwargs):
	"""
	Scale ctrl shapes and set line width

	:param args:  Transform nodes to change
	:param kwargs:  scale_mult | s: amount to scale ctrl curve, default 1
					line_width | lw: line width thickness, ignores if not specified
	"""
	scale_mult = kwargs.pop('scale_mult', kwargs.pop('s', 1))
	line_width = kwargs.pop('line_width', kwargs.pop('lw', None))

	if kwargs:
		raise ValueError('--Unknown argument: {}'.format(kwargs))

	ctrl_ls = makePyNodeList(args)

	for ctrl in ctrl_ls:
		shapes = ctrl.getChildren()
		if ctrl.nodeType() == 'nurbsCurve':
			shapes.append(ctrl)

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
def rotateCtrlShapes(*args, **kwargs):
	"""
	Rotate ctrl shapes around given axis

	:param args:  transform nodes to change
	:param kwargs:  rotate | r: `float` amount to rotate default: 0.0
					axis | a: `list` rotate around these axis default: [1,0,0] TODO: can probs just take rotation value
	:return:  None
	"""
	rot = kwargs.pop('rotate', kwargs.pop('r', 0.0))
	axis = kwargs.pop('axis', kwargs.pop('a', [1, 0, 0]))

	if kwargs:
		raise ValueError('--Unknown argument: {}'.format(kwargs))

	ctrl_ls = makePyNodeList(args)

	result_rot = [a * rot for a in axis]

	for ctrl in ctrl_ls:
		shapes = ctrl.getChildren()
		if ctrl.nodeType() == 'nurbsCurve':
			shapes.append(ctrl)

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
					pm.xform('{}.cv[{}]'.format(shape, i), ro=result_rot)
# end def rotateCtrlShapes():


# ----------------------------------------------------------------------------------------------------------------------
def lockHide(*args, **kwargs):
	"""
	Lock and hide attributes.

	:param args:		List of nodes to lock and hide attributes on.

	:param kwargs:		translate | t : `str` will lock and hide these axis.
						rotate | r : `str` will lock and hide these axis.
						scale | s : `str` will lock and hide these axis.

						Also accepts any attr name with `bool` value eg; visibility = 1
	:return: None
	"""
	objs = makePyNodeList(args)

	to_lock = []
	for item, axis in kwargs.items():
		if any([x == item for x in ['t', 'r', 's', 'translate', 'rotate', 'scale']]):
			for i in range(len(axis)):
				if axis[i] not in ['x', 'y', 'z']:
					raise TypeError('--Not a valid axis: {}. Needs to be x y or z'.format(axis[i]))
				to_lock.append(item + axis[i])

		# for any other attrs just append
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
def resetBindPose(jnts, selected_only=False):
	"""
	Resets the bind pose as if the skin was bound to the skeleton as it exists now it world space.

	:param jnts: `List` of joints to be reset. Use in conjunction with selected flag to get hierarchy.

	:param selected_only: By default will include all children of given jnts unless this is set to True.

	:return: None
	"""
	jnts = makePyNodeList(jnts)

	jnts_to_reset = set()
	if selected_only:
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
# tODO: also if joints are at really small angles it doesn't project it very well
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
		if inverse_parent is not None:
			mult_m = pm.createNode('multMatrix', n='{}_const_multM'.format(name))
			parent_matrix >> mult_m.matrixIn[0]
			inverse_parent >> mult_m.matrixIn[1]
			mult_m.matrixSum >> dcmp_m.inputMatrix
		else:
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
	return offset_dcmp_m
# end matrixConstraint():


# TODO: this doesn't maintain offset hmmm should it?
def matrixBlend(input_a, input_b, blend_attr, name=None):
	"""
	Creates weighted add matrix set up for blending between matrices.

	:param input_a:  `Attribute (Matrix)` or `Matrix` first input to blend.
	:param input_b:  `Attribute (Matrix)` or `Matrix` second input to blend.
	:param blend_attr:  `Attribute` blend from this attribute.
	:param name:  `str` Prefix name for nodes, will use blend_attr node name by default.

	return  `PyNode` of wtAddMatrix node
	"""
	for input in [input_a, input_b]:
		if type(input).__name__ == 'Attribute':
			if not type(input.get()).__name__ == 'Matrix':
				raise TypeError('--Input attribute: {} is not a matrix plug'.format(input))
		else:
			if not type(input).__name__ == 'Matrix':
				raise TypeError('--Input: {} is not of type `Matrix`'.format(input))

	if name is None:
		name = '{}_blnd'.format(blend_attr.node())

	rvrs = pm.createNode('reverse', n='{}_rvrs'.format(name))
	wt_add = pm.createNode('wtAddMatrix', n='{}_wtAdM'.format(name))

	if type(input_a).__name__ == 'Matrix':
		wt_add.wtMatrix[0].m.set(input_a)
	else:
		input_a >> wt_add.wtMatrix[0].m

	if type(input_b).__name__ == 'Matrix':
		wt_add.wtMatrix[1].m.set(input_b)
	else:
		input_b >> wt_add.wtMatrix[1].m

	blend_attr >> rvrs.inputX
	rvrs.outputX >> wt_add.wtMatrix[0].w
	blend_attr >> wt_add.wtMatrix[1].w

	return wt_add
# end def matrixBlend():


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
		setOverrideColour(root_jnt, ctrl_shape, c=user.prefs['module-root-colour'])
		setOutlinerColour(root_jnt, c=user.prefs['module-root-colour'])

		pm.parent(ctrl_shape, root_jnt, r=True, s=True)
		pm.delete(ctrl)

		tags = [
			{'name': 'RB_MODULE_ROOT', 'at': 'enum', 'en': ' ', 'k': 0, 'l': 1},
			{'name': 'RB_module_type', 'k': 0, 'at': 'enum', 'en': '_Root'},
		]
		for tag in tags:
			makeAttr(root_jnt, **tag)

		cog_place = pm.createNode('joint', n='cog_placement')

		cog_place.drawStyle.set(1)
		cog_place.radius.set(0.001)
		setOverrideColour(cog_place, c='pink')
		setOutlinerColour(cog_place, c='pink')

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
		lockHide(*display, r='xyz', s='xyz', t='xyz', v=1)

	return root_jnt
# end def makeRoot():


# ----------------------------------------------------------------------------------------------------------------------
# TODO: This still fails when duplicate names but probably possible to make it work.
def getModuleChildren(modroot):
	"""
	Find all the child joints within a module.

	:param modroot: Module root.
	:return: list of modules joints including module root.
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
# TODO: doesn't pick up nodes between ctrls and nulls eg; reverse nodes for blends.
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
		raise TypeError('--Failed to find input and/or output nodes in hierarchy.')

	module_nodes = {module_grp}
	module_nodes |= set([x for x in iterDgNodes(input, down_stream=True, end=output)])
	module_nodes |= set([x for x in iterDgNodes(output, up_stream=True, end=input)])

	for this_dag in module_dag:
		if this_dag in module_nodes:
			continue
		module_nodes.add(this_dag)

	return module_nodes
# end getModuleNodes():
