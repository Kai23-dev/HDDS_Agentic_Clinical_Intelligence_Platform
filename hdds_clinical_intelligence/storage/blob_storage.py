"""
Azure Blob Storage Helper Module (Stage 1)
Handles connections to Azure Blob Storage to upload and download datasets.
"""

import os
from typing import List, Optional
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

def get_blob_service_client() -> Optional[BlobServiceClient]:
    """Returns the BlobServiceClient if configured, else None."""
    if not CONNECTION_STRING:
        print("WARNING: AZURE_STORAGE_CONNECTION_STRING is missing. Using local files.")
        return None
    try:
        return BlobServiceClient.from_connection_string(CONNECTION_STRING)
    except Exception as e:
        print(f"Error connecting to Azure Blob Storage: {e}")
        return None

def list_blobs(container_name: str) -> List[str]:
    """List all blobs in a given container."""
    client = get_blob_service_client()
    if not client:
        return []
    
    try:
        container_client = client.get_container_client(container_name)
        if not container_client.exists():
            print(f"Container '{container_name}' does not exist.")
            return []
            
        return [blob.name for blob in container_client.list_blobs()]
    except Exception as e:
        print(f"Error listing blobs in {container_name}: {e}")
        return []

def upload_file(container_name: str, local_path: str, blob_path: str) -> bool:
    """Upload a local file to a blob path."""
    client = get_blob_service_client()
    if not client:
        return False
        
    try:
        container_client = client.get_container_client(container_name)
        # Create container if it doesn't exist
        if not container_client.exists():
            container_client.create_container()
            
        blob_client = container_client.get_blob_client(blob_path)
        with open(local_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        print(f"Uploaded {local_path} to {container_name}/{blob_path}")
        return True
    except Exception as e:
        print(f"Error uploading file {local_path}: {e}")
        return False

def download_file(container_name: str, blob_path: str, local_path: str) -> bool:
    """Download a blob to a local path."""
    client = get_blob_service_client()
    if not client:
        return False
        
    try:
        container_client = client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_path)
        
        # Ensure local directory exists
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        with open(local_path, "wb") as file:
            download_stream = blob_client.download_blob()
            file.write(download_stream.readall())
        print(f"Downloaded {container_name}/{blob_path} to {local_path}")
        return True
    except Exception as e:
        print(f"Error downloading file {blob_path}: {e}")
        return False

def download_folder_prefix(container_name: str, prefix: str, local_dir: str) -> bool:
    """Download all blobs in a container that match a prefix to a local directory."""
    client = get_blob_service_client()
    if not client:
        return False
        
    try:
        container_client = client.get_container_client(container_name)
        if not container_client.exists():
            return False
            
        success_count = 0
        for blob in container_client.list_blobs(name_starts_with=prefix):
            # Calculate local path maintaining folder structure relative to prefix
            relative_path = blob.name
            if relative_path.startswith(prefix):
                relative_path = relative_path[len(prefix):].lstrip("/")
            
            # If the relative path is empty, it means the prefix IS the file.
            if not relative_path:
                relative_path = os.path.basename(blob.name)
                
            local_path = os.path.join(local_dir, relative_path)
            if download_file(container_name, blob.name, local_path):
                success_count += 1
                
        return success_count > 0
    except Exception as e:
        print(f"Error downloading folder prefix {prefix}: {e}")
        return False

if __name__ == "__main__":
    # Test script to verify blob access
    print("Verifying Azure Blob Storage Access...")
    
    # Check if connection string is loaded
    if not CONNECTION_STRING:
        print("FAILED: Connection string not found in environment.")
    else:
        print("Connection string found.")
        
    # Attempt to list containers
    client = get_blob_service_client()
    if client:
        try:
            print("\nConnected successfully. Listing all containers in this storage account:")
            containers = client.list_containers()
            found = False
            for c in containers:
                found = True
                print(f" - {c.name}")
            if not found:
                print(" (No containers found. The account exists but is empty.)")
        except Exception as e:
            print(f"FAILED to list containers: {e}")
