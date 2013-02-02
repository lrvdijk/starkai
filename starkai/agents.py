"""
:mod:`starkai.agents` - Specific roles for the agents under command
===================================================================

This module contains classes which define roles for each agent
under command. For example a flag defender, a flag finder, and other
attackers.

.. module:: starkai.agents
   :synopsis: Specific roles for agents

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from starkai.qfeatures import FlagSearcherFeatureProvider, FlagReturnerFeatureProvider
from starkai.states import BotState
from starkai.util import euclidean_dist, find_closest
from api.gameinfo import MatchCombatEvent
from api.commands import Move, Attack, Charge
from api.vector2 import Vector2

available = ['Northman', 'FlagReturner']

class Northman(object):
	"""
		A general agent, can attack and defend
	"""

	qlearner = None
	feature_class = FlagSearcherFeatureProvider

	def __init__(self, bot, commander, living_penalty=0.0):
		"""
			Initializes the agent

			:Arguments:

			* bot_info (:class:`api.gameinfo.BotInfo`): The BotInfo object which has this role
			* commander (:class:`starkai.RobbStarkCommander`): The commander object
			* living_penalty (float): The penalty the agent receives with each tick
		"""

		if not self.qlearner:
			raise Exception("Q-learner not initialized")

		self.bot = bot
		self.living_penalty = living_penalty
		self.commander = commander

		self.last_state = BotState(self.bot.position.x, self.bot.position.y)
		self.last_action = None

		# Find distance to flag
		self.flag_distance = find_closest([(flag.position.x, flag.position.y) for flag in self.commander.game.enemyFlags], self.last_state)

	@classmethod
	def set_qlearner(cls, qlearner):
		cls.qlearner = qlearner

	def handle_event(self, event=None):
		"""
			Called when an event occurs for this agent, like death, killed an enemy
			or captured the flag.

			If this function returns a new command object (from the CTF API),
			this command is executed. When it returns None, nothing is done.
		"""

		state = BotState(self.bot.position.x, self.bot.position.y)
		reward = self.calculate_reward(state, event)

		if state != self.last_state and self.last_action and reward:
			self.qlearner.update(self.last_state, self.last_action, state, reward)
			self.last_state = state

		if not event or not (event.type == MatchCombatEvent.TYPE_KILLED and event.subject == self.bot):
			# Issue a new command
			action = self.qlearner.get_action(state)
			self.last_action = action

			if self.commander.enemy_influence.get_influence(state) < 0.1:
				return Move(self.bot.name, Vector2(state[0] + action[0]+0.5, state[1] + action[1]+0.5), "running")
			else:
				return Attack(self.bot.name, Vector2(state[0] + action[0]+0.5, state[1] + action[1]+0.5), lookAt=None, description="attacking")

		return None

	def calculate_reward(self, state, event=None):
		"""
			This function calculates the reward based on the new state,
			and the type of event.

			This is a separate function for easy overriding.
		"""

		if not event:
			# Return reward based on the distance of the flag
			min_flag_dist = find_closest([(flag.position.x, flag.position.y) for flag in self.commander.game.enemyFlags], state)
			difference = self.flag_distance - min_flag_dist

			self.flag_distance = min_flag_dist
			return difference
		elif event.type == MatchCombatEvent.TYPE_KILLED:
			if event.subject == self.bot:
				# This bot has been killed
				return -100
			elif event.instigator == self.bot:
				return 25
		elif event.instigator == self.bot:
			if event.type == MatchCombatEvent.TYPE_FLAG_CAPTURED:
				return 100
			elif event.type == MatchCombatEvent.TYPE_FLAG_PICKEDUP:
				return 100
			elif event.type == MatchCombatEvent.TYPE_FLAG_DROPPED:
				return -50

		return 0

class FlagReturner(Northman):
	"""
		Agent which returns the flag
	"""

	feature_class = FlagReturnerFeatureProvider

	def __init__(self, commander, living_penalty=0.0):
		Northman.__init__(self, commander, living_penalty)

		# Distance to score location
		score_loc = self.commander.game.team.flagScoreLocation
		self.score_dist = euclidean_dist((score_loc.x, score_loc.y), self.last_state)

	def calculate_reward(self, state, event=None):
		"""
			This function calculates the reward based on the new state,
			and the type of event.

			This is a separate function for easy overriding.
		"""

		if not event:
			# Return reward based on the distance of the flag score location
			score_loc = self.commander.game.team.flagScoreLocation
			distance = euclidean_dist((score_loc.x, score_loc.y), state)
			difference = self.score_dist - distance

			self.score_dist = distance

			return difference
		elif event.type == MatchCombatEvent.TYPE_KILLED:
			if event.subject == self.bot:
				# This bot has been killed
				return -100
			elif event.instigator == self.bot:
				return 25
		elif event.instigator == self.bot:
			if event.type == MatchCombatEvent.TYPE_FLAG_RESTORED:
				return 100
			elif event.type == MatchCombatEvent.TYPE_FLAG_PICKEDUP:
				return 100
			elif event.type == MatchCombatEvent.TYPE_FLAG_DROPPED:
				return -100

		return 0




