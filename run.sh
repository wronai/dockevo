#!/bin/bash

# Container OS MVP Launcher
echo "🚀 Starting Container OS MVP..."

# Check if main file exists
if [ ! -f "container-os.py" ]; then
    echo "❌ container-os.py not found"
    echo "Please run this script from the Container OS directory"
    exit 1
fi

# Check Python dependencies
python3 -c "import docker, psutil" 2>/dev/null || {
    echo "❌ Missing dependencies. Run setup.sh first"
    exit 1
}

# Start Container OS
python3 container-os.py
