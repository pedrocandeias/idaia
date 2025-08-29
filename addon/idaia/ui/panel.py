# Addon/ui/panel.py
# -*- coding: utf-8 -*-
"""
Dockable panel for NL → FreeCAD code generation (using local Ollama persona).
"""

import traceback
from PySide import QtGui, QtCore
import FreeCADGui as Gui

from core.llm_client import ask_llm, DEFAULT_OLLAMA_URL, DEFAULT_MODEL
from core.executor import safe_run

ORG = "NLFreeCAD"
APP = "NLPanel"


def _settings():
    return QtCore.QSettings(ORG, APP)


class NLPanel(QtGui.QWidget):
    def __init__(self):
        super(NLPanel, self).__init__()
        self.setWindowTitle("NL FreeCAD")

        # Inputs
        self.prompt = QtGui.QPlainTextEdit()
        self.prompt.setPlaceholderText("e.g., create a cube 50x50x50 mm")

        s = _settings()
        model = s.value("model", DEFAULT_MODEL)
        url = s.value("ollamaUrl", DEFAULT_OLLAMA_URL)
        temp = float(s.value("temperature", 0.0))

        self.modelEdit = QtGui.QLineEdit(model)
        self.urlEdit = QtGui.QLineEdit(url)

        self.tempSpin = QtGui.QDoubleSpinBox()
        self.tempSpin.setRange(0.0, 2.0)
        self.tempSpin.setSingleStep(0.1)
        self.tempSpin.setValue(temp)

        self.dryRun = QtGui.QCheckBox("Dry run (show code, don’t execute)")

        # Output
        self.output = QtGui.QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setMinimumHeight(140)

        # Buttons
        self.btnRun = QtGui.QPushButton("Generate & Run")
        self.btnRun.clicked.connect(self.on_run)

        self.btnSaveCfg = QtGui.QPushButton("Save Settings")
        self.btnSaveCfg.clicked.connect(self.on_save)

        # Layout
        form = QtGui.QFormLayout()
        form.addRow("Model", self.modelEdit)
        form.addRow("Ollama URL", self.urlEdit)
        form.addRow("Temperature", self.tempSpin)
        form.addRow(self.prompt)
        form.addRow(self.dryRun)
        form.addRow(self.btnRun)
        form.addRow(self.btnSaveCfg)
        form.addRow("Output", self.output)
        self.setLayout(form)

    # Helpers
    def log(self, text):
        self.output.appendPlainText(str(text))

    # Slots
    def on_save(self):
        s = _settings()
        s.setValue("model", self.modelEdit.text().strip())
        s.setValue("ollamaUrl", self.urlEdit.text().strip())
        s.setValue("temperature", self.tempSpin.value())
        self.log("Settings saved.")

    def on_run(self):
        text = self.prompt.toPlainText().strip()
        if not text:
            self.log("No prompt.")
            return
        try:
            code = ask_llm(
                user_text=text,
                base_url=self.urlEdit.text().strip() or DEFAULT_OLLAMA_URL,
                model=self.modelEdit.text().strip() or DEFAULT_MODEL,
                temperature=float(self.tempSpin.value()),
                timeout=30.0,
            )
            self.log("Generated code:\n" + code)
            if not self.dryRun.isChecked():
                safe_run(code)
                self.log("Executed.")
            else:
                self.log("Dry run only (not executed).")
        except Exception as e:
            self.log("ERROR: " + str(e))
            self.log(traceback.format_exc())


# Command to show the dock
class ShowPanelCmdClass:
    def Activated(self):
        panel = NLPanel()
        mw = Gui.getMainWindow()
        dock = mw.findChild(QtGui.QDockWidget, "NLFreeCADDock")
        if dock is None:
            dock = QtGui.QDockWidget("NL FreeCAD", mw)
            dock.setObjectName("NLFreeCADDock")
            dock.setWidget(panel)
            mw.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
        else:
            dock.setWidget(panel)
        dock.show()

    def GetResources(self):
        return {
            "MenuText": "Show NL Panel",
            "ToolTip": "Open the Natural Language panel",
            "Pixmap": "icons/addon.svg",
        }

    def IsActive(self):
        return True


def ShowPanelCmd():
    return ShowPanelCmdClass()

# Addon/ui/panel.py  (append at the end of the file)

import FreeCADGui as Gui

# Register the command with FreeCAD
Gui.addCommand("NL_ShowPanel", ShowPanelCmd())
