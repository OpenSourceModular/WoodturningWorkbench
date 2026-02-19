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
import Sketcher
from BOPTools import BOPFeatures
from varsetOps import setVarsetValue, getVarsetValue, getVarsetInt

class OffcenterTurning:
    
    def GetResources(self):
        """Return the command resources"""
        from pathlib import Path
        return {
            'Pixmap': str(Path(App.getUserAppDataDir()) / "Mod" / "WoodturningWorkbench" / "icons" / "OffcenterTurning.svg"),  
            'MenuText': 'Offcenter Turning',
            'ToolTip': 'Offcenter Turning Command'
        }

    def IsActive(self):
        """Check if the command is active"""
        return App.ActiveDocument is not None

    def Activated(self):
        """Execute the command"""
        class OffcenterTurningPanel:
            #Creates the Task Panel
            def __init__(self):

                self.form = QtWidgets.QWidget()
                self.form.setWindowTitle("Offcenter Turning Task Panel")
                #Local Variables with Default Values
                from varsetOps import setVarsetValue, getVarsetValue, getVarsetInt
                doc = App.ActiveDocument
                if not doc.getObject("OffcenterTurningVariables"):
                    self.varset = doc.addObject("App::VarSet", "BowlVariables")
                    # Add a variable (property) to the VarSet
                    # Syntax: addProperty(type, name, group, tooltip)
                    self.varset.addProperty("App::PropertyInteger", "NumberPoints", "General", "Number of points for the offcenter turning")
                    self.varset.NumberPoints = 3
                    self.varset.addProperty("App::PropertyFloat", "BottomAngle", "General", "Bottom angle in degrees")
                    self.varset.BottomAngle = 30.0  
                    self.varset.addProperty("App::PropertyFloat", "TopAngle", "General", "Top angle in degrees")
                    self.varset.TopAngle = 15.0
                    self.varset.addProperty("App::PropertyFloat", "CylinderHeight", "General", "Height of the cylinder in mm")
                    self.varset.CylinderHeight = 50.0
                    self.varset.addProperty("App::PropertyFloat", "CylinderRadius", "General", "Radius of the cylinder in mm")
                    self.varset.CylinderRadius = 20.0
                    self.varset.addProperty("App::PropertyFloat", "TopRadius", "General", "Radius at the top of the turning in mm")
                    self.varset.TopRadius = 10.0
                    self.varset.addProperty("App::PropertyFloat", "BottomRadius", "General", "Radius at the bottom of the turning in mm")
                    self.varset.BottomRadius = 15.0
                    

                # Create layout
                layout = QtWidgets.QVBoxLayout()
                
                # Title
                title_label = QtWidgets.QLabel("Offcenter Turning Task Panel")
                title_font = title_label.font()
                title_font.setPointSize(12)
                title_font.setBold(True)
                title_label.setFont(title_font)
                layout.addWidget(title_label)

                text_box_layout = QtWidgets.QVBoxLayout()

                self.bottom_angle_input = QtWidgets.QLineEdit(str(getVarsetValue(self.varset, "BottomAngle")))
                self.top_angle_input = QtWidgets.QLineEdit(str(getVarsetValue(self.varset, "TopAngle")))
                self.cylinder_height_input = QtWidgets.QLineEdit(str(getVarsetValue(self.varset, "CylinderHeight")))
                self.cylinder_radius_input = QtWidgets.QLineEdit(str(getVarsetValue(self.varset, "CylinderRadius")))
                self.top_radius_input = QtWidgets.QLineEdit(str(getVarsetValue(self.varset, "TopRadius")))
                self.bottom_radius_input = QtWidgets.QLineEdit(str(getVarsetValue(self.varset, "BottomRadius")))
                self.num_points_input = QtWidgets.QLineEdit(str(getVarsetInt(self.varset, "NumberPoints")))

                bottom_angle_row = QtWidgets.QHBoxLayout()
                bottom_angle_row.addWidget(QtWidgets.QLabel("Bottom Angle:"))
                bottom_angle_row.addWidget(self.bottom_angle_input)
                bottom_angle_row.addWidget(QtWidgets.QLabel("Bowl Radius:"))
                text_box_layout.addLayout(bottom_angle_row)

                top_angle_row = QtWidgets.QHBoxLayout()
                top_angle_row.addWidget(QtWidgets.QLabel("Top Angle:"))
                top_angle_row.addWidget(self.top_angle_input)
                text_box_layout.addLayout(top_angle_row)

                cylinder_height_row = QtWidgets.QHBoxLayout()
                cylinder_height_row.addWidget(QtWidgets.QLabel("Cylinder Height:"))
                cylinder_height_row.addWidget(self.cylinder_height_input)
                text_box_layout.addLayout(cylinder_height_row)

                cylinder_radius_row = QtWidgets.QHBoxLayout()
                cylinder_radius_row.addWidget(QtWidgets.QLabel("Cylinder Radius:"))
                cylinder_radius_row.addWidget(self.cylinder_radius_input)
                text_box_layout.addLayout(cylinder_radius_row)

                top_radius_row = QtWidgets.QHBoxLayout()
                top_radius_row.addWidget(QtWidgets.QLabel("Top Radius:"))
                top_radius_row.addWidget(self.top_radius_input)
                text_box_layout.addLayout(top_radius_row)

                bottom_radius_row = QtWidgets.QHBoxLayout()
                bottom_radius_row.addWidget(QtWidgets.QLabel("Bottom Radius:"))
                bottom_radius_row.addWidget(self.bottom_radius_input)
                text_box_layout.addLayout(bottom_radius_row)

                num_points_row = QtWidgets.QHBoxLayout()
                num_points_row.addWidget(QtWidgets.QLabel("Number of Points:"))
                num_points_row.addWidget(self.num_points_input)
                text_box_layout.addLayout(num_points_row)

                layout.addLayout(text_box_layout)

                # Add spacing
                layout.addSpacing(20)
                
                # Button layout
                button_layout = QtWidgets.QHBoxLayout()

                # Add button A
                self.button_A = QtWidgets.QPushButton("Button A")
                self.button_A.clicked.connect(self.bt_A_clicked)
                button_layout.addWidget(self.button_A)

                # Add sketches button
                self.button_add_sketches = QtWidgets.QPushButton("Add Sketches")
                self.button_add_sketches.clicked.connect(self.bt_add_sketches_clicked)
                button_layout.addWidget(self.button_add_sketches)

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
                App.Console.PrintMessage("Button A clicked\n")

            def bt_add_sketches_clicked(self):
                """Handler for Add Sketches click"""
                doc = App.ActiveDocument
                if doc is None:
                    App.Console.PrintError("No active document.\n")
                    return

                bottom_radius = getVarsetValue(self, "BottomRadius")
                top_radius = getVarsetValue(self, "TopRadius")
                bottom_angle = getVarsetValue(self, "BottomAngle")
                top_angle = getVarsetValue(self, "TopAngle")
                cylinder_height = getVarsetValue(self, "CylinderHeight")
                num_points = getVarsetInt(self, "NumberPoints")
                try:
                    bottom_radius = float(bottom_radius) if bottom_radius is not None else 0.0
                except (TypeError, ValueError):
                    bottom_radius = 0.0
                try:
                    top_radius = float(top_radius) if top_radius is not None else 0.0
                except (TypeError, ValueError):
                    top_radius = 0.0
                try:
                    bottom_angle = float(bottom_angle) if bottom_angle is not None else 0.0
                except (TypeError, ValueError):
                    bottom_angle = 0.0
                try:
                    top_angle = float(top_angle) if top_angle is not None else 0.0
                except (TypeError, ValueError):
                    top_angle = 0.0
                try:
                    cylinder_height = float(cylinder_height) if cylinder_height is not None else 0.0
                except (TypeError, ValueError):
                    cylinder_height = 0.0
                try:
                    num_points = int(num_points) if num_points is not None else 0
                except (TypeError, ValueError):
                    num_points = 0

                bottom_sketch = doc.getObject("Bottom_Sketch")
                if bottom_sketch is None:
                    bottom_sketch = doc.addObject("Sketcher::SketchObject", "Bottom_Sketch")
                elif bottom_sketch.TypeId != "Sketcher::SketchObject":
                    App.Console.PrintError("An object named 'Bottom_Sketch' already exists and is not a sketch.\n")
                    return

                top_sketch = doc.getObject("Top_Sketch")
                if top_sketch is None:
                    top_sketch = doc.addObject("Sketcher::SketchObject", "Top_Sketch")
                elif top_sketch.TypeId != "Sketcher::SketchObject":
                    App.Console.PrintError("An object named 'Top_Sketch' already exists and is not a sketch.\n")
                    return

                bottom_sketch.Placement = App.Placement(App.Vector(0, 0, 0), App.Rotation(0, 0, 0))
                top_sketch.Placement = App.Placement(App.Vector(0, 0, cylinder_height), App.Rotation(0, 0, 0))

                while len(bottom_sketch.Geometry) > 0:
                    bottom_sketch.delGeometry(len(bottom_sketch.Geometry) - 1)
                while len(top_sketch.Geometry) > 0:
                    top_sketch.delGeometry(len(top_sketch.Geometry) - 1)

                bottom_circle = Part.Circle(App.Vector(0, 0, 0), App.Vector(0, 0, 1), bottom_radius)
                top_circle = Part.Circle(App.Vector(0, 0, 0), App.Vector(0, 0, 1), top_radius)

                bottom_cylinder_circle = Part.Circle(App.Vector(0, 0, 0), App.Vector(0, 0, 1), getVarsetValue(self, "CylinderRadius"))  
                top_cylinder_circle = Part.Circle(App.Vector(0, 0, 0), App.Vector(0, 0, 1), getVarsetValue(self, "CylinderRadius"))

                bottom_circle_idx = bottom_sketch.addGeometry(bottom_circle, True)
                top_circle_idx = top_sketch.addGeometry(top_circle, True)

                bottom_cylinder_circle_idx = bottom_sketch.addGeometry(bottom_cylinder_circle, False)
                top_cylinder_circle_idx = top_sketch.addGeometry(top_cylinder_circle, False)

                bottom_sketch.addConstraint(Sketcher.Constraint('Radius', bottom_circle_idx, bottom_radius))
                bottom_sketch.addConstraint(Sketcher.Constraint('Coincident', bottom_circle_idx, 3, -1, 1))
                bottom_sketch.setExpression('Constraints[0]', 'BowlVariables.BottomRadius')
                top_sketch.addConstraint(Sketcher.Constraint('Radius', top_circle_idx, top_radius))
                top_sketch.addConstraint(Sketcher.Constraint('Coincident', top_circle_idx, 3, -1, 1))
                top_sketch.setExpression('Constraints[0]', 'BowlVariables.TopRadius')

                if num_points > 0:
                    step = 2 * math.pi / num_points
                    bottom_line_indices = []
                    top_line_indices = []
                    for i in range(num_points):
                        bottom_point_angle = math.radians(bottom_angle) + (i * step)
                        top_point_angle = math.radians(top_angle) + (i * step)
                        bx = bottom_radius * math.cos(bottom_point_angle)
                        by = bottom_radius * math.sin(bottom_point_angle)
                        tx = top_radius * math.cos(top_point_angle)
                        ty = top_radius * math.sin(top_point_angle)

                        bottom_point_idx = bottom_sketch.addGeometry(Part.Point(App.Vector(bx, by, 0)), False)
                        bottom_sketch.addConstraint(Sketcher.Constraint('PointOnObject', bottom_point_idx, 1, bottom_circle_idx))

                        bottom_line_idx = bottom_sketch.addGeometry(
                            Part.LineSegment(App.Vector(0, 0, 0), App.Vector(bx, by, 0)),
                            True
                        )
                        bottom_line_indices.append(bottom_line_idx)
                        bottom_sketch.addConstraint(Sketcher.Constraint('Coincident', bottom_line_idx, 1, -1, 1))
                        bottom_sketch.addConstraint(Sketcher.Constraint('Coincident', bottom_line_idx, 2, bottom_point_idx, 1))

                        if i == 0:
                            bottom_xaxis_idx = bottom_sketch.addGeometry(
                                Part.LineSegment(App.Vector(0, 0, 0), App.Vector(1, 0, 0)),
                                True
                            )
                            bottom_sketch.addConstraint(Sketcher.Constraint('Coincident', bottom_xaxis_idx, 1, -1, 1))
                            bottom_sketch.addConstraint(Sketcher.Constraint('Horizontal', bottom_xaxis_idx))
                            bottom_angle_constraint = bottom_sketch.addConstraint(
                                Sketcher.Constraint('Angle', bottom_line_idx, bottom_xaxis_idx, bottom_angle)
                            )
                            bottom_sketch.setExpression(
                                f'Constraints[{bottom_angle_constraint}]',
                                'BowlVariables.BottomAngle'
                            )

                        top_point_idx = top_sketch.addGeometry(Part.Point(App.Vector(tx, ty, 0)), False)
                        top_sketch.addConstraint(Sketcher.Constraint('PointOnObject', top_point_idx, 1, top_circle_idx))

                        top_line_idx = top_sketch.addGeometry(
                            Part.LineSegment(App.Vector(0, 0, 0), App.Vector(tx, ty, 0)),
                            True
                        )
                        top_line_indices.append(top_line_idx)
                        top_sketch.addConstraint(Sketcher.Constraint('Coincident', top_line_idx, 1, -1, 1))
                        top_sketch.addConstraint(Sketcher.Constraint('Coincident', top_line_idx, 2, top_point_idx, 1))

                        if i == 0:
                            top_xaxis_idx = top_sketch.addGeometry(
                                Part.LineSegment(App.Vector(0, 0, 0), App.Vector(1, 0, 0)),
                                True
                            )
                            top_sketch.addConstraint(Sketcher.Constraint('Coincident', top_xaxis_idx, 1, -1, 1))
                            top_sketch.addConstraint(Sketcher.Constraint('Horizontal', top_xaxis_idx))
                            top_angle_constraint = top_sketch.addConstraint(
                                Sketcher.Constraint('Angle', top_line_idx, top_xaxis_idx, top_angle)
                            )
                            top_sketch.setExpression(
                                f'Constraints[{top_angle_constraint}]',
                                'BowlVariables.TopAngle'
                            )

                    if num_points > 1:
                        angle_step_deg = 360.0 / num_points
                        print(f"Adding angle constraints between lines with step of {angle_step_deg} degrees")
                        for i in range(num_points - 1):
                            bottom_sketch.addConstraint(
                                Sketcher.Constraint('Angle', bottom_line_indices[i], bottom_line_indices[i + 1], math.radians(angle_step_deg))
                            )
                            top_sketch.addConstraint(
                                Sketcher.Constraint('Angle', top_line_indices[i], top_line_indices[i + 1], math.radians(angle_step_deg))
                            )
                    bottom_point_indices = []
                    top_point_indices = []
                    doc.recompute()

                    for i, geo in enumerate(bottom_sketch.Geometry):
                        if geo.TypeId == "Part::GeomPoint":
                            print(f"Bottom Sketch Geometry: {geo}")
                            bottom_point_indices.append(i)
                    for i, geo in enumerate(top_sketch.Geometry):
                        if geo.TypeId == "Part::GeomPoint":
                            print(f"Top Sketch Geometry: {geo}")
                            top_point_indices.append(i)
                    print(f"Bottom point indices: {bottom_point_indices}")
                    print(f"Top point indices: {top_point_indices}")
                    #bottom_point1 = bottom_sketch.getGeometry(bottom_point_indices[0])
                    #top_point1 = top_sketch.getGeometry(top_point_indices[0])

                    obj = doc.addObject('Part::DatumLine', 'DatumLine')
                    obj.AttachmentOffset = App.Placement(App.Vector(0, 0, 0), App.Rotation(0, 0, 0))
                    obj.MapReversed = False 
                    obj.AttachmentSupport = [(bottom_sketch, ';g6v1;SKT.Vertex3'), (top_sketch, ';g6v1;SKT.Vertex3')]
                    obj.MapPathParameter = 0.0
                    obj.MapMode = 'TwoPointLine'
                    obj.recompute()
                    doc.recompute()

                    obj = doc.addObject('Part::DatumLine', 'DatumLine')
                    obj.AttachmentOffset = App.Placement(App.Vector(0, 0, 0), App.Rotation(0, 0, 0))
                    obj.MapReversed = False 
                    obj.AttachmentSupport = [(bottom_sketch, ';g8v1;SKT.Vertex4'), (top_sketch, ';g8v1;SKT.Vertex4')]
                    obj.MapPathParameter = 0.0
                    obj.MapMode = 'TwoPointLine'
                    obj.recompute()
                    doc.recompute()

                    obj = doc.addObject('Part::DatumLine', 'DatumLine')
                    obj.AttachmentOffset = App.Placement(App.Vector(0, 0, 0), App.Rotation(0, 0, 0))
                    obj.MapReversed = False 
                    obj.AttachmentSupport = [(bottom_sketch, ';g3v1;SKT.Vertex2'), (top_sketch, ';g3v1;SKT.Vertex2')]
                    obj.MapPathParameter = 0.0
                    obj.MapMode = 'TwoPointLine'
                    obj.recompute()
                    doc.recompute()

