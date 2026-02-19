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


def _resolve_varset(self):
    if self is not None:
        if hasattr(self, "PropertiesList"):
            return self
        if hasattr(self, "varset"):
            return self.varset
    doc = App.activeDocument()
    return doc.getObject("BowlVariables") if doc else None


def _unwrap_value(value):
    return value.Value if hasattr(value, "Value") else value


def getVarsetValue(self, property_name):
    varset = _resolve_varset(self)
    if varset and property_name in varset.PropertiesList:
        return _unwrap_value(getattr(varset, property_name))
    print(f"Property {property_name} not found in BowlVariables.")
    return None


def getVarsetInt(self, property_name):
    varset = _resolve_varset(self)
    if varset and property_name in varset.PropertiesList:
        return _unwrap_value(getattr(varset, property_name))
    print(f"Property {property_name} not found in BowlVariables.")
    return None


def setVarsetValue(self, property_name, value):
    varset = _resolve_varset(self)
    if varset and property_name in varset.PropertiesList:
        setattr(varset, property_name, value)
        return
    print(f"Property {property_name} not found in BowlVariables.")

def setVarsetInt(self, property_name, value):
    varset = _resolve_varset(self)
    if varset and property_name in varset.PropertiesList:
        setattr(varset, property_name, value)
        return
    print(f"Property {property_name} not found in BowlVariables.")