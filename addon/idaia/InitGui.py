# Addon/InitGui.py
# -*- coding: utf-8 -*-
"""
InitGui.py for NL FreeCAD Addon
Registers the workbench in the FreeCAD GUI.
"""

import FreeCADGui as Gui

class NLFreeCADWorkbench(Gui.Workbench):
    """Natural Language → FreeCAD workbench"""

    MenuText = "NL FreeCAD"
    ToolTip = "Natural language commands converted into FreeCAD Python (via Ollama)"
    Icon = """
    /* XPM */
    static char * xpm[] = {
    "16 16 2 1",
    "  c None",
    ". c #00AAFF",
    "................",
    "................",
    ".....######.....",
    "....#......#....",
    "...#...##...#...",
    "...#..#..#..#...",
    "...#..#..#..#...",
    "...#...##...#...",
    "....#......#....",
    ".....######.....",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................"};
    """

    def Initialize(self):
        # Import here so it only loads in GUI mode
        from ui import panel  # this makes sure the command is registered

        self.appendToolbar("NL FreeCAD", ["NL_ShowPanel"])
        self.appendMenu("NL FreeCAD", ["NL_ShowPanel"])


    def Activated(self):
        """Called when the workbench is activated"""
        return

    def Deactivated(self):
        """Called when the workbench is deactivated"""
        return

    def GetClassName(self):
        return "Gui::PythonWorkbench"

# Register the workbench
Gui.addWorkbench(NLFreeCADWorkbench())
