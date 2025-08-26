import FreeCAD
import FreeCADGui
from PySide2 import QtCore, QtWidgets


class IdaiaVibeDesignCommand:
    """Main command for IdaiaVibeDesign addon"""
    
    def GetResources(self):
        return {
            'Pixmap': 'IdaiaVibeDesign_Command',
            'MenuText': 'IdaiaVibeDesign Tool',
            'ToolTip': 'Open IdaiaVibeDesign tool'
        }
    
    def Activated(self):
        """Executed when the command is run"""
        QtWidgets.QMessageBox.information(
            None,
            "IdaiaVibeDesign",
            "Hello from IdaiaVibeDesign addon!\n\nThis is a basic menu option."
        )
    
    def IsActive(self):
        """Return True when this command should be available"""
        return True


FreeCADGui.addCommand('IdaiaVibeDesign_Command', IdaiaVibeDesignCommand())