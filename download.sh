#!/bin/bash

# Create target directory if it doesn't exist
mkdir -p ./data/test_data/

echo "This script will download public data from Google Drive"

# For public Google Drive folders, we can use direct download links
# First, check if gdown is installed (pip install gdown)
if ! command -v gdown &> /dev/null; then
    echo "The 'gdown' tool is required but not installed."
    echo "Would you like to install it now? (y/n)"
    read -r answer
    if [[ "$answer" =~ ^[Yy]$ ]]; then
        pip install gdown
    else
        echo "Please install gdown manually with: pip install gdown"
        exit 1
    fi
fi

# folder ID from Google Drive share link
FOLDER_ID="1Oc-uP0hs2kUDN-y6Yv42bqNz-J-sk1Po"

echo "Downloading data from Google Drive folder to ./data/test_data/..."
gdown https://drive.google.com/drive/folders/${FOLDER_ID} -O ./data/test_data/ --folder

echo "Download complete!"
