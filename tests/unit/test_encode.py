from pathlib import Path

from m4baker.encode import _build_ffmpeg_command
from m4baker.model import BookMetadata, BuildPlan, Chapter, SourceFile, TempPaths


def test_build_ffmpeg_command_should_include_cover_and_threads_when_cover_exists(
    tmp_path: Path,
) -> None:
    source_file = SourceFile(path=tmp_path / "input.mp3", title="Input", duration_ms=1000)
    cover_file = tmp_path / "cover.jpg"
    cover_file.write_bytes(b"cover")
    plan = BuildPlan(
        files=(source_file,),
        chapters=(
            Chapter(
                index=1,
                title="Input",
                start_ms=0,
                end_ms=1000,
                source_path=source_file.path,
            ),
        ),
        metadata=BookMetadata(title="Book", artist="Artist", album=None, cover=cover_file),
        output_file=tmp_path / "output.m4b",
        bitrate=64,
        threads=4,
    )
    temp_paths = TempPaths(
        concat_file=tmp_path / "filelist.txt",
        metadata_file=tmp_path / "chapters.txt",
        cover_file=cover_file,
    )

    assert _build_ffmpeg_command(plan, temp_paths) == [
        "ffmpeg",
        "-n",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(temp_paths.concat_file),
        "-i",
        str(temp_paths.metadata_file),
        "-i",
        str(temp_paths.cover_file),
        "-map",
        "0:a",
        "-map_metadata",
        "1",
        "-c:a",
        "aac",
        "-b:a",
        "64k",
        "-threads",
        "4",
        "-map",
        "2:v",
        "-c:v",
        "copy",
        "-disposition:v:0",
        "attached_pic",
        str(plan.output_file),
    ]
