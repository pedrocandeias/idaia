# VibeDesign 🤖 - AI-Powered Natural Language CAD for FreeCAD

[![FreeCAD Version](https://img.shields.io/badge/FreeCAD-0.20+-blue.svg)](https://www.freecad.org/)
[![Python Version](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![AI Powered](https://img.shields.io/badge/AI-Powered-purple.svg)](https://ollama.com/)

**Create 3D CAD models using natural language descriptions!** VibeDesign transforms the way you interact with FreeCAD by letting you describe what you want to create in plain English, and it handles the complex CAD operations for you.

> 🎯 **From**: "I need to create a Part::Box with Length=80mm, Width=80mm, Height=80mm"  
> 🚀 **To**: "create a square box, 8x8x8 cm"  
> 🤖 **AI Mode**: "create a bearing housing for a 20mm shaft with mounting holes"

## ✨ Key Features

### 🧠 **Dual Processing Modes**
- **🤖 AI Agent Mode**: Advanced reasoning with local/cloud LLMs for complex requests
- **⚡ Rule-Based Mode**: Fast, reliable parsing for standard geometric shapes
- **🔄 Smart Fallback**: Automatically switches modes if one fails

### 🎨 **Natural Language Understanding** 
```
✅ "create a box 10x20x30 mm"
✅ "make a cylinder height 50 diameter 25"  
✅ "create a bearing housing with 20mm bore and 35mm outer diameter"
✅ "design a phone stand at 45 degree angle for 6 inch screen"
✅ "make a mounting bracket with 4 bolt holes, 50mm spacing"
```

### 🔧 **Comprehensive Shape Support**
| Shape Type | Keywords | AI Enhanced |
|------------|----------|-------------|
| **Box/Cube** | `box`, `cube`, `rectangular`, `cuboid` | ✅ Positioning & rotation |
| **Cylinder** | `cylinder`, `tube`, `pipe` | ✅ Complex orientations |
| **Sphere** | `sphere`, `ball` | ✅ Multi-sphere assemblies |
| **Cone** | `cone`, `tapered` | ✅ Truncated cones |
| **Torus** | `torus`, `donut`, `ring` | 🤖 AI Only |
| **Wedge** | `wedge`, `ramp` | 🤖 AI Only |

### 🌐 **Multi-Provider AI Support**
| Provider | Type | Privacy | Cost | Best For |
|----------|------|---------|------|----------|
| **Ollama** | Local | 🔒 100% Private | 💰 Free | Daily use, privacy |
| **OpenAI** | Cloud | ⚠️ Data shared | 💳 Pay-per-use | Advanced reasoning |
| **Anthropic** | Cloud | ⚠️ Data shared | 💳 Pay-per-use | Complex instructions |

## 🚀 Quick Start

### 📦 **Installation**

1. **Download the addon:**
   ```bash
   git clone https://github.com/yourusername/VibeDesign.git
   # Or download ZIP from GitHub releases
   ```

2. **Install to FreeCAD:**
   - Copy `VibeDesign` folder to your FreeCAD `Mod` directory:
     - **Linux**: `~/.local/share/FreeCAD/Mod/`
     - **Windows**: `%APPDATA%\FreeCAD\Mod\`
     - **macOS**: `~/Library/Preferences/FreeCAD/Mod/`

3. **Install dependencies:**
   ```bash
   pip install requests
   ```

4. **Restart FreeCAD** and find "Vibe Design" in the workbench selector

### 🎯 **Basic Usage**

1. Switch to the **"Vibe Design"** workbench
2. Click the **"Natural Language Prompt"** tool 📝
3. Enter your description: `"create a box 20x30x40 mm"`
4. Click **"Create Object"** ⚡
5. Watch your object appear! ✨

## 🤖 AI Setup (Optional but Recommended)

### 🏠 **Option 1: Local AI with Ollama (Recommended)**

**Why Ollama?** 🔒 Complete privacy, 💰 free forever, ⚡ fast responses

1. **Install Ollama:**
   ```bash
   # Linux/macOS
   curl -fsSL https://ollama.com/install.sh | sh
   
   # Windows: Download from ollama.com
   ```

2. **Download a model:**
   ```bash
   # Recommended: Good balance of speed and quality
   ollama pull llama3.1:8b
   
   # For better quality (requires more RAM):
   ollama pull llama3.1:70b
   
   # For fastest responses:
   ollama pull qwen2.5:7b
   ```

3. **Start Ollama:**
   ```bash
   ollama serve
   ```

4. **Configure in VibeDesign:**
   - Click **"AI Settings"** ⚙️
   - Provider: `ollama`
   - Model: `llama3.1:8b`
   - Base URL: `http://localhost:11434/v1`
   - Click **"Test Connection"** ✅

### ☁️ **Option 2: OpenAI GPT**

1. **Get API key** from [OpenAI Platform](https://platform.openai.com/)
2. **Configure in VibeDesign:**
   - Provider: `openai`
   - Model: `gpt-4` or `gpt-4-turbo`
   - API Key: `your-openai-key`

### 🔮 **Option 3: Anthropic Claude**

1. **Get API key** from [Anthropic Console](https://console.anthropic.com/)
2. **Configure in VibeDesign:**
   - Provider: `anthropic`
   - Model: `claude-3-5-sonnet-20241022`
   - API Key: `your-anthropic-key`

## 💡 Usage Examples

### 🎯 **Basic Shapes** (Works without AI)
```
create a square box, 8x8x8 cm
make a cylinder height 50 diameter 25 mm
create a sphere radius 15 cm
make a cone height 30 radius 10 mm
```

### 🤖 **AI-Powered Complex Requests**
```
create a bearing housing with 20mm inner diameter, 35mm outer diameter, and 10mm height
make a phone stand at 45 degree angle that fits a 6 inch screen
design a mounting bracket with 4 bolt holes in a square pattern, 50mm spacing
create a simple gear with 20 teeth and 5mm center bore
make a cable management clip for 10mm diameter cables
build a parametric enclosure 100x60x40mm with ventilation slots
```

### 🔄 **Iterative Design** (AI Context Awareness)
```
User: create a box 50x30x20 mm
AI: ✅ Created Box001

User: add a cylinder on top, diameter 10mm, height 15mm  
AI: ✅ Created Cylinder001 positioned on Box001

User: make 4 mounting holes in the corners of the box
AI: ✅ Created 4 holes in Box001 corners
```

## 🎛️ **Advanced Features**

### 📊 **Unit Support**
- **Metric**: `mm` (default), `cm`, `dm`, `m`
- **Imperial**: `in`, `"`, `ft`, `'`
- **Auto-conversion** to FreeCAD's mm standard

### 🧠 **AI Context Awareness**
- Remembers all objects in your current document
- Maintains conversation history for iterative design
- Understands spatial relationships ("on top of", "next to")
- Learns from your design patterns within a session

### ⚙️ **Customizable AI Behavior**
- **Temperature**: Control creativity vs. precision (0.0 - 2.0)
- **Timeout**: Adjust for slow connections (5-300 seconds)
- **Retries**: Automatic retry on failures (1-10 attempts)
- **Model Selection**: Choose optimal model for your hardware

## 🔧 **Troubleshooting**

### ❌ **Common Issues**

| Issue | Solution |
|-------|----------|
| "AI Unavailable" | Install: `pip install requests` |
| "Connection Failed" | Check if Ollama is running: `ollama serve` |
| "Slow AI Response" | Try smaller model or increase timeout |
| "Poor AI Results" | Use more detailed prompts |
| "No Object Created" | Check FreeCAD console for error details |

### 🔍 **Debug Steps**

1. **Check FreeCAD Console** (View → Panels → Report view)
2. **Test AI Connection** (AI Settings → Test Connection)
3. **Try Fallback Mode** (Disable AI toggle, use simple prompts)
4. **Verify Dependencies**: `python -c "import requests; print('OK')"`

### 📖 **Getting Better Results**

#### ✅ **Good Prompts:**
- `"create a bearing housing with 20mm bore, 35mm outer diameter, 10mm height"`
- `"make a rectangular mounting plate 100x50x5mm with 4 holes at corners"`

#### ❌ **Vague Prompts:**
- `"make something round"`  
- `"create a part"`

## 🛣️ **Roadmap**

### 🎯 **Planned Features**
- **Boolean Operations**: "subtract cylinder from box"
- **Assemblies**: Multi-part design with relationships  
- **Parametric Modeling**: Constraint-based design
- **Material Assignment**: "make it aluminum"
- **Standard Parts**: "add M6 bolt here"
- **Sketches & Profiles**: 2D sketch generation
- **Pattern Operations**: Linear and circular arrays

### 🔮 **Future AI Enhancements**
- **Visual Understanding**: Process images and sketches
- **Design Optimization**: AI-suggested improvements
- **Code Generation**: Export to FreeCAD Python scripts
- **Multi-language Support**: Design in your native language

## 🤝 **Contributing**

We welcome contributions! Here's how you can help:

### 🚀 **For Developers**
1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Test** with multiple AI providers
4. **Commit** your changes: `git commit -m 'Add amazing feature'`
5. **Push** to branch: `git push origin feature/amazing-feature`
6. **Open** a Pull Request

### 🐛 **Bug Reports**
- Use GitHub Issues with detailed descriptions
- Include FreeCAD version, OS, and error messages
- Provide example prompts that fail

### 💡 **Feature Requests**
- Describe the use case and expected behavior
- Include example natural language commands
- Consider AI vs. rule-based implementation

## 📊 **Project Stats**

- **🏗️ Architecture**: Modular Python with plugin system
- **📁 Codebase**: ~2000 lines across 6 core files  
- **🧪 Testing**: Compatible with FreeCAD 0.20+
- **🌍 Localization**: English (more languages planned)
- **📦 Dependencies**: Minimal (only `requests` for AI)

## 🙏 **Acknowledgments**

- **FreeCAD Team**: For the amazing open-source CAD platform
- **Ollama Project**: For making local AI accessible
- **OpenAI & Anthropic**: For powerful language models
- **Community Contributors**: For feedback, testing, and improvements

## 📜 **License**

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License - Free for commercial and personal use
✅ Use commercially  ✅ Modify  ✅ Distribute  ✅ Private use
```

## 📞 **Support & Community**

- **🐛 Issues**: [GitHub Issues](https://github.com/yourusername/VibeDesign/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/yourusername/VibeDesign/discussions)  
- **🏛️ Forum**: [FreeCAD Forum](https://forum.freecad.org/)
- **📧 Email**: your-email@example.com

---

<div align="center">

**⭐ Star this repo if VibeDesign helps your CAD workflow! ⭐**

*Made with ❤️ for the FreeCAD community*

[🚀 Get Started](#-quick-start) • [📖 Documentation](#-usage-examples) • [🤖 AI Setup](#-ai-setup-optional-but-recommended) • [🤝 Contribute](#-contributing)

</div>

---

> **💡 Pro Tip**: Start with simple prompts, then gradually try more complex requests as you get comfortable with the AI's capabilities. The conversation memory means each interaction builds on the previous ones!