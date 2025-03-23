import os
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account

def download_drive_folder_with_service_account(
    folder_id, 
    service_account_file, 
    local_folder="docs"
):
    """
    Downloads all files from a Google Drive folder using a service account.
    
    Args:
        folder_id (str): The ID of the Google Drive folder.
        service_account_file (str): Path to the service account JSON key file.
        local_folder (str): The local folder to download files to.
    
    Returns:
        list: List of downloaded file paths.
    """
    # Create the local folder if it doesn't exist
    if not os.path.exists(local_folder):
        os.makedirs(local_folder)
    
    # Define the scopes
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    
    # Authenticate with the service account
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=SCOPES
    )
    
    # Build the Drive API client
    drive_service = build('drive', 'v3', credentials=credentials)
    
    # List all files in the folder
    query = f"'{folder_id}' in parents and trashed = false"
    results = drive_service.files().list(
        q=query,
        pageSize=1000,
        fields="nextPageToken, files(id, name, mimeType)"
    ).execute()
    
    files = results.get('files', [])
    downloaded_files = []
    
    if not files:
        print(f"No files found in the Google Drive folder with ID: {folder_id}")
        return downloaded_files
    
    print(f"Found {len(files)} files/folders in Google Drive folder.")
    
    # Process each file or folder
    for item in files:
        file_id = item['id']
        file_name = item['name']
        mime_type = item['mimeType']
        
        # If it's a folder, recursively download its contents
        if mime_type == 'application/vnd.google-apps.folder':
            subfolder_path = os.path.join(local_folder, file_name)
            print(f"Found subfolder: {file_name}, downloading contents...")
            
            # Create subfolder if it doesn't exist
            if not os.path.exists(subfolder_path):
                os.makedirs(subfolder_path)
            
            # Recursively download files from subfolder
            subfiles = download_drive_folder_with_service_account(
                file_id, service_account_file, subfolder_path
            )
            downloaded_files.extend(subfiles)
        else:
            # Download the file
            try:
                request = drive_service.files().get_media(fileId=file_id)
                file_path = os.path.join(local_folder, file_name)
                
                with io.FileIO(file_path, 'wb') as file_handler:
                    downloader = MediaIoBaseDownload(file_handler, request)
                    done = False
                    while not done:
                        status, done = downloader.next_chunk()
                        print(f"Download {file_name} {int(status.progress() * 100)}%")
                
                downloaded_files.append(file_path)
                print(f"Downloaded: {file_path}")
                
            except Exception as e:
                print(f"Error downloading {file_name}: {str(e)}")
    
    return downloaded_files

# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    # Folder ID can be found in the URL of your Google Drive folder
    # e.g., https://drive.google.com/drive/folders/1A2B3C4D5E6F7G8H9 → FOLDER_ID = "1A2B3C4D5E6F7G8H9"
    
    # Replace with your Google Drive folder ID
    FOLDER_ID = os.getenv('FOLDER_ID')
    
    # Path to your service account key file
    SERVICE_ACCOUNT_FILE = "creds/service-account.json"
    
    # Download all files to the "docs" folder
    downloaded = download_drive_folder_with_service_account(FOLDER_ID, SERVICE_ACCOUNT_FILE)
    print(f"Downloaded {len(downloaded)} files in total.")