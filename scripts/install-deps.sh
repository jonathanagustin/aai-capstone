#!/usr/bin/env bash
set -euo pipefail

# Check if apt-get is available
if ! command -v apt-get >/dev/null 2>&1; then
    echo "This script uses apt-get and is designed for Debian/Ubuntu systems."
    echo "Please install LibreOffice using your system's package manager."
    exit 1
fi

# Check if LibreOffice is installed
if ! command -v libreoffice >/dev/null 2>&1; then
    echo "LibreOffice not found. Installing LibreOffice..."
    # Check if sudo is available
    if ! command -v sudo >/dev/null 2>&1; then
        echo "sudo not found. Please run as root or install sudo first."
        exit 1
    fi

    sudo apt-get update -y
    sudo apt-get install -y libreoffice-common libreoffice-writer
    echo "LibreOffice installed successfully."
else
    echo "LibreOffice is already installed."
fi
