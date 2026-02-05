"""
InitGui.py - Initialize the GUI for Woodturning Workbench
"""

import FreeCAD
import FreeCADGui as Gui	
from pathlib import Path

from AddVase import AddVase
from TaskPanelTemplate import TaskPanelTemplate
from AddSegments import AddSegments
from AddCatenaryCurve import AddCatenaryCurve
from BowlConstructionLines import BowlConstructionLines
from SegmentSpreadsheet import SegmentSpreadsheet

from pathlib import Path


# Register commands at module level with error handling
try:
	Gui.addCommand('BowlConstructionLines', BowlConstructionLines())
	Gui.addCommand('AddSegments', AddSegments())
	Gui.addCommand('AddCatenaryCurve', AddCatenaryCurve())
	Gui.addCommand('SegmentSpreadsheet', SegmentSpreadsheet())
	Gui.addCommand('TaskPanelTemplate', TaskPanelTemplate())
	Gui.addCommand('AddVase', AddVase())
	
	
except Exception as e:
	FreeCAD.Console.PrintError(f"Error registering commands: {str(e)}\n")

class WoodturningWorkbench(Gui.Workbench):
	"""Woodturning Workbench class"""
	from pathlib import Path
	MenuText = "Woodturning Tools"
	ToolTip = "Tools for woodturning design"
	Icon = str(Path(FreeCAD.getUserAppDataDir()) / "Mod" / "WoodturningWorkbench" / "icons" / "WT_Bench.svg")

	def Initialize(self):
		"""Initialize the workbench"""
		# Add commands to toolbar and menu
		self.appendToolbar("Woodturning Tools", ["AddVase","BowlConstructionLines", "AddSegments", "AddCatenaryCurve", "SegmentSpreadsheet", "TaskPanelTemplate"])
		self.appendMenu("Woodturning Tools	", ["AddVase","BowlConstructionLines", "AddSegments","AddCatenaryCurve", "SegmentSpreadsheet", "TaskPanelTemplate"])
		print("Woodturning Tools Workbench initialized")

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
Gui.addWorkbench(WoodturningWorkbench())