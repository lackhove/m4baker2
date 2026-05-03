from pathlib import Path

from m4baker.model import BookMetadata, Chapter, SourceFile
from m4baker.render import render_concat, render_ffmetadata


def test_render_helpers_should_escape_paths_and_metadata_values(tmp_path: Path) -> None:
    file_path = tmp_path / "chapter's intro.mp3"
    file_path.write_bytes(b"a")

    rendered_concat = render_concat((SourceFile(path=file_path, title="Intro", duration_ms=1000),))
    rendered_metadata = render_ffmetadata(
        BookMetadata(title=r"Book=One;#\Test", artist="A\nB", album="Album", cover=None),
        (
            Chapter(
                index=1,
                title="Intro=One",
                start_ms=0,
                end_ms=1000,
                source_path=Path("intro.mp3"),
            ),
        ),
    )

    assert rendered_concat == f"file '{str(file_path.resolve()).replace("'", "'\\''")}'\n"
    assert rendered_metadata == (
        ";FFMETADATA1\n"
        "title=Book\\=One\\;\\#\\\\Test\n"
        "artist=A\\nB\n"
        "album=Album\n"
        "\n"
        "[CHAPTER]\n"
        "TIMEBASE=1/1000\n"
        "START=0\n"
        "END=1000\n"
        "title=Intro\\=One\n"
    )
