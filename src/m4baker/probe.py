"""ffprobe integration for input duration discovery."""

import subprocess
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path

from m4baker.errors import ProbeError


class AudioProber:
    def probe_duration_ms(self, path: Path) -> int:
        """Probe a single input file duration in integer milliseconds."""
        command = [
            "ffprobe",
            "-v",
            "quiet",
            "-show_entries",
            "format=duration",
            "-of",
            "csv=p=0",
            str(path),
        ]
        try:
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as error:
            message = error.stderr.strip() or error.stdout.strip() or str(error)
            raise ProbeError(f"ffprobe failed for {path}: {message}") from error
        except OSError as error:
            raise ProbeError(f"failed to execute ffprobe for {path}: {error}") from error

        return _parse_duration_to_ms(result.stdout.strip(), path)


def _parse_duration_to_ms(raw_duration: str, path: Path) -> int:
    """Convert an ffprobe duration string to rounded integer milliseconds."""
    if not raw_duration:
        raise ProbeError(f"ffprobe returned an empty duration for {path}")

    try:
        duration_ms = int(
            (Decimal(raw_duration) * Decimal("1000")).quantize(
                Decimal("1"),
                rounding=ROUND_HALF_UP,
            )
        )
    except InvalidOperation as error:
        raise ProbeError(f"failed to parse duration for {path}: {raw_duration!r}") from error

    if duration_ms <= 0:
        raise ProbeError(f"ffprobe returned a non-positive duration for {path}: {raw_duration!r}")

    return duration_ms
