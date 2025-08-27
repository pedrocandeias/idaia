#!/bin/bash

# VibeDesign Uninstall Script
# Remove VibeDesign addon, Ollama, and AI models

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
    echo -e "\n${RED}========================================${NC}"
    echo -e "${RED}  VibeDesign Uninstall Script${NC}"
    echo -e "${RED}========================================${NC}\n"
}

# Function to list and remove Ollama models
remove_ollama_models() {
    if ! command -v ollama >/dev/null 2>&1; then
        print_info "Ollama is not installed, skipping model removal"
        return 0
    fi
    
    print_info "Checking for installed Ollama models..."
    
    # Start ollama service temporarily
    ollama serve > /dev/null 2>&1 &
    OLLAMA_PID=$!
    sleep 2
    
    # Get list of installed models
    local models
    if models=$(ollama list 2>/dev/null | grep -v "NAME" | awk '{print $1}' | grep -v "^$"); then
        if [[ -n "$models" ]]; then
            echo -e "\n${YELLOW}Installed Ollama models:${NC}"
            echo "$models" | nl -w2 -s'. '
            echo "  0. Keep all models"
            echo "  -1. Remove all models"
            
            echo
            read -p "Enter model numbers to remove (space-separated, e.g., '1 3'), 0 to keep all, or -1 to remove all: " choice
            
            if [[ "$choice" == "0" ]]; then
                print_info "Keeping all models"
            elif [[ "$choice" == "-1" ]]; then
                print_warning "Removing ALL Ollama models..."
                while IFS= read -r model; do
                    print_info "Removing model: $model"
                    ollama rm "$model" 2>/dev/null || print_warning "Failed to remove $model"
                done <<< "$models"
                print_success "All models removed"
            else
                # Remove selected models
                for num in $choice; do
                    if [[ "$num" =~ ^[0-9]+$ ]]; then
                        local model
                        model=$(echo "$models" | sed -n "${num}p")
                        if [[ -n "$model" ]]; then
                            print_info "Removing model: $model"
                            ollama rm "$model" 2>/dev/null || print_warning "Failed to remove $model"
                        fi
                    fi
                done
                print_success "Selected models removed"
            fi
        else
            print_info "No Ollama models found"
        fi
    else
        print_info "Could not list models (Ollama may not be running)"
    fi
    
    # Stop ollama service
    kill $OLLAMA_PID 2>/dev/null || true
    sleep 1
}

# Function to remove Ollama
remove_ollama() {
    if ! command -v ollama >/dev/null 2>&1; then
        print_info "Ollama is not installed"
        return 0
    fi
    
    print_warning "This will completely remove Ollama from your system"
    read -p "Are you sure you want to remove Ollama? (y/n): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Ollama removal cancelled"
        return 0
    fi
    
    print_info "Removing Ollama..."
    
    # Stop ollama service if running
    pkill -f ollama || true
    sleep 2
    
    # Remove based on installation method
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux - check different installation methods
        if command -v snap >/dev/null 2>&1 && snap list ollama >/dev/null 2>&1; then
            # Snap installation
            print_info "Removing Ollama snap..."
            sudo snap remove ollama
        elif systemctl is-active --quiet ollama 2>/dev/null; then
            # Systemd service (official install script)
            print_info "Stopping Ollama service..."
            sudo systemctl stop ollama 2>/dev/null || true
            sudo systemctl disable ollama 2>/dev/null || true
            
            print_info "Removing Ollama files..."
            sudo rm -f /usr/local/bin/ollama
            sudo rm -rf /usr/share/ollama
            sudo rm -f /etc/systemd/system/ollama.service
            sudo systemctl daemon-reload
            
            # Remove user data
            rm -rf ~/.ollama
            
            print_success "Ollama removed"
        else
            # Manual installation
            print_info "Removing Ollama binary..."
            sudo rm -f /usr/local/bin/ollama /usr/bin/ollama
            rm -rf ~/.ollama
            print_success "Ollama removed"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew >/dev/null 2>&1 && brew list ollama >/dev/null 2>&1; then
            print_info "Removing Ollama via Homebrew..."
            brew uninstall ollama
            rm -rf ~/.ollama
        else
            print_warning "Manual Ollama removal on macOS:"
            print_info "1. Quit Ollama app if running"
            print_info "2. Remove from Applications folder"
            print_info "3. Delete ~/.ollama directory"
        fi
    else
        print_warning "Unsupported OS for automatic Ollama removal"
        print_info "Please remove Ollama manually"
    fi
}

