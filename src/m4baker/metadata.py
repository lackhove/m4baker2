"""Metadata reading and resolution helpers."""

from pathlib import Path
from typing import Any, cast

from mediafile import MediaFile
from mediafile.utils.image import Image

from m4baker.errors import MetadataError
from m4baker.model import BookMetadata, BuildRequest, EmbeddedCover


class MetadataReader:
    def read_book_metadata(self, request: BuildRequest) -> BookMetadata:
        """Read and resolve final book metadata from the first input file and CLI overrides."""
        path = request.input_files[0]
        media_file_any = self._read_media_file(path)
        title = _normalize_text(cast(str | None, media_file_any.title))
        artist = _normalize_text(cast(str | None, media_file_any.artist))
        album = _normalize_text(cast(str | None, media_file_any.album))
        images = tuple(media_file_any.images or ())
        cover = _select_embedded_cover(images)
        return BookMetadata(
            title=request.title_override or title or path.stem,
            artist=request.artist_override or artist or "Unknown Artist",
            album=request.album_override or album,
            cover=request.cover_override or cover,
        )

    def read_source_title(self, path: Path) -> str | None:
        """Read a single source file title tag."""
        media_file_any = self._read_media_file(path)
        return _normalize_text(cast(str | None, media_file_any.title))

    def _read_media_file(self, path: Path) -> Any:
        try:
            media_file = MediaFile(path)
        except Exception as error:  # pragma: no cover - mediafile defines broad failures
            raise MetadataError(f"failed to read metadata from {path}: {error}") from error

        return cast(Any, media_file)


def materialize_cover(cover: Path | EmbeddedCover | None, temp_dir: Path) -> Path | None:
    """Materialize a resolved cover into a filesystem path for ffmpeg."""
    if cover is None:
        return None
    if isinstance(cover, Path):
        return cover
    suffix = _suffix_for_mime_type(cover.mime_type)
    cover_path = temp_dir / f"embedded-cover{suffix}"
    cover_path.write_bytes(cover.data)
    return cover_path


def _select_embedded_cover(images: tuple[Image, ...]) -> EmbeddedCover | None:
    if not images:
        return None

    preferred = next((image for image in images if getattr(image, "type_index", None) == 3), None)
    selected = preferred or images[0]
    return EmbeddedCover(data=selected.data, mime_type=selected.mime_type)


def _normalize_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _suffix_for_mime_type(mime_type: str | None) -> str:
    if mime_type == "image/png":
        return ".png"
    if mime_type in {"image/jpg", "image/jpeg"}:
        return ".jpg"
    return ".img"
