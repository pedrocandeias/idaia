import FreeCAD
import FreeCADGui
from PySide2 import QtWidgets, QtCore
import Part
import re
import os
try:
    from AIAgent import AIAgentManager, AIAgentConfig
    from AISettings import AISettingsPanel
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    FreeCAD.Console.PrintWarning("AI features not available. Install required dependencies.\n")

class VibeDesignPromptCommand:
    """Command to process natural language prompts"""
    
    def GetResources(self):
        return {
            'Pixmap': os.path.join(os.path.dirname(__file__), "Resources", "prompt.svg"),
            'MenuText': "Natural Language Prompt",
            'ToolTip': "Create objects using natural language descriptions"
        }
    
    def Activated(self):
        """Execute the command"""
        panel = VibeDesignPromptPanel()
        FreeCADGui.Control.showDialog(panel)
    
    def IsActive(self):
        """Determine if the command should be enabled"""
        return True

class VibeDesignPromptPanel(QtCore.QObject):
    """Task panel for entering natural language prompts"""
    
    ai_response_signal = QtCore.Signal()
    
    def __init__(self):
        super().__init__()
        self.parser = PromptParser()
        self.ai_manager = None
        self.ai_enabled = False
        
        # Initialize AI manager before creating UI
        if AI_AVAILABLE:
            try:
                self.ai_manager = AIAgentManager()
                self.load_ai_settings()
            except Exception as e:
                FreeCAD.Console.PrintWarning(f"Could not initialize AI agent: {str(e)}\n")
        
        self.form = self.create_ui()
        
        # Connect the signal
        self.ai_response_signal.connect(self.handle_ai_response)
        
        # Update AI status after UI is created
        if hasattr(self, 'ai_status'):
            self.update_ai_status()
    
    def create_ui(self):
        """Create the user interface"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        
        # Title
        title = QtWidgets.QLabel("Natural Language CAD")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # AI Status and Instructions
        status_layout = QtWidgets.QHBoxLayout()
        
        instructions = QtWidgets.QLabel(
            "Enter a description of what you want to create:\n"
            "Examples:\n"
            "• create a box 10x20x30 mm\n"
            "• make a cylinder height 50 diameter 25\n"
            "• create a sphere radius 15 cm\n"
            "• create a bearing housing with 20mm bore\n"
            "• make a phone stand 45 degrees angle"
        )
        instructions.setWordWrap(True)
        status_layout.addWidget(instructions)
        
        # AI status indicator
        self.ai_status = QtWidgets.QLabel()
        self.ai_status.setMaximumWidth(100)
        self.ai_status.setAlignment(QtCore.Qt.AlignTop)
        self.update_ai_status()
        status_layout.addWidget(self.ai_status)
        
        layout.addLayout(status_layout)
        
        # AI/Manual mode toggle
        mode_layout = QtWidgets.QHBoxLayout()
        
        self.mode_label = QtWidgets.QLabel("Processing Mode:")
        mode_layout.addWidget(self.mode_label)
        
        self.ai_toggle = QtWidgets.QCheckBox("Use AI Agent")
        self.ai_toggle.setChecked(self.ai_enabled and AI_AVAILABLE)
        ai_available = AI_AVAILABLE and self.ai_manager and bool(self.ai_manager.is_available())
        self.ai_toggle.setEnabled(ai_available)
        self.ai_toggle.toggled.connect(self.on_ai_toggle)
        mode_layout.addWidget(self.ai_toggle)
        
        mode_layout.addStretch()
        
        # Settings button
        if AI_AVAILABLE:
            self.settings_button = QtWidgets.QPushButton("AI Settings")
            self.settings_button.clicked.connect(self.open_ai_settings)
            mode_layout.addWidget(self.settings_button)
        
        layout.addLayout(mode_layout)
        
        # Prompt input
        self.prompt_input = QtWidgets.QTextEdit()
        self.prompt_input.setPlaceholderText("create a square box, 8x8x8 cm")
        self.prompt_input.setMaximumHeight(80)
        layout.addWidget(self.prompt_input)
        
        # Create button
        button_layout = QtWidgets.QHBoxLayout()
        
        self.create_button = QtWidgets.QPushButton("Create Object")
        self.create_button.clicked.connect(self.create_object)
        button_layout.addWidget(self.create_button)
        
        self.clear_button = QtWidgets.QPushButton("Clear History")
        self.clear_button.clicked.connect(self.clear_history)
        self.clear_button.setEnabled(self.ai_enabled and AI_AVAILABLE)
        button_layout.addWidget(self.clear_button)
        
        layout.addLayout(button_layout)
        
        # Output area
        self.output_text = QtWidgets.QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMaximumHeight(100)
        layout.addWidget(self.output_text)
        
        return widget
    
    def create_object(self):
        """Process the prompt and create the object"""
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            self.output_text.append("Please enter a description.")
            return
        
        try:
            self.output_text.append(f"Processing: {prompt}")
            self.create_button.setEnabled(False)
            self.create_button.setText("Processing...")
            
            if self.ai_enabled and self.ai_manager and self.ai_manager.is_available():
                self.process_with_ai(prompt)
            else:
                result = self.parser.parse_and_execute(prompt)
                if result:
                    self.output_text.append(f"✓ Created: {result}")
                    FreeCAD.ActiveDocument.recompute()
                    FreeCADGui.ActiveDocument.ActiveView.fitAll()
                else:
                    self.output_text.append("✗ Could not understand the prompt")
                
                self.create_button.setEnabled(True)
                self.create_button.setText("Create Object")
                
        except Exception as e:
            self.output_text.append(f"✗ Error: {str(e)}")
            self.create_button.setEnabled(True)
            self.create_button.setText("Create Object")
    
    def accept(self):
        """Called when dialog is accepted"""
        FreeCADGui.Control.closeDialog()
        return True
    
    def reject(self):
        """Called when dialog is cancelled"""
        FreeCADGui.Control.closeDialog()
        return True
    
    def process_with_ai(self, prompt):
        """Process prompt using AI agent"""
        def ai_callback(result):
            # Store result for thread-safe access
            self._ai_result = result
            # Emit signal to handle response in main thread
            self.ai_response_signal.emit()
        
        # Get current context
        context = self.get_current_context()
        
        # Process asynchronously
        success = self.ai_manager.process_async(prompt, ai_callback, context)
        if not success:
            self.output_text.append("✗ AI agent is busy, please wait")
            self.create_button.setEnabled(True)
            self.create_button.setText("Create Object")
    
    @QtCore.Slot()
    def handle_ai_response(self):
        """Handle AI response"""
        result = getattr(self, '_ai_result', {})
        self.create_button.setEnabled(True)
        self.create_button.setText("Create Object")
        
        if "error" in result:
            self.output_text.append(f"✗ AI Error: {result['error']}")
            
            # Try fallback with traditional parser
            if result.get("fallback"):
                self.output_text.append("Trying fallback parser...")
                try:
                    fallback_result = self.parser.parse_and_execute(
                        self.prompt_input.toPlainText().strip()
                    )
                    if fallback_result:
                        self.output_text.append(f"✓ Created: {fallback_result}")
                        FreeCAD.ActiveDocument.recompute()
                        FreeCADGui.ActiveDocument.ActiveView.fitAll()
                except Exception as e:
                    self.output_text.append(f"✗ Fallback failed: {str(e)}")
            return
        
        # Process AI commands
        commands = result.get("commands", [])
        if not commands:
            self.output_text.append("✗ No valid commands generated")
            return
        
        self.output_text.append(f"AI: {result.get('explanation', 'Creating objects...')}")
        
        created_objects = []
        for cmd in commands:
            try:
                obj_result = self.execute_ai_command(cmd)
                if obj_result:
                    created_objects.append(obj_result)
            except Exception as e:
                self.output_text.append(f"✗ Command error: {str(e)}")
        
        if created_objects:
            self.output_text.append(f"✓ Created: {', '.join(created_objects)}")
            FreeCAD.ActiveDocument.recompute()
            FreeCADGui.ActiveDocument.ActiveView.fitAll()
            
            # Update context
            if self.ai_manager.agent:
                self.ai_manager.agent.update_context(
                    created_objects=[obj.split(' ')[0] for obj in created_objects],
                    last_command=self.prompt_input.toPlainText().strip()
                )
        else:
            self.output_text.append("✗ No objects created")
    
    def execute_ai_command(self, command):
        """Execute a single AI command"""
        doc = FreeCAD.ActiveDocument
        if not doc:
            doc = FreeCAD.newDocument()
        
        cmd_type = command.get("type", "create")
        shape = command.get("shape")
        dimensions = command.get("dimensions", {})
        position = command.get("position", {"x": 0, "y": 0, "z": 0})
        rotation = command.get("rotation", {"x": 0, "y": 0, "z": 0})
        name = command.get("name", shape.capitalize() if shape else "Object")
        
        if cmd_type == "create" and shape:
            # Ensure unique name
            name = self.parser.generate_object_name(shape)
            
            if shape == "box":
                result = self.create_ai_box(doc, name, dimensions, position, rotation)
            elif shape == "cylinder":
                result = self.create_ai_cylinder(doc, name, dimensions, position, rotation)
            elif shape == "sphere":
                result = self.create_ai_sphere(doc, name, dimensions, position, rotation)
            elif shape == "cone":
                result = self.create_ai_cone(doc, name, dimensions, position, rotation)
            elif shape == "torus":
                result = self.create_ai_torus(doc, name, dimensions, position, rotation)
            elif shape == "wedge":
                result = self.create_ai_wedge(doc, name, dimensions, position, rotation)
            else:
                return None
            
            return result
        
        return None
    
    def create_ai_box(self, doc, name, dims, pos, rot):
        """Create box from AI command"""
        length = dims.get('length', 10)
        width = dims.get('width', dims.get('length', 10))
        height = dims.get('height', dims.get('length', 10))
        
        obj = doc.addObject("Part::Box", name)
        obj.Length = length
        obj.Width = width
        obj.Height = height
        obj.Placement.Base = FreeCAD.Vector(pos['x'], pos['y'], pos['z'])
        obj.Placement.Rotation = FreeCAD.Rotation(rot['x'], rot['y'], rot['z'])
        
        return f"Box {name} ({length:.1f} x {width:.1f} x {height:.1f} mm)"
    
    def create_ai_cylinder(self, doc, name, dims, pos, rot):
        """Create cylinder from AI command"""
        radius = dims.get('radius', dims.get('diameter', 10) / 2)
        height = dims.get('height', 10)
        
        obj = doc.addObject("Part::Cylinder", name)
        obj.Radius = radius
        obj.Height = height
        obj.Placement.Base = FreeCAD.Vector(pos['x'], pos['y'], pos['z'])
        obj.Placement.Rotation = FreeCAD.Rotation(rot['x'], rot['y'], rot['z'])
        
        return f"Cylinder {name} (radius {radius:.1f} mm, height {height:.1f} mm)"
    
    def create_ai_sphere(self, doc, name, dims, pos, rot):
        """Create sphere from AI command"""
        radius = dims.get('radius', dims.get('diameter', 10) / 2)
        
        obj = doc.addObject("Part::Sphere", name)
        obj.Radius = radius
        obj.Placement.Base = FreeCAD.Vector(pos['x'], pos['y'], pos['z'])
        obj.Placement.Rotation = FreeCAD.Rotation(rot['x'], rot['y'], rot['z'])
        
        return f"Sphere {name} (radius {radius:.1f} mm)"
    
    def create_ai_cone(self, doc, name, dims, pos, rot):
        """Create cone from AI command"""
        radius1 = dims.get('radius', dims.get('diameter', 10) / 2)
        radius2 = dims.get('radius2', 0)
        height = dims.get('height', 10)
        
        obj = doc.addObject("Part::Cone", name)
        obj.Radius1 = radius1
        obj.Radius2 = radius2
        obj.Height = height
        obj.Placement.Base = FreeCAD.Vector(pos['x'], pos['y'], pos['z'])
        obj.Placement.Rotation = FreeCAD.Rotation(rot['x'], rot['y'], rot['z'])
        
        return f"Cone {name} (radius {radius1:.1f} mm, height {height:.1f} mm)"
    
    def create_ai_torus(self, doc, name, dims, pos, rot):
        """Create torus from AI command"""
        radius1 = dims.get('major_radius', dims.get('radius', 20))
        radius2 = dims.get('minor_radius', dims.get('tube_radius', 5))
        
        obj = doc.addObject("Part::Torus", name)
        obj.Radius1 = radius1
        obj.Radius2 = radius2
        obj.Placement.Base = FreeCAD.Vector(pos['x'], pos['y'], pos['z'])
        obj.Placement.Rotation = FreeCAD.Rotation(rot['x'], rot['y'], rot['z'])
        
        return f"Torus {name} (major {radius1:.1f} mm, minor {radius2:.1f} mm)"
    
    def create_ai_wedge(self, doc, name, dims, pos, rot):
        """Create wedge from AI command"""
        length = dims.get('length', 10)
        width = dims.get('width', 10)
        height = dims.get('height', 10)
        
        obj = doc.addObject("Part::Wedge", name)
        obj.Xmax = length
        obj.Ymax = width
        obj.Zmax = height
        obj.Placement.Base = FreeCAD.Vector(pos['x'], pos['y'], pos['z'])
        obj.Placement.Rotation = FreeCAD.Rotation(rot['x'], rot['y'], rot['z'])
        
        return f"Wedge {name} ({length:.1f} x {width:.1f} x {height:.1f} mm)"
    
    def get_current_context(self):
        """Get current FreeCAD context for AI"""
        context = {}
        
        if FreeCAD.ActiveDocument:
            context['active_document'] = FreeCAD.ActiveDocument.Name
            context['created_objects'] = [obj.Name for obj in FreeCAD.ActiveDocument.Objects]
        
        return context
    
    def on_ai_toggle(self, checked):
        """Handle AI toggle"""
        self.ai_enabled = checked and AI_AVAILABLE and bool(self.ai_manager)
        self.clear_button.setEnabled(self.ai_enabled)
        self.update_ai_status()
        
        if self.ai_enabled and self.ai_manager:
            self.prompt_input.setPlaceholderText(
                "Describe what you want to create in detail. AI can handle complex requests like \"create a bearing housing with 20mm bore\"")
        else:
            self.prompt_input.setPlaceholderText("create a square box, 8x8x8 cm")
    
    def clear_history(self):
        """Clear AI conversation history"""
        if self.ai_manager and self.ai_manager.agent:
            self.ai_manager.agent.clear_history()
            self.output_text.append("✓ AI conversation history cleared")
    
    def open_ai_settings(self):
        """Open AI settings dialog"""
        settings_panel = AISettingsPanel()
        settings_panel.agent_manager = self.ai_manager
        
        dialog = QtWidgets.QDialog(self.form)
        dialog.setWindowTitle("AI Agent Settings")
        dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        dialog.resize(500, 600)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.addWidget(settings_panel)
        
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.load_ai_settings()
    
    def load_ai_settings(self):
        """Load AI settings and update agent"""
        if not self.ai_manager:
            return
            
        try:
            import json
            settings_file = os.path.join(FreeCAD.getUserAppDataDir(), "VibeDesign", "ai_settings.json")
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    data = json.load(f)
                
                config = AIAgentConfig()
                config.from_dict(data)
                self.ai_manager.initialize_agent(config)
                
                self.ai_enabled = bool(self.ai_manager.is_available())
                if hasattr(self, 'ai_toggle'):
                    self.ai_toggle.setChecked(self.ai_enabled)
                    self.ai_toggle.setEnabled(True)
            else:
                # Use default config
                self.ai_manager.initialize_agent()
                self.ai_enabled = False
                
        except Exception as e:
            FreeCAD.Console.PrintWarning(f"Could not load AI settings: {str(e)}\n")
            self.ai_enabled = False
        
        # Update AI status if UI exists
        if hasattr(self, 'ai_status'):
            self.update_ai_status()
    
    def update_ai_status(self):
        """Update AI status indicator"""
        if not AI_AVAILABLE:
            self.ai_status.setText("❌ AI Unavailable")
            self.ai_status.setStyleSheet("color: red; font-weight: bold;")
        elif self.ai_enabled and self.ai_manager and self.ai_manager.is_available():
            self.ai_status.setText("🤖 AI Ready")
            self.ai_status.setStyleSheet("color: green; font-weight: bold;")
        elif self.ai_manager:
            self.ai_status.setText("⚙️ AI Disabled")
            self.ai_status.setStyleSheet("color: orange; font-weight: bold;")
        else:
            self.ai_status.setText("❓ AI Unknown")
            self.ai_status.setStyleSheet("color: gray; font-weight: bold;")

class PromptParser:
    """Parser for natural language geometric descriptions"""
    
    def __init__(self):
        # Unit conversion to mm (FreeCAD's default)
        self.units = {
            'mm': 1.0,
            'cm': 10.0,
            'dm': 100.0,
            'm': 1000.0,
            'in': 25.4,
            'ft': 304.8,
            '"': 25.4,
            "'": 304.8
        }
        
        # Shape patterns
        self.shape_patterns = {
            'box': [r'box', r'cube', r'rectangular', r'cuboid'],
            'cylinder': [r'cylinder', r'tube', r'pipe'],
            'sphere': [r'sphere', r'ball'],
            'cone': [r'cone']
        }
    
    def parse_and_execute(self, prompt):
        """Parse prompt and create the object"""
        prompt = prompt.lower().strip()
        
        # Determine shape type
        shape_type = self.detect_shape(prompt)
        if not shape_type:
            return None
        
        # Extract dimensions
        dimensions = self.extract_dimensions(prompt)
        if not dimensions:
            return None
        
        # Create the object
        return self.create_shape(shape_type, dimensions, prompt)
    
    def detect_shape(self, prompt):
        """Detect the shape type from the prompt"""
        for shape, patterns in self.shape_patterns.items():
            for pattern in patterns:
                if re.search(pattern, prompt):
                    return shape
        return None
    
    def extract_dimensions(self, prompt):
        """Extract dimensions from the prompt"""
        # Pattern for dimensions like "10x20x30", "diameter 25", "radius 15", "height 50"
        dimensions = {}
        
        # XxYxZ pattern (e.g., "8x8x8 cm")
        xyz_match = re.search(r'(\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)\s*([a-z"\']*)', prompt)
        if xyz_match:
            x, y, z, unit = xyz_match.groups()
            unit_factor = self.units.get(unit or 'mm', 1.0)
            dimensions = {
                'length': float(x) * unit_factor,
                'width': float(y) * unit_factor,
                'height': float(z) * unit_factor
            }
        
        # Individual dimension patterns
        patterns = {
            'diameter': r'diameter\s+(\d+(?:\.\d+)?)\s*([a-z"\']*)',
            'radius': r'radius\s+(\d+(?:\.\d+)?)\s*([a-z"\']*)',
            'height': r'height\s+(\d+(?:\.\d+)?)\s*([a-z"\']*)',
            'length': r'length\s+(\d+(?:\.\d+)?)\s*([a-z"\']*)',
            'width': r'width\s+(\d+(?:\.\d+)?)\s*([a-z"\']*)'
        }
        
        for dim_name, pattern in patterns.items():
            match = re.search(pattern, prompt)
            if match:
                value, unit = match.groups()
                unit_factor = self.units.get(unit or 'mm', 1.0)
                dimensions[dim_name] = float(value) * unit_factor
        
        return dimensions
    
    def create_shape(self, shape_type, dimensions, prompt):
        """Create the actual FreeCAD shape"""
        doc = FreeCAD.ActiveDocument
        if not doc:
            doc = FreeCAD.newDocument()
        
        obj_name = self.generate_object_name(shape_type)
        
        if shape_type == 'box':
            return self.create_box(doc, obj_name, dimensions)
        elif shape_type == 'cylinder':
            return self.create_cylinder(doc, obj_name, dimensions)
        elif shape_type == 'sphere':
            return self.create_sphere(doc, obj_name, dimensions)
        elif shape_type == 'cone':
            return self.create_cone(doc, obj_name, dimensions)
        
        return None
    
    def create_box(self, doc, name, dims):
        """Create a box/cube"""
        length = dims.get('length', 10)
        width = dims.get('width', length)  # Default to cube if only one dimension
        height = dims.get('height', length)
        
        obj = doc.addObject("Part::Box", name)
        obj.Length = length
        obj.Width = width
        obj.Height = height
        return f"Box ({length:.1f} x {width:.1f} x {height:.1f} mm)"
    
    def create_cylinder(self, doc, name, dims):
        """Create a cylinder"""
        radius = dims.get('radius', dims.get('diameter', 10) / 2)
        height = dims.get('height', 10)
        
        obj = doc.addObject("Part::Cylinder", name)
        obj.Radius = radius
        obj.Height = height
        return f"Cylinder (radius {radius:.1f} mm, height {height:.1f} mm)"
    
    def create_sphere(self, doc, name, dims):
        """Create a sphere"""
        radius = dims.get('radius', dims.get('diameter', 10) / 2)
        
        obj = doc.addObject("Part::Sphere", name)
        obj.Radius = radius
        return f"Sphere (radius {radius:.1f} mm)"
    
    def create_cone(self, doc, name, dims):
        """Create a cone"""
        radius = dims.get('radius', dims.get('diameter', 10) / 2)
        height = dims.get('height', 10)
        
        obj = doc.addObject("Part::Cone", name)
        obj.Radius1 = radius
        obj.Radius2 = 0  # Point at top
        obj.Height = height
        return f"Cone (radius {radius:.1f} mm, height {height:.1f} mm)"
    
    def generate_object_name(self, shape_type):
        """Generate a unique object name"""
        doc = FreeCAD.ActiveDocument
        base_name = shape_type.capitalize()
        counter = 1
        name = base_name
        
        while doc.getObject(name):
            name = f"{base_name}{counter:03d}"
            counter += 1
        
        return name

# Register the command
FreeCADGui.addCommand('VibeDesign_PromptCommand', VibeDesignPromptCommand())

# Import AI settings command if available
if AI_AVAILABLE:
    try:
        from AISettings import AISettingsCommand
        FreeCADGui.addCommand('VibeDesign_AISettings', AISettingsCommand())
    except ImportError:
        pass