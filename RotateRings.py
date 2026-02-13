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
from varsetOps import getVarsetInt

class RotateRings:
    
    def GetResources(self):
        """Return the command resources"""
        from pathlib import Path
        return {
            #'Pixmap': str(Path(App.getUserAppDataDir()) / "Mod" / "WoodturningWorkbench" / "icons" / "RotateRings.svg"),  
            'Pixmap':'',
            'MenuText': 'Rotate Rings',
            'ToolTip': 'Rotate Rings Command'
        }

    def IsActive(self):
        """Check if the command is active"""
        return App.ActiveDocument is not None

    def Activated(self):
        """Execute the command"""
        class RotateRingsPanel:
            #Creates the Task Panel
            def __init__(self):
                
                from PySide import QtGui, QtCore, QtWidgets	
                self.form = QtWidgets.QWidget()
                self.form.setWindowTitle("Task Panel Template")
                #Local Variables with Default Values
                self.rotation_per_ring = 15
                self.num_segments = getVarsetInt(self,"NumSegments")   

                # Create layout
                layout = QtWidgets.QVBoxLayout()
                
                # Title
                title_label = QtWidgets.QLabel("Task Panel Template")
                title_font = title_label.font()
                title_font.setPointSize(12)
                title_font.setBold(True)
                title_label.setFont(title_font)
                layout.addWidget(title_label)

                text_box_layout = QtWidgets.QHBoxLayout()
                
                # Number of Segments input
                num_segments_label = QtWidgets.QLabel("Number of Segments:")
                self.num_segments_input = QtWidgets.QLineEdit()
                self.num_segments_input.setText(str(self.num_segments))
                self.num_segments_input.setMaximumWidth(100)
                text_box_layout.addWidget(num_segments_label)
                text_box_layout.addWidget(self.num_segments_input)
                text_box_layout.addStretch()
                
                layout.addLayout(text_box_layout)

                self.use_percent_layout = QtWidgets.QHBoxLayout()
                self.use_percent_checkbox = QtWidgets.QCheckBox("Use Percent Rotation")
                self.use_percent_checkbox.setChecked(True)
                self.use_percent_layout.addWidget(self.use_percent_checkbox)    

                self.rotation_angle = QtWidgets.QLabel("Rotation Angle:")
                self.rotation_angle_text = QtWidgets.QLineEdit("0")
                self.use_percent_layout.addWidget(self.rotation_angle)  
                self.use_percent_layout.addWidget(self.rotation_angle_text) 
                #self.rotation_angle.setEnabled(False)
                #self.rotation_angle_text.setEnabled(False)  

                layout.addLayout(self.use_percent_layout)

                percent_group = QtWidgets.QGroupBox("Percent Rotation")
                percent_layout = QtWidgets.QHBoxLayout()
                self.percent_radio_25 = QtWidgets.QRadioButton("25%")
                self.percent_radio_33 = QtWidgets.QRadioButton("33%")
                self.percent_radio_50 = QtWidgets.QRadioButton("50%")
                percent_layout.addWidget(self.percent_radio_25)
                percent_layout.addWidget(self.percent_radio_33)
                percent_layout.addWidget(self.percent_radio_50)
                self.percent_radio_50.setChecked(True)  # Default to 50%
                percent_group.setLayout(percent_layout)
                layout.addWidget(percent_group)

                direction_group = QtWidgets.QGroupBox("Direction")
                direction_layout = QtWidgets.QHBoxLayout()
                self.direction_radio_left = QtWidgets.QRadioButton("Left")
                self.direction_radio_right = QtWidgets.QRadioButton("Right")
                self.direction_radio_right.setChecked(True)  # Default to Right
                direction_layout.addWidget(self.direction_radio_left)
                direction_layout.addWidget(self.direction_radio_right)
                direction_group.setLayout(direction_layout)
                layout.addWidget(direction_group)

                # Add spacing
                layout.addSpacing(20)
                
                # Button layout
                button_layout = QtWidgets.QHBoxLayout()

                # Add button A
                self.button_A = QtWidgets.QPushButton("Rotate Rings")
                self.button_A.clicked.connect(self.bt_rotate_rings_click)
                button_layout.addWidget(self.button_A)

                # Add rotate selected ring button
                self.button_rotate_selected = QtWidgets.QPushButton("Rotate Selected Ring")
                self.button_rotate_selected.clicked.connect(self.bt_rotate_selected_ring_click)
                button_layout.addWidget(self.button_rotate_selected)

                # Add reset rotation button
                self.button_reset = QtWidgets.QPushButton("Reset Rotation")
                self.button_reset.clicked.connect(self.reset_rotation)
                button_layout.addWidget(self.button_reset)

                # Add button Close
                self.button_close = QtWidgets.QPushButton("Close")
                self.button_close.clicked.connect(self.on_cancel)
                button_layout.addWidget(self.button_close)

                layout.addLayout(button_layout)
                # Add stretch at end
                layout.addStretch()
                self.form.setLayout(layout)
            def get_rotation_angle(self):
                if self.direction_radio_left.isChecked():
                    direction_multiplier = -1
                elif self.direction_radio_right.isChecked():
                    direction_multiplier = 1   
                if self.use_percent_checkbox.isChecked():
                    if self.percent_radio_25.isChecked():
                        return (360/self.num_segments) * 0.25 * direction_multiplier
                    elif self.percent_radio_33.isChecked():
                        return (360/self.num_segments) * 0.33 * direction_multiplier
                    elif self.percent_radio_50.isChecked():
                        return (360/self.num_segments) * 0.50 * direction_multiplier
                else:
                    try:
                        return float(self.rotation_angle_text.text())*direction_multiplier
                    except ValueError:
                        App.Console.PrintError("Invalid rotation angle. Please enter a number.\n")
                        return 0
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
            def bt_rotate_selected_ring_click(self):
                self.update_values()
                doc = App.ActiveDocument
                selection = Gui.Selection.getSelection()
                if not selection:
                    App.Console.PrintError("No ring selected. Please select a ring object.\n")
                    return
                selected_label = selection[0].Label
                if len(selected_label) < 8:
                    App.Console.PrintError("Selected object label is invalid.\n")
                    return
                ring_prefix = selected_label[:8]
                for obj in doc.Objects:
                    if obj.Label.startswith(ring_prefix):
                        obj = doc.getObject(obj.Name)
                        incremental_rotation = App.Placement(App.Vector(0,0,0), App.Vector(0,0,1), self.rotation_per_ring).Rotation
                        obj.Placement = App.Placement(obj.Placement.Base, incremental_rotation.multiply(obj.Placement.Rotation))
            def reset_rotation(self):
                self.update_values()
                doc = App.ActiveDocument
                ring_objects = [obj for obj in doc.Objects if obj.Label.startswith("Ring")]
                for obj in ring_objects:
                    label_suffix = obj.Label[-3:]
                    try:
                        ring_index = int(label_suffix)
                    except ValueError:
                        continue
                    rotation_angle = (ring_index - 1) * (360 / self.num_segments)
                    obj = doc.getObject(obj.Name)
                    reset_rotation = App.Placement(App.Vector(0,0,0), App.Vector(0,0,1), rotation_angle).Rotation
                    obj.Placement = App.Placement(obj.Placement.Base, reset_rotation)
            def bt_A_clicked(self):
                """Handler for Button A click"""
                App.Console.PrintMessage("Button A clicked\n")

            def set_tooltips(self):
                self.num_segments_input.setToolTip("Number of segments around the bowl")
                self.bowl_layer_heightBox.setToolTip("Height of each layer in mm")
                self.bt_add_segments.setToolTip("Add segments to the bowl")	
                self.bt_delete_segments.setToolTip("Delete all segments created by this macro")

            def update_values(self):
                #Update the local variables with the values in the text boxes
                self.num_segments = int(self.num_segments_input.text())
                self.rotation_per_ring = self.get_rotation_angle()

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
            panel = RotateRingsPanel()
    
            # Show the task panel in FreeCAD
            Gui.Control.showDialog(panel)

        except Exception as e:
            App.Console.PrintError(f"Error adding panel: {str(e)}\n")
