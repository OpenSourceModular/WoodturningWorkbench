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

class SegmentSpreadsheet:
	"""Command to add a catenary curve sketch"""
	def __init__(self):
		pass
	#    obj.Proxy = self
	#    obj.addProperty("App::PropertyInteger", "Sag", "Dimensions").Sag=-1

	def GetResources(self):
		"""Return the command resources"""
		return {
			'Pixmap': '',  # You can add an icon path here
			'MenuText': 'Make Segment Dimension Spreadsheet',
			'ToolTip': 'Create a spreadsheet listing segment dimensions'
		}

	def IsActive(self):
		"""Check if the command is active"""
		return FreeCAD.ActiveDocument is not None

	def Activated(self):
		print("SegmentSpreadsheet Activated")
		import FreeCAD as App
		import FreeCADGui as Gui
		import math
		"""Execute the command"""
		# Get the active document
		doc = App.ActiveDocument
		if not doc:
			App.Console.PrintError("No active document found\n")
			exit()

		segment_objects = []
		for obj in doc.Objects:
			if "Segment" in obj.Label:
				segment_objects.append(obj)
		# Activate the Spreadsheet workbench
		try:
			Gui.activateWorkbench("SpreadsheetWorkbench")
		except:
			App.Console.PrintWarning("Could not activate Spreadsheet workbench\n")

		print("doc:", doc)
		print("type(doc):", type(doc))
		# Create a new spreadsheet
		spreadsheet = doc.addObject("Spreadsheet::Sheet", "Segment Dimension Spreadsheet")
		spreadsheet.set("A1", "Vessel Name:")
		spreadsheet.set("A2", "Vessel Height:")
		spreadsheet.set("A3", "Vessel Diameter:")
		if doc.getObject("BowlVariables"):
			variables = doc.getObject("BowlVariables")
			spreadsheet.set("B2", str(variables.BowlHeight))
			spreadsheet.set("B3", str(variables.BowlWidth))
			
			spreadsheet.setDisplayUnit("B2:B3", "mm")
		spreadsheet.mergeCells('B4:D4')
		spreadsheet.set("B4", "Segment Dimensions (in mm rounded up)")
		spreadsheet.mergeCells('E4:G4')
		spreadsheet.set("E4", "Segment Dimensions (in inches 2 Decimal)")
		spreadsheet.setAlignment('B4:D4', 'center', 'keep')
		spreadsheet.setStyle('B4:D4', 'bold', 'add')
		spreadsheet.setAlignment('E4:G4', 'center', 'keep')
		spreadsheet.setStyle('E4:G4', 'bold', 'add')
		# Add headers
		spreadsheet.set("A5", "Label")
		spreadsheet.set("B5", "Segment Width")
		spreadsheet.set("C5", "Segment End Length")
		spreadsheet.set("D5", "Segment Thickness")
		spreadsheet.set("E5", "Segment Width")
		spreadsheet.set("F5", "Segment End Length")
		spreadsheet.set("G5", "Segment Thickness")

		# Set column widths for better visibility
		#spreadsheet.setColumnWidth("A", 200)
		#spreadsheet.setColumnWidth("B", 150)
		#spreadsheet.setColumnWidth("C", 150)
		#spreadsheet.setColumnWidth("D", 150)

		# Process each selected object and collect data
		object_data = []
		for obj in segment_objects:

			try:
				# Get the label
				label = obj.Label
				
				# Get bounding box if the object has a shape
				if hasattr(obj, 'Shape'):
					bbox = obj.Shape.BoundBox
					x_dim = math.ceil(bbox.XLength)
					y_dim = math.ceil(bbox.YLength)
					z_dim = bbox.ZLength
				else:
					# If no shape, set dimensions to 0
					x_dim = 0
					y_dim = 0
					z_dim = 0
				
				object_data.append((label, x_dim, y_dim, z_dim))
			
			except Exception as e:
				App.Console.PrintWarning(f"Error processing object: {str(e)}\n")

		# Sort the data by label name (ascending)
		object_data.sort(key=lambda x: x[0])

		# Populate the spreadsheet with sorted data
		row = 6
		for label, x_dim, y_dim, z_dim in object_data:
			x_dim2 = x_dim /25.4
			y_dim2 = y_dim /25.4
			z_dim2 = z_dim /25.4

			spreadsheet.set(f"A{row}", label)
			spreadsheet.set(f"B{row}", f"{x_dim:.2f}")
			spreadsheet.set(f"C{row}", f"{y_dim:.2f}")
			spreadsheet.set(f"D{row}", f"{z_dim:.2f}")
			spreadsheet.set(f"E{row}", f"{x_dim:.2f}")
			spreadsheet.set(f"F{row}", f"{y_dim:.2f}")
			spreadsheet.set(f"G{row}", f"{z_dim:.2f}")	
			spreadsheet.setDisplayUnit(f"B{row}:D{row}", "mm")
			spreadsheet.setDisplayUnit(f"E{row}:G{row}", "\"")		
			row += 1
		# App.getDocument('Unnamed').getObject('Segment_Dimension_Spreadsheet').setDisplayUnit('E3:G12', '\"')

		# Recompute the document to update the spreadsheet
		doc.recompute()

		App.Console.PrintMessage(f"Spreadsheet created with {row - 2} objects\n")	
