"""
:mod:`starkai.qfeatures` - Feature providers for approximate q-learning
=======================================================================

When using approximate q-learning, you must provide some features
to base the game state on. This module provides class which in turn
provide the features for appromixate q-learning.

.. module:: starkai.qfeatures
   :synopsis: Q-learning feature providers

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from abc import ABCMeta, abstractmethod
from math import floor

class BaseFeatureProvider(object):

	__metaclass__ = ABCMeta

	@abstractmethod
	def get_features(self, state, action):
		"""
			Get the feature values for the given state-action pair
		"""
		pass

class MapFeatureProvider(BaseFeatureProvider):
	"""
		This class provides features based on different
		influence maps.
	"""

	def __init__(self, my_inf, enemy_inf, final_inf, visibility):
		self.my_inf = my_inf
		self.enemy_inf = enemy_inf
		self.final_inf = final_inf
		self.visibility = visibility

	def get_features(self, state, action):
		position = (floor(state.position[0]+action[0]), floor(state.position[1]+action[1]))

		return {
			'my-influence': self.my_inf.get_influence(position),
			'enemy-influence': self.enemy_inf.get_influence(position),
			'final-influence': self.enemy_inf.get_influence(position),
			'visibility': self.visibility[position]
		}




