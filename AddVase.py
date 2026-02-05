"""
AddSegments.py - Command to add segments to a bowl design
"""

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
from varsetOps import setVarsetValue, getVarsetValue

class AddVase:
    
    def GetResources(self):
        """Return the command resources"""
        from pathlib import Path
        return {
            'Pixmap': str(Path(App.getUserAppDataDir()) / "Mod" / "WoodturningWorkbench" / "icons" / "AddVase.svg"),  
            'MenuText': 'Add Vase Profile',
            'ToolTip': 'Add Vase Profile Command'
        }

    def IsActive(self):
        """Check if the command is active"""
        return App.ActiveDocument is not None

    def Activated(self):
        """Execute the command"""
        class AddVasePanel:
            #Creates the Task Panel
            def __init__(self):
                import FreeCAD
                import FreeCADGui
                from PySide import QtGui, QtCore, QtWidgets
                from pathlib import Path
                doc = FreeCAD.activeDocument()	
                self.form = QtWidgets.QWidget()
                self.form.setWindowTitle("Import Vase")
                #Local Variables with Default Values
                self.svg_height = 254  # Height to scale the SVG to (mm)
                if not doc.getObject("BowlVariables"):
                    self.varset = doc.addObject("App::VarSet", "BowlVariables")
                    # Add a variable (property) to the VarSet
                    # Syntax: addProperty(type, name, group, tooltip)
                    self.varset.addProperty("App::PropertyInteger", "NumSegments", "General", "Number of segments for the bowl")
                    self.varset.NumSegments = 12
                    self.varset.addProperty("App::PropertyLength", "BowlHeight", "General", "Height of the bowl")
                    self.varset.BowlHeight = self.svg_height
                    self.varset.addProperty("App::PropertyLength", "LayerHeight", "General", "Height of each layer")
                    self.varset.LayerHeight = 25.4
                    self.varset.addProperty("App::PropertyAngle", "RotateAngle", "General", "Rotation angle for rings")
                    self.varset.RotateAngle = 15.0
                    self.varset.addProperty("App::PropertyLength", "WallThickness", "General", "Wall thickness of the bowl")
                    self.varset.WallThickness = 10.0	
                # Create layout
                layout = QtWidgets.QVBoxLayout()

                title_label = QtWidgets.QLabel("Import Vase Parameters")
                title_font = title_label.font()
                title_font.setPointSize(12)
                title_font.setBold(True)
                title_label.setFont(title_font)
                layout.addWidget(title_label)

                text_box_layout = QtWidgets.QVBoxLayout()
                image_y_size_label = QtWidgets.QLabel("Image Y Size:")
                self.image_y_size_input = QtWidgets.QLineEdit()
                self.image_y_size_input.setText("254")
                text_box_layout.addWidget(image_y_size_label)
                text_box_layout.addWidget(self.image_y_size_input)
                layout.addLayout(text_box_layout)

                vases_layout = QtWidgets.QHBoxLayout()
                image_path = Path(FreeCAD.getUserAppDataDir()) / "Mod" / "WoodturningWorkbench" / "resources" / "vase1.png"
                btn1 = QtWidgets.QPushButton()
                btn1.setIcon(QtGui.QIcon(str(image_path)))
                btn1.setIconSize(QtCore.QSize(48, 48))   # icon display size
                btn1.clicked.connect(self.bt_click_vase1)

                image_path = Path(FreeCAD.getUserAppDataDir()) / "Mod" / "WoodturningWorkbench" / "resources" / "vase2.png"
                btn2 = QtWidgets.QPushButton()
                btn2.setIcon(QtGui.QIcon(str(image_path)))
                btn2.setIconSize(QtCore.QSize(48, 48))   # icon display size
                btn2.clicked.connect(self.bt_click_vase2)					

                vases_layout.addWidget(btn1)
                vases_layout.addWidget(btn2)
                layout.addLayout(vases_layout)	

                vases_layout2 = QtWidgets.QHBoxLayout()
                image_path = Path(FreeCAD.getUserAppDataDir()) / "Mod" / "WoodturningWorkbench" / "resources" / "vase3.png"
                btn3 = QtWidgets.QPushButton()
                btn3.setIcon(QtGui.QIcon(str(image_path)))
                btn3.setIconSize(QtCore.QSize(48, 48))   # icon display size
                btn3.clicked.connect(self.bt_click_vase3)

                image_path = Path(FreeCAD.getUserAppDataDir()) / "Mod" / "WoodturningWorkbench" / "resources" / "vase4.png"
                btn4 = QtWidgets.QPushButton()
                btn4.setIcon(QtGui.QIcon(str(image_path)))
                btn4.setIconSize(QtCore.QSize(48, 48))   # icon display size
                btn4.clicked.connect(self.bt_click_vase4)					

                vases_layout2.addWidget(btn3)
                vases_layout2.addWidget(btn4)
                layout.addLayout(vases_layout2)

                vases_layout3 = QtWidgets.QHBoxLayout()
                image_path = Path(FreeCAD.getUserAppDataDir()) / "Mod" / "WoodturningWorkbench" / "resources" / "vase5.png"
                btn5 = QtWidgets.QPushButton()
                btn5.setIcon(QtGui.QIcon(str(image_path)))
                btn5.setIconSize(QtCore.QSize(48, 48))   # icon display size
                btn5.clicked.connect(self.bt_click_vase5)

                image_path = Path(FreeCAD.getUserAppDataDir()) / "Mod" / "WoodturningWorkbench" / "resources" / "vase4.png"
                btn6 = QtWidgets.QPushButton()
                btn6.setIcon(QtGui.QIcon(str(image_path)))
                btn6.setIconSize(QtCore.QSize(48, 48))   # icon display size
                btn6.clicked.connect(self.bt_click_vase4)					

                vases_layout2.addWidget(btn5)
                vases_layout2.addWidget(btn6)
                layout.addLayout(vases_layout3)

                # Button layout
                button_layout = QtWidgets.QHBoxLayout()

                # Add Bowl Outlines button

                self.cancel_button = QtWidgets.QPushButton("Close")
                self.cancel_button.clicked.connect(self.on_cancel)
                #button_layout.addWidget(self.add_vase_button)
                button_layout.addWidget(self.cancel_button)
                layout.addLayout(button_layout)
            
                # Add stretch at end
                layout.addStretch()
                
                self.form.setLayout(layout)

            def set_tooltips(self):
                self.add_vase_button.setToolTip("Add the Vase to the document")

            def update_values(self):
                #Update the local variables with the values in the text boxes
                self.svg_height = float(self.image_y_size_input.text())
                setVarsetValue(self, "BowlHeight", self.svg_height)
                
            def bt_add_vase_click_it(self):
                vase_name = "vase1.svg"
                self.bt_add_vase_clicked(vase_name)

            def bt_click_vase1(self):
                vase_name = "vase1.svg"
                self.bt_add_vase_clicked(vase_name)

            def bt_click_vase2(self):
                vase_name = "vase2.svg"
                self.bt_add_vase_clicked(vase_name)
            
            def bt_click_vase3(self):
                vase_name = "vase3.svg"
                self.bt_add_vase_clicked(vase_name)	
            
            def bt_click_vase4(self):
                vase_name = "vase4.svg"
                self.bt_add_vase_clicked(vase_name)	

            def bt_click_vase5(self):
                vase_name = "vase5.svg"
                self.bt_add_vase_clicked(vase_name)	
            
            def bt_click_vase6(self):
                vase_name = "vase6.svg"
                self.bt_add_vase_clicked(vase_name)	
            
            def bt_add_vase_clicked(self, vase_name):
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
                    FreeCAD.Console.PrintMessage("Vase added\n")
                    
                    for obj in doc.Objects:
                        print(obj.Name, obj.TypeId)
                        if obj.TypeId == "Image::ImagePlane":
                            vase_obj = obj
                    
                    y = vase_obj.YSize
                    scale_factor = self.svg_height / y
                    new_x_size = vase_obj.XSize * scale_factor
                    
                    vase_obj.YSize = self.svg_height
                    vase_obj.XSize = new_x_size
                    vase_obj.Placement = FreeCAD.Placement(FreeCAD.Vector(0,0,self.svg_height/2),FreeCAD.Rotation(FreeCAD.Vector(1,0,0),90))
                    doc.recompute()
                    Gui.activeDocument().activeView().viewFront()
                    Gui.SendMsgToActiveView("ViewFit")
                    
                except Exception as e:
                    FreeCAD.Console.PrintError(f"Error adding vase: {str(e)}\n")

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
            panel = AddVasePanel()
    
            # Show the task panel in FreeCAD
            Gui.Control.showDialog(panel)

        except Exception as e:
            App.Console.PrintError(f"Error adding panel: {str(e)}\n")
