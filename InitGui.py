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
import FreeCADGui as Gui	
from pathlib import Path

from AddVase import AddVase
from TaskPanelTemplate import TaskPanelTemplate
from AddSegments import AddSegments
from CatenaryCurve import CatenaryCurve
from BowlConstructionLines import BowlConstructionLines
from SegmentSpreadsheet import SegmentSpreadsheet
from BowlFromABoard import BowlFromABoard
from ApplyColors import ApplyColors
from About import About

from pathlib import Path


# Register commands at module level with error handling
try:
	Gui.addCommand('BowlConstructionLines', BowlConstructionLines())
	Gui.addCommand('AddSegments', AddSegments())
	Gui.addCommand('CatenaryCurve', CatenaryCurve())
	Gui.addCommand('SegmentSpreadsheet', SegmentSpreadsheet())
	Gui.addCommand('BowlFromABoard', BowlFromABoard())
	Gui.addCommand('AddVase', AddVase())
	Gui.addCommand('ApplyColors', ApplyColors())
	Gui.addCommand('About', About())
	
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
		self.appendToolbar("Woodturning Tools", ["AddVase","BowlConstructionLines", "AddSegments",  "SegmentSpreadsheet", "BowlFromABoard", "ApplyColors","CatenaryCurve", "About"])
		self.appendMenu("Woodturning Tools	", ["AddVase","BowlConstructionLines", "AddSegments", "SegmentSpreadsheet", "BowlFromABoard", "ApplyColors", "CatenaryCurve", "About"])
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