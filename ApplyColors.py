#   Copyright (c) 2026 Justin Ahrens <justin@ahrens.net>        
#                                                                         
#   This library is free software; you can redistribute it and/or
#   modify it under the terms of the GNU Library General Public
#   License as published by the Free Software Foundation; either
#   version 2 of the License, or (at your option) any later version.
#
#   This library  is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Library General Public License for more details.
#
#   You should have received a copy of the GNU Library General Public
#   License along with this library; see the file COPYING.LIB. If not,
#   write to the Free Software Foundation, Inc., 59 Temple Place,
#   Suite 330, Boston, MA  02111-1307, USA
# 
import FreeCAD	
import FreeCADGui
import Sketcher
import Part
import json
import os
import random
try:
	from PySide import QtWidgets, QtCore, QtGui
except ImportError:
	import importlib
	QtGui = importlib.import_module("PySide2.QtGui")
	QtCore = importlib.import_module("PySide2.QtCore")
	QtWidgets = importlib.import_module("PySide2.QtWidgets")

class ApplyColors:
	"""Command to apply colors to selected objects in FreeCAD."""
	def __init__(self):
		pass
	#    obj.Proxy = self
	#    obj.addProperty("App::PropertyInteger", "Sag", "Dimensions").Sag=-1

	def GetResources(self):
		"""Return the command resources"""
		import FreeCAD
		from pathlib import Path
		return {
			'Pixmap': str(Path(FreeCAD.getUserAppDataDir()) / "Mod" / "WoodturningWorkbench" / "icons" / "ApplyColors.svg"),  # You can add an icon path here
			#'Pixmap' : '',
			'MenuText': 'Apply Colors',
			'ToolTip': 'Apply colors to selected objects in the document'
		}

	def IsActive(self):
		"""Check if the command is active"""
		return FreeCAD.ActiveDocument is not None

	def Activated(self):
		"""Execute the command"""
		import FreeCAD as App
		
		class ColorListWidget(QtWidgets.QDialog):
			def __init__(self):
				super().__init__()
				self.colors = []  # Store color entries: {"name": str, "color": QColor}
				self.init_ui()

			def _make_color_icon(self, color):
				"""Create a small color swatch icon for list items."""
				size = 25
				pixmap = QtGui.QPixmap(size, size)
				pixmap.fill(color)

				painter = QtGui.QPainter(pixmap)
				painter.setPen(QtGui.QColor(60, 60, 60))
				painter.drawRect(0, 0, size - 1, size - 1)
				painter.end()

				return QtGui.QIcon(pixmap)	

			def init_ui(self):
				import FreeCADGui
				"""Initialize the user interface."""
				self.setWindowTitle("Apply Colors Dialog")
				self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
				#self.setGeometry(100, 100, 400, 500)
				
				top_layout = QtWidgets.QVBoxLayout()
				middle_layout = QtWidgets.QHBoxLayout()
				left_layout = QtWidgets.QVBoxLayout()
				right_layout = QtWidgets.QVBoxLayout()
				right_layout.setAlignment(QtCore.Qt.AlignTop)
				# Label
				label = QtWidgets.QLabel("Colors:")
				left_layout.addWidget(label)
				
				# List widget to display colors
				self.color_list = QtWidgets.QListWidget()
				self.color_list.itemSelectionChanged.connect(self.on_selection_changed)
				self.color_list.itemDoubleClicked.connect(self.edit_color)
				left_layout.addWidget(self.color_list)

				spin_layout = QtWidgets.QHBoxLayout()
				spin_layout.addWidget(QtWidgets.QLabel("Select every x object:"))
				self.every_x_spinbox = QtWidgets.QSpinBox()
				self.every_x_spinbox.setRange(1, 100)
				self.every_x_spinbox.setSingleStep(1)
				self.every_x_spinbox.setValue(2)
				spin_layout.addWidget(self.every_x_spinbox)
				right_layout.addLayout(spin_layout)

				apply_every_x_btn = QtWidgets.QPushButton("Select Every X")
				apply_every_x_btn.clicked.connect(self.apply_every_x_input_click)
				right_layout.addWidget(apply_every_x_btn)				

				apply_color_to_all_btn = QtWidgets.QPushButton("Apply Color to All Segments")
				apply_color_to_all_btn.clicked.connect(self.apply_color_to_all_segments)
				right_layout.addWidget(apply_color_to_all_btn)

				random_colors_btn = QtWidgets.QPushButton("Random Colors")
				random_colors_btn.clicked.connect(self.bt_random_colors)
				right_layout.addWidget(random_colors_btn)

				select_ring_btn = QtWidgets.QPushButton("Select Ring")
				select_ring_btn.clicked.connect(self.select_ring_click)
				right_layout.addWidget(select_ring_btn)

				select_column_btn = QtWidgets.QPushButton("Select Column")
				select_column_btn.clicked.connect(self.select_column_click)
				right_layout.addWidget(select_column_btn)

				get_color_btn = QtWidgets.QPushButton("Get Color from Selected")
				get_color_btn.clicked.connect(self.get_color_from_selected)
				right_layout.addWidget(get_color_btn)

				right_layout.addSpacing(20)

				a_frame = QtWidgets.QFrame()
				a_frame.setFrameShape(QtWidgets.QFrame.HLine)
				a_frame.setFrameShadow(QtWidgets.QFrame.Sunken)
				right_layout.addWidget(a_frame)				



				right_bottom_layout = QtWidgets.QVBoxLayout()
				right_bottom_layout.setAlignment(QtCore.Qt.AlignBottom)

				bottom_1_layout = QtWidgets.QHBoxLayout()

				self.move_up_btn = QtWidgets.QPushButton("Move Up")
				self.move_up_btn.clicked.connect(self.move_color_up)
				self.move_up_btn.setEnabled(False)
				bottom_1_layout.addWidget(self.move_up_btn)

				self.move_down_btn = QtWidgets.QPushButton("Move Down")
				self.move_down_btn.clicked.connect(self.move_color_down)
				self.move_down_btn.setEnabled(False)
				bottom_1_layout.addWidget(self.move_down_btn)

				# Apply color button
				self.apply_btn = QtWidgets.QPushButton("Apply to Selected Object")
				self.apply_btn.clicked.connect(self.apply_color)
				self.apply_btn.setEnabled(False)
				self.apply_btn.setStyleSheet("font-weight: bold;")
				bottom_1_layout.addWidget(self.apply_btn)
			

				# Buttons layout
				bottom_2_layout = QtWidgets.QHBoxLayout()
				
				# Add color button
				self.add_btn = QtWidgets.QPushButton("Add Color")
				self.add_btn.clicked.connect(self.add_color)
				bottom_2_layout.addWidget(self.add_btn)
				
				# Remove color button
				self.remove_btn = QtWidgets.QPushButton("Remove Color")
				self.remove_btn.clicked.connect(self.remove_color)
				self.remove_btn.setEnabled(False)
				bottom_2_layout.addWidget(self.remove_btn)
				

				
				# Clear all button
				self.clear_btn = QtWidgets.QPushButton("Clear All")
				self.clear_btn.clicked.connect(self.clear_all)
				bottom_2_layout.addWidget(self.clear_btn)
				
				bottom_3_layout = QtWidgets.QHBoxLayout()
				self.load_btn = QtWidgets.QPushButton("Load Colors")
				self.load_btn.clicked.connect(self.load_colors_from_json)
				bottom_3_layout.addWidget(self.load_btn)

				# Save current list button
				self.save_btn = QtWidgets.QPushButton("Save Current List")
				self.save_btn.clicked.connect(self.save_colors_to_json)
				self.save_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
				bottom_3_layout.addWidget(self.save_btn)

				
				
				right_layout.addLayout(right_bottom_layout)
				middle_layout.addLayout(left_layout)
				middle_layout.addLayout(right_layout)
				top_layout.addLayout(middle_layout)
				top_layout.addLayout(bottom_1_layout)
				top_layout.addLayout(bottom_2_layout)
				top_layout.addLayout(bottom_3_layout)
				
				self.setLayout(top_layout)
				
				# Pre-populate with colors from JSON file
				self.populate_predefined_colors()

			def select_ring_click(self):
				"""Select all segments in the same column as the first selected object."""
				doc = FreeCAD.activeDocument()
				if not doc:
					QtWidgets.QMessageBox.warning(self, "Error", "No active document in FreeCAD.")
					return
				
				selected_objects = FreeCADGui.Selection.getSelection()
				if not selected_objects:
					QtWidgets.QMessageBox.warning(self, "Error", "Please select an object in FreeCAD first.")
					return
				
				selected_label = selected_objects[0].Label
				selected_label_prefix = selected_label[:9]
				
				# Select all objects with the same prefix
				new_selection = []
				for obj in doc.Objects:
					if obj.Label.startswith(selected_label_prefix):
						new_selection.append(obj)
				
				FreeCADGui.Selection.clearSelection()
				for obj in new_selection:
					FreeCADGui.Selection.addSelection(obj)
				doc.recompute()

			def select_column_click(self):
				"""Select all segments in the same column as the first selected object."""
				doc = FreeCAD.activeDocument()
				if not doc:
					QtWidgets.QMessageBox.warning(self, "Error", "No active document in FreeCAD.")
					return
				
				selected_objects = FreeCADGui.Selection.getSelection()
				if not selected_objects:
					QtWidgets.QMessageBox.warning(self, "Error", "Please select an object in FreeCAD first.")
					return
				
				selected_label = selected_objects[0].Label
				selected_label_postfix = selected_label[-3:]
				
				# Select all objects with the same prefix
				new_selection = []
				for obj in doc.Objects:
					if obj.Label.endswith(selected_label_postfix):
						new_selection.append(obj)
				
				FreeCADGui.Selection.clearSelection()
				for obj in new_selection:
					FreeCADGui.Selection.addSelection(obj)
				doc.recompute()
			def getVarsetInt(self, property_name):
				doc = App.activeDocument()
				varset = doc.getObject("BowlVariables")
				print("hey2")
				if varset and property_name in varset.PropertiesList:
					return getattr(varset, property_name)
				else:
					print(f"Property {property_name} not found in BowlVariables.")
					return None
			def getVarsetInt(self, property_name):
				doc = App.activeDocument()
				varset = doc.getObject("BowlVariables")
				print("hey2")
				if varset and property_name in varset.PropertiesList:
					return getattr(varset, property_name)
				else:
					print(f"Property {property_name} not found in BowlVariables.")
					return None
			def apply_color_to_all_segments(self):
				"""Apply the selected color to all segments in the bowl."""
				doc = FreeCAD.activeDocument()
				if not doc:
					QtWidgets.QMessageBox.warning(self, "Error", "No active document in FreeCAD.")
					return
				selection_set = []
				for obj in doc.Objects:
					if "Ring" in obj.Label:
						selection_set.append(obj)
				FreeCADGui.Selection.clearSelection()
				for obj in selection_set:
					FreeCADGui.Selection.addSelection(obj)
				self.apply_color()
				FreeCADGui.Selection.clearSelection()
				doc.recompute()

			def bt_random_colors(self):
				"""Assign random colors from the current list to all objects labeled Ring*."""
				doc = FreeCAD.activeDocument()
				if not doc:
					QtWidgets.QMessageBox.warning(self, "Error", "No active document in FreeCAD.")
					return

				if not self.colors:
					QtWidgets.QMessageBox.warning(self, "Error", "No colors available in the list.")
					return

				ring_objects = [obj for obj in doc.Objects if obj.Label.startswith("Ring")]
				if not ring_objects:
					QtWidgets.QMessageBox.warning(self, "Error", "No objects found with labels starting with 'Ring'.")
					return

				applied_count = 0
				for obj in ring_objects:
					if not hasattr(obj, "ViewObject"):
						continue

					selected_color = random.choice(self.colors)["color"]
					r = selected_color.red() / 255.0
					g = selected_color.green() / 255.0
					b = selected_color.blue() / 255.0
					obj.ViewObject.ShapeColor = (r, g, b, 1.0)
					applied_count += 1

				doc.recompute()
						
			def apply_every_x_input_click(self):
				"""Get color from the first selected FreeCAD object."""
				doc = FreeCAD.activeDocument()
				if not doc:
					QtWidgets.QMessageBox.warning(self, "Error", "No active document in FreeCAD.")
					return
				
				selected_objects = FreeCADGui.Selection.getSelection()
				if not selected_objects:
					QtWidgets.QMessageBox.warning(self, "Error", "Please select an object in FreeCAD first.")
					return
				new_selection = []
				for obj in selected_objects:
					selected_label = obj.Label
					selected_label_prefix = selected_label[:9]
					current_segment = int(selected_label[-3:])
					#x = int(self.apply_every_x_input.text() )
					x = self.every_x_spinbox.value()
					num_segments = self.getVarsetInt("NumSegments")
					start_segment = current_segment
					not_done = True
					reached_end = False
					while not_done:
						current_segment += x
						if current_segment > num_segments and not reached_end:
							current_segment = current_segment - num_segments
							reached_end = True
						if current_segment >= start_segment and reached_end:
							not_done = False
						#print(current_segment)
						current_segment_string = selected_label_prefix + f"{current_segment:03d}"
						new_selection.append( doc.getObjectsByLabel(current_segment_string)[0] )
				FreeCADGui.Selection.clearSelection()
				for obj in new_selection:
					FreeCADGui.Selection.addSelection(obj)
				doc.recompute()

						


			def get_color_from_selected(self):
				"""Get color from the first selected FreeCAD object."""
				doc = FreeCAD.activeDocument()
				if not doc:
					QtWidgets.QMessageBox.warning(self, "Error", "No active document in FreeCAD.")
					return
				
				selected_objects = FreeCADGui.Selection.getSelection()
				if not selected_objects:
					QtWidgets.QMessageBox.warning(self, "Error", "Please select an object in FreeCAD first.")
					return
				
				obj = selected_objects[0]
				if hasattr(obj, 'ViewObject'):
					color = obj.ViewObject.ShapeColor
					r = int(color[0] * 255)
					g = int(color[1] * 255)
					b = int(color[2] * 255)
					self.on_color_selected((r, g, b))

				else:
					QtWidgets.QMessageBox.warning(self, "Error", "Selected object has no view properties.")
			def add_color(self):
					"""Open color dialog and add selected color to list."""
					color = QtWidgets.QColorDialog.getColor()
					if color.isValid():
						color_name, ok = QtWidgets.QInputDialog.getText(
							self,
							"Color Name",
							"Enter a name for this color:",
							text=color.name()
						)
						if not ok:
							return
						color_name = color_name.strip() or color.name()
						self.colors.append({"name": color_name, "color": color})
						item = QtWidgets.QListWidgetItem()
						item.setText(color_name)
						item.setIcon(self._make_color_icon(color))
						self.color_list.addItem(item)

			def edit_color(self, item):
				"""Edit the color and name of the selected list item."""
				current_row = self.color_list.row(item)
				if current_row < 0:
					return

				current_entry = self.colors[current_row]
				current_color = current_entry["color"]

				color = QtWidgets.QColorDialog.getColor(current_color, self)
				if not color.isValid():
					return

				color_name, ok = QtWidgets.QInputDialog.getText(
					self,
					"Color Name",
					"Enter a name for this color:",
					text=current_entry["name"]
				)
				if not ok:
					return
				color_name = color_name.strip() or current_entry["name"]

				self.colors[current_row] = {"name": color_name, "color": color}
				item.setText(color_name)
				item.setIcon(self._make_color_icon(color))
					
			def remove_color(self):
				"""Remove selected color from list."""
				current_row = self.color_list.currentRow()
				if current_row >= 0:
					self.color_list.takeItem(current_row)
					self.colors.pop(current_row)
					
			def clear_all(self):
				"""Clear all colors from the list."""
				reply = QtWidgets.QMessageBox.question(
					self, 
					"Confirm", 
					"Clear all colors?",
					QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
				)
				if reply == QtWidgets.QMessageBox.Yes:
					self.color_list.clear()
					self.colors.clear()
					
			def on_selection_changed(self):
				"""Enable/disable buttons based on selection."""
				current_row = self.color_list.currentRow()
				has_selection = current_row >= 0
				self.remove_btn.setEnabled(has_selection)
				self.apply_btn.setEnabled(has_selection)
				self.move_up_btn.setEnabled(has_selection and current_row > 0)
				self.move_down_btn.setEnabled(
					has_selection and current_row < (self.color_list.count() - 1)
				)

			def _swap_rows(self, row_a, row_b):
				if row_a == row_b:
					return
				if row_a < 0 or row_b < 0:
					return
				if row_a >= self.color_list.count() or row_b >= self.color_list.count():
					return

				self.colors[row_a], self.colors[row_b] = self.colors[row_b], self.colors[row_a]

				item_a = self.color_list.takeItem(row_a)
				item_b = self.color_list.takeItem(row_b - 1 if row_b > row_a else row_b)

				if row_b > row_a:
					self.color_list.insertItem(row_a, item_b)
					self.color_list.insertItem(row_b, item_a)
					self.color_list.setCurrentRow(row_b)
				else:
					self.color_list.insertItem(row_b, item_a)
					self.color_list.insertItem(row_a, item_b)
					self.color_list.setCurrentRow(row_b)

			def move_color_up(self):
				"""Move the selected color up by one row."""
				current_row = self.color_list.currentRow()
				if current_row <= 0:
					return
				self._swap_rows(current_row, current_row - 1)

			def move_color_down(self):
				"""Move the selected color down by one row."""
				current_row = self.color_list.currentRow()
				if current_row < 0 or current_row >= self.color_list.count() - 1:
					return
				self._swap_rows(current_row, current_row + 1)
				
			def populate_predefined_colors(self):
				"""Pre-populate the color list from a JSON file."""
				# Get the directory of this macro
				import json
				import os
				macro_dir = os.path.dirname(os.path.abspath(__file__))
				colors_file = os.path.join(macro_dir, "ColorListWidget_colors.json")
				
				try:
					with open(colors_file, 'r') as f:
						data = json.load(f)
						colors_data = data.get("colors", [])
				except (FileNotFoundError, json.JSONDecodeError):
					# Fallback to default colors if file not found
					colors_data = [
						{"name": "Walnut Brown", "hex": "#773F1A"},
						{"name": "Saddle Brown", "hex": "#8B4513"},
						{"name": "Sienna", "hex": "#A0522D"},
						{"name": "Wheat", "hex": "#F5DEB3"},
						{"name": "Tan", "hex": "#D4A574"},
						{"name": "Burlywood", "hex": "#DEB887"},
					]
				
				# Add colors to the list
				for color_data in colors_data:
					color_name = color_data.get("name", "Unnamed Color")
					hex_color = color_data.get("hex", "#000000")
					color = QtGui.QColor(hex_color)

					self.colors.append({"name": color_name, "color": color})
					item = QtWidgets.QListWidgetItem()
					item.setText(color_name)
					item.setIcon(self._make_color_icon(color))
					self.color_list.addItem(item)
				
			def save_colors_to_json(self):
				"""Prompt for a filename and save the current list of colors to JSON."""
				macro_dir = os.path.dirname(os.path.abspath(__file__))
				default_file = os.path.join(macro_dir, "ColorListWidget_colors.json")
				colors_file, _ = QtWidgets.QFileDialog.getSaveFileName(
					self,
					"Save Colors",
					default_file,
					"JSON Files (*.json);;All Files (*)"
				)

				if not colors_file:
					return

				if not colors_file.lower().endswith(".json"):
					colors_file += ".json"
				
				# Build the colors data
				colors_data = []
				for color_entry in self.colors:
					colors_data.append({
						"name": color_entry["name"],
						"hex": color_entry["color"].name()
					})
				
				# Write to JSON file (as a plain list of colors)
				try:
					with open(colors_file, 'w') as f:
						json.dump(colors_data, f, indent=2)
				except Exception as e:
					QtWidgets.QMessageBox.critical(
						self,
						"Error",
						f"Failed to save colors: {str(e)}"
					)

			def load_colors_from_json(self):
				"""Prompt for a JSON file and load a list of colors into the dialog."""
				macro_dir = os.path.dirname(os.path.abspath(__file__))
				colors_file, _ = QtWidgets.QFileDialog.getOpenFileName(
					self,
					"Load Colors",
					macro_dir,
					"JSON Files (*.json);;All Files (*)"
				)

				if not colors_file:
					return

				try:
					with open(colors_file, 'r') as f:
						data = json.load(f)

					# Support both plain list format and {"colors": [...]} format.
					if isinstance(data, list):
						colors_data = data
					elif isinstance(data, dict):
						colors_data = data.get("colors", [])
					else:
						raise ValueError("Invalid JSON format. Expected a list of color entries.")

					new_colors = []
					for color_data in colors_data:
						if not isinstance(color_data, dict):
							continue
						color_name = color_data.get("name", "Unnamed Color")
						hex_color = color_data.get("hex", "#000000")
						color = QtGui.QColor(hex_color)
						if not color.isValid():
							continue
						new_colors.append({"name": color_name, "color": color})

					self.color_list.clear()
					self.colors.clear()
					for color_entry in new_colors:
						self.colors.append(color_entry)
						item = QtWidgets.QListWidgetItem()
						item.setText(color_entry["name"])
						item.setIcon(self._make_color_icon(color_entry["color"]))
						self.color_list.addItem(item)

					QtWidgets.QMessageBox.information(
						self,
						"Success",
						f"Loaded {len(self.colors)} colors from {colors_file}."
					)
				except Exception as e:
					QtWidgets.QMessageBox.critical(
						self,
						"Error",
						f"Failed to load colors: {str(e)}"
					)
				
			def apply_color(self):
				"""Apply selected color to the currently selected FreeCAD object."""
				current_row = self.color_list.currentRow()
				if current_row < 0:
					QtWidgets.QMessageBox.warning(self, "Error", "No color selected.")
					return
					
				# Get selected color
				selected_color_entry = self.colors[current_row]
				selected_color = selected_color_entry["color"]
				selected_color_name = selected_color_entry["name"]
				
				# Get selected objects in FreeCAD
				selected_objects = FreeCAD.Gui.Selection.getSelection()
				if not selected_objects:
					QtWidgets.QMessageBox.warning(
						self, 
						"Error", 
						"No object selected in FreeCAD.\nPlease select an object first."
					)
					return
				
				# Apply color to each selected object
				for obj in selected_objects:
					try:
						# Convert QColor to RGB tuple (normalized to 0-1)
						r = selected_color.red() / 255.0
						g = selected_color.green() / 255.0
						b = selected_color.blue() / 255.0
						
						# Set the color properties
						if hasattr(obj, "ViewObject"):
							obj.ViewObject.ShapeColor = (r, g, b, 1.0)
							
						#QtWidgets.QMessageBox.information(
						#	self,
						#	"Success",
						#	f"Applied color {selected_color_name} to {obj.Label}."
						#)
					except Exception as e:
						QtWidgets.QMessageBox.critical(
							self,
							"Error",
							f"Failed to apply color: {str(e)}"
						)

		dialog = ColorListWidget()
		# Make it modeless so you can interact with FreeCAD while the dialog is open
		dialog.setWindowModality(QtCore.Qt.NonModal)
		dialog.show()
		screen = QtWidgets.QApplication.primaryScreen()
		if screen is not None:
			dialog.move(screen.availableGeometry().topLeft())
		else:
			dialog.move(0, 0)
		# Store reference to prevent garbage collection
		#FreeCAD.Gui.MainWindow.color_list_dialog = dialog
		FreeCAD.Gui.getMainWindow().color_list_dialog = dialog