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


class MakeBowlSolid:
    
    
    def GetResources(self):
        """Return the command resources"""
        from pathlib import Path
        return {
            'Pixmap': str(Path(__file__).parent / 'MakeBowlSolid.svg'),  # You can add an icon path here
            'MenuText': 'Make Bowl Solid',
            'ToolTip': 'Make a solid bowl from segments'
        }

    def IsActive(self):
        """Check if the command is active"""
        return FreeCAD.ActiveDocument is not None

    def Activated(self):
        """Execute the command"""
        class MakeBowlSolidTaskPanel:
    #Creates the Task Panel
            def __init__(self):
                
                from PySide import QtGui, QtCore, QtWidgets	
                self.form = QtWidgets.QWidget()
                self.form.setWindowTitle("Make Bowl Solid")
                #Local Variables with Default Values
                
                self.thickness = 10.0
                # Create layout
                layout = QtWidgets.QVBoxLayout()
                
                # Title
                title_label = QtWidgets.QLabel("MakeBowlSolid Parameters")
                title_font = title_label.font()
                title_font.setPointSize(12)
                title_font.setBold(True)
                title_label.setFont(title_font)
                layout.addWidget(title_label)

                thickness_layout = QtWidgets.QHBoxLayout()
                thickness_label = QtWidgets.QLabel("Wall Thickness:")
                thickness_label.setMinimumWidth(150)
                self.thickness_input = QtWidgets.QLineEdit()
                self.thickness_input.setText("10.0")
                self.thickness_input.setPlaceholderText("Enter wall thickness")
                thickness_layout.addWidget(thickness_label)
                thickness_layout.addWidget(self.thickness_input)
                layout.addLayout(thickness_layout)

        # Add spacing
                layout.addSpacing(20)
                
                # Button layout
                button_layout = QtWidgets.QHBoxLayout()
                
                # Add Segments button
                self.make_bowl_solid_button = QtWidgets.QPushButton("Make Bowl Solid")
                self.make_bowl_solid_button.clicked.connect(self.bt_make_bowl_solid_click)
                button_layout.addWidget(self.make_bowl_solid_button)

               
                # Cancel button
                self.cancel_button = QtWidgets.QPushButton("Close")
                self.cancel_button.clicked.connect(self.on_cancel)
                button_layout.addWidget(self.cancel_button)
                
                layout.addLayout(button_layout)

                # Add stretch at end
                layout.addStretch()
                
                self.form.setLayout(layout)

            def bt_make_bowl_solid_click(self):
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
                #doc.Revolve.Base = (1.23456789,2.34567891,3.45678912)
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

                print(a_revolve)

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
                        a_revolve.Visibility = False
                    except Exception:
                        try:
                            a_revolve.ViewObject.Visibility = False
                        except Exception:
                            pass
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
                doc.BowlSolid.Value = -self.thickness
                solid_obj.Visibility = False
                a_thickness.Placement = App.Placement(App.Vector(0,0,0),App.Rotation(App.Vector(0,0,1),90))
                a_thickness.ViewObject.Transparency = 50
                



                doc.recompute()
                print(f"Created BSpline '{bs_obj.Name}' with {len(poles)} poles from sketch '{sketch.Name}'.")

            def set_tooltips(self):
                self.make_bowl_solid_button.setToolTip("Make a solid bowl from points")


            def update_values(self):
                #Update the local variables with the values in the text boxes
                self.thickness = float(self.thickness_input.text())

            
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
            panel = MakeBowlSolidTaskPanel()
    
            # Show the task panel in FreeCAD
            FreeCADGui.Control.showDialog(panel)


        except Exception as e:
            FreeCAD.Console.PrintError(f"Error adding segments: {str(e)}\n")
