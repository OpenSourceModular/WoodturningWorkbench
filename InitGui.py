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

class WoodturningWorkbench(Gui.Workbench):
	"""Woodturning Workbench class"""
	from pathlib import Path

	MenuText = "Woodturning Tools"
	ToolTip = "Tools for woodturning design"
	Icon = str(Path(FreeCAD.getUserAppDataDir()) / "Mod" / "WoodturningWorkbench" / "icons" / "WT_Bench.svg")

	def Initialize(self):
		from collections import OrderedDict
		#from AddVase import AddVase
		from AddVessel import AddVessel
		from AddTorus import AddTorus
		from RotateRings import RotateRings
		from TaskPanelTemplate import TaskPanelTemplate
		from TopView import TopView
		from AddSegments import AddSegments
		from CatenaryCurve import CatenaryCurve
		from BowlConstructionLines import BowlConstructionLines
		from SegmentSpreadsheet import SegmentSpreadsheet
		from BowlFromABoard import BowlFromABoard
		from ApplyColors import ApplyColors
		from About import About
		from WedgeGenerator import WedgeGenerator	
		from OffcenterTurning import OffcenterTurning
		"""Initialize the workbench"""
		# Add commands to toolbar and menu
		try:
			workbench_commands = OrderedDict(
				[	
					('AddVessel', AddVessel()),
					('BowlConstructionLines', BowlConstructionLines()),
					('AddSegments', AddSegments()),
					('RotateRings', RotateRings()),
					('ApplyColors', ApplyColors()),
					('SegmentSpreadsheet', SegmentSpreadsheet()),
					('TopView', TopView()),
					('CatenaryCurve', CatenaryCurve()),
					('BowlFromABoard', BowlFromABoard()),
					('AddTorus', AddTorus()),
					('WedgeGenerator', WedgeGenerator()),
					('OffcenterTurning', OffcenterTurning()),
					('About', About())
				]
			)	
			for command_name, command in workbench_commands.items():
				Gui.addCommand(command_name, command)	
			self.appendToolbar("Woodturning Tools", list(workbench_commands.keys()))
			self.appendMenu("Woodturning Tools", list(workbench_commands.keys()))
		except Exception as e:
			FreeCAD.Console.PrintError(f"Error registering commands: {str(e)}\n")
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