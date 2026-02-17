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

class CatenaryCurve:
    
    def GetResources(self):
        """Return the command resources"""
        from pathlib import Path
        return {
            'Pixmap': str(Path(App.getUserAppDataDir()) / "Mod" / "WoodturningWorkbench" / "icons" / "CatenaryCurve.svg"),  
            'MenuText': 'Catenary Curve',
            'ToolTip': 'Catenary Curve Command'
        }

    def IsActive(self):
        """Check if the command is active"""
        return App.ActiveDocument is not None

    def Activated(self):
        """Execute the command"""
        class CatenaryCurvePanel:
            #Creates the Task Panel
            def __init__(self):

                self.form = QtWidgets.QWidget()
                self.form.setWindowTitle("Draw Catenary Curve")
                #Local Variables with Default Values
                self.sag = 250
                self.XStart=0.0
                self.XEnd=300.0
                self.YStart=0.0
                self.NumPoints=50
                self.WallThickness=0.0

                # Create layout
                layout = QtWidgets.QVBoxLayout()
                
                # Title
                title_label = QtWidgets.QLabel("Catenary Curve Generator")
                title_font = title_label.font()
                title_font.setPointSize(12)
                title_font.setBold(True)
                title_label.setFont(title_font)
                layout.addWidget(title_label)


                # Add spacing
                layout.addSpacing(20)
                
                # Sag input
                sag_layout = QtWidgets.QHBoxLayout()
                sag_label = QtWidgets.QLabel("Sag:")
                sag_label.setMinimumWidth(100)
                self.sag_edit = QtWidgets.QLineEdit()
                self.sag_edit.setText(str(self.sag))
                sag_layout.addWidget(sag_label)
                sag_layout.addWidget(self.sag_edit)
                layout.addLayout(sag_layout)
                
                # XStart input
                xstart_layout = QtWidgets.QHBoxLayout()
                xstart_label = QtWidgets.QLabel("X Start:")
                xstart_label.setMinimumWidth(100)
                self.xstart_edit = QtWidgets.QLineEdit()
                self.xstart_edit.setText(str(self.XStart))
                xstart_layout.addWidget(xstart_label)
                xstart_layout.addWidget(self.xstart_edit)
                layout.addLayout(xstart_layout)
                
                # XEnd input
                xend_layout = QtWidgets.QHBoxLayout()
                xend_label = QtWidgets.QLabel("X End:")
                xend_label.setMinimumWidth(100)
                self.xend_edit = QtWidgets.QLineEdit()
                self.xend_edit.setText(str(self.XEnd))
                xend_layout.addWidget(xend_label)
                xend_layout.addWidget(self.xend_edit)
                layout.addLayout(xend_layout)
                
                # YStart input
                ystart_layout = QtWidgets.QHBoxLayout()
                ystart_label = QtWidgets.QLabel("Y Start:")
                ystart_label.setMinimumWidth(100)
                self.ystart_edit = QtWidgets.QLineEdit()
                self.ystart_edit.setText(str(self.YStart))
                ystart_layout.addWidget(ystart_label)
                ystart_layout.addWidget(self.ystart_edit)
                layout.addLayout(ystart_layout)
                
                # NumPoints input
                numpoints_layout = QtWidgets.QHBoxLayout()
                numpoints_label = QtWidgets.QLabel("Num Points:")
                numpoints_label.setMinimumWidth(100)
                self.numpoints_edit = QtWidgets.QLineEdit()
                self.numpoints_edit.setText(str(self.NumPoints))
                numpoints_layout.addWidget(numpoints_label)
                numpoints_layout.addWidget(self.numpoints_edit)
                layout.addLayout(numpoints_layout)

                # Wall Thickness input
                wall_layout = QtWidgets.QHBoxLayout()
                wall_label = QtWidgets.QLabel("Wall Thickness:")
                wall_label.setMinimumWidth(100)
                self.wall_thickness_edit = QtWidgets.QLineEdit()
                self.wall_thickness_edit.setText(str(self.WallThickness))
                wall_layout.addWidget(wall_label)
                wall_layout.addWidget(self.wall_thickness_edit)
                layout.addLayout(wall_layout)

                # Mirror curve option (about 45° line through origin)
                mirror_layout = QtWidgets.QHBoxLayout()
                mirror_label = QtWidgets.QLabel("Mirror:")
                mirror_label.setMinimumWidth(100)
                self.mirror_curve_radio = QtWidgets.QRadioButton("Mirror on 45° line")
                mirror_layout.addWidget(mirror_label)
                mirror_layout.addWidget(self.mirror_curve_radio)
                layout.addLayout(mirror_layout)
                
                # Add spacing
                layout.addSpacing(20)
                
                # Button layout
                button_layout = QtWidgets.QHBoxLayout()

                # Add button A
                self.button_A = QtWidgets.QPushButton("Button A")
                self.button_A.clicked.connect(self.bt_A_clicked)
                button_layout.addWidget(self.button_A)

                # Add shell button
                self.button_shell = QtWidgets.QPushButton("Shell Revolve")
                self.button_shell.clicked.connect(self.bt_shell_clicked)
                button_layout.addWidget(self.button_shell)

                # Add revolve button
                self.button_revolve = QtWidgets.QPushButton("Revolve Catenary")
                self.button_revolve.clicked.connect(self.bt_revolve_clicked)
                button_layout.addWidget(self.button_revolve)

                # Add button A
                self.button_close = QtWidgets.QPushButton("Close")
                self.button_close.clicked.connect(self.on_cancel)
                button_layout.addWidget(self.button_close)

                layout.addLayout(button_layout)
                # Add stretch at end
                layout.addStretch()
                self.form.setLayout(layout)

            def bt_A_clicked(self):
                # Update values from text boxes first
                self.update_values()
                
                import FreeCAD as App
                try:
                    import math
                    doc = App.ActiveDocument
                    if not doc:
                        App.Console.PrintError("No active document\n")
                        return

                    # Create a new sketch
                    sketch = doc.addObject('Sketcher::SketchObject', 'CatenaryCurveSketch')
                    sketch.Placement = App.Placement(App.Vector(0, 0, 0), App.Rotation(App.Vector(1, 0, 0), 90))
  
                    print (self.sag)
                    poles = []
                    mirror_curve = self.mirror_curve_radio.isChecked()
                    for i in range(50 + 1):
                        x = self.XStart + (self.XEnd - self.XStart) * i / self.NumPoints
                        y = self.YStart + (self.sag * (math.cosh(x / self.sag) - 1))
                        if mirror_curve:
                            x, y = y, x
                        poles.append(App.Vector(x, y, 0))
                    # Create the B-spline curve
                    bspline = Part.BSplineCurve()
                    bspline.buildFromPoles(poles)

                    # Add the B-spline to the sketch
                    sketch.addGeometry(bspline, False)   

                    # Add horizontal line from curve endpoint to X=0
                    if poles:
                        end_point = poles[-1]
                        start_point = App.Vector(0, end_point.y, 0)
                        line = Part.LineSegment(start_point, end_point)
                        sketch.addGeometry(line, False)
                        origin = App.Vector(0, 0, 0)
                        line_to_origin = Part.LineSegment(start_point, origin)
                        sketch.addGeometry(line_to_origin, False)

                    # Recompute the document    
                    doc.recompute()             

                except Exception as e:
                    App.Console.PrintError(f"Error adding Catenary Curve sketch: {str(e)}\n")
                pass

            def bt_revolve_clicked(self):
                import FreeCAD as App
                try:
                    doc = App.ActiveDocument
                    if not doc:
                        App.Console.PrintError("No active document\n")
                        return

                    sketches = [obj for obj in doc.Objects if obj.Name.startswith("CatenaryCurveSketch")]
                    if not sketches:
                        App.Console.PrintError("No catenary sketch found to revolve\n")
                        return

                    sketch = sketches[-1]
                    revolve = doc.addObject("Part::Revolution", "CatenaryRevolve")
                    revolve.Source = sketch
                    revolve.Axis = App.Vector(0, 0, 1)
                    revolve.Base = App.Vector(0, 0, 0)
                    revolve.Angle = 360
                    if hasattr(revolve, "Solid"):
                        revolve.Solid = True

                    doc.recompute()
                except Exception as e:
                    App.Console.PrintError(f"Error creating revolve: {str(e)}\n")

            def bt_shell_clicked(self):
                import FreeCAD as App
                try:
                    self.update_values()
                    doc = App.ActiveDocument
                    if not doc:
                        App.Console.PrintError("No active document\n")
                        return

                    if self.WallThickness <= 0:
                        App.Console.PrintError("Wall thickness must be greater than 0\n")
                        return

                    revolves = [obj for obj in doc.Objects if obj.Name.startswith("CatenaryRevolve")]
                    if not revolves:
                        App.Console.PrintError("No revolve found to shell\n")
                        return

                    revolve = revolves[-1]
                    doc.recompute()

                    shape = revolve.Shape
                    if not shape or not shape.Faces:
                        App.Console.PrintError("Revolve has no faces to shell\n")
                        return

                    open_face = max(shape.Faces, key=lambda f: f.CenterOfMass.z)
                    thickness = -abs(self.WallThickness)
                    shell_shape = shape.makeThickness([open_face], thickness, 1.0e-3)

                    shell_obj = doc.addObject("Part::Feature", "CatenaryShell")
                    shell_obj.Shape = shell_shape
                    doc.recompute()
                except Exception as e:
                    App.Console.PrintError(f"Error creating shell: {str(e)}\n")

            def set_tooltips(self):
                #self.bowl_numSegmentsBox.setToolTip("Number of segments around the bowl")
                pass

            def update_values(self):
                #Update the local variables with the values in the text boxes
                try:
                    self.sag = float(self.sag_edit.text())
                    self.XStart = float(self.xstart_edit.text())
                    self.XEnd = float(self.xend_edit.text())
                    self.YStart = float(self.ystart_edit.text())
                    self.NumPoints = int(self.numpoints_edit.text())
                    self.WallThickness = float(self.wall_thickness_edit.text())
                except ValueError:
                    pass


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
            panel = CatenaryCurvePanel()
    
            # Show the task panel in FreeCAD
            Gui.Control.showDialog(panel)

        except Exception as e:
            App.Console.PrintError(f"Error adding panel: {str(e)}\n")
