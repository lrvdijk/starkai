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

from math import floor
from starkai.qlearner import ApproximateQLearner
from starkai.states import BotState


class Northman(object):
	"""
		A general agent, can attack and defend
	"""

	def __init__(self, bot, commander, living_penalty=0.0, **args):
		"""
			Initializes the agent

			:Arguments:

			* bot_info (:class:`api.gameinfo.BotInfo`): The BotInfo object which has this role
			* commander (:class:`starkai.RobbStarkCommander`): The commander object
			* living_penalty (float): The penalty the agent receives with each tick
			* Other arguments are passed to :class:`ApproximateQLearner`
		"""

		self.bot = bot
		self.living_penalty = living_penalty
		self.qlearner = ApproximateQLearner(**args)
		self.commander = commander

		self.current_state = BotState(self.bot.position.x, self.bot.position.y)
		self.last_action = None

	def tick(self):
		"""
			Issue a new command for this bot
		"""

		new_state = BotState(self.bot.position.x, self.bot.position.y)

		if self.last_action:
			self.qlearner.update(self.current_state, self.last_action, new_state, self.)
		action = self.qlearner.get_action()

