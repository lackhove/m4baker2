"""Stable data structures for the m4baker workflow."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class BuildRequest:
    input_files: tuple[Path, ...]
    output_file: Path
    title_override: str | None = None
    artist_override: str | None = None
    album_override: str | None = None
    cover_override: Path | None = None
    bitrate: int = 64
    threads: int | None = None
    keep_temp: bool = False
    verbose: bool = False


@dataclass(frozen=True, slots=True)
class EmbeddedCover:
    data: bytes
    mime_type: str | None


@dataclass(frozen=True, slots=True)
class BookMetadata:
    title: str
    artist: str
    album: str | None
    cover: Path | EmbeddedCover | None


@dataclass(frozen=True, slots=True)
class SourceFile:
    path: Path
    title: str
    duration_ms: int


@dataclass(frozen=True, slots=True)
class Chapter:
    index: int
    title: str
    start_ms: int
    end_ms: int
    source_path: Path


@dataclass(frozen=True, slots=True)
class BuildPlan:
    files: tuple[SourceFile, ...]
    chapters: tuple[Chapter, ...]
    metadata: BookMetadata
    output_file: Path
    bitrate: int
    threads: int | None


@dataclass(frozen=True, slots=True)
class TempPaths:
    concat_file: Path
    metadata_file: Path
    cover_file: Path | None
