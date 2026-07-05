"""
Sync Datasets from Azure Blob Storage (Stage 2)
Downloads raw dataset files into the local /data directory so existing
ingestion scripts can run unmodified.
"""

import os
import sys

# Ensure parent directory is in path to import storage
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from storage.blob_storage import download_folder_prefix, list_blobs
from dotenv import load_dotenv

load_dotenv()

def sync_raw_data():
    container = os.getenv("AZURE_STORAGE_CONTAINER_RAW", "hdds-raw-data")
    local_target = os.path.join(PROJECT_ROOT, "data")
    
    print(f"Syncing datasets from '{container}' container to local '{local_target}'...")
    
    # We want to pull down the folders: synthea, asclepius, mock_notes
    folders_to_sync = ["synthea/", "asclepius/", "mock_notes/"]
    
    total_downloaded = 0
    for folder in folders_to_sync:
        print(f"\nChecking for folder prefix: {folder}")
        # The target directory is the folder inside 'data/'
        target_dir = os.path.join(local_target, folder.strip("/"))
        
        # Download files matching the prefix
        success = download_folder_prefix(container, folder, target_dir)
        if success:
            print(f"Successfully synced files for {folder}")
            total_downloaded += 1
        else:
            print(f"No files found or error syncing {folder}")
            
    if total_downloaded > 0:
        print("\nSync complete! The local ingestion scripts can now run.")
    else:
        print("\nWarning: No files were downloaded. Make sure the Azure container has files.")

if __name__ == "__main__":
    sync_raw_data()
