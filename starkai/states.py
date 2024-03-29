"""
:mod:`starkai.manager` - Game manager logic
================================================

The classes in this module manages the propagation of
game info to each bot.

.. module:: starkai.manager
   :synopsis: Game manager classes

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from math import floor

# Define some actions a bot can take
MOVE_N = (0, 1)
MOVE_S = (0, -1)
MOVE_E = (1, 0)
MOVE_W = (-1, 0)
MOVE_NE = (1, 1)
MOVE_NW = (-1, 1)
MOVE_SE = (1, -1)
MOVE_SW = (-1, -1)

ACTIONS = (
	MOVE_N,
	MOVE_S,
	MOVE_E,
	MOVE_W,
	MOVE_NE,
	MOVE_NW,
	MOVE_SE,
	MOVE_SW
)

class GameState(object):
	"""
		Overall game state
	"""

	def __init__(self, commander):
		self.commander = commander

		self.blocked = []

		for x, ylist in enumerate(self.commander.level.blockHeights):
			for y, value in enumerate(ylist):
				if value > 0:
					self.blocked.append((x, y))

	def is_blocked(self, *args):
		if len(args) == 1:
			return args[0] in self.blocked
		else:
			return (args[0], args[1]) in self.blocked

	def get_legal_actions(self, bot_state):
		actions = []

		for action in ACTIONS:
			new_pos = (floor(bot_state[0] + action[0]), floor(bot_state[1] + action[1]))

			if new_pos[0] < 0 or new_pos[1] < 0:
				continue

			if new_pos[0] >= self.commander.level.width or new_pos[1] >= self.commander.level.height:
				continue

			occupied = False
			for bot in self.commander.game.team.members:
				if bot.health > 0:
					if (floor(bot.position.x), floor(bot.position.y)) == new_pos:
						occupied = True
						break

			if not self.is_blocked(new_pos) and not occupied:
				actions.append(action)

		return actions

class BotState(object):
	"""
		A state class for bots used for Q-learning, Only contains
		the position.
	"""

	def __init__(self, x, y):
		"""
			Initialize the state
		"""

		self.position = (floor(x), floor(y))

	def __eq__(self, other):
		return self.position == other.position

	def __getitem__(self, item):
		return self.position[item]