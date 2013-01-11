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
from starkai.qlearner import ApproximateQLearner, BaseState

class PositionState(BaseState):
	"""
		A state class used for Q-learning,
	"""

	def __init__(self, position, my_influence, enemy_influence, final_influence):
		"""
			Initialize the state
		"""

		self.position = position
		self.my_influence = my_influence
		self.enemy_influence = enemy_influence
		self.final_influence = final_influence

	def get_legal_actions(self):
		actions = [
			(1, 0),
			(-1, 0),
			(0, 1),
			(0, -1)
		]

		legal = []
		for action in actions:
			position = (floor(self.position[0]+action[0]), floor(self.position[1]+action[1]))

			if position not in self.my_influence.blocked:
				legal.append(action)

		return legal

	def get_features(self, action):
		position = (floor(self.position[0]+action[0]), floor(self.position[1]+action[1]))

		return {
			'my-influence': self.my_influence.get_influence(position),
			'enemy-influence': self.enemy_influence.get_influence(position),
			'final-influence': self.enemy_influence.get_influence(position)
		}

class GeneralAgent(object):
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
		self.movement_learner = ApproximateQLearner(**args)
		self.action_learner = ApproximateQLearner(**args)
		self.commander = commander

		self.current_state = PositionState((self.bot.position.x, self.bot.position.y), commander.my_influence,
			commander.enemy_influence, commander.final_influence)

	def issue_new_command(self, commander):
		"""
			Issue a new command for this bot
		"""

		if self.bot.health <= 0:
			state =
		# Find new position










