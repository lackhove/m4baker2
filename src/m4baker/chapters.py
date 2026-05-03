"""Chapter planning helpers."""

from m4baker.model import Chapter, SourceFile


def build_chapters(files: tuple[SourceFile, ...]) -> tuple[Chapter, ...]:
    """Build chapter offsets from ordered source files."""
    start_ms = 0
    chapters: list[Chapter] = []

    for index, source_file in enumerate(files, start=1):
        end_ms = start_ms + source_file.duration_ms
        chapters.append(
            Chapter(
                index=index,
                title=source_file.title,
                start_ms=start_ms,
                end_ms=end_ms,
                source_path=source_file.path,
            )
        )
        start_ms = end_ms

    return tuple(chapters)
