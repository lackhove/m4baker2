from pathlib import Path

import pytest

from m4baker.cli import (
    _expand_inputs,
    _format_resolved_inputs,
    _validate_inputs_parameter,
    _validate_output_parameter,
)


def test_cli_validators_should_reject_missing_input_and_existing_output(tmp_path: Path) -> None:
    output_file = tmp_path / "book.m4b"
    output_file.write_bytes(b"existing")

    with pytest.raises(ValueError, match="provide at least one input file or directory"):
        _validate_inputs_parameter(object(), [])

    with pytest.raises(ValueError, match="already exists"):
        _validate_output_parameter(object(), output_file)


def test_cli_validator_should_reject_missing_audio_files_in_directory(tmp_path: Path) -> None:
    empty_input_dir = tmp_path / "disc1"
    empty_input_dir.mkdir()

    with pytest.raises(ValueError, match="does not contain any supported audio files"):
        _validate_inputs_parameter(object(), [empty_input_dir])


def test_expand_inputs_should_preserve_mixed_inputs_and_collect_directory_audio_naturally(
    tmp_path: Path,
) -> None:
    disc1 = tmp_path / "disc1"
    disc2 = tmp_path / "disc2"
    disc1.mkdir()
    disc2.mkdir()

    standalone = tmp_path / "prologue.mp3"
    chapter_10 = disc1 / "Chapter 10.mp3"
    chapter_2 = disc1 / "Chapter 2.mp3"
    intro = disc1 / "Chapter 1.mp3"
    notes = disc1 / "notes.txt"
    second_disc_intro = disc2 / "Chapter 3.flac"
    second_disc_outro = disc2 / "Chapter 11.m4a"

    for path in (
        standalone,
        chapter_10,
        chapter_2,
        intro,
        notes,
        second_disc_intro,
        second_disc_outro,
    ):
        path.write_bytes(b"data")

    assert _expand_inputs((standalone, disc1, second_disc_outro, disc2)) == (
        standalone,
        intro,
        chapter_2,
        chapter_10,
        second_disc_outro,
        second_disc_intro,
        second_disc_outro,
    )


def test_cli_validator_should_reject_unsupported_input_files(tmp_path: Path) -> None:
    text_file = tmp_path / "notes.txt"
    text_file.write_text("notes", encoding="utf-8")

    with pytest.raises(ValueError, match="not a supported audio file"):
        _validate_inputs_parameter(object(), [text_file])


def test_format_resolved_inputs_should_print_ordered_file_list(tmp_path: Path) -> None:
    input_files = (tmp_path / "one.mp3", tmp_path / "two.mp3")

    assert _format_resolved_inputs(input_files) == (
        f"Input files:\n  01. {input_files[0]}\n  02. {input_files[1]}"
    )
