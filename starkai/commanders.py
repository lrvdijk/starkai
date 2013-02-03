"""
:mod:`starkai.commanders` - AI Commander classes
================================================

The classes in this module control all the bots in a certain game

.. module:: starkai.commanders
   :synopsis: AI Commander classes

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""
from __future__ import division
from math import floor, exp
import random
import sys
from datetime import datetime

from api import Commander
from api import Vector2
from api.gameinfo import MatchCombatEvent

from starkai import agents, qvalues
from starkai.influencemap import GridInfluenceMap
from starkai.visibility import Wave
from starkai.qlearner import ApproximateQLearner
from starkai.states import GameState
from starkai.util import Counter

DEBUG = True

if DEBUG:
	try:
		from starkai.visualizer import VisualizerWindow
	except ImportError:
		DEBUG = False

class RobbStarkCommander(Commander):
	"""
		Our main commander, uses influence maps to make decisions.
	"""

	def initialize(self):
		self.verbose = True
		self.state = GameState(self)
		self.counter = 0
		self.last_event_index = 0

		# Setup some influence maps
		self.my_influence = GridInfluenceMap(0.2, 0.5, self.level.width, self.level.height,
			is_blocked=self.state.is_blocked)
		self.enemy_influence = GridInfluenceMap(0.1, 0.6, self.level.width, self.level.height,
			is_blocked=self.state.is_blocked)
		self.goal_influence = GridInfluenceMap(0.01, 0.9, self.level.width, self.level.height,
			is_blocked=self.state.is_blocked)

		print "Calculating influence maps..."
		i = 0
		while i < 5:
			for bot in self.game.bots_alive:
				self.my_influence.set_influence((floor(bot.position.x), floor(bot.position.y)), 1.0)

			# If there are some enemy bots visible at the beginning, add them to the influence map
			for bot in self.game.enemyTeam.members:
				if bot.health > 0:
					self.enemy_influence.set_influence((floor(bot.position.x), floor(bot.position.y)), 1.0)

			for flag in self.game.enemyFlags:
				self.goal_influence.set_influence((floor(flag.position.x), floor(flag.position.y)), 1.0)

			# Let the values propagate a bit
			self.my_influence.update_map()
			self.enemy_influence.update_map()
			self.goal_influence.update_map()
			i += 1

			print i

		# Calculate visibility map
		print "Calculating visibility map..."
		self.visibility = Counter()

		max_visibility = 0
		for i in range(1000):
			point = Vector2(random.randint(0, self.level.width - 1), random.randint(0, self.level.height - 1))

			visible_cells = []

			def visible(p):
				delta = (p-point)
				l = delta.length()

				return l <= 15.0

			wave = Wave((self.level.width, self.level.height),
				lambda x, y: self.level.blockHeights[x][y] > 1,
				lambda x, y: visible_cells.append((x, y))
			)

			wave.compute(point)

			for x, y in [c for c in visible_cells if visible(Vector2(c[0]+0.5, c[1]+0.5))]:
				self.visibility[(x, y)] += 1

				max_visibility = max(self.visibility[(x, y)], max_visibility)

			if i % 100 == 0:
				print ".",

		self.visibility.divide_all(max_visibility)

		print " finished"

		# Initialize roles for each bot
		self.learners = {}
		for agent in agents.available:
			if agent in dir(agents):
				cls = getattr(agents, agent)

				features = cls.feature_class(self)

				learner = ApproximateQLearner(self.state, features,
					alpha=self.alpha,
					gamma=self.gamma,
					epsilon=self.epsilon
				)

				if agent in qvalues.latest:
					learner.set_weights(qvalues.latest[agent])

				self.learners[agent] = learner
				cls.set_qlearner(learner)

		self.roles = {}

		# Setup visualizer window
		if DEBUG:
			self.window = VisualizerWindow(self)

	@property
	def influence(self):
		return self.my_influence - self.enemy_influence

	@property
	def final_influence(self):
		return (self.influence + self.goal_influence) / 2

	def tick(self):
		"""
			Time to issue new commands!
		"""

		self.counter += 1

		for bot in self.game.bots_alive:
			if not bot.name in self.roles:
				self.roles[bot.name] = agents.Northman(bot, self, -0.5)

		# Update influence maps
		for bot in self.game.bots_alive:
			self.my_influence.set_influence((floor(bot.position.x), floor(bot.position.y)), 1.0)

		# If there are some enemy bots visible, add them to the influence map
		for bot in self.game.enemyTeam.members:
			if bot.health > 0:
				self.enemy_influence.set_influence((floor(bot.position.x), floor(bot.position.y)), 1.0)

		for flag in self.game.enemyFlags:
			self.goal_influence.set_influence((floor(flag.position.x), floor(flag.position.y)), 1.0)

		if self.counter >= 2:
			print "update maps"
			self.my_influence.update_map()
			self.enemy_influence.update_map()
			self.goal_influence.update_map()

			self.counter = 0

		# Check for new events
		while self.last_event_index < len(self.game.match.combatEvents):
			event = self.game.match.combatEvents[self.last_event_index]

			types = {
				MatchCombatEvent.TYPE_FLAG_CAPTURED: "Flag captured",
				MatchCombatEvent.TYPE_FLAG_PICKEDUP: "Flag picked up",
				MatchCombatEvent.TYPE_FLAG_DROPPED: "Flag Dropped",
				MatchCombatEvent.TYPE_KILLED: "Bot Killed",
				MatchCombatEvent.TYPE_FLAG_RESTORED: "Flag Restored",
				MatchCombatEvent.TYPE_NONE: "None",
				MatchCombatEvent.TYPE_RESPAWN: "Respawn"
			}

			print "Event index:", self.last_event_index
			print "Event:", types[event.type]

			# Check for flag captured
			if event.type == MatchCombatEvent.TYPE_FLAG_PICKEDUP:
				if event.instigator.name in self.roles:
					self.roles[event.instigator.name] = agents.FlagReturner(self)

			if event.subject and event.subject.name in self.roles:
				action = self.roles[event.subject.name].handle_event(event)

				if action:
					self.commandQueue.append(action)

			if event.instigator and event.instigator.name in self.roles:
				action = self.roles[event.instigator.name].handle_event(event)

				if action:
					self.commandQueue.append(action)

			if event.type == MatchCombatEvent.TYPE_KILLED:
				if event.subject.name in self.roles:
					del self.roles[event.subject.name]

			self.last_event_index += 1

		for bot in self.game.bots_available:
			action = self.roles[bot.name].handle_event()

			if action:
				self.commandQueue.append(action)

		if DEBUG:
			self.window.tick()

	def alpha(self):
		"""
			Returns the learning rate based on the time elapsed
		"""

		return 0.15 + (1/5)*exp(-self.game.match.timePassed/75)

	def gamma(self):
		"""
			Returns discount factor
		"""

		return 0.8

	def epsilon(self):
		"""
			Returns the exploration rate based on the time elapsed
		"""

		return 0.05 + (1/8)*exp(-self.game.match.timePassed/50)

	def shutdown(self):
		"""
			Called after each match, stores the updated q-values in a file.
		"""

		for agent in self.learners:
			qvalues.latest[agent] = self.learners[agent].weights

		code = 'latest = {\n'

		for key, value in qvalues.latest.iteritems():
			code += "\t'{key}': {{\n".format(key=key)

			features = []
			for feature, f_value in value.iteritems():
				features.append("\t\t'{key}': {value}".format(key=feature, value=f_value))

			code += ',\n'.join(features)
			code += '\n\t},\n'

		code = code[0:-2] + '\n}'

		try:
			with open(qvalues.__file__.replace('.pyc', '') + datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.py', 'w') as output, \
				open(qvalues.__file__.replace('.pyc', '.py') + '.tpl', 'r') as tpl:
				output.write(tpl.read().format(qvalues=code))
		except IOError as e:
			print >>sys.stderr, "Could not save qvalues to file..."
			import traceback
			traceback.print_exc()
			print
			print >>sys.stderr, "-" * 15
			print >>sys.stderr, code
			print >>sys.stderr, "-" * 15

		if DEBUG:
			del self.window













