import FreeCAD
import FreeCADGui
import os

class VibeDesignWorkbench(FreeCADGui.Workbench):
    """VibeDesign workbench for natural language CAD modeling"""
    
    def __init__(self):
        self.__class__.MenuText = "Vibe Design"
        self.__class__.ToolTip = "Natural language CAD modeling workbench"
        self.__class__.Icon = os.path.join(os.path.dirname(__file__), "Resources", "VibeDesign.svg")
    
    def Initialize(self):
        """This function is executed when FreeCAD starts"""
        from . import VibeDesignCommands
        
        self.list = ["VibeDesign_PromptCommand"]
        
        # Add AI settings if available
        try:
            from . import AISettings
            self.list.append("VibeDesign_AISettings")
        except ImportError:
            pass
        
        self.appendToolbar("Vibe Design", self.list)
        self.appendMenu("Vibe Design", self.list)
    
    def Activated(self):
        """Called when workbench is activated"""
        FreeCAD.Console.PrintMessage("Vibe Design workbench activated\n")
    
    def Deactivated(self):
        """Called when workbench is deactivated"""
        FreeCAD.Console.PrintMessage("Vibe Design workbench deactivated\n")
    
    def GetClassName(self):
        """Required for Python workbenches"""
        return "Gui::PythonWorkbench"

FreeCADGui.addWorkbench(VibeDesignWorkbench())