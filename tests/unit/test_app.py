from pathlib import Path

import pytest

import m4baker.app as app_module
from m4baker.app import _validate_runtime_dependencies, build_audiobook
from m4baker.errors import DependencyError
from m4baker.model import BookMetadata, BuildRequest, Chapter, SourceFile
from tests.fakes import FakeAudiobookEncoder, FakeAudioProber, FakeMetadataReader


def test_build_audiobook_should_use_injected_facades_to_create_output_and_chapters(
    tmp_path: Path,
) -> None:
    input_file = tmp_path / "chapter01.mp3"
    input_file.write_bytes(b"audio")
    request = BuildRequest(input_files=(input_file,), output_file=tmp_path / "book.m4b")
    metadata_reader = FakeMetadataReader(
        metadata=BookMetadata(title="Book", artist="Artist", album=None, cover=None),
        titles={input_file: "Chapter 1"},
    )
    audio_prober = FakeAudioProber({input_file: 1000})
    encoder = FakeAudiobookEncoder()

    result = build_audiobook(
        request,
        metadata_reader=metadata_reader,
        audio_prober=audio_prober,
        audiobook_encoder=encoder,
    )

    assert result == request.output_file
    assert request.output_file.read_bytes() == b"fake-m4b"
    assert metadata_reader.book_metadata_requests == [request]
    assert metadata_reader.title_requests == [input_file]
    assert audio_prober.requests == [input_file]
    assert len(encoder.calls) == 1
    plan, _, verbose, _ = encoder.calls[0]
    assert plan.files == (SourceFile(path=input_file, title="Chapter 1", duration_ms=1000),)
    assert plan.chapters == (
        Chapter(
            index=1,
            title="Chapter 1",
            start_ms=0,
            end_ms=1000,
            source_path=input_file,
        ),
    )
    assert verbose is False


def test_validate_runtime_dependencies_should_error_when_ffprobe_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    request = BuildRequest(
        input_files=(tmp_path / "chapter01.mp3",), output_file=tmp_path / "book.m4b"
    )
    monkeypatch.setattr(
        app_module,
        "which",
        lambda command: "/usr/bin/ffmpeg" if command == "ffmpeg" else None,
    )

    with pytest.raises(DependencyError, match="ffprobe"):
        _validate_runtime_dependencies(request)


def test_build_audiobook_should_preserve_directory_expansion_order(tmp_path: Path) -> None:
    input_files = (
        tmp_path / "disc1" / "Chapter 1.mp3",
        tmp_path / "disc1" / "Chapter 2.mp3",
        tmp_path / "disc2" / "Chapter 10.mp3",
    )
    for input_file in input_files:
        input_file.parent.mkdir(parents=True, exist_ok=True)
        input_file.write_bytes(b"audio")

    request = BuildRequest(input_files=input_files, output_file=tmp_path / "book.m4b")
    metadata_reader = FakeMetadataReader(
        metadata=BookMetadata(title="Book", artist="Artist", album=None, cover=None),
        titles={path: path.stem for path in input_files},
    )
    audio_prober = FakeAudioProber({path: 1000 for path in input_files})
    encoder = FakeAudiobookEncoder()

    build_audiobook(
        request,
        metadata_reader=metadata_reader,
        audio_prober=audio_prober,
        audiobook_encoder=encoder,
    )

    plan, _, _, _ = encoder.calls[0]
    assert tuple(source.path for source in plan.files) == input_files
