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
from starkai.util import flip_coin, Counter
import random

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

		self._epsilon = epsilon
		self._alpha = alpha
		self._gamma = gamma

	@property
	def epsilon(self):
		if callable(self._epsilon):
			return self._epsilon()
		else:
			return self._epsilon

	@property
	def alpha(self):
		if callable(self._alpha):
			return self._alpha()
		else:
			return self._alpha

	@property
	def gamma(self):
		if callable(self._gamma):
			return self._gamma()
		else:
			return self._gamma

	@abstractmethod
	def get_qvalue(self, state, action):
		"""
			Return the actual q-value for the given (state, action) pair
		"""
		pass

	@abstractmethod
	def update(self, state, action, next_state, reward):
		"""
			With this method you can apply rewards, which will in turn
			update the q-values.
		"""

	def get_value(self, state):
		"""
			Returns the value for the given state, which is the max of
			the max_action Q(state, action). Returns 0 if no legal actions
			are available
		"""

		legal_actions = state.get_legal_actions()
		return max([self.get_qvalue(state, action) for action in legal_actions]) if legal_actions else 0

	def get_action(self, state):
		"""
			Returns the best action available an agent can take in the given state
		"""

		actions = state.get_legal_actions()

		if not actions:
			return None

		if flip_coin(self.epsilon):
			return random.choice(actions)
		else:
			highest = max([self.get_qvalue(state, action) for action in actions])

			best_actions = [action for action in actions if self.get_qvalue(state, action) == highest]
			return random.choice(best_actions)

class ApproximateQLearner(BaseQLearner):
	"""
		Using a set of features, approximate the best available action,
		and update the q-values (the weights of each feature) as we play.
	"""

	def __init__(self, **args):
		BaseQLearner.__init__(self, **args)

		self.weights = Counter()

	def set_weights(self, weights):
		"""
			Set the weights for the given features

			:Arguments:
				* weights: A dictionary containing the weights you want to set, doesn't override the others
		"""

		for key in weights:
			self.weights[key] = weights[key]


	def get_qvalue(self, state, action):
		"""
			Returns the q-value based on the given features
		"""

		features = state.get_features(action)

		qvalue = 0
		for feature in features:
			qvalue += self.weights[feature] * features[feature]

		return qvalue

	def update(self, state, action, next_state, reward):
		"""
			When this method is called, we've received a reward for a certain action,
			and the resulting state.

			Update the q-values, and in this case the weights of each feature.
		"""

		correction = reward + self.gamma * self.get_value(next_state) - self.get_qvalue(state, action)
		features = state.get_features(action)

		for feature in features:
			self.weights[feature] += self.alpha * correction * features[feature]




