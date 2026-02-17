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

### Add Construction Lines
Creates a new sketch with a horizontal lines and points on the line. The user moves the points to define the profile of the bowl

### Add Segments
This task uses the selected sketch from the Add Construction Lines command. The user can define the bowl wall width as well as a "fudge" amount to give extra width to the segment. 
Steps:
   Show Bowl lines shows the walls of the bowl based on the curve you drew in the Bowl Profile Sketch
   Add Segments will add segments to the model based on the curve and the text box settings.
   You can delete the segments and make changes to the text box values and re-draw the segments until you are satisfied
   Pressing the Make Bowl Solid button will create a FreeCAD solid shape that represents the shape of the bowl
   Pressing the intersect button will intersect each of the segments with the bowl solid which will show what the segments look like after turning.
   Pressing the Array button will create copies of the segments and turn them into a full ring.

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

