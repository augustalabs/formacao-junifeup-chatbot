# FORMACAO-JUNIFEUP-CHATBOT

A chatbot implementation for JUNIFEUP training.

## Setup Instructions

### Prerequisites
- Python 3.13

### Installation

1. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   ```

2. Activate the virtual environment:
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python3 -m main
   ```

## Google Drive Integration

The application requires access to Google Drive. Follow these steps to set up the required credentials:

### Setting up Google Cloud Account

1. Create a Google Cloud Account (free for this scope)
2. Create a new project in the Google Cloud Console
3. Navigate to IAM & Admin > Service Accounts
4. Create a new service account (no specific role is required)
5. Create a key for this service account (JSON format)
6. Save the downloaded key file to the `creds` folder in your project

> **Important**: Be cautious about committing credential files to git repositories. The current credentials have limited permissions, but it's generally best practice to exclude them from source control.

### Activating Google Drive API

1. In the Google Cloud Console, navigate to APIs & Services
2. Enable the Google Drive API for your project

### Sharing Your Drive Folder

Share your Google Drive folder with the service account email:
- Service account email: `drive-folder-access@formacao-junifeup.iam.gserviceaccount.com`
- Ensure the service account has appropriate access permissions to the folder



### Converting videos
   - Make sure you install ffmpeg with 
   ```bash
   brew install ffmpeg
   ```