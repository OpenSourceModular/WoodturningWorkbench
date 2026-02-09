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

import math
from pydoc import doc
from sys import prefix
from unicodedata import name
import FreeCAD as App
import FreeCADGui as Gui
from FreeCAD import Vector
from math import cos, sin, pi, radians, tan
import PySide.QtGui
import PySide.QtCore
import PySide.QtWidgets
import Part
import Draft
from BOPTools import BOPFeatures

from varsetOps import getVarsetValue, setVarsetValue, getVarsetInt

class AddSegments:
    
    def GetResources(self):
        """Return the command resources"""
        from pathlib import Path
        import FreeCAD
        return {
            'Pixmap': str(Path(FreeCAD.getUserAppDataDir()) / "Mod" / "WoodturningWorkbench" / "icons" / "AddSegments.svg"),
            'MenuText': 'Add Segments',
            'ToolTip': 'Add a segments to the document'
        }

    def IsActive(self):
        """Check if the command is active"""
        return App.ActiveDocument is not None

    def Activated(self):
        """Execute the command"""
        class AddSegmentsTaskPanel:
            #Creates the Task Panel
            def __init__(self):
                
                from PySide import QtGui, QtCore, QtWidgets	

                doc = App.activeDocument()
                self.varset = doc.getObject("BowlVariables")
                prop_names = self.varset.PropertiesList
                print(f"Property Names: {prop_names}")

                self.form = QtWidgets.QWidget()
                self.form.setWindowTitle("Add Segments to Bowl")
                #Local Variables with Default Values
                self.number_of_segments = getVarsetInt(self, "NumSegments")  # Number of segments around the bowl
                self.bowl_height = getVarsetValue(self, "BowlHeight")  # Bowl height in mm
                self.bowl_radius = getVarsetValue(self, "BowlRadius")  # Bowl radius in mm
                self.layer_height = getVarsetValue(self, "LayerHeight")  # Layer height in mm
                self.fudge = 4  # Fudge factor in mm
                self.wall_thickness = getVarsetValue(self, "WallThickness")  # Wall thickness in mm
                self.list_of_segment_names = []
                self.rotation_per_ring = getVarsetValue(self, "RotateAngle")  # Rotation per ring in degrees
                self.solid_bottom = True
                self.list_of_segment_parameters = []

                        # Create layout
                layout = QtWidgets.QVBoxLayout()
                
                # Title
                title_label = QtWidgets.QLabel("Bowl Segment Parameters")
                title_font = title_label.font()
                title_font.setPointSize(12)
                title_font.setBold(True)
                title_label.setFont(title_font)
                layout.addWidget(title_label)

                text_box1_layout = QtWidgets.QHBoxLayout()
                num_segments_label = QtWidgets.QLabel("# of Segments:")
                self.num_segments_input = QtWidgets.QLineEdit()
                self.num_segments_input.setText(str(self.number_of_segments))
                self.fudge_input = QtWidgets.QLineEdit()
                self.fudge_input.setText(str(self.fudge))
                
                wall_thickness_label = QtWidgets.QLabel("Wall Thickness:")
                self.wall_thickness_input = QtWidgets.QLineEdit()
                self.wall_thickness_input.setText(str(self.wall_thickness))
                text_box1_layout.addWidget(num_segments_label)
                text_box1_layout.addWidget(self.num_segments_input)
                text_box1_layout.addWidget(wall_thickness_label)
                text_box1_layout.addWidget(self.wall_thickness_input)
                layout.addLayout(text_box1_layout)

                text_box2_layout = QtWidgets.QHBoxLayout()

                text_box2_layout.addWidget(QtWidgets.QLabel("Fudge Factor:"))
                text_box2_layout.addWidget(self.fudge_input)
                layout.addLayout(text_box2_layout)

                self.solid_bottom_radio = QtGui.QRadioButton("Solid Bottom")
                layout.addWidget(self.solid_bottom_radio)
                self.solid_bottom_radio.setChecked(True)
                
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

                button_layout2 = QtWidgets.QHBoxLayout()
                # Add Segments button
                self.add_segments_button = QtWidgets.QPushButton("Add Segments")
                self.add_segments_button.clicked.connect(self.bt_add_segments_click)
                button_layout2.addWidget(self.add_segments_button)

                # Delete Segments button
                self.delete_segments_button = QtWidgets.QPushButton("Delete Segments")
                self.delete_segments_button.clicked.connect(self.bt_delete_segments_click)
                button_layout2.addWidget(self.delete_segments_button)

                button_layout3 = QtWidgets.QHBoxLayout()
                # Add Bowl Solid button
                self.add_bowl_solid_button = QtWidgets.QPushButton("Add Bowl Solid")
                self.add_bowl_solid_button.clicked.connect(self.bt_add_bowl_solid_click)
                button_layout3.addWidget(self.add_bowl_solid_button)

                # Delete Bowl Solid button
                self.delete_bowl_solid_button = QtWidgets.QPushButton("Delete Bowl Solid")
                self.delete_bowl_solid_button.clicked.connect(self.bt_delete_bowl_solid_click)
                button_layout3.addWidget(self.delete_bowl_solid_button)
              
                button_layout4 = QtWidgets.QHBoxLayout()
                self.intersect_segments_button = QtWidgets.QPushButton("Intersect Segments")
                self.intersect_segments_button.clicked.connect(self.bt_intersect_segments_click)
                button_layout4.addWidget(self.intersect_segments_button)

                self.delete_intersects_button = QtWidgets.QPushButton("Delete Intersect Segments")
                self.delete_intersects_button.clicked.connect(self.bt_delete_intersects_click)
                button_layout4.addWidget(self.delete_intersects_button)

                button_layout5 = QtWidgets.QHBoxLayout()    
                # Array segments around ring button
                self.array_segments_button = QtWidgets.QPushButton("Make Rings")
                self.array_segments_button.clicked.connect(self.bt_array_segments_click)
                button_layout5.addWidget(self.array_segments_button)

                self.array_segments_button = QtWidgets.QPushButton("Delete Arrayed Segments")
                self.array_segments_button.clicked.connect(self.bt_delete_arrayed_segments_click)
                button_layout5.addWidget(self.array_segments_button) 

                text_box3_layout = QtWidgets.QHBoxLayout()
                text_box3_layout.addWidget(QtWidgets.QLabel("Rotation Per Ring:"))
                self.rotation_input = QtWidgets.QLineEdit()
                self.rotation_input.setText(str(self.rotation_per_ring))
                text_box3_layout.addWidget(self.rotation_input)

                button_layout6 = QtWidgets.QHBoxLayout()
                self.rotate_rings_button = QtWidgets.QPushButton("Rotate Rings")
                self.rotate_rings_button.clicked.connect(self.bt_rotate_rings_click)
                button_layout6.addWidget(self.rotate_rings_button)



                button_layout10 = QtWidgets.QHBoxLayout()	
                # Cancel button
                self.cancel_button = QtWidgets.QPushButton("Close")
                self.cancel_button.clicked.connect(self.on_cancel)
                button_layout10.addWidget(self.cancel_button)

                button_layout7 = QtWidgets.QHBoxLayout()
                self.expand_inner_radius_button = QtWidgets.QPushButton("Expand Inner")
                self.expand_inner_radius_button.clicked.connect(self.expand_inner_radius)
                button_layout7.addWidget(self.expand_inner_radius_button)

                
                self.expand_outer_radius_button = QtWidgets.QPushButton("Expand Outer")
                self.expand_outer_radius_button.clicked.connect(self.expand_outer_radius)
                button_layout7.addWidget(self.expand_outer_radius_button)

                button_layout8  = QtWidgets.QHBoxLayout()
                self.decrease_inner_radius_button = QtWidgets.QPushButton("Decrease Inner")
                self.decrease_inner_radius_button.clicked.connect(self.decrease_inner_radius)
                button_layout8.addWidget(self.decrease_inner_radius_button)

                self.decrease_outer_radius_button = QtWidgets.QPushButton("Decrease Outer")
                self.decrease_outer_radius_button.clicked.connect(self.decrease_outer_radius)
                button_layout8.addWidget(self.decrease_outer_radius_button)

                button_layout9 = QtWidgets.QHBoxLayout()
                self.fudge_spinbox = QtWidgets.QSpinBox()
                self.fudge_spinbox.setRange(1, 10)
                self.fudge_spinbox.setSingleStep(1)
                self.fudge_spinbox.setValue(1)
                button_layout9.addWidget(QtWidgets.QLabel("Fudge Adjust:"))
                button_layout9.addWidget(self.fudge_spinbox)
                fudge_group = QtWidgets.QGroupBox("Individual Segment Adjustment")
                
                sub_fudge_layout = QtWidgets.QVBoxLayout()
                sub_fudge_layout.addWidget(QtWidgets.QLabel("Select one segment to adjust."))
                sub_fudge_layout.addLayout(button_layout7)
                sub_fudge_layout.addLayout(button_layout8)
                sub_fudge_layout.addLayout(button_layout9)
                fudge_group.setLayout(sub_fudge_layout)
                
                layout.addLayout(button_layout)
                layout.addLayout(button_layout2)
                layout.addLayout(button_layout3)
                layout.addLayout(button_layout4)
                layout.addLayout(button_layout5)
                layout.addLayout(text_box3_layout)                                    
                layout.addLayout(button_layout6)
                layout.addLayout(button_layout7)
                layout.addWidget(fudge_group)    
                layout.addLayout(button_layout10)
                
                # Add stretch at end
                layout.addStretch()
                
                self.form.setLayout(layout)

            def expand_inner_radius(self):
                self.bt_edit_segment_click(radius_type="inner", direcion="expand")

            def expand_outer_radius(self):
                self.bt_edit_segment_click(radius_type="outer", direcion="expand")

            def decrease_inner_radius(self):
                self.bt_edit_segment_click(radius_type="inner", direcion="decrease")

            def decrease_outer_radius(self):
                self.bt_edit_segment_click(radius_type="outer", direcion="decrease")

            def bt_edit_segment_click(self, radius_type="inner", direcion="decrease"):
                #print(radius)
                fudge_adjust = self.fudge_spinbox.value()
                print("Edit Segment Parameters")
                import FreeCAD
                import FreeCADGui
                doc = FreeCAD.ActiveDocument
                selected_objects = FreeCADGui.Selection.getSelection()
                try:
                    selected_segment = selected_objects[0]
                except IndexError:
                    self.show_error_popup("Selection Error", "No segment selected. Please select one segment to adjust.")
                    return
                seg_name = selected_segment.Label
                seg_number = int(seg_name.split("_")[1])
                print(f"Selected segment number: {seg_number}")
                print(f"Current parameters: {self.list_of_segment_parameters[seg_number]}")
                

                print(f"New parameters: {self.list_of_segment_parameters[seg_number]}")
                num_segments = self.list_of_segment_parameters[seg_number][0]
                radius= self.list_of_segment_parameters[seg_number][1]
                trapezoid_height = self.list_of_segment_parameters[seg_number][2]
                z_level = self.list_of_segment_parameters[seg_number][3]
                extrude_height = self.list_of_segment_parameters[seg_number][4]
                if radius_type == "outer":
                    if direcion == "expand":
                        new_radius = self.list_of_segment_parameters[seg_number][1] + fudge_adjust
                        new_trapezoid_height = self.list_of_segment_parameters[seg_number][2] + fudge_adjust
                    else:
                        new_radius = self.list_of_segment_parameters[seg_number][1] - fudge_adjust
                        new_trapezoid_height = self.list_of_segment_parameters[seg_number][2] - fudge_adjust
                    self.list_of_segment_parameters[seg_number][1] = new_radius
                    self.list_of_segment_parameters[seg_number][2] = new_trapezoid_height
                else:
                    if direcion == "expand":
                        new_trapezoid_height = self.list_of_segment_parameters[seg_number][2] + (2 * fudge_adjust)
                    else:
                        new_trapezoid_height = self.list_of_segment_parameters[seg_number][2] - (2 * fudge_adjust)
                    self.list_of_segment_parameters[seg_number][2] = new_trapezoid_height



                doc.removeObject(selected_segment.Name)
                new_segment = self.make_segment(*self.list_of_segment_parameters[seg_number])
                print(new_segment)
                
                obj = doc.getObject(new_segment)
                obj.ViewObject.Transparency = 45
                obj.Placement = App.Placement(App.Vector(0,0,0),App.Rotation(App.Vector(0,0,1),-90))   
                obj.Label = seg_name
                FreeCADGui.Selection.addSelection(obj)            

            def set_tooltips(self):
                self.bowl_numSegmentsBox.setToolTip("Number of segments around the bowl")
                self.bowl_layer_heightBox.setToolTip("Height of each layer in mm")
                self.bt_add_segments.setToolTip("Add segments to the bowl")	
                self.bt_delete_segments.setToolTip("Delete all segments created by this macro")

            def show_error_popup(self, title, message):
                from PySide import QtWidgets
                # Get the main FreeCAD window
                mw = Gui.getMainWindow()
                # Create and show the message box
                QtWidgets.QMessageBox.critical(mw, title, message)

            def update_values(self):
                #Update the local variables with the values in the text boxes
                self.bowl_num_segments = int(self.num_segments_input.text())
                setVarsetValue(self, "NumSegments", self.bowl_num_segments)
                self.fudge = float(self.fudge_input.text())
                self.wall_thickness = float(self.wall_thickness_input.text())
                setVarsetValue(self, "WallThickness", self.wall_thickness)
                self.rotation_per_ring = float(self.rotation_input.text())
                setVarsetValue(self, "RotateAngle", self.rotation_per_ring)
                
                if self.solid_bottom_radio.isChecked():
                    self.solid_bottom = True
                else:
                    self.solid_bottom = False

            def bt_delete_arrayed_segments_click(self):
                doc = App.ActiveDocument
                print("Deleting Arrayed Segments")
                for obj in doc.Objects:
                    if "Ring_" in obj.Label:
                        print(obj.Name)
                        doc.removeObject(obj.Name)
                for obj in doc.Objects:
                    if "Segment" in obj.Label:
                        print(obj.Name)
                        obj.Visibility = True
                doc.recompute()

            def bt_delete_intersects_click(self):
                doc = App.ActiveDocument
                print("Deleting Intersected Segments")
                for obj in doc.Objects:
                    if "Intersect" in obj.Label:
                        print(obj.Name)
                        doc.removeObject(obj.Name)
                doc.recompute()
                for obj in doc.Objects:
                    if "Segment" in obj.Label:
                        obj.Visibility = True

            def bt_rotate_rings_click(self):
                self.update_values()
                doc = App.ActiveDocument
                #Ring_001_001
                print("Rotating Rings")
                list_of_rings = []
                prefix = "Ring_"
                for obj in doc.Objects:
                    if obj.Label.startswith(prefix):
                        # Check if the object's label starts with the specified prefix
                        left_char = obj.Label[:9]
                        if left_char not in list_of_rings:
                            list_of_rings.append(left_char)
                print (list_of_rings)
                list_of_rings.sort()
                starting_angle = 0
                ring_num = 0
                for ring_name in list_of_rings:
                    print(ring_name)
                    for obj in doc.Objects:
                        if obj.Label.startswith(ring_name):
                            if obj.Label.endswith("001"):
                                print(self.rotation_per_ring*ring_num)
                            obj = doc.getObject(obj.Name)
                            incremental_rotation = App.Placement(App.Vector(0,0,0), App.Vector(0,0,1), self.rotation_per_ring*ring_num).Rotation
                            obj.Placement = App.Placement(obj.Placement.Base, incremental_rotation.multiply(obj.Placement.Rotation))
                    starting_angle = starting_angle - self.rotation_per_ring
                    ring_num = ring_num + 1
            
            def	bt_add_bowl_solid_click(self):
                print("Adding Bowl Solid")
                #import FreeCAD as App
                #import FreeCADGui as Gui    
                self.update_values()
                """Create a BSpline from all point geometries in the selected sketch."""
                doc = App.activeDocument()

                try:
                    sketch = doc.getObjectsByLabel("BowlProfileSketch")[0]
                except:
                    self.show_error_popup("Missing Sketch", "A sketch named 'BowlProfileSketch' was not found in the document. Please run the Add Construction Lines command first.")
                    return


                # Collect point geometries
                poles = []
                list_of_points = []
                self.list_of_segment_names = []  
                for i, geo in enumerate(sketch.Geometry):
                    # Check if the geometry is a point
                    if geo.TypeId == 'Part::GeomPoint':
                        #point_count += 1
                        list_of_points.append(App.Vector(geo.X, geo.Y, geo.Z))
                        print(geo.Y)
                list_of_points.sort(key=lambda v: v.y)
                for item in list_of_points:
                    poles.append(item)

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
                bs_obj.Label = obj_name
                bs_obj.Shape = shape

                # Try to align placement with the sketch
                try:
                    if hasattr(sketch, 'Placement'):
                        bs_obj.Placement = sketch.Placement
                except Exception:
                    pass

                # Create lines from each end of the BSpline to x = 0 (same y,z)
                try:
                    # shape.Vertexes[0] and [-1] correspond to the start and end vertices of the edge
                    start_pt = shape.Vertexes[0].Point
                    end_pt = shape.Vertexes[-1].Point

                    target_start = Vector(0, start_pt.y, start_pt.z)
                    target_end = Vector(0, end_pt.y, end_pt.z)

                    edge1 = Part.makeLine(start_pt, target_start)
                    edge2 = Part.makeLine(end_pt, target_end)

                    line1 = doc.addObject("Part::Feature", obj_name + "_endline1")
                    line1.Label = obj_name + "_endline1"
                    line1.Shape = edge1
                    # match placement so the lines align with the sketch/BSpline
                    try:
                        if hasattr(sketch, 'Placement'):
                            line1.Placement = sketch.Placement
                    except Exception:
                        pass

                    line2 = doc.addObject("Part::Feature", obj_name + "_endline2")
                    line2.Label = obj_name + "_endline2"
                    line2.Shape = edge2
                    try:
                        if hasattr(sketch, 'Placement'):
                            line2.Placement = sketch.Placement
                    except Exception:
                        pass
                except Exception as e:
                    print(f"Warning: failed to create end lines: {e}")
                a_compound = doc.addObject("Part::Compound","Compound")
                doc.Compound.Links = [bs_obj,line1,line2]

                a_revolve = doc.addObject("Part::Revolution","Revolve")
                doc.Revolve.Source = a_compound
                doc.Revolve.Axis = (0.0,0.0,1.0)
                doc.Revolve.Angle = 360.0
                doc.Revolve.Solid = False
                doc.Revolve.AxisLink = None
                doc.Revolve.Symmetric = False
                doc.Compound.Visibility = False

                # Ensure the document is up-to-date so the revolve has a computed shape
                try:
                    doc.recompute()
                except Exception:
                    pass

                

                # Convert the revolve to a solid and hide the original revolve
                try:
                    if not hasattr(a_revolve, 'Shape') or a_revolve.Shape is None:
                        raise ValueError("Revolve has no shape. Recompute may have failed or source is invalid.")
                    faces = a_revolve.Shape.Faces
                    if not faces:
                        raise ValueError("Revolve shape contains no faces; cannot build shell.")
                    shell = Part.Shell(faces)
                    solid = Part.Solid(shell)
                    solid_obj = doc.addObject("Part::Feature", a_revolve.Name + "_solid")
                    solid_obj.Label = a_revolve.Name + " (Solid)"
                    solid_obj.Shape = solid
                    try:
                        doc.recompute()
                        a_revolve.Visibility = False
                        doc.removeObject(a_revolve.Name)
                        doc.removeObject("Compound")
                        for obj in doc.Objects:
                            if obj.Name.startswith("BSpline_from_"):
                                doc.removeObject(obj.Name)
                    except:
                        print("Could not remove revolve object after solid conversion.")
                except Exception as e:
                    print(f"Warning: failed to convert revolve to solid: {e}")
                a_shape = solid_obj.Shape
                faces_list = a_shape.Faces
                print(f"Revolve solid has {len(faces_list)} faces.")
                a_face = faces_list[0]
                highest_face = -1.0
                for i, face in enumerate(faces_list):
                    print(f"Face {i}: Type = {face.ShapeType}, Area = {face.Area}")
                    print(f"Bounding Box: {face.BoundBox.Center.z}")
                    z_height = face.BoundBox.Center.z
                    if (z_height > highest_face):
                        highest_face = z_height
                        a_face = face
                        print(f" New highest face: {i} at Z={z_height}")
                print(a_face)
                a_thickness = doc.addObject("Part::Thickness","BowlSolid")
                doc.BowlSolid.Faces = (solid_obj,['Face3',])
                doc.BowlSolid.Value = -self.wall_thickness
                solid_obj.Visibility = False
                a_thickness.Placement = App.Placement(App.Vector(0,0,0),App.Rotation(App.Vector(0,0,1),90))
                a_thickness.ViewObject.Transparency = 50

                doc.recompute()				

            def	bt_delete_bowl_solid_click(self):
                print("Deleting Bowl Solid")
                doc = App.ActiveDocument
                if doc:
                    for obj in doc.Objects:
                        if "BowlSolid"  in obj.Name:
                            doc.removeObject(obj.Name)
                    for obj in doc.Objects:
                        if "Revolve"  in obj.Name:
                            doc.removeObject(obj.Name)

            def	bt_intersect_segments_click(self):
                
                doc = App.ActiveDocument		
                print("Intersecting Segments")
                bowl_solid_objs = []
                for obj in doc.Objects:
                    if "BowlSolid" in obj.Name:
                        bowl_solid_objs.append(obj)
                
                if len(bowl_solid_objs)==0:
                    self.show_error_popup("Missing Bowl Solid", "This command requires a Bowl Solid. Please click the Make Bowl Solid button first.")
                    return
                if len(bowl_solid_objs)>1:
                    print("Multiple BowlSolid objects found. Using the first one.")
                bowl_solid = bowl_solid_objs[0]

                segment_objs = []
                for obj in doc.Objects:
                    if "Segment" in obj.Label:
                        segment_objs.append(obj.Label)
                segment_objs.sort()
                print(f"Found segment objects: {segment_objs}")
                
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
                    seg_object = doc.getObjectsByLabel(segment_objs[a])[0]
                    
                    new_common = bp.make_multi_common([seg_object.Name] + [bowl_clones[a].Name])
                    #new_common.Label = f"Intersection_{a+1:03d}"
                    intersection_list.append(new_common.Name)
                doc.recompute()
                for a in range(0,len(intersection_list)):
                    print("Making solid:", intersection_list[a])
                    p= doc.getObject(intersection_list[a]).Shape.Faces
                    p = Part.Solid(Part.Shell(p))
                    o = doc.addObject("Part::Feature","Common013_solid")
                    o.Label="Intersect(Solid)_001"
                    o.Shape=p
                    del p, o 
                doc.recompute()

                for obj in doc.Objects:
                    if "Common"in obj.Label or "BowlSolid0" in obj.Label:
                        doc.removeObject(obj.Name)

                doc.recompute()

            def bt_add_bowl_outlines_click(self):
                print("Adding Bowl Outlines")
                self.update_values()
                """Create a BSpline from all point geometries in the selected sketch."""
                doc = App.activeDocument()

                try:
                    sketch = doc.getObjectsByLabel("BowlProfileSketch")[0]
                except:
                    self.show_error_popup("Missing Sketch", "A sketch named 'BowlProfileSketch' was not found in the document. Please run the Add Construction Lines command first.")
                    return
                
                '''
                list_of_points = []
                for i, geo in enumerate(sketch.Geometry):
                    # Check if the geometry is a point
                    if geo.TypeId == 'Part::GeomPoint':
                        #point_count += 1
                        list_of_points.append(App.Vector(geo.X, geo.Y, geo.Z))
                        print(geo.Y)

                if not list_of_points:
                    print(f"No point geometries found in sketch '{sketch.Name}'.")
                    return

                if len(list_of_points) < 2:
                    print("Need at least 2 points to create a BSpline.")
                    return
                '''
                                # Collect point geometries
                poles = []
                list_of_points = []
                self.list_of_segment_names = []  
                for i, geo in enumerate(sketch.Geometry):
                    # Check if the geometry is a point
                    if geo.TypeId == 'Part::GeomPoint':
                        #point_count += 1
                        list_of_points.append(App.Vector(geo.X, geo.Y, geo.Z))
                        print(geo.Y)
                list_of_points.sort(key=lambda v: v.y)
                for item in list_of_points:
                    poles.append(item)

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
                new_copy.Placement = App.Placement(App.Vector(-self.wall_thickness,0,0),App.Rotation(App.Vector(1,0,0),90))
                doc.recompute()
                # Try to align placement with the sketch
                try:
                    if hasattr(sketch, 'Placement'):
                        bs_obj.Placement = sketch.Placement
                except Exception:
                    pass
            
            def make_segment(self, num_segments=12, radius=50, trapezoid_height=19.05, z_level=0,extrude_height=10, solid_bottom=True):
                from math import cos, sin, pi, radians, tan
                self.update_values
                doc = App.ActiveDocument
                angle = 180 / self.bowl_num_segments

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
                    App.Vector(left_bottom, y_bottom, z_level),
                    App.Vector(right_bottom, y_bottom, z_level),
                    App.Vector(right_top, y_top, z_level),
                    App.Vector(left_top, y_top, z_level),
                    App.Vector(left_bottom, y_bottom, z_level)
                ]
                wire = Part.makePolygon(vertices)
                face = Part.Face(wire)
                shape = face.extrude(App.Vector(0, 0, extrude_height))

                obj = doc.addObject("Part::Feature", f"Segment_000")
                
                obj.Shape = shape
                return obj.Name
            
            '''def bt_rotate_segments_click(self):
                doc = App.ActiveDocument
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
            '''   
            def bt_add_segments_click(self):
                doc = App.ActiveDocument
                print("Adding Segments")
                self.update_values()
                
                try:
                    sketch = doc.getObjectsByLabel("BowlProfileSketch")[0]
                except:
                    self.show_error_popup("Missing Sketch", "A sketch named 'BowlProfileSketch' was not found in the document. Please run the Add Construction Lines command first.")
                    return
                point_count = 0
                list_of_points = []
                self.list_of_segment_names = []  
                for i, geo in enumerate(sketch.Geometry):
                    # Check if the geometry is a point
                    if geo.TypeId == 'Part::GeomPoint':
                        point_count += 1
                        list_of_points.append(App.Vector(geo.X, geo.Y, geo.Z))
                        print(geo.Y)
                list_of_points.sort(key=lambda v: v.y)
                triple_list = []
                max_x =0
                min_x =0
                
                for b in range(len(list_of_points)-1):
                    l = list_of_points[b].x-self.wall_thickness
                    m = list_of_points[b].x
                    n = list_of_points[b+1].x-self.wall_thickness
                    o = list_of_points[b+1].x
                    print(f"b={b} l={l} m={m} n={n} o={o}")
                    max_x = max(l, m, n, o)
                    min_x = min(l, m, n, o)
                    seg_length = max_x - min_x
                    if b==0 and self.solid_bottom:
                        self.list_of_segment_parameters.append([self.number_of_segments, max_x+self.fudge, max_x+self.fudge, list_of_points[b].y, list_of_points[b+1].y-list_of_points[b].y, False])
                        a_name = self.make_segment(num_segments=self.number_of_segments, radius=max_x+self.fudge, trapezoid_height=max_x+self.fudge, z_level=list_of_points[b].y, extrude_height=list_of_points[b+1].y-list_of_points[b].y, solid_bottom=False)    
                    else:
                        self.list_of_segment_parameters.append([self.number_of_segments, max_x+self.fudge, seg_length+(2*self.fudge), list_of_points[b].y, list_of_points[b+1].y-list_of_points[b].y, False])
                        a_name = self.make_segment(num_segments=self.number_of_segments, radius=max_x+self.fudge, trapezoid_height=seg_length+(2*self.fudge), z_level=list_of_points[b].y, extrude_height=list_of_points[b+1].y-list_of_points[b].y, solid_bottom=False)

                    obj = doc.getObject(a_name)
                    obj.ViewObject.Transparency = 45
                    obj.Placement = App.Placement(App.Vector(0,0,0),App.Rotation(App.Vector(0,0,1),-90))
                    self.list_of_segment_names.append(a_name)
                print(self.list_of_segment_parameters)
        
            def bt_array_segments_click(self):
                doc = App.ActiveDocument
                print("Arraying Segments Around Ring")
                self.update_values()
                ring_num = 1
                for obj in doc.Objects:
                    if "Intersect" in obj.Label:
                        an_obj = doc.getObject(obj.Name)
                        an_obj.Label =f"Ring_{ring_num:0{3}d}_001"						
                        for i in range(1, self.bowl_num_segments):
                            angle = i * (360 / self.bowl_num_segments)
                            another_obj = App.ActiveDocument.copyObject(an_obj, True)
                            another_obj.Placement = App.Placement(App.Vector(0,0,0),App.Rotation(App.Vector(0,0,1),angle))
                            another_obj.Label = f"Ring_{ring_num:0{3}d}_002"
                        ring_num += 1
                doc.recompute()

            def bt_delete_segments_click(self):
                
                print("Deleting Segments")
                if App.ActiveDocument:
                    print("Objects in the active document:")
                    for obj in App.ActiveDocument.Objects:
                        print(f"Name: {obj.Name}, Label: {obj.Label}")
                        if "Segment" in obj.Name:
                            App.ActiveDocument.removeObject(obj.Name)
                    else:
                        print("No active document found.")

            def bt_delete_bowl_outlines_click(self):
                
                print("Deleting Bowl Outlines")
                if App.ActiveDocument:
                    print("Objects in the active document:")
                    for obj in App.ActiveDocument.Objects:
                        print(f"Name: {obj.Name}, Label: {obj.Label}")
                        if "Bowl_Outline" in obj.Label:
                            App.ActiveDocument.removeObject(obj.Name)
                    else:
                        print("No active document found.")

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
            panel = AddSegmentsTaskPanel()
    
            # Show the task panel in FreeCAD
            Gui.Control.showDialog(panel)

        except Exception as e:
            App.Console.PrintError(f"Error adding segments: {str(e)}\n")
