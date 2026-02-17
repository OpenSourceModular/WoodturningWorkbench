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

"""
This module defines the AddVessel command for the Woodturning Workbench in FreeCAD.
The AddVessel command allows users to import an SVG file as a vessel profile, scale it
according to specified dimensions, and position it in the document for use in woodturning design.
"""
import FreeCAD as App
import FreeCADGui as Gui
from FreeCAD import Vector
from varsetOps import setVarsetValue, getVarsetValue
try:
    from PySide import QtGui, QtCore, QtWidgets
except ImportError:
    import importlib
    QtGui = importlib.import_module("PySide2.QtGui")
    QtCore = importlib.import_module("PySide2.QtCore")
    QtWidgets = importlib.import_module("PySide2.QtWidgets")

class AddVessel:
    
    def GetResources(self):
        """Return the command resources"""
        from pathlib import Path
        return {
            'Pixmap': str(Path(App.getUserAppDataDir()) / "Mod" / "WoodturningWorkbench" / "icons" / "AddVase.svg"),  
            'MenuText': 'Add Vessel Profile',
            'ToolTip': 'Add a Vase/Bowl profile to the document from an SVG file'
        }

    def IsActive(self):
        """Check if the command is active"""
        return App.ActiveDocument is not None

    def Activated(self):
        """Execute the command"""
        class AddVesselPanel:
            #Creates the Task Panel
            def __init__(self):
                import FreeCAD
                from pathlib import Path
                doc = FreeCAD.activeDocument()	
                self.form = QtWidgets.QWidget()
                self.form.setWindowTitle("Import Vessel Profile from SVG")
                #Local Variables with Default Values
                self.svg_height = 254  # Height to scale the SVG to (mm)
                self.svg_width = 100  # Width to scale the SVG to (mm), if None it will be scaled proportionally based on height
                self.num_vessels = 9
                if not doc.getObject("BowlVariables"):
                    self.varset = doc.addObject("App::VarSet", "BowlVariables")
                    # Add a variable (property) to the VarSet
                    # Syntax: addProperty(type, name, group, tooltip)
                    self.varset.addProperty("App::PropertyInteger", "NumSegments", "General", "Number of segments for the bowl")
                    self.varset.NumSegments = 12
                    self.varset.addProperty("App::PropertyLength", "BowlHeight", "General", "Height of the bowl")
                    self.varset.BowlHeight = self.svg_height
                    self.varset.addProperty("App::PropertyLength", "BowlWidth", "General", "Width of the bowl")
                    self.varset.BowlWidth = self.svg_width
                    self.varset.addProperty("App::PropertyLength", "LayerHeight", "General", "Height of each layer")
                    self.varset.LayerHeight = 25.4
                    self.varset.addProperty("App::PropertyAngle", "RotateAngle", "General", "Rotation angle for rings")
                    self.varset.RotateAngle = 15.0
                    self.varset.addProperty("App::PropertyLength", "WallThickness", "General", "Wall thickness of the bowl")
                    self.varset.WallThickness = 10.0	
                # Create layout
                layout = QtWidgets.QVBoxLayout()

                text_box_layout = QtWidgets.QHBoxLayout()
                image_y_size_label = QtWidgets.QLabel("Image Height(mm):")
                self.image_y_size_input = QtWidgets.QLineEdit()
                self.image_y_size_input.setToolTip("Image height in mm.")
                self.image_y_size_input.setText("254")
                self.image_y_size_input.editingFinished.connect(lambda: self.update_text_boxes('y-mm'))
                text_box_layout.addWidget(image_y_size_label)
                text_box_layout.addWidget(self.image_y_size_input)
                
                image_x_size_label = QtWidgets.QLabel("Image Width(mm):")
                self.image_x_size_input = QtWidgets.QLineEdit()
                self.image_x_size_input.setToolTip("Image width in mm.")
                self.image_x_size_input.setText("100")
                self.image_x_size_input.editingFinished.connect(lambda: self.update_text_boxes('x-mm'))
                text_box_layout.addWidget(image_x_size_label)
                text_box_layout.addWidget(self.image_x_size_input)

                text_box2_layout = QtWidgets.QHBoxLayout()
                image_y_size_in_label = QtWidgets.QLabel("Image Height(in):")
                self.image_y_size_in_input = QtWidgets.QLineEdit()
                self.image_y_size_in_input.setToolTip("Image height in inches.")
                self.image_y_size_in_input.setText(str(round(self.svg_height / 25.4, 2)))
                self.image_y_size_in_input.editingFinished.connect(lambda: self.update_text_boxes('y-in'))
                text_box2_layout.addWidget(image_y_size_in_label)
                text_box2_layout.addWidget(self.image_y_size_in_input)
                
                image_x_size_in_label = QtWidgets.QLabel("Image Width(in):")
                self.image_x_size_in_input = QtWidgets.QLineEdit()
                self.image_x_size_in_input.setToolTip("Image width in inches.")
                self.image_x_size_in_input.setText(str(round(self.svg_width / 25.4, 2)))
                self.image_x_size_in_input.editingFinished.connect(lambda: self.update_text_boxes('x-in'))
                text_box2_layout.addWidget(image_x_size_in_label)
                text_box2_layout.addWidget(self.image_x_size_in_input)                
                
                # Radio buttons for scaling preference
                scaling_group = QtWidgets.QGroupBox("Scale By:")
                scaling_layout = QtWidgets.QHBoxLayout()
                
                self.scale_by_y_radio = QtWidgets.QRadioButton("Height")
                self.scale_by_x_radio = QtWidgets.QRadioButton("Width")
                self.scale_by_y_radio.setChecked(True)  # Default to Y
                
                scaling_layout.addWidget(self.scale_by_y_radio)
                scaling_layout.addWidget(self.scale_by_x_radio)
                scaling_group.setLayout(scaling_layout)
                #text_box_layout.addWidget(scaling_group)
                
                layout.addLayout(text_box_layout)
                layout.addLayout(text_box2_layout)
                layout.addWidget(scaling_group)

                def add_vessel_button(vessel_number):
                    """
                    Helper function to create a button for adding a vessel profile
                    """
                    image_path = Path(FreeCAD.getUserAppDataDir()) / "Mod" / "WoodturningWorkbench" / "resources" / f"vase{vessel_number}.png"
                    button = QtWidgets.QPushButton()
                    button.setIcon(QtGui.QIcon(str(image_path)))
                    button.setIconSize(QtCore.QSize(48, 48))  # Set the icon size
                    return button

                p = self.num_vessels//4
                if self.num_vessels % 4 != 0:
                    p += 1
                button_index = 1
                for i in range(p):
                    button_layout = QtWidgets.QHBoxLayout()
                    for j in range(4):
                        if button_index <= self.num_vessels:
                            button = add_vessel_button(button_index)
                            button.setToolTip("Import this vessel profile")
                            button.clicked.connect(lambda checked, num=button_index: self.bt_add_vessel_clicked(f"vase{num}.svg"))
                            button_layout.addWidget(button)
                            button_index += 1
                    layout.addLayout(button_layout)
                
                # Button layout
                button_layout = QtWidgets.QHBoxLayout()

                # Add Bowl Outlines button
                self.browse_vase_button = QtWidgets.QPushButton("Browse SVG")
                self.browse_vase_button.clicked.connect(self.bt_browse_vase)
                self.browse_vase_button.setToolTip("Browse for a custom SVG file to import as a vessel profile")

                self.delete_vase_button = QtWidgets.QPushButton("Delete Vase")
                self.delete_vase_button.clicked.connect(self.bt_delete_vase)
                self.delete_vase_button.setToolTip("Delete all vessel profiles")

                self.cancel_button = QtWidgets.QPushButton("Close")
                self.cancel_button.clicked.connect(self.on_cancel)
                #button_layout.addWidget(self.add_vase_button)
                button_layout.addWidget(self.browse_vase_button)
                button_layout.addWidget(self.delete_vase_button)
                button_layout.addWidget(self.cancel_button)
                layout.addLayout(button_layout)
            
                # Add stretch at end
                layout.addStretch()
                
                self.form.setLayout(layout)
 
                

            def update_values(self):
                """
                Update internal variables based on text box values and scaling preference
                """
                self.svg_height = float(self.image_y_size_input.text())
                self.svg_width = float(self.image_x_size_input.text()) 
                self.scale_by_y = self.scale_by_y_radio.isChecked()

            def update_text_boxes(self, source):
                """
                Update text boxes based on the source of the change
                If a user changes a mm box, update the corresponding inch box and vice versa. Also update internal variables.
                """
                print("Updating text boxes")
                print(source)
                if source == 'y-mm':
                    try:
                        self.svg_height = float(self.image_y_size_input.text())
                        self.image_y_size_in_input.setText(str(round(self.svg_height / 25.4, 2)))
                    except ValueError:
                        pass  # Ignore invalid input
                elif source == 'x-mm':
                    try:
                        self.svg_width = float(self.image_x_size_input.text())
                        self.image_x_size_in_input.setText(str(round(self.svg_width / 25.4, 2)))
                    except ValueError:
                        pass  # Ignore invalid input
                elif source == 'y-in':
                    try:
                        self.svg_height = float(self.image_y_size_in_input.text()) * 25.4
                        self.image_y_size_input.setText(str(round(self.svg_height, 2)))
                    except ValueError:
                        pass  # Ignore invalid input
                elif source == 'x-in':
                    try:
                        self.svg_width = float(self.image_x_size_in_input.text()) * 25.4
                        self.image_x_size_input.setText(str(round(self.svg_width, 2)))
                    except ValueError:
                        pass  # Ignore invalid input
            
            def bt_add_vessel_clicked(self, vase_name):
                """
                Handle click event for adding a vessel profile. 
                This will add the specified SVG file as an image object, scale it according 
                to the current settings, and position it in the document so that the origin is at the bottom middle.                       
                """
                self.update_values()
                try:
                    import FreeCAD
                    from freecad import module_io
                    doc = FreeCAD.ActiveDocument
                    from pathlib import Path
                    #vase_name = "vase1.svg"
                    image = str(Path(FreeCAD.getUserAppDataDir()) / "Mod" / "WoodturningWorkbench" / "resources" / vase_name )
                    #image += "vase1.png"
                    a_vase = module_io.OpenInsertObject("FreeCADGui", image, "insert", "Unnamed")
                    doc.recompute()
                    
                    for obj in doc.Objects:
                        print(obj.Name, obj.TypeId)
                        if obj.TypeId == "Image::ImagePlane":
                            vase_obj = obj
                    
                    if self.scale_by_y:
                        # Scale by Y value
                        y = vase_obj.YSize
                        scale_factor = self.svg_height / y
                        new_x_size = vase_obj.XSize * scale_factor
                        vase_obj.YSize = self.svg_height
                        vase_obj.XSize = new_x_size
                        self.svg_width = new_x_size
                    else:
                        # Scale by X value
                        if self.svg_width:
                            x = vase_obj.XSize
                            scale_factor = self.svg_width / x
                            new_y_size = vase_obj.YSize * scale_factor
                            vase_obj.XSize = self.svg_width
                            vase_obj.YSize = new_y_size
                            self.svg_height = new_y_size
                        else:
                            # If X size not provided, fall back to Y scaling
                            y = vase_obj.YSize
                            scale_factor = self.svg_height / y
                            new_x_size = vase_obj.XSize * scale_factor
                            vase_obj.YSize = self.svg_height
                            vase_obj.XSize = new_x_size
                            self.svg_width = new_x_size
                    
                    vase_obj.Placement = FreeCAD.Placement(FreeCAD.Vector(0,0,self.svg_height/2),FreeCAD.Rotation(FreeCAD.Vector(1,0,0),90))
                    setVarsetValue(self, "BowlHeight", self.svg_height)
                    setVarsetValue(self, "BowlWidth", self.svg_width)
                    self.image_x_size_input.setText(str(round(self.svg_width, 2)))
                    self.image_y_size_input.setText(str(round(self.svg_height, 2)))
                    self.image_x_size_in_input.setText(str(round(self.svg_width / 25.4, 2)))
                    self.image_y_size_in_input.setText(str(round(self.svg_height / 25.4, 2)))
                    doc.recompute()
                    Gui.activeDocument().activeView().viewFront()
                    Gui.SendMsgToActiveView("ViewFit")
                    Gui.activeDocument().activeView().setAxisCross(True)
                    
                except Exception as e:
                    FreeCAD.Console.PrintError(f"Error adding vase: {str(e)}\n")

            def bt_delete_vase(self):
                """
                Delete any image objects that start with 'vase' in the document. 
                This is a simple way to remove previously added vessel profiles.
                """
                try:
                    import FreeCAD
                    doc = FreeCAD.ActiveDocument
                    
                    # Collect objects to delete (can't delete while iterating)
                    objects_to_delete = []
                    for obj in doc.Objects:
                        if obj.Name.lower().startswith("vase"):
                            doc.removeObject(obj.Name)
                    
                except Exception as e:
                    FreeCAD.Console.PrintError(f"Error deleting vase: {str(e)}\n")

            def bt_browse_vase(self):
                """
                Open a file dialog to browse for an SVG file, then add and scale it as a vessel profile
                """
                try:
                    import FreeCAD
                    from pathlib import Path
                    
                    # Open file dialog
                    file_dialog = QtWidgets.QFileDialog()
                    file_path, _ = file_dialog.getOpenFileName(
                        None,
                        "Select SVG File",
                        str(Path.home()),  # Start in home directory
                        "SVG Files (*.svg);;All Files (*)"
                    )
                    
                    if not file_path:
                        FreeCAD.Console.PrintMessage("File selection cancelled\n")
                        return
                    
                    # Verify file exists
                    if not Path(file_path).exists():
                        FreeCAD.Console.PrintError(f"File not found: {file_path}\n")
                        return
                    
                    # Add and scale the vase
                    self._add_and_scale_vase(file_path)
                    
                except Exception as e:
                    FreeCAD.Console.PrintError(f"Error browsing vase file: {str(e)}\n")

            def _add_and_scale_vase(self, file_path):
                """
                Helper method to add and scale a vase SVG file
                """
                try:
                    import FreeCAD
                    from freecad import module_io
                    
                    self.update_values()
                    doc = FreeCAD.ActiveDocument
                    
                    # Insert the SVG file
                    a_vase = module_io.OpenInsertObject("FreeCADGui", file_path, "insert", "Unnamed")
                    doc.recompute()
                    FreeCAD.Console.PrintMessage(f"Vase added from: {file_path}\n")
                    
                    # Find the image object
                    vase_obj = None
                    for obj in doc.Objects:
                        if obj.TypeId == "Image::ImagePlane":
                            vase_obj = obj
                    
                    if not vase_obj:
                        FreeCAD.Console.PrintError("Could not find image object\n")
                        return
                    
                    # Apply scaling logic
                    if self.scale_by_y:
                        # Scale by Y value
                        y = vase_obj.YSize
                        scale_factor = self.svg_height / y
                        new_x_size = vase_obj.XSize * scale_factor
                        vase_obj.YSize = self.svg_height
                        vase_obj.XSize = new_x_size
                    else:
                        # Scale by X value
                        if self.svg_width:
                            x = vase_obj.XSize
                            scale_factor = self.svg_width / x
                            new_y_size = vase_obj.YSize * scale_factor
                            vase_obj.XSize = self.svg_width
                            vase_obj.YSize = new_y_size
                        else:
                            # If X size not provided, fall back to Y scaling
                            y = vase_obj.YSize
                            scale_factor = self.svg_height / y
                            new_x_size = vase_obj.XSize * scale_factor
                            vase_obj.YSize = self.svg_height
                            vase_obj.XSize = new_x_size
                    
                    vase_obj.Placement = FreeCAD.Placement(FreeCAD.Vector(0, 0, self.svg_height / 2), FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), 90))
                    self.update_values()
                    doc.recompute()
                    Gui.activeDocument().activeView().viewFront()
                    Gui.SendMsgToActiveView("ViewFit")
                    FreeCAD.Console.PrintMessage("Vase scaled and positioned\n")
                    
                except Exception as e:
                    FreeCAD.Console.PrintError(f"Error adding and scaling vase: {str(e)}\n")

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
                return 0		
        try:
            panel = AddVesselPanel()
    
            # Show the task panel in FreeCAD
            Gui.Control.showDialog(panel)

        except Exception as e:
            App.Console.PrintError(f"Error adding panel: {str(e)}\n")
