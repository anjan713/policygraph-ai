from pathlib import Path
from uuid import uuid4
import shutil
from fastapi import UploadFile
from ..core.config import settings

class StorageError(RuntimeError):
    pass

class StorageService:
    def save_upload(self, file: UploadFile) -> tuple[str, str]:
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise StorageError("Only PDF files are supported.")

        document_id = str(uuid4())
        safe_name = Path(file.filename).name.replace(" ", "_")
        object_name = f"{document_id}_{safe_name}"
        local_path = Path(settings.local_upload_dir) / object_name
        local_path.parent.mkdir(parents=True, exist_ok=True)

        with local_path.open("wb") as out:
            shutil.copyfileobj(file.file, out)

        if settings.use_gcs:
            if not settings.gcs_bucket:
                raise StorageError("USE_GCS=true but GCS_BUCKET is not configured.")
            try:
                from google.cloud import storage
            except ImportError as exc:
                raise StorageError("google-cloud-storage is not installed. Run: pip install google-cloud-storage") from exc
            key = f"{settings.gcs_prefix.rstrip('/')}/{object_name}"
            client = storage.Client(project=settings.google_cloud_project or None)
            bucket = client.bucket(settings.gcs_bucket)
            blob = bucket.blob(key)
            blob.upload_from_filename(str(local_path), content_type="application/pdf")
            return document_id, f"gs://{settings.gcs_bucket}/{key}"

        return document_id, f"local://{local_path.resolve()}"

    def resolve_local_path(self, storage_uri: str) -> Path:
        if storage_uri.startswith("local://"):
            return Path(storage_uri.removeprefix("local://"))
        if storage_uri.startswith("gs://"):
            if not settings.gcs_bucket:
                raise StorageError("GCS_BUCKET is not configured.")
            try:
                from google.cloud import storage
            except ImportError as exc:
                raise StorageError("google-cloud-storage is not installed. Run: pip install google-cloud-storage") from exc
            bucket_and_key = storage_uri.removeprefix("gs://")
            bucket_name, key = bucket_and_key.split("/", 1)
            local_name = Path(settings.local_upload_dir) / Path(key).name
            if local_name.exists():
                return local_name
            client = storage.Client(project=settings.google_cloud_project or None)
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(key)
            blob.download_to_filename(str(local_name))
            return local_name
        raise StorageError(f"Unsupported storage URI: {storage_uri}")
