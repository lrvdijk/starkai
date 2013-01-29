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

from starkai.states import BotState
from api.gameinfo import MatchCombatEvent
from api.commands import Move, Attack, Charge
from api.vector2 import Vector2

available = ['Northman']

class Northman(object):
	"""
		A general agent, can attack and defend
	"""

	qlearner = None

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

		self.current_state = BotState(self.bot.position.x, self.bot.position.y)
		self.last_action = None

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

		new_state = BotState(self.bot.position.x, self.bot.position.y)
		reward = self.calculate_reward(event)

		if self.last_action and reward:
			self.qlearner.update(self.current_state, self.last_action, new_state, reward)

		if not (event.type == MatchCombatEvent.TYPE_KILLED and event.subject == self.bot):
			# Issue a new command
			action = self.qlearner.get_action(new_state)

			if self.commander.enemy_influence < 0.1:
				return Move(self.bot, Vector2(action[0]+0.5, action[1]+0.5), "running")
			else:
				return Attack(self.bot, Vector2(action[0]+0.5, action[1]+0.5), "attacking")

		return None

	def calculate_reward(self, event=None):
		"""
			This function calculates the reward based on the new state,
			and the type of event.

			This is a separate function for easy overriding.
		"""

		if not event:
			# Bot reached destination, give it its living penalty
			return self.living_penalty
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



