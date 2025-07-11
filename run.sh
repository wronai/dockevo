#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Logging functions
log() { echo -e "${GREEN}[RUN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
info() { echo -e "${BLUE}[INFO]${NC} $1"; }

# Check if running in a virtual environment
in_venv() {
    python3 -c 'import sys; sys.exit(0) if hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix) else sys.exit(1)'
}

# Main execution
main() {
    log "🚀 Starting dockevOS..."
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        error "Python 3.8+ is required but not installed"
    fi
    
    # Check if running in virtual environment
    if ! in_venv; then
        warn "Not running in a virtual environment. It's recommended to use one."
        read -p "Do you want to create and activate a virtual environment? [y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            python3 -m venv venv
            source venv/bin/activate
        fi
    fi
    
    # Install package in development mode if not already installed
    if ! python3 -c "import dockevos" &> /dev/null; then
        log "Installing dockevOS in development mode..."
        pip install -e .
    fi
    
    # Check for required dependencies
    for dep in docker psutil; do
        python3 -c "import $dep" 2>/dev/null || {
            error "Missing required dependency: $dep. Run 'pip install $dep' or 'pip install -e .[stt]' for all dependencies"
        }
    done
    
    # Run the application
    log "Starting dockevOS..."
    python3 -m dockevos "$@"
}

# Only run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
