from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_FILE = "service_account.json"
PARENT_FOLDER_ID = "1F2oxw2W4o1MAL0iQdVkzCc2Zjw4z5XoM"  # Folder ID only

# google drive authentication
def authenticate():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return creds


def upload_photo(file_path):
    creds = authenticate()
    service = build("drive", "v3", credentials=creds)

    file_metadata = {
        "name": "hello.txt ",  # Keep original file name or change it dynamically
        "parents": [PARENT_FOLDER_ID]
    }

    media = MediaFileUpload(file_path, mimetype="text/plain")  # Adjust MIME type as needed

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    print(f"File uploaded successfully. File ID: {file.get('id')}")


upload_photo("text.txt")



