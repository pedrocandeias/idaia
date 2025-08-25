import FreeCAD
import FreeCADGui
from PySide2 import QtWidgets, QtCore, QtGui
import json
import os
from .AIAgent import AIAgentConfig, AIAgentManager

class AISettingsPanel(QtWidgets.QWidget):
    """Settings panel for AI configuration"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = AIAgentConfig()
        self.agent_manager = None
        self.load_settings()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QtWidgets.QVBoxLayout(self)
        
        # Title
        title = QtWidgets.QLabel("AI Agent Configuration")
        title.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px 0px;")
        layout.addWidget(title)
        
        # Provider selection
        provider_group = QtWidgets.QGroupBox("AI Provider")
        provider_layout = QtWidgets.QVBoxLayout(provider_group)
        
        self.provider_combo = QtWidgets.QComboBox()
        self.provider_combo.addItems(["ollama", "openai", "anthropic"])
        self.provider_combo.setCurrentText(self.config.provider)
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)
        provider_layout.addWidget(self.provider_combo)
        
        # Model configuration
        model_layout = QtWidgets.QFormLayout()
        
        self.model_input = QtWidgets.QLineEdit(self.config.model)
        model_layout.addRow("Model:", self.model_input)
        
        self.base_url_input = QtWidgets.QLineEdit(self.config.base_url)
        model_layout.addRow("Base URL:", self.base_url_input)
        
        self.api_key_input = QtWidgets.QLineEdit(self.config.api_key)
        self.api_key_input.setEchoMode(QtWidgets.QLineEdit.Password)
        model_layout.addRow("API Key:", self.api_key_input)
        
        provider_layout.addLayout(model_layout)
        layout.addWidget(provider_group)
        
        # Advanced settings
        advanced_group = QtWidgets.QGroupBox("Advanced Settings")
        advanced_layout = QtWidgets.QFormLayout(advanced_group)
        
        self.temperature_spin = QtWidgets.QDoubleSpinBox()
        self.temperature_spin.setRange(0.0, 2.0)
        self.temperature_spin.setSingleStep(0.1)
        self.temperature_spin.setValue(self.config.temperature)
        advanced_layout.addRow("Temperature:", self.temperature_spin)
        
        self.timeout_spin = QtWidgets.QSpinBox()
        self.timeout_spin.setRange(5, 300)
        self.timeout_spin.setValue(self.config.timeout)
        self.timeout_spin.setSuffix(" seconds")
        advanced_layout.addRow("Timeout:", self.timeout_spin)
        
        self.retries_spin = QtWidgets.QSpinBox()
        self.retries_spin.setRange(1, 10)
        self.retries_spin.setValue(self.config.max_retries)
        advanced_layout.addRow("Max Retries:", self.retries_spin)
        
        layout.addWidget(advanced_group)
        
        # Model suggestions
        suggestions_group = QtWidgets.QGroupBox("Model Suggestions")
        suggestions_layout = QtWidgets.QVBoxLayout(suggestions_group)
        
        self.suggestions_text = QtWidgets.QTextEdit()
        self.suggestions_text.setReadOnly(True)
        self.suggestions_text.setMaximumHeight(80)
        self.update_suggestions()
        suggestions_layout.addWidget(self.suggestions_text)
        
        layout.addWidget(suggestions_group)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        self.test_button = QtWidgets.QPushButton("Test Connection")
        self.test_button.clicked.connect(self.test_connection)
        button_layout.addWidget(self.test_button)
        
        button_layout.addStretch()
        
        self.save_button = QtWidgets.QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)
        
        self.reset_button = QtWidgets.QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self.reset_settings)
        button_layout.addWidget(self.reset_button)
        
        layout.addLayout(button_layout)
        
        # Status
        self.status_label = QtWidgets.QLabel("Ready")
        self.status_label.setStyleSheet("color: #666; font-style: italic; margin: 5px 0px;")
        layout.addWidget(self.status_label)
        
        # Initial provider setup
        self.on_provider_changed(self.config.provider)
    
    def on_provider_changed(self, provider):
        """Handle provider change"""
        if provider == "ollama":
            self.model_input.setText("llama3.1:8b")
            self.base_url_input.setText("http://localhost:11434/v1")
            self.api_key_input.setEnabled(False)
            self.api_key_input.setText("")
        elif provider == "openai":
            self.model_input.setText("gpt-4")
            self.base_url_input.setText("https://api.openai.com/v1")
            self.api_key_input.setEnabled(True)
        elif provider == "anthropic":
            self.model_input.setText("claude-3-5-sonnet-20241022")
            self.base_url_input.setText("https://api.anthropic.com")
            self.api_key_input.setEnabled(True)
        
        self.update_suggestions()
    
    def update_suggestions(self):
        """Update model suggestions based on provider"""
        provider = self.provider_combo.currentText()
        
        suggestions = {
            "ollama": "Recommended models: llama3.1:8b (good balance), llama3.1:70b (best quality), qwen2.5:7b (fast), deepseek-r1:8b (reasoning)",
            "openai": "Available models: gpt-4, gpt-4-turbo, gpt-3.5-turbo. Note: API key required and costs apply per request.",
            "anthropic": "Available models: claude-3-5-sonnet-20241022, claude-3-5-haiku-20241022. Note: API key required and costs apply per request."
        }
        
        self.suggestions_text.setPlainText(suggestions.get(provider, ""))
    
    def test_connection(self):
        """Test connection to AI service"""
        self.test_button.setEnabled(False)
        self.test_button.setText("Testing...")
        self.status_label.setText("Testing connection...")
        
        # Update config from UI
        self.update_config_from_ui()
        
        # Test in separate thread to avoid blocking UI
        def test_worker():
            try:
                manager = AIAgentManager()
                manager.initialize_agent(self.config)
                
                if manager.test_connection():
                    QtCore.QMetaObject.invokeMethod(
                        self, "on_test_success", QtCore.Qt.QueuedConnection
                    )
                else:
                    QtCore.QMetaObject.invokeMethod(
                        self, "on_test_failure", QtCore.Qt.QueuedConnection,
                        QtCore.Q_ARG(str, "Connection failed")
                    )
            except Exception as e:
                QtCore.QMetaObject.invokeMethod(
                    self, "on_test_failure", QtCore.Qt.QueuedConnection,
                    QtCore.Q_ARG(str, str(e))
                )
        
        import threading
        thread = threading.Thread(target=test_worker)
        thread.daemon = True
        thread.start()
    
    @QtCore.Slot()
    def on_test_success(self):
        """Handle successful connection test"""
        self.test_button.setEnabled(True)
        self.test_button.setText("Test Connection")
        self.status_label.setText("✓ Connection successful!")
        self.status_label.setStyleSheet("color: green; font-style: italic; margin: 5px 0px;")
    
    @QtCore.Slot(str)
    def on_test_failure(self, error):
        """Handle failed connection test"""
        self.test_button.setEnabled(True)
        self.test_button.setText("Test Connection")
        self.status_label.setText(f"✗ Connection failed: {error}")
        self.status_label.setStyleSheet("color: red; font-style: italic; margin: 5px 0px;")
    
    def update_config_from_ui(self):
        """Update config object from UI values"""
        self.config.provider = self.provider_combo.currentText()
        self.config.model = self.model_input.text()
        self.config.base_url = self.base_url_input.text()
        self.config.api_key = self.api_key_input.text()
        self.config.temperature = self.temperature_spin.value()
        self.config.timeout = self.timeout_spin.value()
        self.config.max_retries = self.retries_spin.value()
    
    def save_settings(self):
        """Save settings to file"""
        try:
            self.update_config_from_ui()
            
            settings_dir = os.path.join(FreeCAD.getUserAppDataDir(), "VibeDesign")
            os.makedirs(settings_dir, exist_ok=True)
            
            settings_file = os.path.join(settings_dir, "ai_settings.json")
            with open(settings_file, 'w') as f:
                json.dump(self.config.to_dict(), f, indent=2)
            
            self.status_label.setText("✓ Settings saved successfully!")
            self.status_label.setStyleSheet("color: green; font-style: italic; margin: 5px 0px;")
            
            # Notify parent if it exists
            if hasattr(self.parent(), 'on_settings_changed'):
                self.parent().on_settings_changed(self.config)
                
        except Exception as e:
            self.status_label.setText(f"✗ Error saving settings: {str(e)}")
            self.status_label.setStyleSheet("color: red; font-style: italic; margin: 5px 0px;")
    
    def load_settings(self):
        """Load settings from file"""
        try:
            settings_file = os.path.join(FreeCAD.getUserAppDataDir(), "VibeDesign", "ai_settings.json")
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    data = json.load(f)
                self.config.from_dict(data)
        except Exception as e:
            FreeCAD.Console.PrintWarning(f"Could not load AI settings: {str(e)}\n")
    
    def reset_settings(self):
        """Reset settings to defaults"""
        reply = QtWidgets.QMessageBox.question(
            self, "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            self.config = AIAgentConfig()
            self.provider_combo.setCurrentText(self.config.provider)
            self.model_input.setText(self.config.model)
            self.base_url_input.setText(self.config.base_url)
            self.api_key_input.setText(self.config.api_key)
            self.temperature_spin.setValue(self.config.temperature)
            self.timeout_spin.setValue(self.config.timeout)
            self.retries_spin.setValue(self.config.max_retries)
            self.on_provider_changed(self.config.provider)
            self.status_label.setText("Settings reset to defaults")
            self.status_label.setStyleSheet("color: #666; font-style: italic; margin: 5px 0px;")

class AISettingsCommand:
    """Command to open AI settings"""
    
    def GetResources(self):
        return {
            'Pixmap': os.path.join(os.path.dirname(__file__), "Resources", "ai_settings.svg"),
            'MenuText': "AI Settings",
            'ToolTip': "Configure AI agent settings"
        }
    
    def Activated(self):
        """Execute the command"""
        panel = AISettingsPanel()
        
        # Create dialog
        dialog = QtWidgets.QDialog(FreeCADGui.getMainWindow())
        dialog.setWindowTitle("AI Agent Settings")
        dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        dialog.resize(500, 600)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.addWidget(panel)
        
        # Buttons
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Close
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        dialog.exec_()
    
    def IsActive(self):
        """Determine if the command should be enabled"""
        return True

# Register the command
FreeCADGui.addCommand('VibeDesign_AISettings', AISettingsCommand())