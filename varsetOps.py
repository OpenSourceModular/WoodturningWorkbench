import FreeCAD as App

def getVarsetValue(self, property_name):
    doc = App.activeDocument()
    varset = doc.getObject("BowlVariables")
    print("hey3")
    if varset and property_name in varset.PropertiesList:
        print(type(getattr(varset, property_name)))
        return getattr(varset, property_name).Value
    else:
        print(f"Property {property_name} not found in BowlVariables.")
        return None
def getVarsetInt(self, property_name):
    doc = App.activeDocument()
    varset = doc.getObject("BowlVariables")
    print("hey2")
    if varset and property_name in varset.PropertiesList:
        return getattr(varset, property_name)
    else:
        print(f"Property {property_name} not found in BowlVariables.")
        return None
def setVarsetValue(self, property_name, value):
    doc = App.activeDocument()
    varset = doc.getObject("BowlVariables")
    if varset and property_name in varset.PropertiesList:
        setattr(varset, property_name, value)
    else:
        print(f"Property {property_name} not found in BowlVariables.")