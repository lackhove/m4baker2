"""Render ffmpeg concat and chapter metadata files."""

from m4baker.model import BookMetadata, Chapter, SourceFile


def render_concat(files: tuple[SourceFile, ...]) -> str:
    """Render an ffmpeg concat manifest using absolute file paths."""
    lines = [
        f"file '{_escape_concat_path(str(source_file.path.resolve()))}'" for source_file in files
    ]
    return "\n".join(lines) + ("\n" if lines else "")


def render_ffmetadata(metadata: BookMetadata, chapters: tuple[Chapter, ...]) -> str:
    """Render an FFMETADATA1 document for book and chapter metadata."""
    lines = [";FFMETADATA1"]
    lines.append(f"title={_escape_ffmetadata_value(metadata.title)}")
    lines.append(f"artist={_escape_ffmetadata_value(metadata.artist)}")
    if metadata.album is not None:
        lines.append(f"album={_escape_ffmetadata_value(metadata.album)}")

    for chapter in chapters:
        lines.extend(
            [
                "",
                "[CHAPTER]",
                "TIMEBASE=1/1000",
                f"START={chapter.start_ms}",
                f"END={chapter.end_ms}",
                f"title={_escape_ffmetadata_value(chapter.title)}",
            ]
        )

    return "\n".join(lines) + "\n"


def _escape_concat_path(path: str) -> str:
    return path.replace("'", "'\\''")


def _escape_ffmetadata_value(value: str) -> str:
    return (
        value.replace("\\", r"\\")
        .replace(";", r"\;")
        .replace("#", r"\#")
        .replace("=", r"\=")
        .replace("\n", r"\n")
    )
