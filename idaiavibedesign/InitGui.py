import FreeCAD
import FreeCADGui
import os

class VibeDesignWorkbench(FreeCADGui.Workbench):
    """VibeDesign workbench for natural language CAD modeling"""
    
    def __init__(self):
        self.__class__.MenuText = "Vibe Design"
        self.__class__.ToolTip = "Natural language CAD modeling workbench"
        
        # Try to get addon directory path for icon
        try:
            # First try using __file__ if available
            addon_dir = ""
            try:
                if '__file__' in globals():
                    addon_dir = os.path.dirname(__file__)
            except:
                pass
            
            # Fallback: search in FreeCAD Mod directories
            if not addon_dir:
                import sys
                for path in sys.path:
                    test_path = os.path.join(path, "idaiavibedesign")
                    if os.path.exists(test_path):
                        addon_dir = test_path
                        break
            
            # Set icon if we found the directory
            if addon_dir:
                icon_path = os.path.join(addon_dir, "Resources", "VibeDesign.svg")
                if os.path.exists(icon_path):
                    self.__class__.Icon = icon_path
        except:
            pass  # Continue without icon if path detection fails
    
    def Initialize(self):
        """This function is executed when FreeCAD starts"""
        import VibeDesignCommands
        
        self.list = ["VibeDesign_PromptCommand"]
        
        # Add AI settings if available
        try:
            import AISettings
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