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
from varsetOps import getVarsetInt
from pathlib import Path

class TopView:
    
    def GetResources(self):
        """Return the command resources"""
        from pathlib import Path
        return {
            'Pixmap': str(Path(App.getUserAppDataDir()) / "Mod" / "WoodturningWorkbench" / "icons" / "TopView.svg"),  
            'MenuText': 'Top View',
            'ToolTip': 'Top View Command'
        }

    def IsActive(self):
        """Check if the command is active"""
        return App.ActiveDocument is not None

    def Activated(self):
        """Execute the command"""
        class TopViewPanel:
            #Creates the Task Panel
            def __init__(self):

                self.form = QtWidgets.QWidget()
                self.form.setWindowTitle("Create Top View of Segments")
                #Local Variables with Default Values
                self.num_segments = getVarsetInt(self,"NumSegments")  
                self.segment_original_locations = []

                # Create layout
                layout = QtWidgets.QVBoxLayout()
                
                text_box_layout = QtWidgets.QVBoxLayout()
                input_A_label = QtWidgets.QLabel("Input A:")
                self.A_input = QtWidgets.QLineEdit()
                self.A_input.setText("A")
 
                layout.addLayout(text_box_layout)

                # Add spacing
                layout.addSpacing(20)
                
                # Button layout
                button_layout1 = QtWidgets.QHBoxLayout()

                # Add rotate segments button
                self.button_rotate_segments = QtWidgets.QPushButton("Rotate Segments")
                self.button_rotate_segments.clicked.connect(self.bt_rotate_segments)
                button_layout1.addWidget(self.button_rotate_segments)

                # Add make drawing button
                self.button_make_drawing = QtWidgets.QPushButton("Make Drawing")
                self.button_make_drawing.clicked.connect(self.bt_make_drawing)
                button_layout1.addWidget(self.button_make_drawing)

                button_layout2 = QtWidgets.QHBoxLayout()
                # Add array segments for plan button
                self.button_array_segments_for_plan = QtWidgets.QPushButton("Array Segments for Plan")
                self.button_array_segments_for_plan.clicked.connect(self.bt_array_segments_for_plan)
                button_layout2.addWidget(self.button_array_segments_for_plan)

                
                # Add restore segment locations button
                self.button_restore_segment_locations = QtWidgets.QPushButton("Restore Segment Locations")
                self.button_restore_segment_locations.clicked.connect(self.bt_restore_segment_locations)
                button_layout2.addWidget(self.button_restore_segment_locations)
                
                button_layout3 = QtWidgets.QHBoxLayout()
                # Add close button
                self.button_close = QtWidgets.QPushButton("Close")
                self.button_close.clicked.connect(self.on_cancel)
                button_layout3.addWidget(self.button_close)

                layout.addLayout(button_layout1)
                layout.addLayout(button_layout2)
                layout.addLayout(button_layout3)
                # Add stretch at end
                layout.addStretch()
                self.form.setLayout(layout)

            def bt_rotate_segments(self):
                """Handler for Rotate Segments button click"""
                App.Console.PrintMessage("Rotate Segments button clicked\n")
                doc = App.ActiveDocument
                Gui.ActiveDocument.ActiveView.viewTop()
                segment_objects = self._get_segment_objects()
                if not segment_objects:
                    App.Console.PrintError("No segment objects found.\n")
                    return

                current_names = [obj.Name for obj in segment_objects]
                saved_names = [name for name, _ in self.segment_original_locations]
                if (not self.segment_original_locations) or (saved_names != current_names):
                    self.segment_original_locations = [
                        (obj.Name, App.Placement(obj.Placement)) for obj in segment_objects
                    ]
                    App.Console.PrintMessage(
                        f"Saved original locations for {len(self.segment_original_locations)} segments.\n"
                    )                
                segment_list = []
                for obj in doc.Objects:
                    print(f"Object: {obj.Name}, Label: {obj.Label}")
                    if obj.Label.startswith("Segment"):
                        if hasattr(obj, "ViewObject"):
                            obj.ViewObject.Visibility = True
                        segment_list.append(obj.Label)
                    else:
                        if hasattr(obj, "ViewObject"): 
                            obj.ViewObject.Visibility = False
                    segment_list.sort()
                start_angle = 0
                rotation_angle = 360 / self.num_segments
                count = 0
                for label in segment_list:
                    print(f"Segment Object: {label}")
                    obj = doc.getObjectsByLabel(label)[0]
                    incremental_rotation = App.Placement(App.Vector(0,0,0), App.Vector(0,0,1), rotation_angle*count).Rotation
                    obj.Placement = App.Placement(obj.Placement.Base, incremental_rotation.multiply(obj.Placement.Rotation))
                    count += 1

            def bt_array_segments_for_plan(self):
                """Arrange segment objects in a rectangular X/Y array for plan view."""
                doc = App.ActiveDocument
                if doc is None:
                    App.Console.PrintError("No active document found.\n")
                    return

                Gui.ActiveDocument.ActiveView.viewTop()
                segment_objects = self._get_segment_objects()
                if not segment_objects:
                    App.Console.PrintError("No segment objects found.\n")
                    return

                current_names = [obj.Name for obj in segment_objects]
                saved_names = [name for name, _ in self.segment_original_locations]
                if (not self.segment_original_locations) or (saved_names != current_names):
                    self.segment_original_locations = [
                        (obj.Name, App.Placement(obj.Placement)) for obj in segment_objects
                    ]
                    App.Console.PrintMessage(
                        f"Saved original locations for {len(self.segment_original_locations)} segments.\n"
                    )

                cols = 4
                cols = max(1, int(cols))

                max_x = 0.0
                max_y = 0.0
                for obj in segment_objects:
                    if hasattr(obj, "Shape") and hasattr(obj.Shape, "BoundBox"):
                        bbox = obj.Shape.BoundBox
                        max_x = max(max_x, bbox.XLength)
                        max_y = max(max_y, bbox.YLength)

                spacing_x = (max_x) 
                spacing_y = (max_y) 
                
                for index, obj in enumerate(segment_objects):
                    col = index % cols
                    row = index // cols
                    current_base = obj.Placement.Base
                    #target_base = App.Vector(spacing_x * col, spacing_y * row, current_base.z)
                    target_base = App.Vector(spacing_x * col, spacing_y * row, 0)
                    obj.Placement = App.Placement(
                        target_base,
                        obj.Placement.Rotation,
                    )
                    if hasattr(obj, "ViewObject"):
                        obj.ViewObject.Visibility = True

                doc.recompute()
                App.Console.PrintMessage(
                    f"Arrayed {len(segment_objects)} segment objects for plan view in {cols} columns.\n"
                )

            def bt_restore_segment_locations(self):
                """Restore segment objects to their saved original placements."""
                doc = App.ActiveDocument
                if doc is None:
                    App.Console.PrintError("No active document found.\n")
                    return

                if not self.segment_original_locations:
                    App.Console.PrintError("No saved segment locations found.\n")
                    return

                restored_count = 0
                missing_count = 0
                for object_name, saved_placement in self.segment_original_locations:
                    obj = doc.getObject(object_name)
                    if obj is None:
                        missing_count += 1
                        continue
                    obj.Placement = App.Placement(saved_placement)
                    restored_count += 1

                doc.recompute()
                App.Console.PrintMessage(
                    f"Restored {restored_count} segment locations. Missing: {missing_count}.\n"
                )

            def _get_segment_objects(self):
                """Return all objects with labels starting with Segment."""
                doc = App.ActiveDocument
                if doc is None:
                    return []
                segment_objects = []
                for obj in doc.Objects:
                    if hasattr(obj, "Label") and obj.Label.startswith("Segment"):
                        segment_objects.append(obj)
                segment_objects.sort(key=lambda o: o.Label)
                return segment_objects

            def _get_techdraw_template(self):
                """Return a template path for the new TechDraw page, if available."""
                candidates = [
                    Path(App.getResourceDir()) / "Mod" / "TechDraw" / "Templates" / "ISO" / "A4_Landscape_blank.svg",
                    #Path(App.getResourceDir()) / "Mod" / "TechDraw" / "Templates" / "ISO" / "A4_Landscape.svg",
                ]
                for candidate in candidates:
                    if candidate.exists():
                        return str(candidate)
                return None

            def bt_make_drawing(self):
                """Create a new TechDraw sheet and add a view of all segment objects."""
                doc = App.ActiveDocument
                if doc is None:
                    App.Console.PrintError("No active document found.\n")
                    return

                segment_objects = self._get_segment_objects()
                if not segment_objects:
                    App.Console.PrintError("No segment objects found.\n")
                    return

                Gui.Selection.clearSelection()
                for segment_obj in segment_objects:
                    Gui.Selection.addSelection(doc.Name, segment_obj.Name)

                page = doc.addObject("TechDraw::DrawPage", "TopViewPage")
                template_path = self._get_techdraw_template()
                if template_path:
                    template = doc.addObject("TechDraw::DrawSVGTemplate", "TopViewTemplate")
                    template.Template = template_path
                    page.Template = template

                view = doc.addObject("TechDraw::DrawViewPart", "TopViewSegments")
                view.Source = segment_objects
                view.Direction = App.Vector(0, 0, 1)
                page.addView(view)
                self.get_selected_bounding_box()  # Print bounding box info for selected objects
                #Gui.Selection.clearSelection()
                #Gui.Selection.addSelection(doc.Name, 'Edge1')  # Select the first edge of the view to make dimensions available
