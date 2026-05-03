# m4baker

CLI tool for building a single chapterized `.m4b` from an explicit ordered list of input audio files.

## Usage

```bash
uv run m4baker \
  "01 Intro.mp3" \
  "02 Chapter One.mp3" \
  "03 Chapter Two.mp3" \
  book.m4b \
  --title "My Book" \
  --artist "Author Name" \
  --threads 4
```

## Container Usage

Build the image with Podman:

```bash
podman build -t m4baker .
```

Run the container against files from the current directory:

```bash
podman run --rm -v "$PWD":/work:z m4baker \
  "01 Intro.mp3" \
  "02 Chapter One.mp3" \
  book.m4b
```

## Notes

- Input file ordering is preserved exactly as provided on the command line.
- The last positional argument is the output `.m4b` path.
- Metadata is read from the first input file and can be overridden with CLI flags.
- FFmpeg and ffprobe must be available on `PATH`.
- Existing output files are never overwritten.
- `--threads` lets you set ffmpeg worker threads; if omitted, ffmpeg uses its default threading behavior.
- Use `--keep-temp` to preserve the generated concat and metadata files for inspection.
