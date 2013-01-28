"""
:mod:`starkai.commanders` - AI Commander classes
================================================

The classes in this module control all the bots in a certain game

.. module:: starkai.commanders
   :synopsis: AI Commander classes

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from api import Commander
from api import Vector2
from api.gameinfo import MatchCombatEvent
from math import floor
import random

from starkai import agents
from starkai.influencemap import GridInfluenceMap
from starkai.visibility import Wave
from starkai.qlearner import ApproximateQLearner
from starkai.qfeatures import MapFeatureProvider
from starkai.states import GameState
from starkai.util import Counter

class RobbStarkCommander(Commander):
	"""
		Our main commander, uses influence maps to make decisions.
	"""

	def initialize(self):
		self.verbose = True
		self.state = GameState(self.game)

		# Setup some influence maps
		self.my_influence = GridInfluenceMap(width=self.level.width, height=self.level.height,
			is_blocked=self.state.is_blocked)
		self.enemy_influence = GridInfluenceMap(width=self.level.width, height=self.level.height,
			is_blocked=self.state.is_blocked)
		self.goal_influence = GridInfluenceMap(0.7, 0.8, self.level.width, self.level.height,
			is_blocked=self.state.is_blocked)

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
		self.my_influence.update_map(3)
		self.enemy_influence.update_map(3)
		self.goal_influence.update_map(3)

		self.influence_map = self.my_influence - self.enemy_influence
		self.final_influence = self.influence_map + self.goal_influence

		# Calculate visibility map
		print "Calculating visibility map..."
		self.visibility = Counter()

		for i in range(1000):
			point = Vector2(random.randint(0, self.level.width), random.randint(0, self.level.height))

			visible_cells = []

			def visible(p):
				delta = (p-point)
				l = delta.length()

				return l <= self.game.characterRadius

			wave = Wave((self.level.width, self.level.height),
				lambda x, y: self.game.blockHeights[x][y] > 1,
				lambda x, y: visible_cells.append((x, y))
			)

			wave.compute(point)

			for x, y in [c for c in visible_cells if visible(Vector2(c[0]+0.5, c[1]+0.5))]:
				self.visibility[(x, y)] += 1

			if i % 100 == 0:
				print ".",

		self.visibility.normalize()

		print " finished"

		# Initialize roles for each bot
		northman_features = MapFeatureProvider(self.my_influence, self.enemy_influence,
			self.final_influence, self.visibility)
		agents.Northman.set_qlearner(ApproximateQLearner(northman_features))

		self.roles = {}

	def tick(self):
		"""
			Time to issue new commands!
		"""

		for bot in self.game.bots_alive:
			if not bot.name in self.roles:
				self.roles[bot.name] = agents.Northman(bot, self, -0.5)

		# Update influence maps
		for bot in self.game.bots_alive:
			self.my_influence.set_influence((floor(bot.position.x), floor(bot.position.y)), 1.0)

		# If there are some enemy bots visible, add them to the influence map
		for bot in self.game.enemyTeam.members:
			if bot.health > 0:
				print bot.position
				self.enemy_influence.set_influence((floor(bot.position.x), floor(bot.position.y)), 1.0)

		for flag in self.game.enemy_flags:
			self.goal_influence.set_influence((floor(flag.position.x), floor(flag.position.y)), 2.0)

		self.my_influence.update_map()
		self.enemy_influence.update_map()
		self.goal_influence.update_map()

		# Check for new events
		for event in self.game.combatEvents:
			if event.subject.name in self.roles:
				action = self.roles[event.subject.name].handle_event(event)

				if action:
					self.commandQueue.append(action)

			if event.instigator.name in self.roles:
				action = self.roles[event.instigator.name].handle_event(event)

				if action:
					self.commandQueue.append(action)

			if event.type == MatchCombatEvent.TYPE_KILLED:
				if event.subject.name in self.roles:
					self.roles[event.subject.name].died()
					del self.roles[event.subject.name]

		self.game.combatEvents[:] = []

		for bot in self.game.bots_available:
			action = self.roles[bot.name].handle_event()

			if action:
				self.commandQueue.append(action)









