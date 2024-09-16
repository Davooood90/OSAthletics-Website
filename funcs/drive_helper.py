import io
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# API Scope
SCOPES = ['https://www.googleapis.com/auth/drive']

# Set up the Google Drive API client
def build_drive_service():
    creds = Credentials.from_authorized_user_file('./token.json', SCOPES)
    return build('drive', 'v3', credentials=creds)

# Upload File to Google Drive
def upload_file(service, file, filename, folder_id):
    # File Information
    file_metadata = {'name': filename}
    # Folder to Upload to
    if folder_id is not None:
        file_metadata['parents'] = [folder_id]
    media = MediaIoBaseUpload(io.BytesIO(file.read()), mimetype=file.content_type, resumable=True)
    # Create Google DriveFile
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    # Return File Id
    return file.get('id')

# Retrieve File From Google Drive
def get_file(service, id):
    # Set File Permissions
    permission = {
        'role': 'reader',
        'type': 'anyone',
        'allowFileDiscovery': False
    }
    result = service.permissions().create(fileId=id, body=permission).execute()
    file = service.files().get(fileId=id, fields='webViewLink').execute()
    # Get File Link
    return file.get('webViewLink')
