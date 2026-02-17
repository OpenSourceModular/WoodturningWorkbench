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
from unicodedata import name
import FreeCAD as App
import FreeCADGui as Gui
from FreeCAD import Vector
from math import cos, sin, pi, radians, tan
try:
    from PySide import QtGui, QtCore, QtWidgets
except ImportError:
    import importlib
    QtGui = importlib.import_module("PySide2.QtGui")
    QtCore = importlib.import_module("PySide2.QtCore")
    QtWidgets = importlib.import_module("PySide2.QtWidgets")
import Part
import Draft
from BOPTools import BOPFeatures

class AddTorus:
    
    def GetResources(self):
        """Return the command resources"""
        from pathlib import Path
        return {
            'Pixmap': str(Path(App.getUserAppDataDir()) / "Mod" / "WoodturningWorkbench" / "icons" / "AddTorus.svg"),  
            'MenuText': 'AddTorus',
            'ToolTip': 'AddTorus Command'
        }

    def IsActive(self):
        """Check if the command is active"""
        return App.ActiveDocument is not None

    def Activated(self):
        """Execute the command"""
        class AddTorusPanel:
            #Creates the Task Panel
            def __init__(self):

                self.form = QtWidgets.QWidget()
                self.form.setWindowTitle("AddTorus")
                #Local Variables with Default Values
                self.num_segments_per_ring = 12
                self.torus_outside_radius = 200.0 
                self.torus_inside_radius = 100.0
                self.num_rings_per_torus = 16

                self.ring_diameter = (self.torus_outside_radius - self.torus_inside_radius)


                # Create layout
                layout = QtWidgets.QVBoxLayout()
                
                # Title
                title_label = QtWidgets.QLabel("AddTorus")
                title_font = title_label.font()
                title_font.setPointSize(12)
                title_font.setBold(True)
                title_label.setFont(title_font)
                layout.addWidget(title_label)

                text_box_layout = QtWidgets.QVBoxLayout()
                num_segments_per_ring_label = QtWidgets.QLabel("Number of Segments Per Ring:")
                self.num_segments_per_ring_input = QtWidgets.QLineEdit()
                self.num_segments_per_ring_input.setText(str(self.num_segments_per_ring))
                text_box_layout.addWidget(num_segments_per_ring_label)
                text_box_layout.addWidget(self.num_segments_per_ring_input)

                torus_outside_radius_label = QtWidgets.QLabel("Torus Outside Radius:")
                self.torus_outside_radius_input = QtWidgets.QLineEdit()
                self.torus_outside_radius_input.setText(str(self.torus_outside_radius))
                text_box_layout.addWidget(torus_outside_radius_label)
                text_box_layout.addWidget(self.torus_outside_radius_input)

                torus_inside_radius_label = QtWidgets.QLabel("Torus Inside Radius:")
                self.torus_inside_radius_input = QtWidgets.QLineEdit()
                self.torus_inside_radius_input.setText(str(self.torus_inside_radius))
                text_box_layout.addWidget(torus_inside_radius_label)
                text_box_layout.addWidget(self.torus_inside_radius_input)

                ring_diameter_label = QtWidgets.QLabel("Calculated Ring Diameter:")
                self.ring_diameter_input = QtWidgets.QLineEdit()
                self.ring_diameter_input.setReadOnly(True)
                self.ring_diameter_input.setText(str(self.ring_diameter))
                text_box_layout.addWidget(ring_diameter_label)
                text_box_layout.addWidget(self.ring_diameter_input)

                num_rings_per_torus_label = QtWidgets.QLabel("Number of Rings Per Torus:")
                self.num_rings_per_torus_input = QtWidgets.QLineEdit()
                self.num_rings_per_torus_input.setText(str(self.num_rings_per_torus))
                text_box_layout.addWidget(num_rings_per_torus_label)
                text_box_layout.addWidget(self.num_rings_per_torus_input)

                self.torus_outside_radius_input.textChanged.connect(self.on_torus_diameter_changed)
                self.torus_inside_radius_input.textChanged.connect(self.on_torus_diameter_changed)
 
                layout.addLayout(text_box_layout)

                # Add spacing
                layout.addSpacing(20)
                
                # Button layout
                button_layout = QtWidgets.QHBoxLayout()

                # Add button A
                self.button_A = QtWidgets.QPushButton("Button A")
                self.button_A.clicked.connect(self.bt_A_clicked)
                button_layout.addWidget(self.button_A)

                self.button_create_sketch = QtWidgets.QPushButton("Create Sketch")
                self.button_create_sketch.clicked.connect(self.on_create_sketch)
                button_layout.addWidget(self.button_create_sketch)

                button_layout2 = QtWidgets.QHBoxLayout()
                self.button_make_ring = QtWidgets.QPushButton("Make Ring")
                self.button_make_ring.clicked.connect(self.bt_make_ring)
                button_layout2.addWidget(self.button_make_ring)
                
                button_layout3 = QtWidgets.QHBoxLayout()
                self.button_make_extrude = QtWidgets.QPushButton("Make Extrude")
                self.button_make_extrude.clicked.connect(self.bt_make_extrude)
                button_layout3.addWidget(self.button_make_extrude)

                self.button_intersect_segments = QtWidgets.QPushButton("Intersect Extrude")
                self.button_intersect_segments.clicked.connect(lambda: self.bt_intersect_segments_click("Torus_Extrude_Solid","Segment"))
                button_layout3.addWidget(self.button_intersect_segments)

                self.button_intersect_segments = QtWidgets.QPushButton("Intersect Torus")
                self.button_intersect_segments.clicked.connect(lambda: self.bt_intersect_segments_click("Cut","Intersect"))
                button_layout3.addWidget(self.button_intersect_segments)

                self.button_array = QtWidgets.QPushButton("Array")
                self.button_array.clicked.connect(self.bt_array_segments_click)
                button_layout3.addWidget(self.button_array)


                # Add button A
                self.button_close = QtWidgets.QPushButton("Close")
                self.button_close.clicked.connect(self.on_cancel)
                button_layout2.addWidget(self.button_close)

                layout.addLayout(button_layout)
                layout.addLayout(button_layout2)
                layout.addLayout(button_layout3)
                # Add stretch at end
                layout.addStretch()
                self.form.setLayout(layout)

            def bt_A_clicked(self):
                """Handler for Button A click"""
                try:
                    self.update_values()
                    App.Console.PrintMessage("AddTorus values updated:\n")
                    App.Console.PrintMessage(f"  Number of Segments Per Ring: {self.num_segments_per_ring}\n")
                    App.Console.PrintMessage(f"  Torus Outside Diameter: {self.torus_outside_radius}\n")
                    App.Console.PrintMessage(f"  Torus Inside Diameter: {self.torus_inside_radius}\n")
                    App.Console.PrintMessage(f"  Number of Rings Per Torus: {self.num_rings_per_torus}\n")
                except ValueError:
                    App.Console.PrintError("Invalid input: enter numeric values in all AddTorus fields.\n")

            def on_create_sketch(self):
                try:
                    self.update_values()

                    if App.ActiveDocument is None:
                        App.Console.PrintError("No active document.\n")
                        return

                    doc = App.ActiveDocument
                    sketch = doc.getObject("Torus_Profile")
                    sketch2 = doc.getObject("Torus_Profile2")

                    if sketch is None:
                        sketch = doc.addObject("Sketcher::SketchObject", "Torus_Profile")
                    elif sketch.TypeId != "Sketcher::SketchObject":
                        App.Console.PrintError("An object named 'Torus_Profile' already exists and is not a sketch.\n")
                        return
                    if sketch2 is None:
                        sketch2 = doc.addObject("Sketcher::SketchObject", "Torus_Profile2") 
                    elif sketch2.TypeId != "Sketcher::SketchObject":
                        App.Console.PrintError("An object named 'Torus_Profile2' already exists and is not a sketch.\n")
                        return  
                    

                    sketch.Placement = App.Placement(App.Vector(0, 0, 0), App.Rotation(0, 0, 0))
                    sketch2.Placement = App.Placement(App.Vector(0, 0, 0), App.Rotation(0, 0, 0))

                    while len(sketch.Geometry) > 0:
                        sketch.delGeometry(len(sketch.Geometry) - 1)

                    center_x = self.torus_outside_radius - (self.ring_diameter / 2.0)
                    radius = self.ring_diameter / 2.0

                    circle = Part.Circle(App.Vector(center_x, 0, 0), App.Vector(0, 0, 1), radius)
                    circle2 = Part.Circle(App.Vector(center_x, 0, 0), App.Vector(0, 0, 1), radius-20)
                    sketch.addGeometry(circle, False)
                    sketch2.addGeometry(circle2, False)
                    sketch.Visibility = False
                    sketch2.Visibility = False

                    doc.recompute()
                    #Gui.Selection.clearSelection()
                    #Gui.Selection.addSelection(doc.Name, sketch.Name)

                    a_revolve = doc.addObject("Part::Revolution","Revolve")
                    doc.Revolve.Source = sketch
                    doc.Revolve.Axis = (0.0,1.0,0.0)
                    doc.Revolve.Angle = 360.0
                    doc.Revolve.Solid = True
                    doc.Revolve.AxisLink = None
                    doc.Revolve.Symmetric = False

                    a_revolve2 = doc.addObject("Part::Revolution","Revolve2")
                    doc.Revolve2.Source = sketch2
                    doc.Revolve2.Axis = (0.0,1.0,0.0)
                    doc.Revolve2.Angle = 360.0
                    doc.Revolve2.Solid = True
                    doc.Revolve2.AxisLink = None
                    doc.Revolve.Symmetric = False

                    doc.recompute()
                    from BOPTools import BOPFeatures
                    bp = BOPFeatures.BOPFeatures(App.activeDocument())
                    bp.make_cut(["Revolve", "Revolve2", ])
                    doc.recompute()

                    Gui.activeDocument().activeView().viewFront()
                    Gui.SendMsgToActiveView("ViewFit")
                     
                    #Gui.ActiveDocument.setEdit(sketch.Name)
                    App.Console.PrintMessage("Created sketch 'Torus_Profile' with torus profile circle.\n")

                except ValueError:
                    App.Console.PrintError("Invalid input: enter numeric values before creating sketch.\n")
                except Exception as e:
                    App.Console.PrintError(f"Error creating Torus_Profile sketch: {str(e)}\n")

            def	bt_intersect_segments_click(self, object_name, object2_name):
                
                doc = App.ActiveDocument		
                print("Intersecting Segments")
                bowl_solid_objs = []
                for obj in doc.Objects:
                    if object_name in obj.Name or object_name in obj.Label:
                        bowl_solid_objs.append(obj)
                
                if len(bowl_solid_objs)==0:
                    self.show_error_popup("Missing Bowl Solid", "This command requires a Bowl Solid. Please click the Make Bowl Solid button first.")
                    return
                if len(bowl_solid_objs)>1:
                    print("Multiple BowlSolid objects found. Using the first one.")
                bowl_solid = bowl_solid_objs[0]

                segment_objs = []
                for obj in doc.Objects:
                    if object2_name in obj.Label:
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
                if (object2_name == "Segment"):
                    prefix = "Intersect"
                else:
                    prefix = "Smooth"
                for a in range(0,len(intersection_list)):
                    print("Making solid:", intersection_list[a])
                    p= doc.getObject(intersection_list[a]).Shape.Faces
                    p = Part.Solid(Part.Shell(p))
                    o = doc.addObject("Part::Feature","Common013_solid")
                    
                    o.Label=f"{prefix}(Solid)_001"
                    o.Shape=p
                    del p, o 
                doc.recompute()

                for obj in doc.Objects:
                    if "Common"in obj.Label or "BowlSolid0" in obj.Label:
                        doc.removeObject(obj.Name)

                doc.recompute()

            def bt_array_segments_click(self):
                doc = App.ActiveDocument
                print("Arraying Segments Around Ring")
                self.update_values()
                ring_num = 1
                for obj in doc.Objects:
                    if "Smooth" in obj.Label:
                        an_obj = doc.getObject(obj.Name)
                        an_obj.Label =f"Ring_{ring_num:0{3}d}_001"						
                        for i in range(1, self.num_rings_per_torus):
                            angle = i * (360 / self.num_rings_per_torus)
                            another_obj = App.ActiveDocument.copyObject(an_obj, True)
                            another_obj.Placement = App.Placement(App.Vector(0,0,0),App.Rotation(App.Vector(0,1,0),angle))
                            another_obj.Label = f"Ring_{ring_num:0{3}d}_002"
                        ring_num += 1
                doc.recompute()

            def bt_make_extrude(self):
                try:
                    self.update_values()

                    if App.ActiveDocument is None:
                        App.Console.PrintError("No active document.\n")
                        return
                    if self.num_rings_per_torus == 0:
                        App.Console.PrintError("num_rings_per_torus cannot be zero.\n")
                        return

                    doc = App.ActiveDocument
                    sketch = doc.getObject("Torus_Extrude")

                    if sketch is None:
                        sketch = doc.addObject("Sketcher::SketchObject", "Torus_Extrude")
                    elif sketch.TypeId != "Sketcher::SketchObject":
                        App.Console.PrintError("An object named 'Torus_Extrude' already exists and is not a sketch.\n")
                        return

                    sketch.Placement = App.Placement(
                        App.Vector(0, 0, 0),
                        App.Rotation(App.Vector(1, 0, 0), 90)
                    )

                    while len(sketch.Geometry) > 0:
                        sketch.delGeometry(len(sketch.Geometry) - 1)

                    side_length = self.torus_outside_radius
                    angle = radians((360.0 / self.num_rings_per_torus))
                    base_x = side_length
                    base_height = side_length * sin(angle)

                    apex = App.Vector(0, 0, 0)
                    upper = App.Vector(base_x, base_height, 0)
                    lower = App.Vector(base_x, 0, 0)

                    sketch.addGeometry(Part.LineSegment(apex, upper), False)
                    sketch.addGeometry(Part.LineSegment(apex, lower), False)
                    sketch.addGeometry(Part.LineSegment(upper, lower), False)

                    torus_outside_diameter = self.torus_outside_radius * 2.0
                    torus_inside_diameter = self.torus_inside_radius * 2.0
                    extrude_length = torus_outside_diameter - torus_inside_diameter

                    extrusion = doc.getObject("Torus_Extrude_Solid")
                    if extrusion is None:
                        extrusion = doc.addObject("Part::Extrusion", "Torus_Extrude_Solid")
                    elif extrusion.TypeId != "Part::Extrusion":
                        App.Console.PrintError("An object named 'Torus_Extrude_Solid' already exists and is not an extrusion.\n")
                        return

                    extrusion.Base = sketch
                    extrusion.Dir = App.Vector(0, extrude_length, 0)
                    extrusion.Solid = True
                    extrusion.TaperAngle = 0
                    extrusion.Placement = App.Placement(
                        App.Vector(0, -extrude_length / 2.0, 0),
                        App.Rotation(0, 0, 0)
                    )

                    doc.recompute()
                    App.Console.PrintMessage("Created sketch 'Torus_Extrude' and symmetric Y-axis extrusion.\n")

                except ValueError:
                    App.Console.PrintError("Invalid input: enter numeric values before creating extrude sketch.\n")
                except Exception as e:
                    App.Console.PrintError(f"Error creating Torus_Extrude sketch: {str(e)}\n")

            def bt_make_ring(self):
                App.Console.PrintMessage("Making Ring\n")
                self.update_values()
                doc = App.ActiveDocument
                opposite_height = (self.torus_outside_radius) * sin(radians(360 / self.num_rings_per_torus))
                inside_length = (self.torus_inside_radius) * cos(radians(360 / self.num_rings_per_torus))

                print(f"Opposite Height: {opposite_height}\n")
                a_segment = self.make_segment(num_segments=self.num_segments_per_ring, radius=(self.ring_diameter/2.0)+self.torus_inside_radius-inside_length, trapezoid_height=20, z_level=0, extrude_height=opposite_height, solid_bottom=False)
                ring_center = self.torus_outside_radius - (self.ring_diameter / 2.0)
                an_obj = doc.getObject(a_segment)
                for i in range(1, self.num_segments_per_ring):
                    angle = i * (360 / self.num_segments_per_ring)
                    another_obj = App.ActiveDocument.copyObject(an_obj, True)
                    another_obj.Placement = App.Placement(App.Vector(0,0,0),App.Rotation(App.Vector(0,0,1),angle))
                    self.move_object(another_obj, x=ring_center)
                self.move_object(an_obj, x=ring_center)

                #doc.getObject(a_segment).Placement = App.Placement(App.Vector(0, 0, 0), App.Rotation(App.Vector(0, 0, 1), 90))
                #doc.getObject(a_segment).Placement = App.Placement(App.Vector(0, -self.torus_outside_radius/2.0, 0), App.Rotation(App.Vector(0, 0, 0), 0))  
                #another_obj.Placement = App.Placement(App.Vector(0,0,0),App.Rotation(App.Vector(0,0,1),angle))



            def make_segment(self, num_segments=12, radius=50, trapezoid_height=19.05, z_level=0,extrude_height=10, solid_bottom=True):
                from math import cos, sin, pi, radians, tan
                self.update_values
                doc = App.ActiveDocument
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

            def move_object(self, an_object, x):
                base = an_object.Placement.Base
                rotation = an_object.Placement.Rotation
                an_object.Placement = App.Placement(
                    App.Vector(base.x + x, base.y, base.z),
                    rotation
                )
            
            def set_tooltips(self):
                self.num_segments_per_ring_input.setToolTip("Number of segments per ring")
                self.torus_outside_radius_input.setToolTip("Outside diameter of the torus")
                self.torus_inside_radius_input.setToolTip("Inside diameter of the torus")
                self.ring_diameter_input.setToolTip("Calculated from outside and inside torus diameters")
                self.num_rings_per_torus_input.setToolTip("Number of rings per torus")

            def on_torus_diameter_changed(self):
                self.update_ring_diameter()

            def update_ring_diameter(self):
                try:
                    outside_diameter = float(self.torus_outside_radius_input.text())
                    inside_diameter = float(self.torus_inside_radius_input.text())
                    self.ring_diameter = outside_diameter - inside_diameter
                    self.ring_diameter_input.setText(str(self.ring_diameter))
                except ValueError:
                    self.ring_diameter_input.setText("")

            def update_values(self):
                #Update the local variables with the values in the text boxes
                self.num_segments_per_ring = int(self.num_segments_per_ring_input.text())
                self.torus_outside_radius = float(self.torus_outside_radius_input.text())
                self.torus_inside_radius = float(self.torus_inside_radius_input.text())
                self.ring_diameter = self.torus_outside_radius - self.torus_inside_radius
                self.ring_diameter_input.setText(str(self.ring_diameter))
                self.num_rings_per_torus = int(self.num_rings_per_torus_input.text())

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
            panel = AddTorusPanel()
    
            # Show the task panel in FreeCAD
            Gui.Control.showDialog(panel)

        except Exception as e:
            App.Console.PrintError(f"Error adding panel: {str(e)}\n")
