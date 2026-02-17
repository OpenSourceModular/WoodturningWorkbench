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
import platform
import os

class WedgeGenerator:
    
    def GetResources(self):
        """Return the command resources"""
        from pathlib import Path
        return {
            'Pixmap': str(Path(App.getUserAppDataDir()) / "Mod" / "WoodturningWorkbench" / "icons" / "WedgeGenerator.svg"),  
            'MenuText': 'Wedgie Generator',
            'ToolTip': 'Wedgie Generator Command'
        }

    def IsActive(self):
        """Check if the command is active"""
        return App.ActiveDocument is not None

    def Activated(self):
        """Execute the command"""
        class WedgeGeneratorPanel:
            #Creates the Task Panel
            def __init__(self):

                self.form = QtWidgets.QWidget()
                self.form.setWindowTitle("Wedgie Generator")
                #Local Variables with Default Values
                self.wedge_length = 150
                self.wedge_small_end_width = 50
                self.number_of_segments = 16
                self.wedge_thickness = 12.7
                self.offset_distance = 16
                self.cut_out_center = True
                self.add_text_label = True


                # Create layout
                layout = QtWidgets.QVBoxLayout()
                
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

                # Cut out center checkbox
                self.cutout_checkbox = QtWidgets.QCheckBox("Cut out center")
                self.cutout_checkbox.setChecked(self.cut_out_center)
                layout.addWidget(self.cutout_checkbox)

                # Add Text Label checkbox
                self.textlabel_checkbox = QtWidgets.QCheckBox("Add Text Label")
                self.textlabel_checkbox.setChecked(self.add_text_label)
                layout.addWidget(self.textlabel_checkbox)

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
                import Draft
                from BOPTools import BOPFeatures
                
                def get_font_file():
                    """Get the appropriate font file path based on the operating system"""
                    system = platform.system()
                    print(f"Detected operating system: {system}")
                    
                    if system == "Windows":
                        font_paths = [
                            "C:/Windows/Fonts/arial.ttf",
                            "C:/WINDOWS/Fonts/arial.ttf"
                        ]
                    elif system == "Darwin":  # macOS
                        font_paths = [
                            "/Library/Fonts/Arial.ttf",
                            "/System/Library/Fonts/Supplemental/Arial.ttf",
                            "/Library/Fonts/Arial.ttc"
                        ]
                    else:  # Linux and others
                        font_paths = [
                            "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",
                            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
                        ]
                    
                    # Return first font file that exists
                    for font_path in font_paths:
                        if os.path.exists(font_path):
                            return font_path
                    
                    # Fallback to first path if none exist
                    return font_paths[0]
                
                def make_trapezoid_sketch(a_sketch, small_end_width_l, wedge_length_, segment_angle_deg_l, x_offset):
                    import Sketcher
                    half_angle_rad = radians(segment_angle_deg_l / 2.0)
                    y_half_width_long = (small_end_width_l / 2.0) + wedge_length_ * tan(half_angle_rad)
                    p1 = Vector(0+ x_offset, -small_end_width_l / 2.0, 0)  # Bottom-left
                    p2 = Vector(0+ x_offset, small_end_width_l / 2.0, 0)   # Top-left
                    # Long end (at x=wedge_length)
                    p3 = Vector(wedge_length_+x_offset, y_half_width_long, 0)      # Top-right
                    p4 = Vector(wedge_length_+x_offset, -y_half_width_long, 0)     # Bottom-right
                    line0 = a_sketch.addGeometry(Part.LineSegment(p1, p2))
                    # Line from p2 to p3 (top angled side)
                    line1 = a_sketch.addGeometry(Part.LineSegment(p2, p3))
                    # Line from p3 to p4 (long end)
                    line2 = a_sketch.addGeometry(Part.LineSegment(p3, p4))
                    # Line from p4 to p1 (bottom angled side)
                    line3 = a_sketch.addGeometry(Part.LineSegment(p4, p1))
                    # Constrain endpoints to be coincident
                    a_sketch.addConstraint(Sketcher.Constraint('Coincident', line0, 2, line1, 1))
                    a_sketch.addConstraint(Sketcher.Constraint('Coincident', line1, 2, line2, 1))
                    a_sketch.addConstraint(Sketcher.Constraint('Coincident', line2, 2, line3, 1))
                    a_sketch.addConstraint(Sketcher.Constraint('Coincident', line3, 2, line0, 1))
                try:
                    # Get values from input fields
                    self.update_values()
                    
                    # Get checkbox states
                    self.cut_out_center = self.cutout_checkbox.isChecked()
                    self.add_text_label = self.textlabel_checkbox.isChecked()
                    
                    # Create a new sketch
                    doc = App.ActiveDocument
                    sketch = doc.addObject("Sketcher::SketchObject", "wedge")
                    sketch.MapReversed = False
                    
                    # Calculate the angle for each segment (in radians)
                    segment_angle_deg = 360.0 / self.number_of_segments
                    
                    make_trapezoid_sketch(sketch, self.wedge_small_end_width, self.wedge_length, segment_angle_deg, 0)
                    
                    # Only create the inner trapezoid if cut_out_center is checked
                    if self.cut_out_center:
                        make_trapezoid_sketch(sketch, self.wedge_small_end_width - (self.offset_distance * 2), self.wedge_length - (self.offset_distance * 2), segment_angle_deg, self.offset_distance)

                    sketch.Visibility = False  # Hide the sketch in the view
                    # Extrude the sketch in +Z by the wedge thickness
                    extrusion = doc.addObject("Part::Extrusion", "wedge_extrude")
                    extrusion.Base = sketch
                    extrusion.Dir = Vector(0, 0, self.wedge_thickness)
                    extrusion.Solid = True
                    extrusion.TaperAngle = 0
                    extrusion.Label = f"Wedge-{self.number_of_segments}-Segments"
                    
                    # Only create and cut the text label if add_text_label is checked
                    if self.add_text_label:
                        # Recompute the document to update the view
                        font_file = get_font_file()
                        ss = Draft.make_shapestring(String=str(self.number_of_segments), FontFile=font_file, Size=6.0, Tracking=0.0)
                        ss.Placement = App.Placement(App.Vector(5,(self.wedge_small_end_width/2)-8,self.wedge_thickness),App.Rotation(App.Vector(0,0,1),0))

                        ss_extrusion = doc.addObject("Part::Extrusion", "text_extrude")
                        ss_extrusion.Base = ss  
                        ss_extrusion.Dir = Vector(0, 0, -2)
                        ss_extrusion.Solid = True 
                        ss.Visibility = False  # Hide the original shape string in the view

                        doc.recompute()
             
                        bp = BOPFeatures.BOPFeatures(doc)
                        cut_result = bp.make_cut(["wedge_extrude", "text_extrude", ])
                        cut_result.Label = f"Wedge-{self.number_of_segments}-Segments"
                    
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
