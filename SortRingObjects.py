"""
FreeCAD Macro: Sort Ring Objects
This macro finds all objects with labels starting with "Ring" and sorts them by name in the model pane.
"""

import FreeCAD
from FreeCAD import App

def sort_ring_objects():
    """Find all objects starting with 'Ring' and sort them in the document."""
    
    # Get the active document
    doc = App.activeDocument()
    
    if doc is None:
        FreeCAD.Console.PrintError("No active document found.\n")
        return
    
    # Find all objects with labels starting with "Ring"
    ring_objects = []
    for obj in doc.Objects:
        if obj.Label.startswith("Ring"):
            ring_objects.append(obj)
    
    if not ring_objects:
        FreeCAD.Console.PrintMessage("No objects found with labels starting with 'Ring'.\n")
        return
    
    # Sort by name (object name, not label)
    ring_objects.sort(key=lambda x: x.Name)
    
    # Reorder objects in the document by moving them
    # We need to move them to the end in sorted order
    for obj in ring_objects:
        doc.moveObject(obj, None)
    
    # Print the sorted list
    FreeCAD.Console.PrintMessage(f"Sorted {len(ring_objects)} Ring objects by name:\n")
    for obj in ring_objects:
        FreeCAD.Console.PrintMessage(f"  - {obj.Name}: {obj.Label}\n")
    
    # Recompute the document to refresh the view
    doc.recompute()
    FreeCAD.Console.PrintMessage("Sorting complete.\n")

# Run the macro
sort_ring_objects()
