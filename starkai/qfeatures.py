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
from __future__ import division
from abc import ABCMeta, abstractmethod
from math import floor
import sys
from starkai.util import euclidean_dist, Counter, find_closest

class BaseFeatureProvider(object):

	__metaclass__ = ABCMeta

	@abstractmethod
	def get_features(self, state, action):
		"""
			Get the feature values for the given state-action pair
		"""
		pass

class FlagSearcherFeatureProvider(BaseFeatureProvider):
	"""
		This class provides features based on different
		influence maps, and on the positions of some enemies,
		of course the flag location.
	"""

	def __init__(self, commander):
		self.commander = commander

	def get_features(self, state, action):
		position = (floor(state.position[0]+action[0]), floor(state.position[1]+action[1]))

		min_flag_dist = find_closest([(flag.position.x, flag.position.y) for flag in self.commander.game.enemyFlags], position)
		min_enemy_dist = find_closest(
			[(bot.position.x, bot.position.y) for bot in self.commander.game.enemyTeam.members if bot.health > 0 and bot.seenlast < 5],
			position
		)

		max_level_distance = euclidean_dist((0, 0), (self.commander.level.width, self.commander.level.height))

		features = Counter()
		features['bias'] = 1.0
		features['my-influence'] = self.commander.my_influence[position]
		features['enemy-influence'] = self.commander.enemy_influence[position]
		features['goal-influence'] = self.commander.goal_influence[position]
		features['visibility'] = self.commander.visibility[position]
		features['flag-distance'] = 1.0 - (min_flag_dist / max_level_distance)
		features['enemy-distance'] = min_enemy_dist / max_level_distance if min_enemy_dist != sys.maxint else 1.0

		#features.divide_all(10.0)

		return features

class FlagReturnerFeatureProvider(BaseFeatureProvider):
	"""
		This class provides features based on different
		influence maps, and on the positions of some enemies,
		of course the flag location.
	"""

	def __init__(self, commander):
		self.commander = commander

	def get_features(self, state, action):
		position = (floor(state.position[0]+action[0]), floor(state.position[1]+action[1]))

		score_loc = self.commander.game.team.flagScoreLocation
		score_dist = euclidean_dist((score_loc.x, score_loc.y), position)
		min_enemy_dist = find_closest(
			[(bot.position.x, bot.position.y) for bot in self.commander.game.enemyTeam.members if bot.health > 0 and bot.seenlast < 5],
			position
		)

		max_level_distance = euclidean_dist((0, 0), (self.commander.level.width, self.commander.level.height))

		features = Counter()
		features['bias'] = 1.0
		features['my-influence'] = self.commander.my_influence[position]
		features['enemy-influence'] = self.commander.enemy_influence[position]
		features['goal-influence'] = self.commander.goal_influence[position]
		features['visibility'] = self.commander.visibility[position]
		features['flag-distance'] = 1.0 - (score_dist / max_level_distance)
		features['enemy-distance'] = min_enemy_dist / max_level_distance if min_enemy_dist != sys.maxint else 1.0

		#features.divide_all(10.0)

		return features





