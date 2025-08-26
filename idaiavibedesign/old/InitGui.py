import FreeCADGui
import os


class IdaiaVibeDesignWorkbench(FreeCADGui.Workbench):
    """
    IdaiaVibeDesign workbench for FreeCAD
    """
    
    MenuText = "IdaiaVibeDesign"
    ToolTip = "IdaiaVibeDesign addon for FreeCAD"
    Icon = os.path.join(os.path.dirname(__file__), "icon.svg")
    
    def Initialize(self):
        """This function is executed when FreeCAD starts"""
        import IdaiaVibeDesignCommands
        
        self.list = ["IdaiaVibeDesign_Command"]
        self.appendToolbar("IdaiaVibeDesign", self.list)
        self.appendMenu("IdaiaVibeDesign", self.list)
    
    def Activated(self):
        """This function is executed when the workbench is activated"""
        pass
    
    def Deactivated(self):
        """This function is executed when the workbench is deactivated"""
        pass


FreeCADGui.addWorkbench(IdaiaVibeDesignWorkbench())