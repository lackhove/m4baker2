"""ffmpeg command construction and execution."""

from collections.abc import Callable

from ffmpeg_progress_yield import FfmpegProgress

from m4baker.errors import EncodeError
from m4baker.model import BuildPlan, TempPaths


def _build_ffmpeg_command(plan: BuildPlan, temp_paths: TempPaths) -> list[str]:
    """Build the ffmpeg command for the resolved plan."""
    command = [
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
    ]
    if temp_paths.cover_file is not None:
        command.extend(["-i", str(temp_paths.cover_file)])

    command.extend(
        [
            "-map",
            "0:a",
            "-map_metadata",
            "1",
            "-c:a",
            "aac",
            "-b:a",
            f"{plan.bitrate}k",
        ]
    )

    if plan.threads is not None:
        command.extend(["-threads", str(plan.threads)])

    if temp_paths.cover_file is not None:
        command.extend(
            [
                "-map",
                "2:v",
                "-c:v",
                "copy",
                "-disposition:v:0",
                "attached_pic",
            ]
        )

    command.append(str(plan.output_file))
    return command


class AudiobookEncoder:
    def encode(
        self,
        plan: BuildPlan,
        temp_paths: TempPaths,
        *,
        verbose: bool,
        progress_handler: Callable[[float], None] | None = None,
    ) -> None:
        """Run ffmpeg and stream progress to the console."""
        command = _build_ffmpeg_command(plan, temp_paths)
        progress_runner = FfmpegProgress(command)

        try:
            for progress in progress_runner.run_command_with_progress():
                if progress_handler is not None:
                    progress_handler(progress)
        except RuntimeError as error:
            detail = progress_runner.stderr or str(error)
            raise EncodeError(f"ffmpeg encode failed: {detail}") from error

        if verbose and progress_runner.stderr:
            print(progress_runner.stderr)
