# Contributing to VibeDesign 🤝

Thank you for your interest in contributing to VibeDesign! This document provides guidelines and information for contributors.

## 🌟 Ways to Contribute

### 🐛 **Bug Reports**
- Use [GitHub Issues](https://github.com/yourusername/VibeDesign/issues) with the "bug" label
- Include detailed reproduction steps
- Provide FreeCAD version, OS, and Python version
- Share example prompts that fail
- Include FreeCAD console output if available

### 💡 **Feature Requests**
- Use [GitHub Issues](https://github.com/yourusername/VibeDesign/issues) with the "enhancement" label
- Describe the use case and expected behavior
- Include example natural language commands
- Consider whether the feature should use AI or rule-based implementation
- Provide mockups or sketches if applicable

### 📝 **Documentation**
- Improve README, CHANGELOG, or inline code documentation
- Add usage examples and tutorials
- Translate documentation to other languages
- Create video tutorials or blog posts

### 🛠️ **Code Contributions**
- Fix bugs and implement new features
- Improve AI prompt handling and accuracy
- Add support for new shapes or operations
- Optimize performance and memory usage
- Add new AI provider integrations

## 🚀 **Development Setup**

### **Prerequisites**
- FreeCAD 0.20+ installed
- Python 3.8+ with pip
- Git for version control
- (Optional) Ollama for local AI testing

### **Local Development**
1. **Fork and clone:**
   ```bash
   git clone https://github.com/yourusername/VibeDesign.git
   cd VibeDesign
   ```

2. **Install dependencies:**
   ```bash
   pip install requests
   # Optional for enhanced testing:
   # pip install openai anthropic
   ```

3. **Set up FreeCAD link:**
   ```bash
   # Create symlink to your FreeCAD Mod directory
   ln -s $(pwd) ~/.local/share/FreeCAD/Mod/VibeDesign
   ```

4. **Test installation:**
   - Start FreeCAD
   - Switch to "Vibe Design" workbench
   - Test basic functionality

### **Testing with AI Providers**

#### **Ollama (Local Testing)**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull test model
ollama pull llama3.1:8b

# Start service
ollama serve

# Test connection
curl http://localhost:11434/api/tags
```

#### **OpenAI (Cloud Testing)**
```bash
# Set environment variable for testing
export OPENAI_API_KEY="your-test-key"

# Test connection
python -c "
import requests
r = requests.post('https://api.openai.com/v1/models', 
                  headers={'Authorization': f'Bearer {OPENAI_API_KEY}'})
print(r.status_code)
"
```

## 📋 **Development Guidelines**

### **Code Style**
- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings for all public functions
- Keep functions focused and under 50 lines when possible
- Use type hints where appropriate

```python
def create_box(self, doc: FreeCAD.Document, name: str, dimensions: Dict[str, float]) -> str:
    """Create a box object from dimensions.
    
    Args:
        doc: FreeCAD document to add object to
        name: Unique name for the object
        dimensions: Dict with 'length', 'width', 'height' keys
    
    Returns:
        Human-readable description of created object
        
    Raises:
        ValueError: If dimensions are invalid
    """
```

### **Error Handling**
- Always handle potential exceptions gracefully
- Provide meaningful error messages to users
- Log detailed error information to FreeCAD console
- Implement fallback mechanisms where possible

```python
try:
    result = self.ai_manager.process_prompt(prompt)
except ConnectionError as e:
    FreeCAD.Console.PrintWarning(f"AI connection failed: {e}\n")
    return self.fallback_parser.parse(prompt)
except Exception as e:
    FreeCAD.Console.PrintError(f"Unexpected error: {e}\n")
    return None
```

### **AI Integration**
- Always provide fallback to rule-based parsing
- Handle API rate limits and timeouts gracefully
- Validate AI responses before executing commands
- Support multiple AI providers consistently

### **FreeCAD Integration**
- Use FreeCAD's native object types when possible
- Follow FreeCAD naming conventions
- Integrate with FreeCAD's undo/redo system
- Respect user preferences and units

## 🧪 **Testing**

### **Manual Testing Checklist**
- [ ] Basic shape creation (box, cylinder, sphere, cone)
- [ ] Unit conversion (mm, cm, m, in, ft)
- [ ] AI provider switching (Ollama, OpenAI, Anthropic)
- [ ] Error handling with invalid prompts
- [ ] Settings persistence across sessions
- [ ] Fallback mode when AI is unavailable

### **AI Testing Prompts**
Test these prompts across different AI providers:

```
# Basic shapes
create a box 10x20x30 mm
make a cylinder diameter 25 height 50

# Complex requests
create a bearing housing with 20mm bore
make a mounting bracket with 4 holes
design a phone stand for 6 inch screen

# Edge cases
make a very small sphere 0.1mm radius
create a huge box 1000x1000x1000 mm
build something impossible
```

### **Cross-Platform Testing**
- Test on Linux, Windows, and macOS when possible
- Verify path handling and file system differences
- Check FreeCAD version compatibility (0.20, 0.21+)

## 📝 **Pull Request Process**

### **Before Submitting**
1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Test thoroughly with multiple scenarios
3. Update documentation if needed
4. Add/update examples in README
5. Run basic functionality tests

### **PR Description Template**
```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that breaks existing functionality)
- [ ] Documentation update

## Testing
- [ ] Tested with Ollama
- [ ] Tested with OpenAI/Anthropic (if applicable)
- [ ] Tested fallback mode
- [ ] Tested on [OS name]
- [ ] Added/updated examples

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### **Review Process**
1. Automated checks (if set up)
2. Manual review by maintainers
3. Testing by community members
4. Feedback incorporation
5. Final approval and merge

## 🏗️ **Architecture Overview**

### **Core Components**
```
VibeDesign/
├── InitGui.py              # Workbench registration
├── VibeDesignCommands.py   # Main UI and command handling
├── AIAgent.py              # AI integration and processing
├── AISettings.py           # Configuration management
└── Resources/              # Icons and assets
```

### **Key Classes**
- `VibeDesignPromptPanel`: Main user interface
- `AIAgent`: Handles LLM communication and response parsing
- `PromptParser`: Rule-based fallback parsing
- `AIAgentManager`: Threading and async processing
- `AISettingsPanel`: Configuration UI

### **Data Flow**
1. User enters natural language prompt
2. UI determines processing mode (AI vs. rule-based)
3. Prompt is processed asynchronously (if AI)
4. Structured commands are generated
5. FreeCAD objects are created
6. UI provides feedback to user

## 🎯 **Priority Areas for Contribution**

### **High Priority**
- Bug fixes for existing functionality
- Performance optimizations
- Better error handling and user feedback
- Cross-platform compatibility issues
- Documentation improvements

### **Medium Priority**
- New AI provider integrations
- Additional shape types (torus, wedge improvements)
- Better prompt understanding patterns
- UI/UX enhancements
- Translation support

### **Low Priority**
- Advanced features (boolean operations, assemblies)
- Code generation and export features
- Visual prompt processing
- Integration with other FreeCAD workbenches

## 🤔 **Questions?**

- **General Questions**: Use [GitHub Discussions](https://github.com/yourusername/VibeDesign/discussions)
- **Development Help**: Ask in the "Development" discussion category
- **Bug Reports**: Create an issue with detailed information
- **Feature Ideas**: Start a discussion before creating an issue

## 🎉 **Recognition**

Contributors will be:
- Listed in the project README
- Mentioned in release notes
- Given credit in commit messages
- Invited to be maintainers (for significant contributions)

Thank you for helping make VibeDesign better! 🚀