# # Gui.Selection.addSelection('Unnamed','TopViewSegments','Edge1')
# ### Begin command TechDraw_CompDimensionTools
# App.activeDocument().addObject('TechDraw::DrawViewDimension', 'Dimension003')
# App.activeDocument().Dimension003.translateLabel('DrawViewDimension', 'Dimension', 'Dimension003')
# App.activeDocument().Dimension003.Type = 'Distance'
# App.activeDocument().Dimension003.MeasureType = 'Projected'
# App.activeDocument().TopViewPage.addView(App.activeDocument().Dimension003)                

                doc.recompute()
                App.Console.PrintMessage(f"Created TechDraw sheet with {len(segment_objects)} segment objects.\n")
            def get_selected_bounding_box(self):
                combined_bbox = App.BoundBox()
    
    # Iterate through selected objects and add their bounding boxes
                selected_objects = Gui.Selection.getSelection()
                for obj in selected_objects:
                    try:
                        # Access the Shape.BoundBox attribute
                        bbox = obj.Shape.BoundBox
                        combined_bbox.add(bbox) # Combine all selected object bounding boxes
                        App.Console.PrintMessage(f"Object: {obj.Name}\n")
                        App.Console.PrintMessage(f"  X min/max: {bbox.XMin}, {bbox.XMax}\n")
                        App.Console.PrintMessage(f"  Y min/max: {bbox.YMin}, {bbox.YMax}\n")
                        App.Console.PrintMessage(f"  Z min/max: {bbox.ZMin}, {bbox.ZMax}\n")
                        #App.Console.PrintMessage(f"  Length: {bbox.Length}, Width: {bbox.Width}, Height: {bbox.Height}\n")
                    except Exception as e:
                        App.Console.PrintMessage(f"Could not get bounding box for {obj.Name}: {e}\n")

                # Print the combined bounding box for all selected objects
                App.Console.PrintMessage("\nCombined Bounding Box:\n")
                App.Console.PrintMessage(f"  X min/max: {combined_bbox.XMin}, {combined_bbox.XMax}\n")
                App.Console.PrintMessage(f"  Y min/max: {combined_bbox.YMin}, {combined_bbox.YMax}\n")
                App.Console.PrintMessage(f"  Z min/max: {combined_bbox.ZMin}, {combined_bbox.ZMax}\n")
                #App.Console.PrintMessage(f"  Total Length: {combined_bbox.Length}, Total Width: {combined_bbox.Width}, Total Height: {combined_bbox.Height}\n")
            
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
            panel = TopViewPanel()
    
            # Show the task panel in FreeCAD
            Gui.Control.showDialog(panel)

        except Exception as e:
            App.Console.PrintError(f"Error adding panel: {str(e)}\n")
