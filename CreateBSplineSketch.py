"""
FreeCAD Python Macro: Create a Sketch with B-Spline through Three Points

This macro creates a new sketch and adds a B-spline constrained to pass through
three specified points: (1,1), (1,4), and (6,6).
"""

import FreeCAD as App
from FreeCAD import Vector
import Sketcher

def create_bspline_sketch():
    """Create a sketch with a B-spline constrained to three points."""
    
    # Create a new document if none exists
    doc = App.activeDocument()
    if doc is None:
        doc = App.newDocument()
    
    # Create a new sketch
    sketch = doc.addObject("Sketcher::SketchObject", "Sketch")
    
    # Attach sketch to XY plane (origin)
    from App import Placement, Rotation
    sketch.Placement = Placement(Vector(0, 0, 0), Rotation(0, 0, 0))
    
    # Enter edit mode for the sketch
    doc.recompute()
    
    # Define the three points
    p1 = Vector(1, 1, 0)
    p2 = Vector(1, 4, 0)
    p3 = Vector(6, 6, 0)
    
    # Add the three points as geometry
    point1_index = sketch.addGeometry(Sketcher.Point(p1))
    point2_index = sketch.addGeometry(Sketcher.Point(p2))
    point3_index = sketch.addGeometry(Sketcher.Point(p3))
    
    # Create a B-spline through the three points
    # B-spline is defined by its poles (control points)
    poles = [p1, p2, p3]
    knots = [0.0, 0.5, 1.0]
    multiplicities = [2, 1, 2]  # Clamped B-spline
    degree = 2
    
    bspline = Sketcher.BSpline(poles, degree, False, False, knots, multiplicities)
    bspline_index = sketch.addGeometry(bspline)
    
    # Add constraints to make the B-spline pass through the three points
    # Constrain the first point of the B-spline to p1
    sketch.addConstraint(Sketcher.Constraint('Coincident', bspline_index, 1, point1_index, 1))
    
    # Constrain the second point of the B-spline to p2
    sketch.addConstraint(Sketcher.Constraint('Coincident', bspline_index, 2, point2_index, 1))
    
    # Constrain the third point of the B-spline to p3
    sketch.addConstraint(Sketcher.Constraint('Coincident', bspline_index, 3, point3_index, 1))
    
    # Recompute the document to update the sketch
    doc.recompute()
    
    print("B-Spline sketch created successfully!")
    print(f"Sketch name: {sketch.Name}")
    print(f"Points created at: {p1}, {p2}, {p3}")
    print(f"B-Spline geometry added and constrained to the three points")
    
    return sketch

if __name__ == "__main__":
    create_bspline_sketch()
