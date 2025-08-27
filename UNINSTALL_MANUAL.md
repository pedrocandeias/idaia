# Manual Uninstall Guide

If you need to manually remove VibeDesign and Ollama components, follow these steps:

## 🗑️ Remove VibeDesign Addon

Delete the `idaiavibedesign` folder from your FreeCAD Mod directory:

### Linux
```bash
# For Snap installation
rm -rf ~/snap/freecad/common/Mod/idaiavibedesign

# For Flatpak installation  
rm -rf ~/.var/app/org.freecadweb.FreeCAD/data/FreeCAD/Mod/idaiavibedesign

# For standard installation
rm -rf ~/.local/share/FreeCAD/Mod/idaiavibedesign
```

### macOS
```bash
rm -rf ~/Library/Preferences/FreeCAD/Mod/idaiavibedesign
```

### Windows
```cmd
rmdir /s "%APPDATA%\FreeCAD\Mod\idaiavibedesign"
```

## 🤖 Remove Ollama Models

### List installed models:
```bash
ollama list
```

### Remove specific model:
```bash
ollama rm model-name
# Example: ollama rm llama3.1:8b
```

### Remove all models:
```bash
ollama list | grep -v NAME | awk '{print $1}' | xargs -I {} ollama rm {}
```

## 🔧 Remove Ollama Installation

### Linux (Official Install Script)
```bash
# Stop service
sudo systemctl stop ollama
sudo systemctl disable ollama

# Remove files
sudo rm /usr/local/bin/ollama
sudo rm -rf /usr/share/ollama
sudo rm /etc/systemd/system/ollama.service
sudo systemctl daemon-reload

# Remove user data
rm -rf ~/.ollama
```

### Linux (Snap)
```bash
sudo snap remove ollama
```

### macOS (Homebrew)
```bash
brew uninstall ollama
rm -rf ~/.ollama
```

### macOS (Manual)
1. Quit Ollama app if running
2. Delete Ollama from Applications folder
3. Remove user data: `rm -rf ~/.ollama`

## 📦 Remove Python Dependencies

**⚠️ Warning**: Only remove if not used by other applications

```bash
pip uninstall requests
# or
pip3 uninstall requests
```

## ✅ Verify Removal

Check that everything is removed:
```bash
# Check Ollama
which ollama  # Should return nothing

# Check models directory
ls ~/.ollama  # Should not exist

# Check FreeCAD addon (adjust path for your installation)
ls ~/.local/share/FreeCAD/Mod/idaiavibedesign  # Should not exist
```

## 🚀 Quick Removal Commands

### Complete Linux Removal (One-liner)
```bash
# Remove VibeDesign from common locations
rm -rf ~/snap/freecad/common/Mod/idaiavibedesign \
       ~/.var/app/org.freecadweb.FreeCAD/data/FreeCAD/Mod/idaiavibedesign \
       ~/.local/share/FreeCAD/Mod/idaiavibedesign \
       ~/.FreeCAD/Mod/idaiavibedesign

# Remove Ollama (if installed via official script)
sudo systemctl stop ollama 2>/dev/null || true
sudo systemctl disable ollama 2>/dev/null || true
sudo rm -f /usr/local/bin/ollama /etc/systemd/system/ollama.service
rm -rf ~/.ollama
```

## 🆘 Need Help?

If you encounter issues:
1. Try the automated uninstall script: `./uninstall.sh`
2. Check if processes are running: `ps aux | grep ollama`
3. Restart FreeCAD after removal
4. Create an issue on GitHub if problems persist