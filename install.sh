#!/bin/bash

# VibeDesign Installation Script
# Interactive installer for FreeCAD VibeDesign addon

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}  VibeDesign FreeCAD Addon Installer${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

# Global arrays for detected installations
declare -a freecad_paths
declare -a installation_types  
declare -a installation_descriptions

# Function to detect FreeCAD installation type and paths
detect_freecad() {
    freecad_paths=()
    installation_types=()
    installation_descriptions=()
    
    print_info "Detecting FreeCAD installations..."
    
    # Check for snap installation
    if command -v snap >/dev/null 2>&1 && snap list freecad >/dev/null 2>&1; then
        freecad_paths+=("$HOME/snap/freecad/common/Mod")
        installation_types+=("snap")
        installation_descriptions+=("FreeCAD Snap (Ubuntu/Linux)")
        print_info "Found FreeCAD Snap installation"
    fi
    
    # Check for flatpak installation
    if command -v flatpak >/dev/null 2>&1 && flatpak list | grep -q org.freecadweb.FreeCAD; then
        freecad_paths+=("$HOME/.var/app/org.freecadweb.FreeCAD/data/FreeCAD/Mod")
        installation_types+=("flatpak")
        installation_descriptions+=("FreeCAD Flatpak")
        print_info "Found FreeCAD Flatpak installation"
    fi
    
    # Check for standard system installations
    local standard_paths=(
        "$HOME/.local/share/FreeCAD/Mod"      # Linux user install
        "$HOME/.FreeCAD/Mod"                  # Alternative Linux path
        "/usr/share/freecad/Mod"              # System-wide Linux
        "$HOME/Library/Preferences/FreeCAD/Mod" # macOS
    )
    
    for path in "${standard_paths[@]}"; do
        if [[ -d "$(dirname "$path")" ]] || command -v freecad >/dev/null 2>&1; then
            freecad_paths+=("$path")
            installation_types+=("standard")
            if [[ "$path" == *"Library/Preferences"* ]]; then
                installation_descriptions+=("Standard FreeCAD (macOS)")
            elif [[ "$path" == "/usr/share"* ]]; then
                installation_descriptions+=("System-wide FreeCAD (Linux)")
            else
                installation_descriptions+=("User FreeCAD (Linux)")
            fi
            print_info "Found standard FreeCAD installation path: $path"
            break
        fi
    done
    
    # Check for FreeCAD executable
    if command -v freecad >/dev/null 2>&1; then
        print_info "FreeCAD executable found in PATH"
    fi
    
    # If no installations found, provide manual options
    if [[ ${#freecad_paths[@]} -eq 0 ]]; then
        print_warning "No FreeCAD installations detected automatically"
        freecad_paths+=("$HOME/.local/share/FreeCAD/Mod")
        installation_types+=("manual")
        installation_descriptions+=("Default path (create if needed)")
    fi
    
    print_info "Detection complete: found ${#freecad_paths[@]} installation(s)"
}

# Function to select installation path
select_installation_path() {
    if [[ ${#freecad_paths[@]} -eq 1 ]]; then
        print_info "Single installation found, using: ${freecad_paths[0]}"
        selected_path="${freecad_paths[0]}"
        return
    fi
    
    echo -e "\n${YELLOW}Multiple FreeCAD installations detected:${NC}"
    for i in "${!freecad_paths[@]}"; do
        echo "  $((i+1)). ${installation_descriptions[i]}"
        echo "      📁 ${freecad_paths[i]}"
    done
    
    echo "  $((${#freecad_paths[@]}+1)). Custom path (manual entry)"
    
    echo
    while true; do
        read -p "Select installation path [1-$((${#freecad_paths[@]}+1))]: " choice
        
        if [[ "$choice" =~ ^[0-9]+$ ]] && [[ $choice -ge 1 ]] && [[ $choice -le $((${#freecad_paths[@]}+1)) ]]; then
            if [[ $choice -eq $((${#freecad_paths[@]}+1)) ]]; then
                echo
                read -p "Enter custom FreeCAD Mod directory path: " custom_path
                selected_path="$custom_path"
                return
            else
                selected_path="${freecad_paths[$((choice-1))]}"
                return
            fi
        else
            print_error "Invalid selection. Please choose 1-$((${#freecad_paths[@]}+1))"
        fi
    done
}

# Function to install dependencies
install_dependencies() {
    local install_type="$1"
    
    print_info "Installing Python dependencies..."
    
    case "$install_type" in
        "snap")
            print_warning "FreeCAD Snap installation detected"
            print_warning "AI features may be limited due to snap sandboxing"
            print_info "Attempting to install requests for system Python..."
            if command -v pip3 >/dev/null 2>&1; then
                pip3 install --user requests || print_warning "Failed to install requests via pip3"
            elif command -v pip >/dev/null 2>&1; then
                pip install --user requests || print_warning "Failed to install requests via pip"
            else
                print_warning "pip not found. Please install requests manually: pip install requests"
            fi
            ;;
        "flatpak")
            print_warning "FreeCAD Flatpak installation detected"
            print_warning "Dependencies need to be installed in the Flatpak environment"
            print_info "Please run: flatpak run --command=pip3 org.freecadweb.FreeCAD install requests"
            ;;
        *)
            if command -v pip3 >/dev/null 2>&1; then
                pip3 install --user requests
                print_success "Installed requests via pip3"
            elif command -v pip >/dev/null 2>&1; then
                pip install --user requests
                print_success "Installed requests via pip"
            else
                print_error "pip not found. Please install Python pip first"
                return 1
            fi
            ;;
    esac
}

# Function to select and download AI model
select_and_download_model() {
    echo -e "\n${YELLOW}Available AI Models:${NC}"
    echo "  1. Llama 3.1 8B (Recommended) - Good balance of speed and quality (~4.7GB)"
    echo "  2. Llama 3.1 70B - Best quality but slower, needs 32GB+ RAM (~40GB)"
    echo "  3. Llama 3.2 3B - Fast and lightweight (~2GB)"
    echo "  4. Qwen2.5 7B - Fast alternative with good coding skills (~4.4GB)"
    echo "  5. Qwen2.5 14B - Better quality, moderate speed (~8.4GB)"
    echo "  6. CodeLlama 7B - Specialized for code generation (~3.8GB)"
    echo "  7. Mistral 7B - Efficient general-purpose model (~4.1GB)"
    echo "  8. Phi-3 Mini - Microsoft's compact model (~2.3GB)"
    echo "  9. Skip - Don't download any model now"
    
    echo
    while true; do
        read -p "Select a model [1-9]: " choice
        
        case $choice in
            1)
                selected_model="llama3.1:8b"
                model_name="Llama 3.1 8B"
                break
                ;;
            2)
                selected_model="llama3.1:70b"
                model_name="Llama 3.1 70B"
                print_warning "This model requires 32GB+ RAM. Proceed only if you have sufficient memory."
                read -p "Continue with download? (y/n): " -n 1 -r
                echo
                if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                    print_info "Model download cancelled"
                    return
                fi
                break
                ;;
            3)
                selected_model="llama3.2:3b"
                model_name="Llama 3.2 3B"
                break
                ;;
            4)
                selected_model="qwen2.5:7b"
                model_name="Qwen2.5 7B"
                break
                ;;
            5)
                selected_model="qwen2.5:14b"
                model_name="Qwen2.5 14B"
                print_warning "This model requires 16GB+ RAM for optimal performance."
                break
                ;;
            6)
                selected_model="codellama:7b"
                model_name="CodeLlama 7B"
                break
                ;;
            7)
                selected_model="mistral:7b"
                model_name="Mistral 7B"
                break
                ;;
            8)
                selected_model="phi3:mini"
                model_name="Phi-3 Mini"
                break
                ;;
            9)
                print_info "Skipping model download. You can download models later with: ollama pull <model>"
                return
                ;;
            *)
                print_error "Invalid selection. Please choose 1-9"
                continue
                ;;
        esac
    done
    
    print_info "Downloading $model_name ($selected_model)..."
    print_info "This may take several minutes depending on your internet connection..."
    
    # Start ollama service if not running
    ollama serve > /dev/null 2>&1 &
    OLLAMA_PID=$!
    sleep 2
    
    # Download the selected model
    if ollama pull "$selected_model"; then
        print_success "Model $model_name downloaded successfully"
        print_info "To start using AI features, run: ollama serve"
        print_info "In VibeDesign, configure AI settings with model: $selected_model"
    else
        print_error "Failed to download model $model_name"
        print_info "You can try downloading it later with: ollama pull $selected_model"
    fi
    
    # Stop ollama service
    kill $OLLAMA_PID 2>/dev/null || true
}

# Function to install Ollama
install_ollama() {
    print_info "Installing Ollama..."
    
    if command -v ollama >/dev/null 2>&1; then
        print_warning "Ollama is already installed"
        return 0
    fi
    
    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl -fsSL https://ollama.com/install.sh | sh
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew >/dev/null 2>&1; then
            brew install ollama
        else
            print_warning "Homebrew not found. Please install Ollama manually from https://ollama.com"
            return 1
        fi
    else
        print_warning "Unsupported OS. Please install Ollama manually from https://ollama.com"
        return 1
    fi
    
    print_success "Ollama installed successfully"
    
    # Ask if user wants to download a model
    read -p "Do you want to download an AI model? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        select_and_download_model
    fi
}

# Function to copy addon files
copy_addon() {
    local target_path="$1"
    local source_path="$(dirname "$0")/idaiavibedesign"
    
    # Check if source exists
    if [[ ! -d "$source_path" ]]; then
        print_error "Source directory not found: $source_path"
        print_info "Please run this script from the idaia repository root directory"
        exit 1
    fi
    
    # Create target directory if it doesn't exist
    mkdir -p "$target_path"
    
    # Copy addon files
    print_info "Copying VibeDesign addon to $target_path..."
    cp -r "$source_path" "$target_path/"
    
    # Set proper permissions
    chmod -R 755 "$target_path/idaiavibedesign"
    
    print_success "VibeDesign addon copied successfully"
}

# Function to verify installation
verify_installation() {
    local target_path="$1"
    local addon_path="$target_path/idaiavibedesign"
    
    if [[ -d "$addon_path" ]] && [[ -f "$addon_path/InitGui.py" ]]; then
        print_success "Installation verified: Files are in place"
        return 0
    else
        print_error "Installation verification failed"
        return 1
    fi
}

# Main installation function
main() {
    # Check for uninstall flag
    if [[ "$1" == "--uninstall" ]] || [[ "$1" == "-u" ]]; then
        if [[ -f "$(dirname "$0")/uninstall.sh" ]]; then
            exec "$(dirname "$0")/uninstall.sh"
        else
            print_error "Uninstall script not found"
            print_info "Please run the uninstall.sh script directly"
            exit 1
        fi
    fi
    
    # Check for help flag
    if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
        print_header
        echo "Usage: $0 [OPTIONS]"
        echo
        echo "Options:"
        echo "  -h, --help        Show this help message"
        echo "  -u, --uninstall   Run the uninstall script"
        echo
        echo "Interactive installation will start if no options are provided."
        echo
        exit 0
    fi
    
    print_header
    
    # Check if running from correct directory
    if [[ ! -d "idaiavibedesign" ]]; then
        print_error "Please run this script from the idaia repository root directory"
        print_info "Expected to find 'idaiavibedesign' directory in current location"
        exit 1
    fi
    
    # Detect FreeCAD installations
    detect_freecad
    
    
    # Select installation path
    select_installation_path
    # The function will set the selected_path variable
    print_success "Selected installation path: $selected_path"
    
    # Determine installation type
    install_type="standard"
    if echo "$selected_path" | grep -q "snap"; then
        install_type="snap"
    elif echo "$selected_path" | grep -q "flatpak"; then
        install_type="flatpak"
    fi
    
    # Ask about Ollama installation
    echo
    read -p "Do you want to install Ollama for local AI features? (y/n): " -n 1 -r
    echo
    install_ollama_choice="$REPLY"
    
    # Install dependencies
    echo
    install_dependencies "$install_type"
    
    # Copy addon files
    echo
    copy_addon "$selected_path"
    
    # Install Ollama if requested
    if [[ $install_ollama_choice =~ ^[Yy]$ ]]; then
        echo
        install_ollama
    fi
    
    # Verify installation
    echo
    verify_installation "$selected_path"
    
    # Final instructions
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}       Installation Complete!${NC}"
    echo -e "${GREEN}========================================${NC}\n"
    
    print_info "Next steps:"
    echo "  1. Restart FreeCAD"
    echo "  2. Look for 'Vibe Design' in the workbench selector"
    echo "  3. Click the 'Natural Language Prompt' tool to start creating!"
    
    if [[ $install_ollama_choice =~ ^[Yy]$ ]]; then
        echo
        print_info "To use AI features with Ollama:"
        echo "  1. Start Ollama: ollama serve"
        echo "  2. In FreeCAD, click 'AI Settings' and configure:"
        echo "     - Provider: ollama"
        echo "     - Model: llama3.1:8b"
        echo "     - Base URL: http://localhost:11434/v1"
    fi
    
    case "$install_type" in
        "snap")
            echo
            print_warning "Note for Snap users:"
            echo "  - AI features may be limited due to snap sandboxing"
            echo "  - Basic natural language parsing will work without AI"
            echo "  - Try 'sudo snap install --classic freecad' for better AI support"
            ;;
        "flatpak")
            echo
            print_warning "Note for Flatpak users:"
            echo "  - Make sure to install dependencies in the Flatpak environment"
            echo "  - Run: flatpak run --command=pip3 org.freecadweb.FreeCAD install requests"
            ;;
    esac
    
    echo
    print_success "Happy designing with VibeDesign! 🚀"
}

# Run main function
main "$@"