# Source Generated with Decompyle++ (manually fixed)
# File: field_config.cpython-310.pyc (Python 3.10)

"""Django field configuration extraction for sample test command."""

from django_pgai.fields import VectorizedTextField


def extract_field_config(model_class, field_name: str) -> dict | None:
    """Extract field configuration from Django model.

    Args:
        model_class: Django model class
        field_name: Name of the vectorized field

    Returns:
        Field configuration dict or None if not found/vectorized

    Raises:
        FieldDoesNotExist: If field_name doesn't exist on model
    """
    try:
        field = model_class._meta.get_field(field_name)
        if not isinstance(field, VectorizedTextField):
            return None

        config = field.get_vectorizer_config()
        if config is None:
            return None

        return config.to_dict()
    except Exception:
        return None


def _get_config_value(config_data, *keys, default=None):
    """Get configuration value trying multiple key names.

    Args:
        config_data: Configuration dict or object
        *keys: Key names to try (new format first, then legacy)
        default: Default value if no key found

    Returns:
        Configuration value or default
    """
    if config_data is None:
        return default

    for key in keys:
        if isinstance(config_data, dict):
            if key in config_data:
                return config_data[key]
        elif hasattr(config_data, key):
            return getattr(config_data, key)

    return default


def get_vectorized_fields(model_class) -> list:
    """Get all VectorizedTextField fields from a model."""
    return [
        field for field in model_class._meta.get_fields()
        if isinstance(field, VectorizedTextField)
    ]


__all__ = [
    'extract_field_config',
    'get_vectorized_fields',
]
