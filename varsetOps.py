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