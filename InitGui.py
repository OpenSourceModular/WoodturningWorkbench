"""
InitGui.py - Initialize the GUI for SampleWorkbench
"""

#from curses.panel import panel
#from curses import panel
import math
import FreeCAD
import FreeCADGui
import Sketcher
import Part
#from PySide import QtGui, QtCore, QtWidgets
from FreeCAD import Vector
import Sketcher
from math import cos, sin, pi, radians, tan
import PySide.QtGui
import PySide.QtCore
import PySide.QtWidgets
from pathlib import Path

from AddSegments import AddSegments
from AddCatenaryCurve import AddCatenaryCurve
from BowlConstructionLines import BowlConstructionLines
from MakeBowlSolid import MakeBowlSolid	
'''
import PartDesignGui
>>> ### End command Std_Workbench
>>> ### Begin command Sketcher_NewSketch
>>> App.activeDocument().addObject('Sketcher::SketchObject', 'Sketch')
>>> App.activeDocument().Sketch.Placement = App.Placement(App.Vector(0.000000, 0.000000, 0.000000), App.Rotation(0.707107, 0.000000, 0.000000, 0.707107))
>>> App.activeDocument().Sketch.MapMode = "Deactivated"
'''
#a_path = str(Path(__file__).parent / 'WT_Bench.svg')

class NewXYSketch:
	"""Command to add a sphere"""

	def GetResources(self):
		"""Return the command resources"""
		return {
			'Pixmap': '',   # You can add an icon path here
			'MenuText': 'New XY Sketch',
			'ToolTip': 'Add a new XY sketch to the document'
		}

	def IsActive(self):
		"""Check if the command is active"""
		return FreeCAD.ActiveDocument is not None

	def Activated(self):
		"""Execute the command"""
		try:
			doc = FreeCAD.ActiveDocument
			if not doc:
				FreeCAD.Console.PrintError("No active document\n")
				return

			# Create a new sketch
			sketch = doc.addObject('Sketcher::SketchObject', 'Sketch')
			sketch.Placement = FreeCAD.Placement(FreeCAD.Vector(0, 0, 0), FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), 90))
			sketch.MapMode = "Deactivated"	
			# Recompute the document
			doc.recompute()
		except Exception as e:
			FreeCAD.Console.PrintError(f"Error adding sphere: {str(e)}\n")

class AddVase:

	def GetResources(self):
		"""Return the command resources"""
		return {
			'Pixmap': '',  # You can add an icon path here
			'MenuText': 'Add Vase',
			'ToolTip': 'Add a vase'
		}

	def IsActive(self):
		"""Check if the command is active"""
		return FreeCAD.ActiveDocument is not None

	def Activated(self):
		"""Execute the command"""
		try:
			from freecad import module_io
			from pathlib import Path
			doc = FreeCAD.ActiveDocument
			image = str(Path(__file__).parent / 'Vase.svg')
			module_io.OpenInsertObject("FreeCADGui", image, "insert", "Unnamed")
			FreeCAD.Console.PrintMessage("Vase added\n")
		except Exception as e:
			FreeCAD.Console.PrintError(f"Error adding vase: {str(e)}\n")

class AddSphere:
	"""Command to add a sphere"""

	def GetResources(self):
		"""Return the command resources"""
		return {
			'Pixmap': '',  # You can add an icon path here
			'MenuText': 'Add Sphere',
			'ToolTip': 'Add a sphere to the document'
		}

	def IsActive(self):
		"""Check if the command is active"""
		return FreeCAD.ActiveDocument is not None

	def Activated(self):
		"""Execute the command"""
		try:
			doc = FreeCAD.ActiveDocument
			if not doc:
				FreeCAD.Console.PrintError("No active document\n")
				return

			# Create a sphere
			sphere = Part.makeSphere(50.0)  # Radius of 50 mm

			# Create a Part object and assign the sphere shape
			part = doc.addObject("Part::Feature", "Sphere")
			part.Shape = sphere

			# Set the placement (position)
			part.Placement.Base = FreeCAD.Vector(0, 0, 0)

			# Recompute the document
			doc.recompute()

			# Select the new object
			FreeCADGui.Selection.clearSelection()
			FreeCADGui.Selection.addSelection(part)

			FreeCAD.Console.PrintMessage("Sphere added\n")
		except Exception as e:
			FreeCAD.Console.PrintError(f"Error adding sphere: {str(e)}\n")

# Register commands at module level with error handling
try:
	FreeCADGui.addCommand('BowlConstructionLines', BowlConstructionLines())
	FreeCADGui.addCommand('AddSegments', AddSegments())
	FreeCADGui.addCommand('AddCatenaryCurve', AddCatenaryCurve())
	FreeCADGui.addCommand('NewXYSketch', NewXYSketch())
	FreeCADGui.addCommand('AddSphere', AddSphere())
	FreeCADGui.addCommand('AddVase', AddVase())
	
	FreeCADGui.addCommand('MakeBowlSolid', MakeBowlSolid())
except Exception as e:
	FreeCAD.Console.PrintError(f"Error registering commands: {str(e)}\n")

class WoodturningWorkbench(FreeCADGui.Workbench):
	"""Woodturning Workbench class"""
	from pathlib import Path
	MenuText = "Woodturning Tools"
	ToolTip = "Tools for woodturning design"
	Icon = ""  # You can add an icon path here

	def Initialize(self):
		"""Initialize the workbench"""
		# Add commands to toolbar and menu
		
		self.appendToolbar("Woodturning Tools", ["BowlConstructionLines", "AddSegments", "AddCatenaryCurve", "NewXYSketch", "AddVase" ])
		self.appendMenu("Woodturning Tools	", ["BowlConstructionLines", "AddSegments","AddCatenaryCurve", "NewXYSketch", "AddVase" ])

	def Activated(self):
		"""Called when the workbench is activated"""
		FreeCAD.Console.PrintMessage("Woodturning Tools Workbench activated\n")

	def Deactivated(self):
		"""Called when the workbench is deactivated"""
		FreeCAD.Console.PrintMessage("Woodturning Tools Workbench deactivated\n")
	def GetClassName(self):
		"""Return the class name"""
		return "Gui::PythonWorkbench"

# Create and register the workbench
FreeCADGui.addWorkbench(WoodturningWorkbench())