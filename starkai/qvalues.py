"""
:mod:`starkai.qvalues` - Latest Q-values for Q-learning
=======================================================

This file will contain the latest obtained q-values. Note that
this file will be overwritten after each run.

.. module:: starkai.commanders
   :synopsis: AI Commander classes

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

latest = {
	'Northman': {
		'goal-influence': 1,
		'enemy-influece': 1,
		'my-influence': 1,
		'visibility': 1,
		'flag-distance': 1,
		'enemy-distance': -1
	}
}
