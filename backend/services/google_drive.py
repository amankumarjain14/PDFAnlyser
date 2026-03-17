import os
from typing import Optional, Tuple

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False


def upload_to_drive(
    file_path: str,
    file_name: str,
    credentials_path: Optional[str] = None,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Upload a file to Google Drive root folder.
    Returns (web_view_link, web_content_link) or (None, None) if skipped.
    """
    if not GOOGLE_AVAILABLE:
        return None, None
    if not credentials_path or not os.path.exists(credentials_path):
        return None, None

    try:
        SCOPES = ["https://www.googleapis.com/auth/drive.file"]
        creds = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=SCOPES
        )
        service = build("drive", "v3", credentials=creds)

        # Make the file publicly readable
        file_metadata = {
            "name": file_name,
            "parents": ["root"],
        }
        media = MediaFileUpload(
            file_path,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            resumable=True,
        )
        file = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id,webViewLink,webContentLink")
            .execute()
        )

        # Set public permission
        service.permissions().create(
            fileId=file["id"],
            body={"type": "anyone", "role": "reader"},
        ).execute()

        return file.get("webViewLink"), file.get("webContentLink")
    except Exception as e:
        print(f"[Google Drive] Upload failed: {e}")
        return None, None
