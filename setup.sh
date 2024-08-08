#!/bin/bash

# Update package list
sudo apt update

# Install Python3 and venv if not already installed
sudo apt install -y python3 python3-venv python3-pip nginx

# Create a virtual environment in the 'venv' directory
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install the required packages
if [ -f requirements.txt ]; then
    venv/bin/pip install -r requirements.txt
else
    echo "requirements.txt file not found!"
fi

# Deactivate the virtual environment
deactivate

echo "Setup complete!"
