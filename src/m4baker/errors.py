"""Explicit application errors for m4baker."""


class M4BakerError(Exception):
    """Base exception for predictable application failures."""


class ValidationError(M4BakerError):
    """Raised when a build request is invalid."""


class DependencyError(M4BakerError):
    """Raised when a required external dependency is unavailable."""


class MetadataError(M4BakerError):
    """Raised when metadata cannot be read or resolved."""


class ProbeError(M4BakerError):
    """Raised when ffprobe probing fails."""


class EncodeError(M4BakerError):
    """Raised when ffmpeg encoding fails."""
