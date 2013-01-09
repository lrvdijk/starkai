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
from abc import ABCMeta, abstractmethod
from starkai.qlearner import ApproximateQLearner, BaseState

class CTFState(BaseState):
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
		A general agent, tries to balance between attacking and defending
	"""

	def __init__(self, living_penalty=0.0, **args):
		"""
			Initializes the agent

			:Arguments:

			* living_penalty (float): The penalty the agent receives with each tick
			* Other arguments are passed to :class:`ApproximateQLearner`
		"""

		self.living_penalty = living_penalty

	def tick(self, commander):
		"""
			Perform commands
		"""



