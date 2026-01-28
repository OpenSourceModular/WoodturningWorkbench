"""
AddSegments.py - Command to add segments to a bowl design
"""

import math
from pydoc import doc
from unicodedata import name
import FreeCAD
import FreeCADGui
from FreeCAD import Vector
from math import cos, sin, pi, radians, tan
import PySide.QtGui
import PySide.QtCore
import PySide.QtWidgets
import Part
import Draft
from BOPTools import BOPFeatures


class AddSegments:
	
	
	def GetResources(self):
		"""Return the command resources"""
		return {
			'Pixmap': '',  # You can add an icon path here
			'MenuText': 'Add Segments',
			'ToolTip': 'Add a segments to the document'
		}

	def IsActive(self):
		"""Check if the command is active"""
		return FreeCAD.ActiveDocument is not None

	def Activated(self):
		"""Execute the command"""
		class AddSegmentsTaskPanel:
	#Creates the Task Panel
			def __init__(self):
				
				from PySide import QtGui, QtCore, QtWidgets	
				self.form = QtWidgets.QWidget()
				self.form.setWindowTitle("Add Segments to Bowl")
				#Local Variables with Default Values
				self.number_of_segments = 12  # Number of segments around the bowl
				self.bowl_height = 254.0  # Bowl height in mm
				self.bowl_radius = 127.0  # Bowl radius in mm
				self.layer_height = 19.05 # Layer height in mm
				self.fudge = 6.35  # Fudge factor in mm
				self.wall_thickness = 18.0  # Wall thickness in mm
				self.list_of_segment_names = []

						# Create layout
				layout = QtWidgets.QVBoxLayout()
				
				# Title
				title_label = QtWidgets.QLabel("Bowl Segment Parameters")
				title_font = title_label.font()
				title_font.setPointSize(12)
				title_font.setBold(True)
				title_label.setFont(title_font)
				layout.addWidget(title_label)

				num_segments_layout = QtWidgets.QHBoxLayout()
				num_segments_label = QtWidgets.QLabel("Number of Segments:")
				num_segments_label.setMinimumWidth(150)
				self.num_segments_input = QtWidgets.QLineEdit()
				self.num_segments_input.setText(str(self.number_of_segments))
				self.num_segments_input.setPlaceholderText("Enter number of segments")
				num_segments_layout.addWidget(num_segments_label)
				num_segments_layout.addWidget(self.num_segments_input)
				layout.addLayout(num_segments_layout)

				fudge_layout = QtWidgets.QHBoxLayout()
				fudge_label = QtWidgets.QLabel("Fudge Factor:")
				fudge_label.setMinimumWidth(150)
				self.fudge_input = QtWidgets.QLineEdit()
				self.fudge_input.setText("0")
				self.fudge_input.setPlaceholderText("Enter fudge factor")
				fudge_layout.addWidget(fudge_label)
				fudge_layout.addWidget(self.fudge_input)
				layout.addLayout(fudge_layout)
				num_segments_layout.addWidget(self.num_segments_input)
				layout.addLayout(num_segments_layout)

				wall_thickness_layout = QtWidgets.QHBoxLayout()
				wall_thickness_label = QtWidgets.QLabel("Wall Thickness:")
				wall_thickness_label.setMinimumWidth(150)
				self.wall_thickness_input = QtWidgets.QLineEdit()
				self.wall_thickness_input.setText("19.05")
				self.wall_thickness_input.setPlaceholderText("Enter wall thickness")
				wall_thickness_layout.addWidget(wall_thickness_label)
				wall_thickness_layout.addWidget(self.wall_thickness_input)
				layout.addLayout(wall_thickness_layout)
				fudge_layout.addWidget(fudge_label)
				fudge_layout.addWidget(self.fudge_input)
				layout.addLayout(fudge_layout)
				num_segments_layout.addWidget(self.num_segments_input)
				layout.addLayout(num_segments_layout)


		# Add spacing
				layout.addSpacing(20)
				
				# Button layout
				button_layout = QtWidgets.QHBoxLayout()

				# Add Bowl Outlines button
				self.add_bowl_outlines_button = QtWidgets.QPushButton("Add Bowl Outlines")
				self.add_bowl_outlines_button.clicked.connect(self.bt_add_bowl_outlines_click)
				button_layout.addWidget(self.add_bowl_outlines_button)

				# Delete Bowl Outlines button
				self.delete_bowl_outlines_button = QtWidgets.QPushButton("Delete Bowl Outlines")
				self.delete_bowl_outlines_button.clicked.connect(self.bt_delete_bowl_outlines_click)
				button_layout.addWidget(self.delete_bowl_outlines_button)

				# Add Segments button
				self.add_segments_button = QtWidgets.QPushButton("Add Segments")
				self.add_segments_button.clicked.connect(self.bt_add_segments_click)
				button_layout.addWidget(self.add_segments_button)

				# Delete Segments button
				self.delete_segments_button = QtWidgets.QPushButton("Delete Segments")
				self.delete_segments_button.clicked.connect(self.bt_delete_segments_click)
				button_layout.addWidget(self.delete_segments_button)

				button2_layout = QtWidgets.QHBoxLayout()
				
				# Array segments around ring button
				self.array_segments_button = QtWidgets.QPushButton("Array Segments Around Ring")
				self.array_segments_button.clicked.connect(self.bt_array_segments_click)
				button2_layout.addWidget(self.array_segments_button)

				# Delete Segments button
				self.delete_segments_button = QtWidgets.QPushButton("Delete Segments")
				self.delete_segments_button.clicked.connect(self.bt_delete_segments_click)
				button2_layout.addWidget(self.delete_segments_button)

				self.intersect_segments_button = QtWidgets.QPushButton("Intersect Segments")
				self.intersect_segments_button.clicked.connect(self.bt_intersect_segments_click)
				button2_layout.addWidget(self.intersect_segments_button)

				button3_layout = QtWidgets.QHBoxLayout()	
				# Cancel button
				self.cancel_button = QtWidgets.QPushButton("Close")
				self.cancel_button.clicked.connect(self.on_cancel)
				button3_layout.addWidget(self.cancel_button)

				layout.addLayout(button_layout)
				layout.addLayout(button2_layout)
				layout.addLayout(button3_layout)
				
				# Add stretch at end
				layout.addStretch()
				
				self.form.setLayout(layout)


			def set_tooltips(self):
				self.bowl_numSegmentsBox.setToolTip("Number of segments around the bowl")
				self.bowl_layer_heightBox.setToolTip("Height of each layer in mm")
				self.bt_add_segments.setToolTip("Add segments to the bowl")	
				self.bt_delete_segments.setToolTip("Delete all segments created by this macro")

			def update_values(self):
				#Update the local variables with the values in the text boxes
				self.bowl_num_segments = int(self.num_segments_input.text())
				self.fudge = float(self.fudge_input.text())
				self.wall_thickness = float(self.wall_thickness_input.text())
				#self.layer_height = float(self.bowl_layer_heightBox.text())

			def	bt_intersect_segments_click(self):
				import FreeCAD as App
				doc = FreeCAD.ActiveDocument		
				print("Intersecting Segments")
				bowl_solid_objs = []
				for obj in FreeCAD.ActiveDocument.Objects:
					if "BowlSolid" in obj.Name:
						bowl_solid_objs.append(obj)
				
				if len(bowl_solid_objs)==0:
					print("No BowlSolid objects found for intersection.")
					return
				if len(bowl_solid_objs)>1:
					print("Multiple BowlSolid objects found. Using the first one.")
				bowl_solid = bowl_solid_objs[0]

				segment_objs = []
				for obj in FreeCAD.ActiveDocument.Objects:
					if "Segment" in obj.Name:
						segment_objs.append(obj)
				
				if len(segment_objs)==0:
					print("No Segment objects found for intersection.")
					return
				bowl_clones = []
				for j in range(0,len(segment_objs)):
					view_obj = bowl_solid
					cloned_object = Draft.clone(view_obj)
					bowl_clones.append(cloned_object)
				intersection_list = []
				for a in range(0,len(bowl_clones)):
					bp = BOPFeatures.BOPFeatures(App.activeDocument())
					new_common = bp.make_multi_common([segment_objs[a].Name] + [bowl_clones[a].Name])
					#new_common.Label = f"Intersection_{a+1:03d}"
					intersection_list.append(new_common.Name)
				doc.recompute()
				for a in range(0,len(intersection_list)):
					print("Making solid:", intersection_list[a])
					p= App.ActiveDocument.getObject(intersection_list[a]).Shape.Faces
					p = Part.Solid(Part.Shell(p))
					o = App.ActiveDocument.addObject("Part::Feature","Common013_solid")
					o.Label="Intersect(Solid)_001"
					o.Shape=p
					del p, o 
				doc.recompute()

				for obj in doc.Objects:
					if "Common"in obj.Label or "BowlSolid0" in obj.Label:
						doc.removeObject(obj.Name)

				doc.recompute()

			def bt_add_bowl_outlines_click(self):
				import FreeCAD as App
				import FreeCADGui as Gui
				self.update_values()
				"""Create a BSpline from all point geometries in the selected sketch."""
				doc = App.activeDocument()
				if not doc:
					print("Error: No active document. Open a document first.")
					return

				sel = Gui.Selection.getSelection()
				if not sel:
					print("Error: No object selected. Select a sketch and try again.")
					return
				obj = sel[0]
				if obj.TypeId != 'Sketcher::SketchObject':
					print(f"Error: Selected object '{obj.Name}' is not a sketch (TypeId={obj.TypeId}).")
					return

				sketch = obj

				# Collect point geometries
				poles = []
				for i, geo in enumerate(sketch.Geometry):
					if getattr(geo, 'TypeId', '') == 'Part::GeomPoint':
						# geo.X, geo.Y, geo.Z contain the coordinates of the sketch point
						poles.append(Vector(geo.X, geo.Y, geo.Z))

				if not poles:
					print(f"No point geometries found in sketch '{sketch.Name}'.")
					return

				if len(poles) < 2:
					print("Need at least 2 points to create a BSpline.")
					return

				# Build BSpline curve from poles
				try:
					curve = Part.BSplineCurve()
					curve.buildFromPoles(poles)
					shape = curve.toShape()
				except Exception as e:
					print(f"Failed to build BSpline: {e}")
					return

				# Create Part::Feature to hold the result
				obj_name = f"BSpline_from_{sketch.Name}"
				bs_obj = doc.addObject("Part::Feature", obj_name)
				bs_obj.Label = "Bowl_Outline"
				bs_obj.Shape = shape

				new_copy = App.ActiveDocument.copyObject(bs_obj, True)
				new_copy.Label = "Bowl_Outline"
				new_copy.Placement = FreeCAD.Placement(FreeCAD.Vector(-self.wall_thickness,0,0),FreeCAD.Rotation(FreeCAD.Vector(1,0,0),90))
				doc.recompute()
				# Try to align placement with the sketch
				try:
					if hasattr(sketch, 'Placement'):
						bs_obj.Placement = sketch.Placement
				except Exception:
					pass
			
			def make_segment(self, num_segments=12, radius=50, trapezoid_height=19.05, z_level=0,extrude_height=10, solid_bottom=True):
				from math import cos, sin, pi, radians, tan
				import FreeCADGui as Gui
				doc = FreeCAD.ActiveDocument
				angle = 180 / num_segments

				left_top = -((radius * tan(radians(angle))))
				right_top = (radius * tan(radians(angle)))
				left_bottom = -((radius - trapezoid_height) * tan(radians(angle)))
				right_bottom = ((radius - trapezoid_height) * tan(radians(angle)))

				y_bottom = radius-trapezoid_height
				y_top = radius

				if solid_bottom:
					left_bottom = 0
					right_bottom = 0
					y_bottom = 0

				vertices = [
					FreeCAD.Vector(left_bottom, y_bottom, z_level),
					FreeCAD.Vector(right_bottom, y_bottom, z_level),
					FreeCAD.Vector(right_top, y_top, z_level),
					FreeCAD.Vector(left_top, y_top, z_level),
					FreeCAD.Vector(left_bottom, y_bottom, z_level)
				]
				wire = Part.makePolygon(vertices)
				face = Part.Face(wire)
				shape = face.extrude(FreeCAD.Vector(0, 0, extrude_height))

				obj = doc.addObject("Part::Feature", f"Segment_000")
				
				obj.Shape = shape
				return obj.Name
			def bt_rotate_segments_click(self):
				doc = FreeCAD.ActiveDocument
				import FreeCAD as App
				import Draft
				rotate_angle = 15
				for name in self.list_of_segment_names:
					print(name)
					obj = doc.getObject(name)
					obj.ViewObject.Transparency = 20
					another_obj = Draft.make_polar_array(obj, number=12, angle=360.0, center=App.Vector(0.0, 0.0, 0.0), use_link=True)
					another_obj.Placement = App.Placement(App.Vector(0,0,0),App.Rotation(App.Vector(0,0,1),rotate_angle))
					another_obj.Label = "Ring_001"
					rotate_angle = rotate_angle + 15
					print(name)
					print(rotate_angle)
				doc.recompute()
		
		
			def bt_add_segments_click(self):
				doc = FreeCAD.ActiveDocument
				print("Adding Segments")
				self.update_values()
				#fudge = 6.35
				#wall_thickness = 18
				selection = FreeCADGui.Selection.getSelection()
				if not selection:
					print("Error: No object selected. Please select a sketch.")
					return
				selected_obj = selection[0]
				sketch = selected_obj
				point_count = 0
				list_of_points = []
				self.list_of_segment_names = []  
				for i, geo in enumerate(sketch.Geometry):
					# Check if the geometry is a point
					if geo.TypeId == 'Part::GeomPoint':
						point_count += 1
						list_of_points.append(FreeCAD.Vector(geo.X, geo.Y, geo.Z))
						#print(geo.X)
				triple_list = []
				max_x =0
				min_x =0
				if False:
					for b in range(len(list_of_points)):
						if (b<len(list_of_points)-2): # Not the last point
							bottom = list_of_points[b].x
							top = list_of_points[b+1].x
							max_x = max(bottom, top, list_of_points[b+2].x)
							min_x = min(bottom, top)
							triple_list.append((max_x, min_x, list_of_points[b+1].x))
						elif (b<len(list_of_points)-1): # Second to last point
							bottom = list_of_points[b].x
							top = list_of_points[b+1].x
							max_x = max(bottom, top)
							min_x = min(bottom, top)
							triple_list.append((max_x, min_x, top))
						else: # Last point
							bottom = list_of_points[b].x
							top = list_of_points[b].x
							max_x = max(bottom, top)
							min_x = min(bottom, top)
							triple_list.append((max_x, min_x, max_x))

						seg_length = max_x - min_x - self.fudge


						if (b==0):
							#a_name = self.make_segment(num_segments=self.bowl_num_segments, radius=max_x+self.fudge, trapezoid_height=self.wall_thickness+(2*self.fudge), z_level=list_of_points[b].y, extrude_height=list_of_points[1].y, solid_bottom=True)
							a_name = self.make_segment(num_segments=self.bowl_num_segments, radius=max_x+self.fudge, trapezoid_height=seg_length, z_level=list_of_points[b].y, extrude_height=list_of_points[1].y, solid_bottom=True)
						else:
							a_name = self.make_segment(num_segments=self.bowl_num_segments, radius=max_x+self.fudge, trapezoid_height=self.wall_thickness+(2*self.fudge), z_level=list_of_points[b].y, extrude_height=list_of_points[b].y-list_of_points[b-1].y, solid_bottom=False)
							#a_name = self.make_segment(num_segments=self.bowl_num_segments, radius=max_x+self.fudge, trapezoid_height=seg_length, z_level=list_of_points[b].y, extrude_height=list_of_points[b].y-list_of_points[b-1].y, solid_bottom=False)
						obj = doc.getObject(a_name)
						obj.ViewObject.Transparency = 45
						obj.Placement = FreeCAD.Placement(FreeCAD.Vector(0,0,0),FreeCAD.Rotation(FreeCAD.Vector(0,0,1),-90))
						self.list_of_segment_names.append(a_name)

				if True:
					for b in range(len(list_of_points)-1):
						l = list_of_points[b].x-self.wall_thickness
						m = list_of_points[b].x
						n = list_of_points[b+1].x-self.wall_thickness
						o = list_of_points[b+1].x
						print(f"b={b} l={l} m={m} n={n} o={o}")
						max_x = max(l, m, n, o)
						min_x = min(l, m, n, o)
						seg_length = max_x - min_x

						a_name = self.make_segment(num_segments=self.number_of_segments, radius=max_x+self.fudge, trapezoid_height=seg_length+(2*self.fudge), z_level=list_of_points[b].y, extrude_height=list_of_points[b+1].y-list_of_points[b].y, solid_bottom=False)

						obj = doc.getObject(a_name)
						obj.ViewObject.Transparency = 45
						obj.Placement = FreeCAD.Placement(FreeCAD.Vector(0,0,0),FreeCAD.Rotation(FreeCAD.Vector(0,0,1),-90))
						self.list_of_segment_names.append(a_name)
			
			def bt_array_segments_click(self):
				doc = FreeCAD.ActiveDocument
				print("Arraying Segments Around Ring")
				self.update_values()
				import FreeCAD as App
				for obj in FreeCAD.ActiveDocument.Objects:
					if "Intersect" in obj.Label:
						print(obj.Name)
						
						for i in range(1, self.number_of_segments):
							obj.Label = f"Ring_001_Segment_{i:02d}"
							angle = i * (360 / self.number_of_segments)
							another_obj = App.ActiveDocument.copyObject(obj, True)
							another_obj.Placement = App.Placement(App.Vector(0,0,0),App.Rotation(App.Vector(0,0,1),angle))
							another_obj.Label = f"Ring_001_Segment_{i:02d}"

				doc.recompute()


			def bt_delete_segments_click(self):
				
				print("Deleting Segments")
				if FreeCAD.ActiveDocument:
					print("Objects in the active document:")
					for obj in FreeCAD.ActiveDocument.Objects:
						print(f"Name: {obj.Name}, Label: {obj.Label}")
						if "Segment" in obj.Name:
							FreeCAD.ActiveDocument.removeObject(obj.Name)
					else:
						print("No active document found.")
			def bt_delete_bowl_outlines_click(self):
				
				print("Deleting Bowl Outlines")
				if FreeCAD.ActiveDocument:
					print("Objects in the active document:")
					for obj in FreeCAD.ActiveDocument.Objects:
						print(f"Name: {obj.Name}, Label: {obj.Label}")
						if "Bowl_Outline" in obj.Label:
							FreeCAD.ActiveDocument.removeObject(obj.Name)
					else:
						print("No active document found.")
			def on_cancel(self):
				"""Cancel and close the task panel"""
				FreeCADGui.Control.closeDialog()
		
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
			panel = AddSegmentsTaskPanel()
	
			# Show the task panel in FreeCAD
			FreeCADGui.Control.showDialog(panel)


		except Exception as e:
			FreeCAD.Console.PrintError(f"Error adding segments: {str(e)}\n")
