# AGENTS

This repository builds the `m4baker` CLI described in `PLAN.md`.

## Workflow

- Follow the milestone order in `PLAN.md` unless a change clearly spans multiple milestones.
- Run quality gates before finishing a step: `uv run ruff format --check .`, `uv run ruff check .`, `uv run mypy`, and `uv run pytest`.
- Create a git commit after each completed step.

## Engineering Rules

- Keep the app CLI-only and preserve input ordering exactly as provided.
- The CLI shape is `m4baker INPUT [INPUT ...] OUTPUT.m4b`; validate user-facing path/value rules in Cyclopts where possible.
- Do not overwrite existing output files; reject them before encode starts.
- Keep progress presentation in the CLI layer and execution logic in lower-level modules.
- Use frozen dataclasses, pure helpers, and explicit exceptions.
- Make module-internal helpers private with a leading underscore.
- Prefer FFmpeg and ffprobe subprocess integration over extra abstractions.
- The `monkeypatch` fixture is allowed in tests. Avoid the broader practice of patching parts of the system under test just to make them testable.
