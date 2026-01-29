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

		# Get selected objects
		#selected_objects = Gui.Selection.getSelectionEx()
		#if not selected_objects:
		#    App.Console.PrintError("No objects selected\n")
		#    exit()
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
		spreadsheet = doc.addObject("Spreadsheet::Sheet", "Sheet2")
		spreadsheet.mergeCells('A1:D1')
		spreadsheet.set("A1", "Segment Dimensions (in mm rounded up)")
		spreadsheet.setAlignment('A1:D1', 'center', 'keep')
		spreadsheet.setStyle('A1:D1', 'bold', 'add')
		# Add headers
		spreadsheet.set("A2", "Label")
		spreadsheet.set("B2", "Segment Width")
		spreadsheet.set("C2", "Segment End Length")
		spreadsheet.set("D2", "Segment Thickness")

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
		row = 3
		for label, x_dim, y_dim, z_dim in object_data:
			spreadsheet.set(f"A{row}", label)
			spreadsheet.set(f"B{row}", f"{x_dim:.2f}")
			spreadsheet.set(f"C{row}", f"{y_dim:.2f}")
			spreadsheet.set(f"D{row}", f"{z_dim:.2f}")
			row += 1

		# Recompute the document to update the spreadsheet
		doc.recompute()

		App.Console.PrintMessage(f"Spreadsheet created with {row - 2} objects\n")	
