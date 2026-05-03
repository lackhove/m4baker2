from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace

import m4baker.metadata as metadata_module
from m4baker.encode import AudiobookEncoder
from m4baker.metadata import MetadataReader
from m4baker.model import BookMetadata, BuildPlan, BuildRequest, TempPaths
from m4baker.probe import AudioProber


class FakeMetadataReader(MetadataReader):
    def __init__(self, *, metadata: BookMetadata, titles: dict[Path, str | None]) -> None:
        self.metadata = metadata
        self.titles = titles
        self.book_metadata_requests: list[BuildRequest] = []
        self.title_requests: list[Path] = []

    def read_book_metadata(self, request: BuildRequest) -> BookMetadata:
        self.book_metadata_requests.append(request)
        return self.metadata

    def read_source_title(self, path: Path) -> str | None:
        self.title_requests.append(path)
        return self.titles[path]


class FakeAudioProber(AudioProber):
    def __init__(self, durations: dict[Path, int]) -> None:
        self.durations = durations
        self.requests: list[Path] = []

    def probe_duration_ms(self, path: Path) -> int:
        self.requests.append(path)
        return self.durations[path]


class FakeAudiobookEncoder(AudiobookEncoder):
    def __init__(self, *, progress_steps: tuple[float, ...] = (25.0, 100.0)) -> None:
        self.progress_steps = progress_steps
        self.calls: list[tuple[BuildPlan, TempPaths, bool, Callable[[float], None] | None]] = []

    def encode(
        self,
        plan: BuildPlan,
        temp_paths: TempPaths,
        *,
        verbose: bool,
        progress_handler: Callable[[float], None] | None = None,
    ) -> None:
        self.calls.append((plan, temp_paths, verbose, progress_handler))
        if progress_handler is not None:
            for progress in self.progress_steps:
                progress_handler(progress)
        plan.output_file.write_bytes(b"fake-m4b")


class FakeMediaFiles:
    def __init__(self) -> None:
        self._entries: dict[Path, object] = {}

    def install(self) -> None:
        metadata_module.MediaFile = self.build

    def set(
        self,
        path: Path,
        *,
        title: str | None = None,
        artist: str | None = None,
        album: str | None = None,
        images: tuple[object, ...] = (),
    ) -> None:
        self._entries[path] = SimpleNamespace(
            title=title,
            artist=artist,
            album=album,
            images=images,
        )

    def set_error(self, path: Path, error: Exception) -> None:
        self._entries[path] = error

    def build(self, path: Path) -> object:
        entry = self._entries[path]
        if isinstance(entry, Exception):
            raise entry
        return entry
