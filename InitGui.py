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
from SegmentSpreadsheet import SegmentSpreadsheet
'''
import PartDesignGui
>>> ### End command Std_Workbench
>>> ### Begin command Sketcher_NewSketch
>>> App.activeDocument().addObject('Sketcher::SketchObject', 'Sketch')
>>> App.activeDocument().Sketch.Placement = App.Placement(App.Vector(0.000000, 0.000000, 0.000000), App.Rotation(0.707107, 0.000000, 0.000000, 0.707107))
>>> App.activeDocument().Sketch.MapMode = "Deactivated"
'''
#a_path = str(Path(__file__).parent / 'WT_Bench.svg')

from pathlib import Path
import FreeCAD

install_mod = Path(FreeCAD.getHomePath()) / "Mod"
user_mod = Path(FreeCAD.getUserAppDataDir()) / "Mod" / "WoodturningTools" / "Resources" 


print("Install Mod:", install_mod)
print("User Mod:   ", user_mod)

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
		import FreeCAD as App
		import FreeCADGui as Gui
		
		class AddVasePanel:
				
			def __init__(self):

				from PySide import QtGui, QtCore, QtWidgets
				from pathlib import Path	
				self.form = QtWidgets.QWidget()
				self.form.setWindowTitle("Import Vase")
				#Local Variables with Default Values
				self.svg_height = 254  # Height to scale the SVG to (mm)

				# Create layout
				layout = QtWidgets.QVBoxLayout()

				title_label = QtWidgets.QLabel("Import Vase Parameters")
				title_font = title_label.font()
				title_font.setPointSize(12)
				title_font.setBold(True)
				title_label.setFont(title_font)
				layout.addWidget(title_label)

				text_box_layout = QtWidgets.QVBoxLayout()
				image_y_size_label = QtWidgets.QLabel("Image Y Size:")
				self.image_y_size_input = QtWidgets.QLineEdit()
				self.image_y_size_input.setText("254")
				text_box_layout.addWidget(image_y_size_label)
				text_box_layout.addWidget(self.image_y_size_input)
				layout.addLayout(text_box_layout)

				vases_layout = QtWidgets.QHBoxLayout()
				image_path = Path(FreeCAD.getUserAppDataDir()) / "Mod" / "WoodturningWorkbench" / "resources" / "vase1.png"
				btn1 = QtWidgets.QPushButton()
				btn1.setIcon(QtGui.QIcon(str(image_path)))
				btn1.setIconSize(QtCore.QSize(48, 48))   # icon display size
				btn1.clicked.connect(lambda: FreeCADGui.Console.PrintMessage("btn1 clicked\n"))	

				image_path = Path(FreeCAD.getUserAppDataDir()) / "Mod" / "WoodturningWorkbench" / "resources" / "vase2.png"
				btn2 = QtWidgets.QPushButton()
				btn2.setIcon(QtGui.QIcon(str(image_path)))
				btn2.setIconSize(QtCore.QSize(48, 48))   # icon display size
				btn2.clicked.connect(lambda: FreeCADGui.Console.PrintMessage("btn2 clicked\n"))						

				vases_layout.addWidget(btn1)
				vases_layout.addWidget(btn2)
				layout.addLayout(vases_layout)	

				# Button layout
				button_layout = QtWidgets.QHBoxLayout()

				# Add Bowl Outlines button
				self.add_vase_button = QtWidgets.QPushButton("Add Vase")
				self.add_vase_button.clicked.connect(self.bt_add_vase_clicked)
				self.cancel_button = QtWidgets.QPushButton("Close")
				self.cancel_button.clicked.connect(self.on_cancel)
				button_layout.addWidget(self.add_vase_button)
				button_layout.addWidget(self.cancel_button)
				layout.addLayout(button_layout)
			
				# Add stretch at end
				layout.addStretch()
				
				self.form.setLayout(layout)

			def set_tooltips(self):
				self.add_vase_button.setToolTip("Add the Vase to the document")

			def update_values(self):
				#Update the local variables with the values in the text boxes
				self.svg_height = float(self.image_y_size_input.text())
				
			
			
			def bt_add_vase_clicked(self):
				self.update_values()
				try:
					
					from freecad import module_io
					doc = FreeCAD.ActiveDocument
					from pathlib import Path
					image = str(Path(FreeCAD.getUserAppDataDir()) / "Mod" / "WoodturningWorkbench" / "resources" / "vase2.svg")
					a_vase = module_io.OpenInsertObject("FreeCADGui", image, "insert", "Unnamed")
					
					
					doc.recompute()
					FreeCAD.Console.PrintMessage("Vase added\n")
					
					for obj in doc.Objects:
						print(obj.Name, obj.TypeId)
						if obj.TypeId == "Image::ImagePlane":
							vase_obj = obj
					
					y = vase_obj.YSize
					scale_factor = self.svg_height / y
					new_x_size = vase_obj.XSize * scale_factor
					
					vase_obj.YSize = self.svg_height
					vase_obj.XSize = new_x_size
					vase_obj.Placement = FreeCAD.Placement(FreeCAD.Vector(0,0,self.svg_height/2),FreeCAD.Rotation(FreeCAD.Vector(1,0,0),90))
					
					
				except Exception as e:
					FreeCAD.Console.PrintError(f"Error adding vase: {str(e)}\n")

			def on_cancel(self):
				"""Cancel and close the task panel"""
				Gui.Control.closeDialog()
		
			def accept(self):
				"""Accept method (required by task panel)"""
				self.on_create_cube()
			
			def reject(self):
				"""Reject method (required by task panel)"""
				self.on_cancel()
			
			def getStandardButtons(self):
				"""Define which standard buttons to show (0 = none, we use custom buttons)"""
				#return int(QtWidgets.QDialogButtonBox.NoButton)
				return 0
			
		try:
			panel = AddVasePanel()
	
			# Show the task panel in FreeCAD
			Gui.Control.showDialog(panel)


		except Exception as e:
			App.Console.PrintError(f"Error adding segments: {str(e)}\n")

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
	FreeCADGui.addCommand('SegmentSpreadsheet', SegmentSpreadsheet())
	
	#FreeCADGui.addCommand('MakeBowlSolid', MakeBowlSolid())
except Exception as e:
	FreeCAD.Console.PrintError(f"Error registering commands: {str(e)}\n")

class WoodturningWorkbench(FreeCADGui.Workbench):
	"""Woodturning Workbench class"""
	from pathlib import Path
	image = str(Path(FreeCAD.getUserAppDataDir()) / "Mod" / "WoodturningWorkbench" / "icons" / "WT_Bench.svg")
	MenuText = "Woodturning Tools"
	ToolTip = "Tools for woodturning design"
	Icon = image  # You can add an icon path here

	def Initialize(self):
		"""Initialize the workbench"""
		# Add commands to toolbar and menu
		
		self.appendToolbar("Woodturning Tools", ["BowlConstructionLines", "AddSegments", "AddCatenaryCurve", "NewXYSketch", "AddVase", "SegmentSpreadsheet"])
		self.appendMenu("Woodturning Tools	", ["BowlConstructionLines", "AddSegments","AddCatenaryCurve", "NewXYSketch", "AddVase", "SegmentSpreadsheet"])

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