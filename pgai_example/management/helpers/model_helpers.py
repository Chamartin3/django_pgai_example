# Source Generated with Decompyle++ (manually fixed)
# File: model_helpers.cpython-310.pyc (Python 3.10)

"""Model helpers - business logic for model operations."""


def extract_title(instance, max_length: int = 50) -> str:
    """
    Extract title from a model instance.

    Args:
        instance: Model instance
        max_length: Maximum title length

    Returns:
        Title string truncated to max_length
    """
    if hasattr(instance, 'title') and instance.title:
        return str(instance.title)[:max_length]
    return str(instance)[:max_length]


def get_model_table_name(model_class) -> str:
    """Get database table name for model."""
    return model_class._meta.db_table


def get_model_app_label(model_class) -> str:
    """Get app label for model."""
    return model_class._meta.app_label


__all__ = [
    'extract_title',
    'get_model_table_name',
    'get_model_app_label',
]
