"""
Saving reports: Azure Table Storage (text) + Azure Blob Storage (photos).
"""
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

CONN = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "").strip()
TABLE_NAME = "reports"
CONTAINER_NAME = "report-photos"
LOCAL_DIR = Path("local_data")


def using_azure() -> bool:
    return bool(CONN)


def save_report(text: str, location: str, photo_bytes: bytes | None = None,
                photo_ext: str = "") -> str:
    """Store one report and return its id."""
    report_id = uuid.uuid4().hex
    created_at = datetime.now(timezone.utc).isoformat()
    photo_blob = ""

    if using_azure():
        from azure.data.tables import TableServiceClient
        from azure.storage.blob import BlobServiceClient

        if photo_bytes:
            blob_service = BlobServiceClient.from_connection_string(CONN)
            container = blob_service.get_container_client(CONTAINER_NAME)
            if not container.exists():
                container.create_container()  # private by default
            photo_blob = f"{report_id}{photo_ext}"
            container.upload_blob(photo_blob, photo_bytes)

        table_service = TableServiceClient.from_connection_string(CONN)
        table = table_service.create_table_if_not_exists(TABLE_NAME)
        table.create_entity({
            "PartitionKey": "report",
            "RowKey": report_id,
            "text": text,
            "location": location,
            "photo_blob": photo_blob,
            "status": "open",
            "created_at": created_at,
        })
    else:
        LOCAL_DIR.mkdir(exist_ok=True)
        if photo_bytes:
            photo_blob = f"{report_id}{photo_ext}"
            (LOCAL_DIR / photo_blob).write_bytes(photo_bytes)
        record = {"id": report_id, "text": text, "location": location,
                  "photo_blob": photo_blob, "status": "open",
                  "created_at": created_at}
        (LOCAL_DIR / f"{report_id}.json").write_text(json.dumps(record, indent=2))

    return report_id
