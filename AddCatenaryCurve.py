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
import FreeCAD
import Part

class AddCatenaryCurve:
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
			'Pixmap': str(Path(FreeCAD.getUserAppDataDir()) / "Mod" / "WoodturningWorkbench" / "icons" / "AddCatenaryCurve.svg"),  # You can add an icon path here
			'MenuText': 'Add Catenary Curve',
			'ToolTip': 'Add a catenary curve sketch to the document'
		}

	def IsActive(self):
		"""Check if the command is active"""
		return FreeCAD.ActiveDocument is not None

	def Activated(self):
		"""Execute the command"""
		import FreeCAD as App
		try:
			import math
			doc = FreeCAD.ActiveDocument
			if not doc:
				FreeCAD.Console.PrintError("No active document\n")
				return

			# Create a new sketch
			sketch = doc.addObject('Sketcher::SketchObject', 'CatenaryCurveSketch')
			sketch.Placement = FreeCAD.Placement(App.Vector(0, 0, 0), App.Rotation(App.Vector(1, 0, 0), 90))

			sketch.addProperty("App::PropertyInteger", "Sag", "Dimensions").Sag=250
			sketch.addProperty("App::PropertyFloat", "XStart", "Dimensions").XStart=0.0
			sketch.addProperty("App::PropertyFloat", "XEnd", "Dimensions").XEnd=300.0
			sketch.addProperty("App::PropertyFloat", "YStart", "Dimensions").YStart=0.0
			sketch.addProperty("App::PropertyInteger", "NumPoints", "Dimensions").NumPoints=50

			print (sketch.Sag)
			poles = []
			for i in range(50 + 1):
				x = sketch.XStart + (sketch.XEnd - sketch.XStart) * i / sketch.NumPoints
				y = sketch.YStart + (sketch.Sag * (math.cosh(x / sketch.Sag) - 1))
				poles.append(FreeCAD.Vector(x, y, 0))
			# Create the B-spline curve
			bspline = Part.BSplineCurve()
			bspline.buildFromPoles(poles)

			# Add the B-spline to the sketch
			sketch.addGeometry(bspline, False)

			# Recompute the document
			doc.recompute()

		except Exception as e:
			FreeCAD.Console.PrintError(f"Error adding Catenary Curve sketch: {str(e)}\n")