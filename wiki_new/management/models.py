# Source Generated with Decompyle++ (manually fixed)
# File: models.cpython-310.pyc (Python 3.10)

"""Model selection utilities for sample commands."""
from enum import Enum
from django.apps import apps

# Mapping from model keys to actual model class names
model_name_mapping = {
    'minilm': 'WikiArticleMiniLM',
    'snowflake': 'WikiArticleSnowflake',
}


class Dataset(Enum):
    """Available datasets for loading into models."""
    WIKIPEDIA = 'wikipedia'

    @property
    def huggingface_name(self) -> str:
        """Get HuggingFace dataset identifier."""
        datasets = {
            'wikipedia': 'wikimedia/wikipedia',
        }
        return datasets.get(self.value, '')

    @property
    def config(self) -> str:
        """Get dataset configuration/version."""
        configs = {
            'wikipedia': '20231101.en',
        }
        return configs.get(self.value, '')

    @property
    def field_types(self) -> dict[str, str]:
        """Get field type mappings for this dataset."""
        return {"id": "INTEGER"}

    @property
    def description(self) -> str:
        """Get description for this dataset."""
        descriptions = {
            'wikipedia': 'Wikipedia articles (November 2023, English)',
        }
        return descriptions.get(self.value, '')


class SampleModel(Enum):
    """Available sample models for testing - dynamically maps to wiki_new models."""
    MINILM = 'minilm'
    SNOWFLAKE = 'snowflake'

    @property
    def key(self) -> str:
        """Get the key for this model."""
        return self.value

    @property
    def description(self) -> str:
        """Get description for this model."""
        descriptions = {
            'minilm': 'all-MiniLM-L6-v2 (384d) - Fast, general purpose',
            'snowflake': 'snowflake-arctic-embed (1024d) - High quality multilingual',
        }
        return descriptions.get(self.value, '')

    @property
    def table_name(self) -> str:
        """Get database table name for this model."""
        try:
            model_class = self.get_model_class()
            return model_class._meta.db_table
        except LookupError:
            # Fallback to constructed name if model not yet loaded
            return f"wiki_new_{model_name_mapping.get(self.value, '').lower()}"

    def get_model_class(self):
        """
        Get Django model class from enum by dynamically loading from wiki_new app.

        Returns:
            Django model class

        Raises:
            LookupError: If model not found in wiki_new app
        """
        model_name = model_name_mapping.get(self.value)
        if not model_name:
            raise LookupError(f"Model '{self.value}' not found in SampleModel mapping")

        try:
            return apps.get_model('wiki_new', model_name)
        except LookupError:
            raise LookupError(f"Model '{model_name}' not found in wiki_new app")


# Mapping from models to their datasets (must be after SampleModel definition)
MODEL_DATASET_MAP = {
    SampleModel.MINILM: Dataset.WIKIPEDIA,
    SampleModel.SNOWFLAKE: Dataset.WIKIPEDIA,
}


def get_model_from_string(model_str: str):
    """
    Get Django model class from string identifier by dynamic lookup.

    Args:
        model_str: Model identifier (e.g., "minilm", "snowflake")

    Returns:
        Django model class or None if not found
    """
    if not model_str:
        return None

    # Try to find matching SampleModel enum
    model_str_lower = model_str.lower()
    for sample_model in SampleModel:
        if sample_model.value == model_str_lower:
            try:
                return sample_model.get_model_class()
            except LookupError:
                return None

    return None


__all__ = [
    'SampleModel',
    'Dataset',
    'MODEL_DATASET_MAP',
    'get_model_from_string',
]
