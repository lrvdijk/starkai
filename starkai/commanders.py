"""
:mod:`starkai.commanders` - AI Commander classes
================================================

The classes in this module control all the bots in a certain game

.. module:: starkai.commanders
   :synopsis: AI Commander classes

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from api import Commander
from api import commands
from api import Vector2
from math import floor

from starkai.influencemap import GridInfluenceMap

class RobbStarkCommander(Commander):
	"""
		Our main commander, uses influence maps to make decisions.
	"""

	def initialize(self):
		self.verbose = True

		self.blocked = []

		for x, ylist in enumerate(self.game.blockHeights):
			for y, value in enumerate(ylist):
				if value > 0:
					self.blocked.append((x, y))

		# Setup some influence maps
		self.my_influence = GridInfluenceMap(width=self.level.width, height=self.level.height)
		self.enemy_influence = GridInfluenceMap(width=self.level.width, height=self.level.height)
		self.goal_influence = GridInfluenceMap(0.7, 0.8, self.level.width, self.level.height)

		self.my_influence.set_blocked(self.blocked)
		self.enemy_influence.set_blocked(self.blocked)
		self.goal_influence.set_blocked(self.blocked)

		for bot in self.game.bots_alive:
			self.my_influence.set_influence((floor(bot.position.x), floor(bot.position.y)), 1.0)

		# If there are some enemy bots visible at the beginning, add them to the influence map
		for bot in self.game.enemyTeam.members:
			if bot.health > 0:
				print bot.position
				self.enemy_influence.set_influence((floor(bot.position.x), floor(bot.position.y)), 1.0)

		for flag in self.game.enemy_flags:
			self.goal_influence.set_influence((floor(flag.position.x), floor(flag.position.y)), 2.0)

		# Let the values propagate a bit
		self.my_influence.update_map(20)
		self.enemy_influence.update_map(20)
		self.goal_influence.update_map(20)

		self.influence_map = self.my_influence - self.enemy_influence
		self.final_influence = self.influence_map + self.goal_influence

	def tick(self):
		"""
			Time to issue new commands!
		"""



