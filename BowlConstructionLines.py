import FreeCAD as App 
import FreeCADGui as Gui
from PySide import QtGui, QtCore
from FreeCAD import Vector
import Part
import Sketcher


class BowlConstructionLines:
	def GetResources(self):
		"""Return the command resources"""
		return {
			'Pixmap': '',  # You can add an icon path here
			'MenuText': 'Add Construction Lines to Bowl',
			'ToolTip': 'Add construction lines to the document'
		}

	def IsActive(self):
		"""Check if the command is active"""
		return App.ActiveDocument is not None

	def Activated(self):
		"""Execute the command"""
		class AddBowlConstructionLines:
			
			from PySide import QtGui, QtCore
			from FreeCAD import Vector
			import Part
			import Sketcher	

	#Creates the Dialog Box
			def __init__(self):
				#Local Variables with Default Values
				print("Initializing Bowl Construction Lines GUI")
				from PySide import QtGui, QtCore, QtWidgets	
				self.form = QtWidgets.QWidget()
				self.form.setWindowTitle("Make Sketch with Bowl Construction Lines")
				self.bowl_height = 254.0  # Bowl height in mm
				self.bowl_radius = 127.0  # Bowl radius in mm
				self.layer_height = 19.05 # Layer height in mm
				self.construction_lines = True

				self.list_of_points = []
				self.list_of_lines = []	
				
				#super(AddBowlConstructionLines, self).__init__()
				#Window
				#self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
				#self.setWindowTitle("Add Layer Construction Lines for Bowl")	
				#self.resize(400,100)
				#self.show()
				layout = QtWidgets.QVBoxLayout()
				
				# Title
				title_label = QtWidgets.QLabel("Bowl Construction Line Parameters")
				title_font = title_label.font()
				title_font.setPointSize(12)
				title_font.setBold(True)
				title_label.setFont(title_font)
				layout.addWidget(title_label)

				#Buttons
				self.bt_generate_lines = QtGui.QPushButton("Generate Lines")
				self.bt_delete_lines = QtGui.QPushButton("Delete Lines")
				self.bt_generate_lines.clicked.connect(self.bt_generate_lines_click)
				self.bt_delete_lines.clicked.connect(self.bt_delete_lines_click)

				#QtCore.QObject.connect(self.bt_generate_lines, QtCore.SIGNAL("pressed()"), self.bt_generate_lines_click)
				#QtCore.QObject.connect(self.bt_delete_lines, QtCore.SIGNAL("pressed()"), self.bt_delete_lines_click)

				self.bowl_heightBox = QtGui.QLineEdit(str(self.bowl_height))
				self.bowl_radiusBox = QtGui.QLineEdit(str(self.bowl_radius))
				self.layer_heightBox = QtGui.QLineEdit(str(self.layer_height))
				self.construction_lines_radio = QtGui.QRadioButton("Construction lines")
						
				#Layout
				#layout = QtGui.QVBoxLayout()

				layout.addWidget(QtGui.QLabel("Bowl Height:"))
				layout.addWidget(self.bowl_heightBox)
				layout.addWidget(QtGui.QLabel("Bowl Radius:"))
				layout.addWidget(self.bowl_radiusBox)	
				layout.addWidget(QtGui.QLabel("Layer Height:"))
				layout.addWidget(self.construction_lines_radio)
				self.construction_lines_radio.setChecked(True)
				layout.addWidget(self.layer_heightBox)
				layout.addWidget(self.bt_generate_lines)		
				layout.addWidget(self.bt_delete_lines)	

				self.form.setLayout(layout)	
				#self.setLayout(layout)
				#self.set_tooltips()

			def set_tooltips(self):
				self.bowl_heightBox.setToolTip("Height of the bowl in mm")
				self.bowl_radiusBox.setToolTip("Radius of the bowl in mm")
				self.layer_heightBox.setToolTip("Height of each layer in mm")
				self.bt_generate_lines.setToolTip("Generate construction lines for each layer of the bowl")	
				self.bt_delete_lines.setToolTip("Delete all construction lines created by this macro")

			def update_values(self):
				#Update the local variables with the values in the text boxes
				self.bowl_height = float(self.bowl_heightBox.text())
				self.bowl_radius = float(self.bowl_radiusBox.text())
				self.layer_height = float(self.layer_heightBox.text())
				if self.construction_lines_radio.isChecked():
					self.construction_lines = True
				else:
					self.construction_lines = False
				
			def bt_generate_lines_click(self):
				print("Generating Lines")
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
					print("Creating New Sketch")
				
					self.list_of_points = []
				a_point = sketch.addGeometry(Part.Point(App.Vector(self.bowl_radius/2, 0, 0)), False)
				self.list_of_points.append(a_point) 
				sketch.addConstraint(Sketcher.Constraint('PointOnObject', a_point, 1, -1)) 
				num_lines = int(self.bowl_height / self.layer_height)
				for i in range(1, num_lines + 1):
					y_position = i * self.layer_height
					start = Vector(0, y_position, 0)
					end = Vector(self.bowl_radius, y_position, 0)
					line_idx = sketch.addGeometry(Part.LineSegment(start, end), False)
					if(self.construction_lines):
						sketch.setConstruction(line_idx, True)
					print(line_idx)
					sketch.addConstraint(Sketcher.Constraint('Horizontal', line_idx))
					z = sketch.addConstraint(Sketcher.Constraint('DistanceY', -1, 1 , line_idx, 1, self.layer_height * i))
					sketch.addConstraint(Sketcher.Constraint('PointOnObject', line_idx, 1, -2))
					a_point = sketch.addGeometry(Part.Point(App.Vector((self.bowl_radius/2)+i*5, y_position, 0)), False)
					self.list_of_points.append(a_point) 
					sketch.addConstraint(Sketcher.Constraint('PointOnObject', a_point, 1, line_idx))
				doc.recompute()
				Gui.SendMsgToActiveView("ViewFit")

			def bt_delete_lines_click(self):
				print("Deleting Lines")	
				print(self.list_of_points)
						# Get the active document
				doc = App.activeDocument()
				if not doc:
					show_message("Error", "No active document. Please open a document first.")
					return
				# Get the active sketch

				sketch = doc.getObject("BowlProfileSketch")
				geoList = []
				for i, geo in enumerate(sketch.Geometry):
					# Print information about the geometry
					print(f"  Element index {i}: {geo.TypeId}")
					geoList.append(i)
				geoList.sort()
				geoList.reverse()
				for i in geoList:	
					sketch.delGeometry(i)

				doc.recompute()
					
				
			def closeEvent(self, event):
				print("closing")
			
			#def getStandardButtons(self):
			#	"""Define which standard buttons to show (0 = none, we use custom buttons)"""
				#return int(QtWidgets.QDialogButtonBox.NoButton)
			#	return 0
		
		try:
			panel = AddBowlConstructionLines()
	
			# Show the task panel in FreeCAD
			Gui.Control.showDialog(panel)


		except Exception as e:
			App.Console.PrintError(f"Error adding construction lines: {str(e)}\n")