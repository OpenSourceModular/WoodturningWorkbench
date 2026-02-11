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

class WedgeGenerator:
    
    def GetResources(self):
        """Return the command resources"""
        from pathlib import Path
        return {
            #'Pixmap': str(Path(App.getUserAppDataDir()) / "Mod" / "WoodturningWorkbench" / "icons" / "WedgeGenerator.svg"),  
            'Pixmap': '',
            'MenuText': 'Wedge Generator',
            'ToolTip': 'Wedge Generator Command'
        }

    def IsActive(self):
        """Check if the command is active"""
        return App.ActiveDocument is not None

    def Activated(self):
        """Execute the command"""
        class WedgeGeneratorPanel:
            #Creates the Task Panel
            def __init__(self):
                
                from PySide import QtGui, QtCore, QtWidgets	
                self.form = QtWidgets.QWidget()
                self.form.setWindowTitle("Wedge Generator")
                #Local Variables with Default Values
                self.wedge_length = 100
                self.wedge_small_end_width = 50
                self.number_of_segments = 16
                self.wedge_thickness = 10
                self.offset_distance = 12.7


                # Create layout
                layout = QtWidgets.QVBoxLayout()
                
                # Title
                title_label = QtWidgets.QLabel("Wedge Generator")
                title_font = title_label.font()
                title_font.setPointSize(12)
                title_font.setBold(True)
                title_label.setFont(title_font)
                layout.addWidget(title_label)

                # Wedge Length
                wedge_length_layout = QtWidgets.QHBoxLayout()
                wedge_length_label = QtWidgets.QLabel("Wedge Length:")
                self.wedge_length_input = QtWidgets.QLineEdit()
                self.wedge_length_input.setText(str(self.wedge_length))
                wedge_length_layout.addWidget(wedge_length_label)
                wedge_length_layout.addWidget(self.wedge_length_input)
                layout.addLayout(wedge_length_layout)

                # Wedge Small End Width
                wedge_width_layout = QtWidgets.QHBoxLayout()
                wedge_width_label = QtWidgets.QLabel("Wedge Small End Width:")
                self.wedge_width_input = QtWidgets.QLineEdit()
                self.wedge_width_input.setText(str(self.wedge_small_end_width))
                wedge_width_layout.addWidget(wedge_width_label)
                wedge_width_layout.addWidget(self.wedge_width_input)
                layout.addLayout(wedge_width_layout)

                # Number of Segments
                segments_layout = QtWidgets.QHBoxLayout()
                segments_label = QtWidgets.QLabel("Number of Segments:")
                self.segments_input = QtWidgets.QLineEdit()
                self.segments_input.setText(str(self.number_of_segments))
                segments_layout.addWidget(segments_label)
                segments_layout.addWidget(self.segments_input)
                layout.addLayout(segments_layout)

                # Wedge Thickness
                thickness_layout = QtWidgets.QHBoxLayout()
                thickness_label = QtWidgets.QLabel("Wedge Thickness:")
                self.thickness_input = QtWidgets.QLineEdit()
                self.thickness_input.setText(str(self.wedge_thickness))
                thickness_layout.addWidget(thickness_label)
                thickness_layout.addWidget(self.thickness_input)
                layout.addLayout(thickness_layout)

                # Offset Distance
                offset_layout = QtWidgets.QHBoxLayout()
                offset_label = QtWidgets.QLabel("Offset Distance:")
                self.offset_input = QtWidgets.QLineEdit()
                self.offset_input.setText(str(self.offset_distance))
                offset_layout.addWidget(offset_label)
                offset_layout.addWidget(self.offset_input)
                layout.addLayout(offset_layout)

                # Add spacing
                layout.addSpacing(20)
                
                # Button layout
                button_layout = QtWidgets.QHBoxLayout()

                # Add button Make Wedge
                self.button_make_wedge = QtWidgets.QPushButton("Make Wedge")
                self.button_make_wedge.clicked.connect(self.bt_make_wedge)
                button_layout.addWidget(self.button_make_wedge)

                # Add button Close
                self.button_close = QtWidgets.QPushButton("Close")
                self.button_close.clicked.connect(self.on_cancel)
                button_layout.addWidget(self.button_close)

                layout.addLayout(button_layout)
                # Add stretch at end
                layout.addStretch()
                self.form.setLayout(layout)

            def bt_make_wedge(self):
                """Handler for Make Wedge button click"""
                try:
                    # Get values from input fields
                    self.update_values()
                    
                    # Create a new sketch
                    doc = App.ActiveDocument
                    sketch = doc.addObject("Sketcher::SketchObject", "wedge")
                    sketch.MapReversed = False
                    
                    # Calculate the angle for each segment (in radians)
                    segment_angle_deg = 360.0 / self.number_of_segments
                    half_angle_rad = radians(segment_angle_deg / 2.0)
                    
                    # Calculate Y coordinates at the long end
                    
                    # Start with the half-width of the short end, then add the expansion
                    y_half_width_long = (self.wedge_small_end_width / 2.0) + self.wedge_length * tan(half_angle_rad)
                    offset_small = self.wedge_small_end_width / 2.0 - self.offset_distance
                    y_half_width_long_offset = offset_small + (self.wedge_length-self.offset_distance) * tan(half_angle_rad)
                    # Create offset lines 12.7mm inward
                                      
                    # Define the four vertices of the trapezoid
                    # Short end (at x=0, centered on Y axis)
                    p1 = Vector(0, -self.wedge_small_end_width / 2.0, 0)  # Bottom-left

                    p2 = Vector(0, self.wedge_small_end_width / 2.0, 0)   # Top-left
                    
                    # Long end (at x=wedge_length)
                    p3 = Vector(self.wedge_length, y_half_width_long, 0)      # Top-right
                    
                    p4 = Vector(self.wedge_length, -y_half_width_long, 0)     # Bottom-right
                    
                    p5 = Vector(self.offset_distance, -offset_small, 0)  # Bottom-left offset
                    p6 = Vector(self.offset_distance, offset_small, 0)   # Top-left offset
                    p7 = Vector(self.wedge_length-self.offset_distance, y_half_width_long_offset, 0)  # Top-right offset
                    p8 = Vector(self.wedge_length-self.offset_distance, -y_half_width_long_offset, 0)  # Bottom-right offset


                    
                    # Add the four lines to form the trapezoid
                    # Line from p1 to p2 (short end)
                    sketch.addGeometry(Part.LineSegment(p1, p2))
                    
                    
                    # Line from p2 to p3 (top angled side)
                    sketch.addGeometry(Part.LineSegment(p2, p3))
                    
                    # Line from p3 to p4 (long end)
                    sketch.addGeometry(Part.LineSegment(p3, p4))
                    
                    # Line from p4 to p1 (bottom angled side)
                    sketch.addGeometry(Part.LineSegment(p4, p1))

                    sketch.addGeometry(Part.LineSegment(p5, p6))
                    sketch.addGeometry(Part.LineSegment(p6, p7))
                    sketch.addGeometry(Part.LineSegment(p7, p8))
                    sketch.addGeometry(Part.LineSegment(p8, p5))

                    
                    # Add coincident constraints to close the trapezoid
                    import Sketcher
                    # Constrain end of line 0 to start of line 1
                    sketch.addConstraint(Sketcher.Constraint('Coincident', 0, 2, 1, 1))
                    # Constrain end of line 1 to start of line 2
                    sketch.addConstraint(Sketcher.Constraint('Coincident', 1, 2, 2, 1))
                    # Constrain end of line 2 to start of line 3
                    sketch.addConstraint(Sketcher.Constraint('Coincident', 2, 2, 3, 1))
                    # Constrain end of line 3 to start of line 0
                    sketch.addConstraint(Sketcher.Constraint('Coincident', 3, 2, 0, 1))
                    

                    
                    
                    
                    # Recompute the document to update the view
                    doc.recompute()
                    App.Console.PrintMessage(f"Wedge sketch created with angle {segment_angle_deg:.2f} degrees and {self.offset_distance}mm inward offset\n")
                    
                except Exception as e:
                    App.Console.PrintError(f"Error creating wedge: {str(e)}\n")

            def set_tooltips(self):
                #self.bowl_numSegmentsBox.setToolTip("Number of segments around the bowl")
                pass

            def update_values(self):
                #Update the local variables with the values in the text boxes
                self.wedge_length = float(self.wedge_length_input.text())
                self.wedge_small_end_width = float(self.wedge_width_input.text())
                self.number_of_segments = int(self.segments_input.text())
                self.wedge_thickness = float(self.thickness_input.text())
                self.offset_distance = float(self.offset_input.text())
            
            def on_cancel(self):
                """Cancel and close the task panel"""
                Gui.Control.closeDialog()
        
            def accept(self):
                """Accept method (required by task panel)"""
                self.bt_make_wedge()
            
            def reject(self):
                """Reject method (required by task panel)"""
                self.on_cancel()
            
            def getStandardButtons(self):
                """Define which standard buttons to show (0 = none, we use custom buttons)"""
                #return int(QtWidgets.QDialogButtonBox.NoButton)
                return 0		
        try:
            panel = WedgeGeneratorPanel()
    
            # Show the task panel in FreeCAD
            Gui.Control.showDialog(panel)

        except Exception as e:
            App.Console.PrintError(f"Error adding panel: {str(e)}\n")
