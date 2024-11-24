from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def get_credentials():
    creds = None
    # Check if we have valid saved credentials
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials available, let user login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for future runs
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def sync_notebooks():
    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)
    
    folder_id = os.getenv('FOLDER_ID')
    
    # Query for Jupyter notebooks in the specified folder
    results = service.files().list(
        q=f"'{folder_id}' in parents and mimeType='application/x-ipynb+json'",
        fields="files(id, name, modifiedTime)"
    ).execute()
    
    items = results.get('files', [])
    
    for item in items:
        # Download each notebook
        request = service.files().get_media(fileId=item['id'])
        file_content = request.execute()
        
        # Save to local repository
        with open(item['name'], 'wb') as f:
            f.write(file_content)

if __name__ == '__main__':
    sync_notebooks()
