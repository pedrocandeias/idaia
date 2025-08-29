# Addon/Init.py
# -*- coding: utf-8 -*-
"""
Marker module so FreeCAD recognizes this directory as a workbench/addon.
Console-safe (no GUI imports here). GUI bits live in InitGui.py.
"""

__title__   = "NL FreeCAD"
__author__  = "Pedro + friends"
__version__ = "0.1.0"

# Optional hook FreeCAD calls when loading the module (non-GUI context).
def Initialize():
    # Put non-GUI initialization here if you ever need it.
    # For now, we keep it empty.
    pass

