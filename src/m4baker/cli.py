"""Command line interface for m4baker."""

import re
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Annotated

import cyclopts
from cyclopts import Parameter
from cyclopts.types import ExistingImagePath, PositiveInt
from cyclopts.validators import Path as PathValidator
from tqdm import tqdm

from m4baker.app import build_audiobook
from m4baker.errors import M4BakerError
from m4baker.model import BuildRequest

_SUPPORTED_AUDIO_SUFFIXES = frozenset(
    {
        ".aac",
        ".aif",
        ".aiff",
        ".flac",
        ".m4a",
        ".m4b",
        ".mp3",
        ".mp4",
        ".oga",
        ".ogg",
        ".opus",
        ".wav",
        ".wma",
    }
)
_NATURAL_SORT_PATTERN = re.compile(r"(\d+)")


def _natural_sort_key(path: Path) -> tuple[object, ...]:
    parts = _NATURAL_SORT_PATTERN.split(path.name)
    return tuple(int(part) if part.isdigit() else part.casefold() for part in parts)


def _is_supported_audio_file(path: Path) -> bool:
    return path.is_file() and path.suffix.casefold() in _SUPPORTED_AUDIO_SUFFIXES


def _audio_files_in_directory(directory: Path) -> tuple[Path, ...]:
    return tuple(
        sorted(
            (path for path in directory.iterdir() if _is_supported_audio_file(path)),
            key=_natural_sort_key,
        )
    )


def _expand_inputs(inputs: Iterable[Path]) -> tuple[Path, ...]:
    expanded_inputs: list[Path] = []
    for input_path in inputs:
        if input_path.is_dir():
            expanded_inputs.extend(_audio_files_in_directory(input_path))
        else:
            expanded_inputs.append(input_path)
    return tuple(expanded_inputs)


def _format_resolved_inputs(input_files: Iterable[Path]) -> str:
    lines = ["Input files:"]
    for index, input_file in enumerate(input_files, start=1):
        lines.append(f"  {index:02d}. {input_file}")
    return "\n".join(lines)


def _validate_inputs_parameter(type_: object, inputs: list[Path]) -> None:
    del type_

    if not inputs:
        raise ValueError("provide at least one input file or directory")

    for input_path in inputs:
        if not input_path.exists():
            raise ValueError(f"input path does not exist: {input_path}")
        if input_path.is_dir() and not _audio_files_in_directory(input_path):
            raise ValueError(
                f"input directory does not contain any supported audio files: {input_path}"
            )
        if input_path.is_file() and not _is_supported_audio_file(input_path):
            raise ValueError(f"input file is not a supported audio file: {input_path}")
        if not input_path.is_file() and not input_path.is_dir():
            raise ValueError(f"input path is neither a file nor a directory: {input_path}")


def _validate_output_parameter(type_: object, output: Path) -> None:
    PathValidator(file_okay=True, dir_okay=False, ext=("m4b",))(type_, output)
    if output.exists():
        raise ValueError(f"output file already exists: {output}")


app = cyclopts.App(
    name="m4baker",
    help="Build a chapterized .m4b from input audio files and directories.",
)


@app.default
def build(
    inputs: Annotated[
        list[Path],
        Parameter(
            help=(
                "Ordered input files or directories. Directories expand to supported "
                "audio files in natural sort order."
            ),
            validator=_validate_inputs_parameter,
        ),
    ],
    output: Annotated[
        Path,
        Parameter(
            help="Output .m4b file path.",
            validator=_validate_output_parameter,
        ),
    ],
    /,
    title: Annotated[str | None, Parameter(help="Override the output title.")] = None,
    artist: Annotated[str | None, Parameter(help="Override the output artist.")] = None,
    album: Annotated[str | None, Parameter(help="Override the output album.")] = None,
    cover: Annotated[
        ExistingImagePath | None,
        Parameter(help="Override the cover image with a JPG or PNG file."),
    ] = None,
    bitrate: Annotated[
        PositiveInt,
        Parameter(help="AAC audio bitrate in kbps."),
    ] = 64,
    threads: Annotated[
        PositiveInt | None,
        Parameter(help="Number of ffmpeg worker threads. Omit to use ffmpeg defaults."),
    ] = None,
    keep_temp: Annotated[
        bool,
        Parameter(help="Keep generated temp files instead of deleting the workspace."),
    ] = False,
    verbose: Annotated[bool, Parameter(help="Print ffmpeg diagnostics after encoding.")] = False,
) -> None:
    """Build a single `.m4b` audiobook from ordered input files and directories."""
    request = BuildRequest(
        input_files=_expand_inputs(inputs),
        output_file=output,
        title_override=title,
        artist_override=artist,
        album_override=album,
        cover_override=cover,
        bitrate=bitrate,
        threads=threads,
        keep_temp=keep_temp,
        verbose=verbose,
    )
    print(_format_resolved_inputs(request.input_files))
    progress_value = 0.0

    with tqdm(total=100.0, unit="%", desc="Encoding") as progress_bar:

        def report_progress(progress: float) -> None:
            nonlocal progress_value
            bounded_progress = min(max(progress, progress_value), 100.0)
            progress_bar.update(bounded_progress - progress_value)
            progress_value = bounded_progress

        build_audiobook(request, progress_handler=report_progress)


def main() -> None:
    try:
        app()
    except M4BakerError as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1) from error
