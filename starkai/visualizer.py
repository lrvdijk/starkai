"""
:mod:`starkai.commanders` - AI Commander classes
================================================

The classes in this module control all the bots in a certain game

.. module:: starkai.commanders
   :synopsis: AI Commander classes

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from __future__ import division
import math
from os.path import dirname, join
from gi.repository import Gtk

class VisualizerWindow(object):
	"""
		This class helps visualizing different data of the commander
	"""

	def __init__(self, commander):
		self.commander = commander
		self.builder = Gtk.Builder()
		self.builder.add_from_file(join(dirname(__file__), 'data', 'visualizer.glade'))

		self.scale_x = self.scale_y = 10

		window = self.builder.get_object('mainWindow')
		window.show_all()

		# Setup drawing area
		self.drawing_area = self.builder.get_object('drawingGrid')
		self.drawing_area.set_size_request(commander.level.width*self.scale_x, commander.level.height*self.scale_y)

		# Setup agents combobox
		agent_combo = self.builder.get_object('comboAgent')
		for agent in self.commander.learners:
			agent_combo.append_text(agent)

		# Setup map combobox
		self.maps = {
			'My Influence': 'my_influence',
			'Enemy Influence': 'enemy_influence',
			'Goal Influence': 'goal_influence',
			'Visibility': 'visibility'
		}

		map_combo = self.builder.get_object('comboMap')
		for map in self.maps:
			map_combo.append_text(map)

		# Setup TreeView
		tree = self.builder.get_object('treeQvalues')
		feature_renderer = Gtk.CellRendererText()
		feature_column = Gtk.TreeViewColumn("Feature", feature_renderer, text=0)

		value_renderer = Gtk.CellRendererText()
		value_column = Gtk.TreeViewColumn("Value", value_renderer, text=1)

		tree.append_column(feature_column)
		tree.append_column(value_column)

		self.builder.connect_signals(self)
		self.active_map = None

	def fill_tree(self, agent):
		tree = self.builder.get_object('treeQvalues')
		store = Gtk.ListStore(str, float)

		for key, value in self.commander.learners[agent].weights.iteritems():
			store.append([key, float(value)])

		tree.set_model(store)

	def tick(self):
		while Gtk.events_pending():
			Gtk.main_iteration()

		self.builder.get_object('drawingGrid').queue_draw()

	def on_agent_changed(self, combo):
		agent = combo.get_active_text()

		self.fill_tree(agent)

	def on_map_changed(self, combo):
		map = combo.get_active_text()
		attr = getattr(self.commander, self.maps[map], None)

		if attr:
			self.active_map = attr

	def on_draw(self, widget, ctx):
		"""
			Called when we should redraw the drawing area
		"""

		width = widget.get_allocation().width
		height = widget.get_allocation().height

		self.scale_x = width / self.commander.level.width
		self.scale_y = height / self.commander.level.height

		# Draw blocks
		for x in range(self.commander.level.width):
			for y in range(self.commander.level.height):
				if self.commander.level.blockHeights[x][y] > 2:
					self.draw_pixel(ctx, x, y, (0, 0, 0))
				elif self.commander.level.blockHeights[x][y] > 1:
					self.draw_pixel(ctx, x, y, (0.1, 0.1, 0.1))

		# Draw bots
		for name, bot in self.commander.game.bots.items():
			if not bot.position:
				continue

			if 'Red' in name:
				if bot.seenlast > 0.0:
					color = (0.8, 0.0, 0.0)
				else:
					color = (1.0, 0.0, 0.0)
			else:
				if bot.seenlast > 0.0:
					color = (0.0, 0.0, 0.8)
				else:
					color = (0.0, 0.0, 1.0)

			if bot.health <= 0.0:
				color = (0, 0, 0)

			self.draw_circle(ctx, bot.position.x, bot.position.y, min(self.scale_x, self.scale_y)/2, color)
			self.draw_line(ctx, bot.position.x, bot.position.y, bot.facingDirection, min(self.scale_x, self.scale_y), color)

		if self.active_map:
			for x in range(self.commander.level.width):
				for y in range(self.commander.level.height):
					value = self.active_map[(x,y)]

					alpha = math.fabs(value)

					if value > 0:
						color = (1.0, 102/255, 51/255, alpha)
					else:
						color = (51/255, 102/255, 1.0, alpha)

					self.draw_pixel(ctx, x, y, color)

	def draw_pixel(self, ctx, x, y, color):
		"""
			Draws a pixel on the grid, scaled to match the window size
		"""

		x = x * self.scale_x
		y = y * self.scale_y

		ctx.set_source_rgba(*color)
		ctx.rectangle(x, y, self.scale_x, self.scale_y)
		ctx.fill()

	def draw_circle(self, ctx, x, y, radius, color):
		x = x * self.scale_x
		y = y * self.scale_y

		ctx.set_source_rgba(*color)
		ctx.arc(x, y, radius, 0, 2 * math.pi)
		ctx.fill()

	def draw_line(self, ctx, x, y, direction, length, color):
		x = x * self.scale_x
		y = y * self.scale_y

		ctx.set_source_rgba(*color)
		ctx.move_to(x, y)
		ctx.line_to(x + (direction.x*length), y + (direction.y*length))
		ctx.stroke()