# Function to find and remove VibeDesign addon
remove_vibedesign() {
    print_info "Searching for VibeDesign addon installations..."
    
    local found_installations=()
    local addon_paths=(
        "$HOME/snap/freecad/common/Mod/idaiavibedesign"
        "$HOME/.var/app/org.freecadweb.FreeCAD/data/FreeCAD/Mod/idaiavibedesign"
        "$HOME/.local/share/FreeCAD/Mod/idaiavibedesign"
        "$HOME/.FreeCAD/Mod/idaiavibedesign"
        "/usr/share/freecad/Mod/idaiavibedesign"
        "$HOME/Library/Preferences/FreeCAD/Mod/idaiavibedesign"
    )
    
    # Find existing installations
    for path in "${addon_paths[@]}"; do
        if [[ -d "$path" ]]; then
            found_installations+=("$path")
        fi
    done
    
    if [[ ${#found_installations[@]} -eq 0 ]]; then
        print_info "No VibeDesign addon installations found"
        return 0
    fi
    
    echo -e "\n${YELLOW}Found VibeDesign installations:${NC}"
    for i in "${!found_installations[@]}"; do
        echo "  $((i+1)). ${found_installations[i]}"
    done
    echo "  0. Keep all installations"
    echo "  -1. Remove all installations"
    
    echo
    read -p "Select installations to remove (space-separated numbers), 0 to keep all, or -1 to remove all: " choice
    
    if [[ "$choice" == "0" ]]; then
        print_info "Keeping all VibeDesign installations"
        return 0
    elif [[ "$choice" == "-1" ]]; then
        # Remove all
        for path in "${found_installations[@]}"; do
            print_info "Removing: $path"
            rm -rf "$path"
        done
        print_success "All VibeDesign installations removed"
    else
        # Remove selected
        for num in $choice; do
            if [[ "$num" =~ ^[0-9]+$ ]] && [[ $num -ge 1 ]] && [[ $num -le ${#found_installations[@]} ]]; then
                local path="${found_installations[$((num-1))]}"
                print_info "Removing: $path"
                rm -rf "$path"
            fi
        done
        print_success "Selected VibeDesign installations removed"
    fi
}

# Function to remove Python dependencies
remove_dependencies() {
    print_info "Checking for VibeDesign Python dependencies..."
    
    read -p "Remove requests library installed for VibeDesign? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Note: This may affect other Python applications that use requests"
        read -p "Continue with requests removal? (y/n): " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Attempting to remove requests..."
            if command -v pip3 >/dev/null 2>&1; then
                pip3 uninstall requests -y || print_warning "Failed to remove requests via pip3"
            elif command -v pip >/dev/null 2>&1; then
                pip uninstall requests -y || print_warning "Failed to remove requests via pip"
            fi
        fi
    fi
}

# Main uninstall function
main() {
    print_header
    
    echo -e "${YELLOW}This script will help you remove:${NC}"
    echo "  • VibeDesign FreeCAD addon"
    echo "  • Ollama AI models"
    echo "  • Ollama installation"
    echo "  • Python dependencies (optional)"
    echo
    
    read -p "Continue with uninstallation? (y/n): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Uninstallation cancelled"
        exit 0
    fi
    
    echo
    print_info "Starting uninstallation process..."
    
    # Remove VibeDesign addon
    echo
    remove_vibedesign
    
    # Handle Ollama models
    echo
    remove_ollama_models
    
    # Remove Ollama
    echo
    remove_ollama
    
    # Remove dependencies
    echo
    remove_dependencies
    
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}       Uninstallation Complete!${NC}"
    echo -e "${GREEN}========================================${NC}\n"
    
    print_success "Uninstallation process finished"
    print_info "You may need to restart FreeCAD to see changes"
    
    # Show what remains
    if command -v ollama >/dev/null 2>&1; then
        print_info "Ollama is still installed"
    fi
    
    echo
    print_info "Thank you for trying VibeDesign! 👋"
}

# Run main function
main "$@"