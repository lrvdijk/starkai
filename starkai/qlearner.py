"""
:mod:`starkai.qlearner` - Q-value reinforcement learner implementation
=======================================================================

This module contains helper classes to use reinforcement learning. It
uses a method based on Q-values.

.. module:: starkai.qlearner
   :synopsis: Q-value learner class

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from abc import abstractmethod, ABCMeta

class BaseQLearner(object):
	"""
		Base class for a q-learner agent
	"""

	__metaclass__ = ABCMeta

	def __init__(self, epsilon=0.05, alpha=0.2, gamma=0.8):
		"""
			Initializes the Q-learner, with the following parameters:

			* epsilon: Exploration rate
			* alpha: learning factor
			* gamma: discount factor
		"""

		self.epsilon = epsilon
		self.alpha = alpha
		self.gamma = gamma

	@abstractmethod
	def get_qvalue(self, state, action):
		"""
			Return the actual q-value for the given (state, action) pair
		"""




