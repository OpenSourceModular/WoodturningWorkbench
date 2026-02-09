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
import PySide.QtGui
import PySide.QtCore
import PySide.QtWidgets
import Part
import Draft
from BOPTools import BOPFeatures

class BowlFromABoard:
    
    def GetResources(self):
        """Return the command resources"""
        from pathlib import Path
        return {
            'Pixmap': str(Path(App.getUserAppDataDir()) / "Mod" / "WoodturningWorkbench" / "icons" / "TaskPanelTemplate.svg"),  
            'MenuText': 'Bowl From A Board',
            'ToolTip': 'Bowl From A Board Command'
        }

    def IsActive(self):
        """Check if the command is active"""
        return App.ActiveDocument is not None

    def Activated(self):
        """Execute the command"""
        class BowlFromABoardPanel:
            #Creates the Task Panel
            def __init__(self):
                
                from PySide import QtGui, QtCore, QtWidgets	
                self.form = QtWidgets.QWidget()
                self.form.setWindowTitle("Bowl From A Board")
                #Local Variables with Default Values
                self.board_width = 304.8
                self.slice_thickness = 50.8
                self.slice_angle = 45
                self.bowl_height = 150
                self.base_ring_radius = 50.8
                self.ring_thickness = 20
                self.ring_width = 25.4
                self.clone_list = []
                self.number_of_rings = 6
                self.number_of_slices = 32

                # Create layout
                layout = QtWidgets.QVBoxLayout()
                
                # Title
                title_label = QtWidgets.QLabel("Bowl From A Board")
                title_font = title_label.font()
                title_font.setPointSize(12)
                title_font.setBold(True)
                title_label.setFont(title_font)
                layout.addWidget(title_label)

                board_width_label = QtWidgets.QLabel("Board Width:")
                self.board_width_input = QtWidgets.QLineEdit()
                self.board_width_input.setText(str(self.board_width))
                layout.addWidget(board_width_label)
                layout.addWidget(self.board_width_input)

                slice_thickness_label = QtWidgets.QLabel("Slice Thickness:")
                self.slice_thickness_input = QtWidgets.QLineEdit()
                self.slice_thickness_input.setText(str(self.slice_thickness))
                layout.addWidget(slice_thickness_label)
                layout.addWidget(self.slice_thickness_input)                
                # Add spacing
                layout.addSpacing(20)
                
                # Button layout
                button_layout = QtWidgets.QHBoxLayout()

                # Add button A
                self.button_A = QtWidgets.QPushButton("Button A")
                self.button_A.clicked.connect(self.bt_A_clicked)
                button_layout.addWidget(self.button_A)

                # Add button A
                self.button_close = QtWidgets.QPushButton("Close")
                self.button_close.clicked.connect(self.on_cancel)
                button_layout.addWidget(self.button_close)

                layout.addLayout(button_layout)
                # Add stretch at end
                layout.addStretch()
                self.form.setLayout(layout)

            def bt_A_clicked(self):
                """Handler for Button A click"""
                import FreeCAD as App
                self.update_values()
                doc = App.ActiveDocument
                App.Console.PrintMessage("Button A clicked\n")
                print(self.number_of_slices)
                self.make_ring(0, 0, self.ring_thickness, self.base_ring_radius, self.slice_angle, "bottom", "Ring0")
                for i in range(0,self.number_of_rings-2):
                    a_name = "Ring" + str(i+1)
                    self.make_ring(self.base_ring_radius+self.ring_width*i, self.ring_thickness*(i+1), self.ring_thickness, self.ring_width, self.slice_angle, "inner", a_name)
                a_name = "Ring" + str(i+2)
                self.make_ring(self.base_ring_radius+(self.ring_width*(i+1)), self.ring_thickness*(i+1)+self.ring_thickness, self.ring_thickness, self.ring_width, self.slice_angle, "top", a_name)

                #box_group = doc.addObject("App::DocumentObjectGroup", "boxes")
                bowl_width = (self.base_ring_radius+(self.ring_width*(self.number_of_rings)))*2
                bowl_height = (self.slice_thickness*self.number_of_rings)+(2*self.slice_thickness)
                box_list = []
                for p in range(0,self.number_of_rings):
                    for i in range(0,self.number_of_slices):
                        box = doc.addObject("Part::Box", "Box")
                        box.Length = bowl_width
                        slice_width = bowl_width / self.number_of_slices
                        #box.Width = slice_thickness
                        box.Width = slice_width
                        box.Height = bowl_height
                        shift = bowl_width/2

                        box.Placement = App.Placement(App.Vector(-(box.Length/2), -shift+(i*slice_width), 0), App.Rotation(0, 0, 0))
                        box_list.append(box.Name)
                        #box_group.addObject(box)
                if(True):
                    for a in range(0,len(self.clone_list)):
                        bp = BOPFeatures.BOPFeatures(App.activeDocument())
                        new_common = bp.make_multi_common([box_list[a]] + [self.clone_list[a]])
                        
                        x = App.ActiveDocument.getObject(self.clone_list[a])
                        aName = x.Label
                        aSplit = aName.split("_")[0]
                        new_common.Label = "C_" + aSplit + "_"
                        obj = App.ActiveDocument.getObject(new_common.Name)
                        
                        doc.recompute()
                        #print(type(new_common))
                        try:
                            obj = App.ActiveDocument.getObject(new_common.Name)
                            r_ = 118/256
                            g_ = 81/256
                            b_ = 68/256
                            obj.ViewObject.ShapeColor = (r_, g_, b_)
                            #print(obj.Shape.Volume)
                            if (obj.Shape.Volume < 0.1):
                                doc.removeObject(new_common.Name)
                                doc.removeObject(box_list[a])
                                doc.removeObject(self.clone_list[a])
                        except:
                            print("Failed to get object:", new_common.Name)         

            def set_tooltips(self):
                self.bowl_numSegmentsBox.setToolTip("Number of segments around the bowl")
                self.bowl_layer_heightBox.setToolTip("Height of each layer in mm")
                self.bt_add_segments.setToolTip("Add segments to the bowl")	
                self.bt_delete_segments.setToolTip("Delete all segments created by this macro")

            def update_values(self):
                #Update the local variables with the values in the text boxes
                self.board_width = float(self.board_width_input.text())
                self.slice_thickness = float(self.slice_thickness_input.text())
                

            def make_ring(self, inner_radius, start_height, ring_height, base_length, angle_deg, ring_type, ring_name):
                import Sketcher
                import FreeCAD
                pass
                print(self.number_of_slices)
                doc = FreeCAD.ActiveDocument
                # Create a new sketch on the XY plane
                sketch = doc.addObject('Sketcher::SketchObject', 'TrapezoidSketch')
                sketch.Placement = App.Placement(App.Vector(0, 0, 0), App.Rotation(App.Vector(1, 0, 0),90))

                angle_rad = math.radians(angle_deg)

                # Calculate points
                cos_angle = math.cos(angle_rad)
                sin_angle = math.sin(angle_rad)
                tan_angle = math.tan(angle_rad)

                if (ring_type == "inner"):
                    A = App.Vector(inner_radius, start_height, 0)  # Bottom left
                    B = App.Vector(inner_radius+base_length, start_height, 0)  # Bottom right
                    C = App.Vector(inner_radius+base_length + ring_height/tan_angle, start_height + ring_height, 0)  # Top right
                    D = App.Vector(inner_radius + ring_height/tan_angle, start_height + ring_height, 0)  # Top left
                if (ring_type == "bottom"):
                    A = App.Vector(0, 0, 0)  # Bottom left
                    B = App.Vector(base_length, 0, 0)  # Bottom right
                    C = App.Vector(base_length + ring_height/tan_angle, ring_height, 0)  # Top right
                    D = App.Vector(0, ring_height, 0)  # Top left
                if (ring_type == "top"):
                    A = App.Vector(inner_radius, start_height, 0)  # Bottom left
                    B = App.Vector(inner_radius+base_length, start_height, 0)  # Bottom right
                    C = App.Vector(inner_radius+base_length, start_height + ring_height, 0)  # Top right
                    D = App.Vector(inner_radius + ring_height/tan_angle, start_height + ring_height, 0)  # Top left

                # Add geometry: lines
                sketch.addGeometry(Part.LineSegment(A, B), False)  # Line 0: A to B
                sketch.addGeometry(Part.LineSegment(B, C), False)  # Line 1: B to C
                sketch.addGeometry(Part.LineSegment(C, D), False)  # Line 2: C to D
                sketch.addGeometry(Part.LineSegment(D, A), False)  # Line 3: D to A

                # Add constraints
                # Coincident constraints for connected points
                sketch.addConstraint(Sketcher.Constraint('Coincident', 0, 2, 1, 1))  # End of line 0 to start of line 1
                sketch.addConstraint(Sketcher.Constraint('Coincident', 1, 2, 2, 1))  # End of line 1 to start of line 2
                sketch.addConstraint(Sketcher.Constraint('Coincident', 2, 2, 3, 1))  # End of line 2 to start of line 3
                sketch.addConstraint(Sketcher.Constraint('Coincident', 3, 2, 0, 1))  # End of line 3 to start of line 0

                sketch.Visibility = False
                axis = FreeCAD.Vector(0, 0, 1)

                # Define the angle of revolution (360 degrees for full revolution)
                angle = 360

                # Create the revolve feature
                revolve = doc.addObject("Part::Revolution", ring_name)
                revolve.Source = sketch
                revolve.Axis = axis
                revolve.Angle = angle
                view_obj = doc.getObject(ring_name)
                view_obj.ViewObject.Transparency = 70
                view_obj.Visibility = False
                for i in range(0, self.number_of_slices):
                # Create a linked clone
                    cloned_object = Draft.clone(view_obj)
                    cloned_object.Label = ring_name + "_1"
                    self.clone_list.append(cloned_object.Name)

            
            if(False):
                for w in range(0,number_of_rings):
                    prefix = "C_Ring" + str(w) + "_"
                    for obj in doc.Objects:
                        # Check if the object's label starts with the specified prefix
                        if obj.Label.startswith(prefix):
                            incremental_rotation = App.Placement(App.Vector(0,0,0), App.Vector(0,0,1), 15*w).Rotation
                            obj.Placement = App.Placement(obj.Placement.Base, incremental_rotation.multiply(obj.Placement.Rotation))

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
            panel = BowlFromABoardPanel()
    
            # Show the task panel in FreeCAD
            Gui.Control.showDialog(panel)

        except Exception as e:
            App.Console.PrintError(f"Error adding panel: {str(e)}\n")
