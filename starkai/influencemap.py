"""
:mod:`starkai.influencemap` - Module with an influencemap implementation
=======================================================================

This module contains a class for creating and modifying influence maps.

.. module:: starkai.influencemap
   :synopsis: Infuence map implementations
  
.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from starkai.util import Counter, lerp
from abc import ABCMeta, abstractmethod
import math

class BaseInfluenceMap(object):
	"""
		Class which represents an influence map
	"""
	
	__metaclass__ = ABCMeta
	
	def __init__(self, decay=0.2, momentum=0.5):
		self.decay = decay
		self.momentum = momentum
		
		self.influence = Counter()

	
	def set_influence(self, position, influence):
		self.influence[position] = influence
	
	def get_influence(self, position):
		return self.influence[position] if position in self.influence else 0.0
		
	@abstractmethod
	def get_neighbours(self, position):
		"""
			This method should return its neighbours for a given point. 
			
			The return value should be a list of tuples in the form of:
			    (position, distance)
		"""
	
	def update_map(self, num_times=1):
		"""
			Performs a new iteration over the influence maps, and calculates
			the new values for each point
		"""
		
		new_influence = {}

		i = 0
		while i < num_times:
			for position in self.influence:
				max_infl = 0.0

				for neighbour, distance in self.get_neighbours(position):
					influence = self.get_influence(neighbour) * math.exp(-distance * self.decay)

					max_infl = max(influence, max_infl)

				new_influence[position] = lerp(self.get_influence(position), max_infl, self.momentum)

			i += 1
		
		del self.influence
		self.influence = new_influence
	
	def __add__(self, other):
		"""
			Adds two influence maps to each other, and returns an union
			of keys of both maps
			
			The new map has default values for decay and momentum
		"""
		
		new_map = self.__class__()
		
		for key in self.influence:
			new_map.influence[key] = self.influence[key] + other.get_influence(key)
		
		for key in other.influence:
			if not key in self.influence:
				new_map.influence[key] = other.influence[key]
		
		return new_map
		
	def __sub__(self, other):
		"""
			Adds two influence maps to each other, and returns an union
			of keys of both maps
			
			The new map has default values for decay and momentum
		"""
		
		new_map = self.__class__()
		
		for key in self.influence:
			new_map.influence[key] = self.influence[key] - other.get_influence(key)
		
		for key in other.influence:
			if not key in self.influence:
				new_map.influence[key] = other.influence[key]
		
		return new_map
	
	def __mul__(self, scalar):
		"""
			Multiplies each element with the given scalar
		"""
		
		new_map = self.__class__()
		
		for key in self.influence:
			new_map.influence[key] = self.influence[key] * scalar
		
		
		return new_map

	def __getitem__(self, item):
		return self.get_influence(item)
		
class GridInfluenceMap(BaseInfluenceMap):
	"""
		Influence map for grid based worlds
	"""
	
	def __init__(self, decay=0.2, momentum=0.5, width=0, height=0, is_blocked=lambda x, y: False):
		BaseInfluenceMap.__init__(self, decay, momentum)
		
		self.width = width
		self.height = height
		
		self.is_blocked = is_blocked

		# Initialize counter object with all known positions
		queue = [(0,0)]
		checked = set()
		while queue:
			position = queue.pop()
			self.set_influence(position, 0.0)
			checked.add(position)

			queue.extend([neighbour[0] for neighbour in self.get_neighbours(position) if not neighbour[0] in checked])
	
	def get_neighbours(self, position):
		neighbours = []
		
		actions = [
			(1, 0),
			(-1, 0),
			(0, 1),
			(0, -1)
		]
		
		for action in actions:
			new_pos = (position[0] + action[0], position[1] + action[1])
			
			if self.is_blocked(new_pos):
				continue
			
			if new_pos[0] < 0 or new_pos[0] >= self.width:
				continue
			
			if new_pos[1] < 0 or new_pos[1] >= self.height:
				continue
			
			neighbours.append((new_pos, 1))
		
		return neighbours

	def __add__(self, other):
		new_map = BaseInfluenceMap.__add__(self, other)
		new_map.is_blocked = self.is_blocked

		return new_map

	def __sub__(self, other):
		new_map = BaseInfluenceMap.__sub__(self, other)
		new_map.is_blocked = self.is_blocked

		return new_map

	def __mul__(self, other):
		new_map = BaseInfluenceMap.__mul__(self, other)
		new_map.is_blocked = self.is_blocked

		return new_map
