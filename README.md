# WoodTuring Tools

A FreeCAD workbench with tools for wood turners.

## Installation

1. Copy the `WoodTurningWorkbench` folder to your FreeCAD Mod directory:
   - Windows: `%APPDATA%\FreeCAD\Mod\`
   - Linux: `~/.FreeCAD/Mod/`
   - macOS: `~/Library/Preferences/FreeCAD/Mod/`

2. Restart FreeCAD

3. The workbench should appear in the workbench selector

## Commands

### Add Profile Points (Construction Lines)
Creates a new sketch with horizontal guide lines and profile points. Move the points to define the bowl profile used by other tools.

### Add Segments
This task uses the selected sketch from the Add Construction Lines command. The user can define the bowl wall width as well as a "fudge" amount to give extra width to the segment. 
Steps:
   Show Bowl lines shows the walls of the bowl based on the curve you drew in the Bowl Profile Sketch
   Add Segments will add segments to the model based on the curve and the text box settings.
   You can delete the segments and make changes to the text box values and re-draw the segments until you are satisfied
   Pressing the Make Bowl Solid button will create a FreeCAD solid shape that represents the shape of the bowl
   Pressing the intersect button will intersect each of the segments with the bowl solid which will show what the segments look like after turning.
   Pressing the Array button will create copies of the segments and turn them into a full ring.

### Rotate Rings
Rotates ring objects (labels starting with Ring_) by a per-ring angle. Supports percent-based rotation presets, manual angles, left/right direction, and rotation of a selected ring or resetting rotations.

### Apply Colors
Opens a modeless dialog for maintaining a color list and applying colors to selected objects.

- **Load Colors** opens a file picker and loads colors from a `.json` file.
- **Save Current List** opens a save dialog and lets you choose the output filename.
- Saving writes a plain JSON list format.
- Loading supports both the plain list format and the legacy wrapped format.

Supported plain list format:

```json
[
   { "name": "Walnut Brown", "hex": "#773F1A" },
   { "name": "Saddle Brown", "hex": "#8B4513" }
]
```

Also accepted when loading (legacy format):

```json
{
   "colors": [
      { "name": "Walnut Brown", "hex": "#773F1A" },
      { "name": "Saddle Brown", "hex": "#8B4513" }
   ]
}
```

### Make Segment Dimension Spreadsheet
Creates a Spreadsheet workbench sheet with segment dimensions (mm and inches) and bowl metadata, derived from objects labeled "Segment" and BowlVariables.

### Top View
Provides tools to rotate segments into a circular top view, array them into a rectangular plan layout, generate a TechDraw page of all segments, and restore original placements.

### Catenary Curve
Generates a catenary curve sketch from parameters (sag, start/end, number of points), with options to revolve or shell-revolve the curve. Can mirror the curve about a 45° line.

### Bowl From A Board
Builds ring geometry from a board by slice thickness/angle settings and can generate the resulting bowl form.

### Add Vessel Profile
Imports an SVG vessel profile, scales it to the specified dimensions, and places it in the document. Includes preset profile buttons and a custom SVG browser.

### Add Torus
Creates torus profile sketches and tools for building a segmented torus: ring creation, extrude, intersect, and array operations.

### Wedgie Generator
Builds a wedge (segment) blank based on length, width, thickness, and segment count. Optional center cutout and text labeling.

### Offcenter Turning
Generates top and bottom sketches for off-center turning based on radii, angles, cylinder height/radius, and point count. Includes utilities to delete/rebuild sketches.

### About Woodturning Workbench
Opens the About dialog with workbench information, author details, and a reference image.

