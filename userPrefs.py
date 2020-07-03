# ----------------------------------------------------------------------------------------------------------------------
'''

   USERPREFS.PY

  !Warning: Changing any naming convention prefs here may mean re-rigging any 
   current scenes from the initial set-up stage unless you change them back to 
   the prefs you originally used.

'''
# ----------------------------------------------------------------------------------------------------------------------


class user:

	_prefs = {
			'root-joint'			: 'root_BIND',
			'bind-skeleton-suffix'	: 'BIND',
			'default-jnt-colour'	: 'grey-blue',
			'module-root-colour'	: 'pale-orange',

			'root-ctrl-name'		: 'GOD',
			'root2-ctrl-name'		: 'GOD_02',
			'ctrl-suffix'			: 'ctrl',
			'num-offset-ctrls'		: 1,

			'left-prefix'			: 'L',
			'right-prefix'			: 'R',
		}

	@staticmethod
	def prefs(pref):
		return user._prefs[pref]
	# end def prefs(pref):
# end class user:
