import pytest

from app.services.storage_service import StorageService, StorageError


class _FakeUpload:
    """Minimal stand-in for fastapi.UploadFile for the rejection path."""

    def __init__(self, filename: str):
        self.filename = filename


def test_save_upload_rejects_non_pdf():
    with pytest.raises(StorageError):
        StorageService().save_upload(_FakeUpload("notes.txt"))


def test_resolve_local_path_parses_local_uri(tmp_path):
    target = tmp_path / "doc.pdf"
    resolved = StorageService().resolve_local_path(f"local://{target}")
    assert str(resolved) == str(target)


def test_resolve_local_path_rejects_unknown_scheme():
    with pytest.raises(StorageError):
        StorageService().resolve_local_path("ftp://somewhere/doc.pdf")