#obj = App.activeDocument().addObject('Part::DatumLine','DatumLine')
#App.getDocument('Unnamed').getObject('DatumLine').AttachmentOffset = App.Placement(App.Vector(0.0000000000, 0.0000000000, 0.0000000000),  App.Rotation(0.0000000000, 0.0000000000, 0.0000000000))
#App.getDocument('Unnamed').getObject('DatumLine').MapReversed = False
#App.getDocument('Unnamed').getObject('DatumLine').AttachmentSupport = [(App.getDocument('Unnamed').getObject('Bottom_Sketch'),';g8v1;SKT.Vertex4'),(App.getDocument('Unnamed').getObject('Top_Sketch'),';g8v1;SKT.Vertex4')]
#App.getDocument('Unnamed').getObject('DatumLine').MapPathParameter = 0.000000
#App.getDocument('Unnamed').getObject('DatumLine').MapMode = 'TwoPointLine'
#App.getDocument('Unnamed').getObject('DatumLine').recompute()
                doc.recompute()
                App.Console.PrintMessage("Created Bottom_Sketch and Top_Sketch.\n")

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
            panel = OffcenterTurningPanel()
    
            # Show the task panel in FreeCAD
            Gui.Control.showDialog(panel)

        except Exception as e:
            App.Console.PrintError(f"Error adding panel: {str(e)}\n")
