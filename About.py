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
#from click import Path
import FreeCAD	
import FreeCADGui
import Sketcher
import Part

class About:
	"""Command to add a catenary curve sketch"""
	def __init__(self):
		pass
	#    obj.Proxy = self
	#    obj.addProperty("App::PropertyInteger", "Sag", "Dimensions").Sag=-1

	def GetResources(self):
		"""Return the command resources"""
		import FreeCAD
		from pathlib import Path
		return {
			'Pixmap': str(Path(FreeCAD.getUserAppDataDir()) / "Mod" / "WoodturningWorkbench" / "icons" / "About.svg"),  # You can add an icon path here
			#'Pixmap' : '',
			'MenuText': 'About Woodturning Workbench',
			'ToolTip': 'About the Woodturning Workbench and its creator'
		}

	def IsActive(self):
		"""Check if the command is active"""
		return FreeCAD.ActiveDocument is not None

	def Activated(self):
		"""Execute the command"""
		import FreeCAD as App
		from PySide import QtWidgets, QtCore, QtGui
		
		class AboutDialog(QtWidgets.QDialog):
			import json
			import os
			def __init__(self):
				super().__init__()
				self.colors = []  # Store color entries: {"name": str, "color": QColor}
				self.init_ui()

			def init_ui(self):
				import FreeCADGui
				from PySide import QtWidgets, QtCore, QtGui
				from pathlib import Path
				"""Initialize the user interface."""
				self.setWindowTitle("WoodTurning Workbench About Page")
				self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
				self.setGeometry(100, 100, 740, 740)

				self.image_label = QtWidgets.QLabel()

				# Define the image path (use an absolute path for reliability)
				#image_path = os.path.join(os.getcwd(), "logo.png") # Replace "logo.png" with your image filename
				image_path = str(Path(FreeCAD.getUserAppDataDir()) / "Mod" / "WoodturningWorkbench" / "resources" / "AboutVase.svg")
				# Create a QPixmap object from the image file
				try:
					pixmap = QtGui.QPixmap(image_path)
					if pixmap.isNull():
						print(f"Error: Could not load image from {image_path}")
						return
					self.image_label.setPixmap(pixmap)
				except Exception as e:
					print(f"An error occurred: {e}")
					return



				
				layout = QtWidgets.QVBoxLayout(self)
				layout.setAlignment(QtCore.Qt.AlignCenter)
				layout.addWidget(self.image_label)
				self.text_edit = QtWidgets.QTextBrowser(self)
				html_content = """
				<h1>Welcome to WoodTurning Workbench</h1>
				<p>This workbench provides tools for designing and simulating woodturning projects in FreeCAD.</p>
				<p><a href="https://github.com/OpenSourceModular/WoodTurningWorkbench"</a></p>
				"""
				self.text_edit.setHtml(html_content)
				
				layout.addWidget(self.text_edit)


				close_btn = QtWidgets.QPushButton("Close")
				close_btn.clicked.connect(self.close)
				
				layout.addWidget(close_btn)
				self.setLayout(layout)

		dialog = AboutDialog()
		# Make it modeless so you can interact with FreeCAD while the dialog is open
		dialog.setWindowModality(QtCore.Qt.NonModal)
		dialog.show()
		# Store reference to prevent garbage collection
		#FreeCAD.Gui.MainWindow.color_list_dialog = dialog
		FreeCAD.Gui.getMainWindow().about_dialog = dialog