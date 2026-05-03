from pathlib import Path

from m4baker.chapters import build_chapters
from m4baker.model import Chapter, SourceFile


def test_build_chapters_should_accumulate_offsets_in_input_order() -> None:
    files = (
        SourceFile(path=Path("one.mp3"), title="One", duration_ms=1000),
        SourceFile(path=Path("two.mp3"), title="Two", duration_ms=2500),
    )

    assert build_chapters(files) == (
        Chapter(index=1, title="One", start_ms=0, end_ms=1000, source_path=Path("one.mp3")),
        Chapter(index=2, title="Two", start_ms=1000, end_ms=3500, source_path=Path("two.mp3")),
    )
