"""
:mod:`starkai.commanders` - AI Commander classes
================================================

The classes in this module control all the bots in a certain game

.. module:: starkai.commanders
   :synopsis: AI Commander classes
  
.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from api import Commander
from api import commands
from api import Vector2
from math import floor

from starkai.influencemap import GridInfluenceMap

class RobbStarkCommander(Commander):
	"""
		Our main commander, uses influence maps to make decisions.
	"""
	
	def initialize(self):
		self.verbose = True
		
		# Setup some influence maps
		self.my_influence = GridInfluenceMap(width=self.level.width, height=self.level.height)
		self.enemy_influence = GridInfluenceMap(width=self.level.width, height=self.level.height)
		self.goal_influence = GridInfluenceMap(width=self.level.width, height=self.level.height)
		
		for bot in self.bots_alive:
			self.my_influence.set_influence((floor(bot.position.x), floor(bot.position.y)), 1.0)
		
		
	
	def tick(self):
		"""
			Time to issue new commands!
		"""
		
		
	
