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
prefs = \
	{
		'root-joint'			: 'root_BIND',
		'bind-skeleton-suffix'	: 'BIND',
		'default-jnt-colour'	: 'grey-blue',
		'module-root-colour'	: 'light-orange',

		'module-group-name'		: 'modules',

		'root-ctrl-name'		: 'GOD',
		'root2-ctrl-name'		: 'GOD_2',
		'cog-ctrl-name'			: 'cog',
		'pivot-ctrl-name'		: 'cog_pivot',
		'ctrl-suffix'			: 'ctrl',
		'num-offset-ctrls'		: 0,
		'default-line-width'	: 2,

		'left-prefix'			: 'L',
		'right-prefix'			: 'R',

		'viewport-colour-space'	: 'sRGB',
	}

# TODO: node naming convention pref? ^


class RigNode(object):
	def __init__(self, component, children=None):
		self.component = component
		self.children = children
# end class RigNode():


# RigTree = RigNode('RIG', [
# 			RigNode('ctrl_grp', [RigNode(prefs['root-ctrl-name'])]), RigNode(prefs['root-joint']),
# 			RigNode(prefs['module-group-name'])
# 	]
# )


RigTree = RigNode(
	prefs['root-ctrl-name'],
		[
		RigNode(prefs['root-joint']), RigNode(prefs['module-group-name'])
		]
	)
