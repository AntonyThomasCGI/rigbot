# ----------------------------------------------------------------------------------------------------------------------
"""

   USER.PY

  !Warning: Changing any naming convention prefs here may mean re-rigging any 
   current scenes from the initial set-up stage unless you change them back to 
   the prefs you originally used.

"""
# ----------------------------------------------------------------------------------------------------------------------

# config
debug = True

# preferences
prefs = {
	'root-joint'			: 'root_BIND',
	'bind-skeleton-suffix'	: 'BIND',
	'default-jnt-colour'	: 'grey-blue',
	'module-root-colour'	: 'pale-orange',

	'rig-group-name'		: 'do_not_touch',
	'joint-group-name'		: 'joints',

	'root-ctrl-name'		: 'GOD',
	'root2-ctrl-name'		: 'PLACEMENT',
	'ctrl-suffix'			: 'ctrl',
	'num-offset-ctrls'		: 1,
	'default-line-width'	: 2,

	'left-prefix'			: 'L',
	'right-prefix'			: 'R',
}


class RigNode(object):
	def __init__(self, component, children=None):
		self.component = component
		self.children = children
# end class RigNode():


# RigTree = RigNode('RIG', [
# 			RigNode('ctrl_grp', [RigNode(prefs['root-ctrl-name'])]), RigNode(prefs['joint-group-name']),
# 			RigNode(prefs['module-group-name']), RigNode(prefs['rig-group-name'], [
# 				RigNode('transform'), RigNode('no_transform')
# 		])
# 	]
# )
RigTree = RigNode(
	prefs['root-ctrl-name'],
		[
		RigNode(prefs['joint-group-name']), RigNode('modules')
		]
	)
