"""Custom exceptions for sample commands."""


class SampleCommandError(Exception):
    """Base exception for sample commands."""
    pass


class MissingSimilarInError(SampleCommandError):
    """Model missing similar_in manager."""
    pass


__all__ = [
    'SampleCommandError',
    'MissingSimilarInError',
]
