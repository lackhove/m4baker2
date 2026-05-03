from pathlib import Path
from types import SimpleNamespace

import pytest

from m4baker.errors import MetadataError
from m4baker.metadata import MetadataReader, materialize_cover
from m4baker.model import BookMetadata, BuildRequest, EmbeddedCover


def test_metadata_reader_should_apply_overrides_and_fallbacks(
    tmp_path: Path, fake_media_files
) -> None:
    input_file = tmp_path / "chapter01.mp3"
    input_file.write_bytes(b"audio")
    fake_media_files.set(
        input_file,
        title="File Title",
        artist=None,
        album="File Album",
        images=(SimpleNamespace(data=b"front", mime_type="image/png", type_index=3),),
    )

    result = MetadataReader().read_book_metadata(
        BuildRequest(
            input_files=(input_file,),
            output_file=tmp_path / "book.m4b",
            title_override="CLI Title",
        )
    )

    assert result == BookMetadata(
        title="CLI Title",
        artist="Unknown Artist",
        album="File Album",
        cover=EmbeddedCover(data=b"front", mime_type="image/png"),
    )


def test_metadata_reader_should_error_when_mediafile_read_fails(
    tmp_path: Path, fake_media_files
) -> None:
    input_file = tmp_path / "chapter01.flac"
    input_file.write_bytes(b"audio")
    fake_media_files.set_error(input_file, RuntimeError("bad tags"))

    with pytest.raises(MetadataError, match="failed to read metadata"):
        MetadataReader().read_book_metadata(
            BuildRequest(input_files=(input_file,), output_file=tmp_path / "book.m4b")
        )


def test_materialize_cover_should_write_embedded_cover_with_expected_suffix(tmp_path: Path) -> None:
    result = materialize_cover(EmbeddedCover(data=b"cover-bytes", mime_type="image/png"), tmp_path)

    assert result is not None
    assert result == tmp_path / "embedded-cover.png"
    assert result.read_bytes() == b"cover-bytes"
