import pytest

from tests.fakes import FakeMediaFiles


@pytest.fixture
def fake_media_files(monkeypatch: pytest.MonkeyPatch) -> FakeMediaFiles:
    files = FakeMediaFiles()
    monkeypatch.setattr("m4baker.metadata.MediaFile", files.build)
    return files
