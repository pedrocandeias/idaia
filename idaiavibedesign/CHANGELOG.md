# Changelog

All notable changes to the VibeDesign FreeCAD addon will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-08-25

### Added 🤖
- **AI Agent Integration**: Complete AI-powered natural language processing system
  - Multi-provider support (Ollama, OpenAI, Anthropic Claude)
  - Context-aware object creation with conversation memory
  - Complex prompt understanding and reasoning capabilities
  - Async processing with real-time feedback
- **AI Configuration Panel**: Comprehensive settings for AI providers
  - Provider selection (Ollama/OpenAI/Anthropic)
  - Model configuration and API key management
  - Advanced settings (temperature, timeout, retries)
  - Connection testing and model suggestions
- **Enhanced Shape Support**: Additional primitive shapes via AI
  - Torus creation with major/minor radius support
  - Wedge (triangular prism) generation
  - Multi-object assemblies from single prompts
- **Advanced UI Features**:
  - AI/Manual mode toggle with status indicators
  - Conversation history management
  - Enhanced prompt examples for complex requests
  - Real-time AI status updates (🤖 Ready, ⚙️ Disabled, ❌ Unavailable)
- **Intelligent Fallback System**: Automatic fallback to rule-based parser when AI fails
- **Context Persistence**: AI remembers created objects and conversation history
- **Privacy-First Design**: Local AI support with Ollama for offline processing

### Enhanced
- **Prompt Parser**: Extended dimension extraction patterns
- **Object Creation**: Support for positioning and rotation via AI commands
- **Error Handling**: Improved error messages and recovery mechanisms
- **UI Layout**: Reorganized interface for better AI integration
- **Documentation**: Comprehensive setup guides for different AI providers

### Technical
- **Dependencies**: Added `requests` for HTTP API calls
- **Architecture**: Modular AI system with pluggable providers
- **Threading**: Non-blocking AI processing to prevent UI freezing
- **Configuration**: JSON-based settings storage in FreeCAD user directory

## [1.0.0] - 2025-08-25

### Added
- **Initial Release**: VibeDesign FreeCAD workbench for natural language CAD modeling
- **Rule-Based Parser**: Regex-based natural language understanding
  - Shape detection (box, cylinder, sphere, cone)
  - Dimension extraction with unit conversion
  - Multiple dimension formats (XxYxZ, individual parameters)
- **Core Shape Support**:
  - Box/Cube creation with length/width/height
  - Cylinder generation with radius/diameter and height
  - Sphere creation with radius/diameter
  - Cone generation with base radius and height
- **Unit System**: Comprehensive unit conversion
  - Metric: mm (default), cm, dm, m
  - Imperial: inches, feet with symbol support (", ')
  - Automatic conversion to FreeCAD's mm base unit
- **User Interface**:
  - Task panel integration with FreeCAD
  - Real-time feedback and error reporting
  - Example commands and usage instructions
  - Clean, intuitive design following FreeCAD conventions
- **FreeCAD Integration**:
  - Proper workbench registration and icon system
  - Document management and object creation
  - Automatic view fitting and document recomputation
  - Unique object naming with collision detection
- **Package Management**:
  - FreeCAD Addon Manager compatibility
  - Proper package.xml metadata
  - MIT license for open source distribution

### Technical Foundation
- **Python Architecture**: Clean, modular code structure
- **Error Handling**: Comprehensive exception management
- **Logging**: FreeCAD console integration for user feedback
- **Extensibility**: Designed for easy feature additions

## [Unreleased]

### Planned Features
- **Advanced AI Capabilities**:
  - Boolean operations via natural language
  - Parametric modeling with constraints
  - Assembly creation and part relationships
  - Material and appearance assignment
- **Extended Shape Library**:
  - Helical features (springs, threads)
  - Profile-based extrusions
  - Swept and lofted features
  - Custom shape definitions
- **Workflow Enhancements**:
  - Batch object creation
  - Template and preset systems
  - Design history and versioning
  - Export/import of natural language scripts
- **Integration Features**:
  - Part libraries and catalogs
  - Standard hardware integration
  - Engineering calculations
  - Design rule checking

---

## Version History Summary

| Version | Date | Key Features |
|---------|------|--------------|
| 1.1.0 | 2025-08-25 | 🤖 AI Agents, Multi-provider support, Context awareness |
| 1.0.0 | 2025-08-25 | 🎯 Initial release, Rule-based parsing, Core shapes |

## Migration Notes

### From 1.0.0 to 1.1.0
- **Backward Compatible**: All existing prompts continue to work
- **New Dependencies**: Install `requests` library for AI features
- **Optional AI Setup**: AI features are optional, addon works without configuration
- **Settings Migration**: No manual migration needed, settings are auto-created

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on:
- Code style and conventions
- Testing procedures
- Pull request process
- Issue reporting

## Support

- **Documentation**: See [README.md](README.md) for complete setup instructions
- **Issues**: Report bugs and feature requests on [GitHub Issues](https://github.com/yourusername/VibeDesign/issues)
- **Discussions**: Join conversations in [GitHub Discussions](https://github.com/yourusername/VibeDesign/discussions)
- **FreeCAD Forum**: Get help from the community at [FreeCAD Forum](https://forum.freecad.org/)

---

*This changelog follows the [Keep a Changelog](https://keepachangelog.com/) format. For the complete commit history, see the [GitHub repository](https://github.com/yourusername/VibeDesign).*