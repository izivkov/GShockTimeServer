#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip, setuptools, and wheel
pip install --upgrade pip setuptools wheel

# Install twine for uploading the package
pip install twine

# Clean previous builds
rm -rf build dist *.egg-info

# Build the source distribution and wheel distribution
python setup.py sdist bdist_wheel

# Deactivate the virtual environment
deactivate

echo "Build complete. Distribution packages are in the 'dist' directory."

