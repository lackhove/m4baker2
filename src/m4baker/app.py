"""Application orchestration and validation."""

from collections.abc import Callable
from pathlib import Path
from shutil import which
from tempfile import TemporaryDirectory

from m4baker.chapters import build_chapters
from m4baker.encode import AudiobookEncoder
from m4baker.errors import DependencyError
from m4baker.metadata import MetadataReader, materialize_cover
from m4baker.model import BuildPlan, BuildRequest, SourceFile, TempPaths
from m4baker.probe import AudioProber
from m4baker.render import render_concat, render_ffmetadata

_DEFAULT_METADATA_READER = MetadataReader()
_DEFAULT_AUDIO_PROBER = AudioProber()
_DEFAULT_AUDIOBOOK_ENCODER = AudiobookEncoder()


def _validate_runtime_dependencies(request: BuildRequest) -> None:
    """Validate external runtime dependencies required for a build."""
    del request
    _require_dependency("ffmpeg")
    _require_dependency("ffprobe")


def _require_dependency(command: str) -> None:
    if which(command) is None:
        raise DependencyError(f"required dependency is not available on PATH: {command}")


def build_audiobook(
    request: BuildRequest,
    progress_handler: Callable[[float], None] | None = None,
    metadata_reader: MetadataReader = _DEFAULT_METADATA_READER,
    audio_prober: AudioProber = _DEFAULT_AUDIO_PROBER,
    audiobook_encoder: AudiobookEncoder = _DEFAULT_AUDIOBOOK_ENCODER,
) -> Path:
    """Validate the request and build the logical audiobook plan."""
    _validate_runtime_dependencies(request)
    metadata = metadata_reader.read_book_metadata(request)
    source_files = _build_source_files(
        request.input_files,
        metadata_reader=metadata_reader,
        audio_prober=audio_prober,
    )
    chapters = build_chapters(source_files)

    with TemporaryDirectory(prefix="m4baker-", delete=not request.keep_temp) as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        plan = BuildPlan(
            files=source_files,
            chapters=chapters,
            metadata=metadata,
            output_file=request.output_file,
            bitrate=request.bitrate,
            threads=request.threads,
        )
        temp_paths = _write_temp_files(plan, temp_dir)
        audiobook_encoder.encode(
            plan,
            temp_paths,
            verbose=request.verbose,
            progress_handler=progress_handler,
        )
    return request.output_file


def _build_source_files(
    paths: tuple[Path, ...],
    *,
    metadata_reader: MetadataReader,
    audio_prober: AudioProber,
) -> tuple[SourceFile, ...]:
    return tuple(
        SourceFile(
            path=path,
            title=metadata_reader.read_source_title(path) or path.stem,
            duration_ms=audio_prober.probe_duration_ms(path),
        )
        for path in paths
    )


def _write_temp_files(plan: BuildPlan, temp_dir: Path) -> TempPaths:
    """Write concat and ffmetadata temp files for a build plan."""
    concat_file = temp_dir / "filelist.txt"
    metadata_file = temp_dir / "chapters.txt"
    cover_file = materialize_cover(plan.metadata.cover, temp_dir)
    concat_file.write_text(render_concat(plan.files), encoding="utf-8")
    metadata_file.write_text(render_ffmetadata(plan.metadata, plan.chapters), encoding="utf-8")
    return TempPaths(
        concat_file=concat_file,
        metadata_file=metadata_file,
        cover_file=cover_file,
    )
