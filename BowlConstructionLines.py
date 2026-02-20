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
from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
try:
	from PySide import QtGui, QtCore, QtWidgets
except ImportError:
	import importlib
	QtGui = importlib.import_module("PySide2.QtGui")
	QtCore = importlib.import_module("PySide2.QtCore")
	QtWidgets = importlib.import_module("PySide2.QtWidgets")
from FreeCAD import Vector
import Part
import Sketcher


class BowlConstructionLines:
	def GetResources(self):
		"""Return the command resources"""
		from pathlib import Path
		import FreeCAD
		#image = str(Path(FreeCAD.getUserAppDataDir()) / "Mod" / "WoodturningWorkbench" / "icons" / "BowlConstructionLines.svg")
		return {
			'Pixmap': str(Path(FreeCAD.getUserAppDataDir()) / "Mod" / "WoodturningWorkbench" / "icons" / "BowlConstructionLines.svg"),
			'MenuText': 'Add Profile Points',
			'ToolTip': 'Add profile points'
		}

	def IsActive(self):
		"""Check if the command is active"""
		return App.ActiveDocument is not None

	def Activated(self):
		"""Execute the command"""
		class AddBowlConstructionLines:

			from FreeCAD import Vector

			#Creates the Dialog Box
			def __init__(self):
				#Local Variables with Default Values
				from varsetOps import setVarsetValue, getVarsetValue, getVarsetInt
				doc = App.activeDocument()
				self.bowl_height = 254.0  # Bowl height in mm
				self.bowl_radius = 127.0  # Bowl radius in mm
				self.layer_height = 25.4 # Layer height in mm
				self.construction_lines = True
				if not doc.getObject("BowlVariables"):
					self.varset = doc.addObject("App::VarSet", "BowlVariables")
					# Add a variable (property) to the VarSet
					# Syntax: addProperty(type, name, group, tooltip)
					self.varset.addProperty("App::PropertyInteger", "NumSegments", "General", "Number of segments for the bowl")
					self.varset.NumSegments = 12
					self.varset.addProperty("App::PropertyLength", "BowlHeight", "General", "Height of the bowl")
					self.varset.BowlHeight = self.bowl_height
					self.varset.addProperty("App::PropertyLength", "BowlWidth", "General", "Width of the bowl")
					self.varset.BowlWidth = 100.0
					self.varset.addProperty("App::PropertyLength", "LayerHeight", "General", "Height of each layer")
					self.varset.LayerHeight = self.layer_height
					self.varset.addProperty("App::PropertyAngle", "RotateAngle", "General", "Rotation angle for rings")
					self.varset.RotateAngle = 15.0
					self.varset.addProperty("App::PropertyLength", "WallThickness", "General", "Wall thickness of the bowl")
					self.varset.WallThickness = 10.0
				else:
					self.bowl_height = getVarsetValue(self,"BowlHeight")
					self.layer_height = getVarsetValue(self,"LayerHeight")
					self.bowl_radius = round(getVarsetValue(self,"BowlWidth") / 2)
					self.num_segments = getVarsetInt(self,"NumSegments")
					self.rotate_angle = getVarsetValue(self,"RotateAngle")
					self.wall_thickness = getVarsetValue(self,"WallThickness")


				self.form = QtWidgets.QWidget()
				self.form.setWindowTitle("Make Sketch with Profile Points")

				self.list_of_points = []
				self.list_of_lines = []

				layout = QtWidgets.QVBoxLayout()

				layout1 = QtGui.QHBoxLayout()
				layout1.addWidget(QtGui.QLabel("Bowl Height(mm):"))	
				self.bowl_heightBox = QtGui.QLineEdit(str(self.bowl_height))
				layout1.addWidget(self.bowl_heightBox)
				layout1.addWidget(QtGui.QLabel("Bowl Radius(mm):"))
				self.bowl_radiusBox = QtGui.QLineEdit(str(self.bowl_radius))
				layout1.addWidget(self.bowl_radiusBox)
				layout.addLayout(layout1)

				layout2 = QtGui.QHBoxLayout()
				layout2.addWidget(QtGui.QLabel("Bowl Height(in):"))	
				self.bowl_heightBox_in = QtGui.QLineEdit(str(self.bowl_height / 25.4))
				self.bowl_heightBox_in.setReadOnly(True)
				layout2.addWidget(self.bowl_heightBox_in)
				layout2.addWidget(QtGui.QLabel("Bowl Radius(in):"))
				self.bowl_radiusBox_in = QtGui.QLineEdit(str((self.bowl_radius) / 25.4))
				self.bowl_radiusBox_in.setReadOnly(True)
				layout2.addWidget(self.bowl_radiusBox_in)
				layout.addLayout(layout2)				

				layout3 = QtGui.QHBoxLayout()
				layout3.addWidget(QtGui.QLabel("Layer Height(mm):"))
				self.layer_heightBox = QtGui.QLineEdit(str(self.layer_height))
				self.layer_heightBox.editingFinished.connect(lambda: self.update_text_boxes('layer_height'))
				layout3.addWidget(self.layer_heightBox)

				layout3.addWidget(QtGui.QLabel("Number of Layers:"))
				self.num_layersBox = QtGui.QLineEdit(str(int(self.bowl_height / self.layer_height)))
				self.num_layersBox.editingFinished.connect(lambda: self.update_text_boxes('num_layers'))
				layout3.addWidget(self.num_layersBox)
				layout.addLayout(layout3)

				layout4 = QtGui.QHBoxLayout()
				layout4.addWidget(QtGui.QLabel("Layer Height(in):"))
				self.layer_heightBox_in = QtGui.QLineEdit(str(self.layer_height / 25.4))
				self.layer_heightBox_in.setReadOnly(True)
				layout4.addWidget(self.layer_heightBox_in)
				layout.addLayout(layout4)
				
				self.construction_lines_radio = QtGui.QRadioButton("Add Construction lines")
				layout.addWidget(self.construction_lines_radio)
				self.construction_lines_radio.setChecked(True)

				#Buttons
				self.bt_generate_lines = QtGui.QPushButton("Add Points(Lines)")
				self.bt_delete_lines = QtGui.QPushButton("Delete Points(Lines)")
				self.bt_generate_lines.clicked.connect(self.bt_generate_lines_click)
				self.bt_delete_lines.clicked.connect(self.bt_delete_lines_click)

				button_layout = QtGui.QHBoxLayout()
				button_layout.addWidget(self.bt_generate_lines)
				button_layout.addWidget(self.bt_delete_lines)
				layout.addLayout(button_layout)
				self.cancel_button = QtWidgets.QPushButton("Close")
				self.cancel_button.clicked.connect(self.on_cancel)
				layout.addWidget(self.cancel_button)

				self.form.setLayout(layout)
				#self.setLayout(layout)
				#self.set_tooltips()

			def set_tooltips(self):
				self.bowl_heightBox.setToolTip("Height of the bowl in mm")
				self.bowl_radiusBox.setToolTip("Radius of the bowl in mm")
				self.layer_heightBox.setToolTip("Height of each layer in mm")
				self.bt_generate_lines.setToolTip("Generate construction lines for each layer of the bowl")
				self.bt_delete_lines.setToolTip("Delete all construction lines created by this macro")
			def getVarsetValue(self, property_name):
				doc = App.activeDocument()
				varset = doc.getObject("BowlVariables")
				if varset and property_name in varset.PropertiesList:
					return getattr(varset, property_name).Value
				else:
					print(f"Property {property_name} not found in BowlVariables.")
					return None
			def setVarsetValue(self, property_name, value):
				doc = App.activeDocument()
				varset = doc.getObject("BowlVariables")
				if varset and property_name in varset.PropertiesList:
					setattr(varset, property_name, value)
				else:
					print(f"Property {property_name} not found in BowlVariables.")

			def update_values(self):
				#Update the local variables with the values in the text boxes

				self.bowl_height = float(self.bowl_heightBox.text())
				self.bowl_heightBox_in.setText(str(round(self.bowl_height / 25.4, 2)))
				self.bowl_radius = float(self.bowl_radiusBox.text())
				self.bowl_radiusBox_in.setText(str(round(self.bowl_radius / 25.4, 2)))
				self.layer_height = float(self.layer_heightBox.text())

				if self.construction_lines_radio.isChecked():
					self.construction_lines = True
				else:
					self.construction_lines = False
				self.setVarsetValue("NumSegments", 12)
				self.setVarsetValue("BowlHeight", self.bowl_height)
				self.setVarsetValue("LayerHeight", self.layer_height)

			def update_text_boxes(self, source):
				if source == 'layer_height':
					try:
						layer_height = float(self.layer_heightBox.text())
						num_layers = int(self.bowl_height / layer_height)
						self.num_layersBox.setText(str(num_layers))
						self.layer_heightBox_in.setText(str(round(layer_height / 25.4, 2)))
					except Exception as e:
						print(f"Error updating text boxes: {str(e)}")
						pass
				elif source == 'num_layers':
					try:
						num_layers = int(self.num_layersBox.text())
						layer_height = self.bowl_height / num_layers
						self.layer_heightBox.setText(str(round(layer_height, 2)))
						self.layer_heightBox_in.setText(str(round(layer_height / 25.4, 2)))
					
					except ValueError:
						pass

				#self.update_values()

				#self.update_text_boxes()

				#self.update_values()

				#self.update_text_boxes()

				

				#self.update_values()

			def bt_generate_lines_click(self):
				self.update_values()
				# Get the active document
				doc = App.activeDocument()
				if not doc:
					show_message("Error", "No active document. Please open a document first.")
					return

				sketch = doc.getObject("BowlProfileSketch")

				if sketch == None:
					sketch = doc.addObject('Sketcher::SketchObject', 'BowlProfileSketch')
					sketch.Placement = App.Placement(App.Vector(0, 0, 0), App.Rotation(App.Vector(1, 0, 0), 90))
					sketch.MapMode = "Deactivated"
					self.list_of_points = []

				a_point = sketch.addGeometry(Part.Point(App.Vector(self.bowl_radius/2, 0, 0)), False)
				self.list_of_points.append(a_point)
				sketch.addConstraint(Sketcher.Constraint('PointOnObject', a_point, 1, -1))
				num_lines = int(self.bowl_height / self.layer_height)
				for i in range(1, num_lines + 1):
					y_position = i * self.layer_height
					start = Vector(0, y_position, 0)
					end = Vector(self.bowl_radius+25, y_position, 0)
					line_idx = sketch.addGeometry(Part.LineSegment(start, end), False)
					if(self.construction_lines):
						sketch.setConstruction(line_idx, True)
					sketch.addConstraint(Sketcher.Constraint('Horizontal', line_idx))
					z = sketch.addConstraint(Sketcher.Constraint('DistanceY', -1, 1 , line_idx, 1, self.layer_height * i))
					sketch.addConstraint(Sketcher.Constraint('PointOnObject', line_idx, 1, -2))
					a_point = sketch.addGeometry(Part.Point(App.Vector((self.bowl_radius/2)+i*5, y_position, 0)), False)
					self.list_of_points.append(a_point)
					sketch.addConstraint(Sketcher.Constraint('PointOnObject', a_point, 1, line_idx))
				doc.recompute()
				Gui.SendMsgToActiveView("ViewFit")

			def bt_delete_lines_click(self):
				# Get the active document
				doc = App.activeDocument()
				if not doc:
					show_message("Error", "No active document. Please open a document first.")
					return
				# Get the active sketch

				sketch = doc.getObject("BowlProfileSketch")
				geoList = []
				for i, geo in enumerate(sketch.Geometry):
					geoList.append(i)
				geoList.sort()
				geoList.reverse()
				for i in geoList:
					sketch.delGeometry(i)

				doc.recompute()

			def on_cancel(self):
				"""Cancel and close the task panel"""
				Gui.Control.closeDialog()

			def closeEvent(self, event):
				print("closing")

			def getStandardButtons(self):
				"""Define which standard buttons to show (0 = none, we use custom buttons)"""
				#return int(QtWidgets.QDialogButtonBox.NoButton)
				return 0

		try:
			panel = AddBowlConstructionLines()

			# Show the task panel in FreeCAD
			Gui.Control.showDialog(panel)


		except Exception as e:
			App.Console.PrintError(f"Error adding construction lines: {str(e)}\n")