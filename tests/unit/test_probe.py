from pathlib import Path

import pytest

from m4baker.errors import ProbeError
from m4baker.probe import _parse_duration_to_ms


def test_parse_duration_to_ms_should_round_and_reject_invalid_values(tmp_path: Path) -> None:
    path = tmp_path / "input.mp3"

    assert _parse_duration_to_ms("1.2345", path) == 1235

    with pytest.raises(ProbeError, match="failed to parse"):
        _parse_duration_to_ms("not-a-number", path)
