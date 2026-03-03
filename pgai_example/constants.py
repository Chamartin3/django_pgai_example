"""Vectorizer configurations and sample models - single source of truth."""
from enum import Enum
from typing import TYPE_CHECKING, Literal, NamedTuple

from django.apps import apps

if TYPE_CHECKING:
    from django.db.models import Model


class DatasetConfig(NamedTuple):
    """Dataset configuration for seeding."""
    huggingface_name: str
    config: str | None
    field_types: dict[str, str]
    description: str


class VectorizerConfig(NamedTuple):
    """Complete vectorizer configuration."""
    key: str                      # "minilm", "movies-qwen"
    description: str              # Human-readable
    app_label: str                # "pgai_example"
    model_class_name: str         # "WikiArticleMiniLM"
    field_name: str               # "text" or "overview"
    embedding_model: str          # "all-minilm"
    embedding_dimensions: int     # 384, 1024
    dataset: DatasetConfig


# Reusable dataset definitions
DATASET_WIKIPEDIA = DatasetConfig(
    huggingface_name='wikimedia/wikipedia',
    config='20231101.en',
    field_types={"id": "INTEGER"},
    description='Wikipedia articles (November 2023, English)',
)

DATASET_MOVIES = DatasetConfig(
    huggingface_name='Cohere/movies',
    config=None,
    field_types={},
    description='Cohere movies dataset with titles, overviews, genres, cast',
)


class SampleModel(Enum):
    """
    Single source of truth for all vectorizer configurations.

    Each member contains complete metadata about a model+field combination.
    Access via:
        sample_model = SampleModel.from_key('minilm')
        model_class = sample_model.get_model_class()
        field_name = sample_model.field_name
    """

    MINILM = VectorizerConfig(
        key='wk-minilm',
        description='all-MiniLM-L6-v2 (384d) - Fast, general purpose',
        app_label='pgai_example',
        model_class_name='WikiArticleMiniLM',
        field_name='text',
        embedding_model='all-minilm',
        embedding_dimensions=384,
        dataset=DATASET_WIKIPEDIA,
    )

    SNOWFLAKE = VectorizerConfig(
        key='wk-snow',
        description='snowflake-arctic-embed (1024d) - High quality multilingual',
        app_label='pgai_example',
        model_class_name='WikiArticleSnowflake',
        field_name='text',
        embedding_model='snowflake-arctic-embed',
        embedding_dimensions=1024,
        dataset=DATASET_WIKIPEDIA,
    )

    MOVIES_QWEN = VectorizerConfig(
        key='mv-qwen',
        description='Movies with qwen3-embedding (1024d)',
        app_label='pgai_example',
        model_class_name='MovieQwen',
        field_name='overview',
        embedding_model='qwen3-embedding',
        embedding_dimensions=1024,
        dataset=DATASET_MOVIES,
    )

    MOVIES_MXBAI = VectorizerConfig(
        key='mv-mxbai',
        description='Movies with mxbai-embed-large (1024d)',
        app_label='pgai_example',
        model_class_name='MovieMxbai',
        field_name='overview',
        embedding_model='mxbai-embed-large:latest',
        embedding_dimensions=1024,
        dataset=DATASET_MOVIES,
    )

    # === Property Accessors ===

    @property
    def key(self) -> str:
        """Get the short key for this vectorizer."""
        return self.value.key

    @property
    def description(self) -> str:
        """Get description for this vectorizer."""
        return self.value.description

    @property
    def app_label(self) -> str:
        """Get the Django app label."""
        return self.value.app_label

    @property
    def model_class_name(self) -> Literal[
        'WikiArticleMiniLM',
        'WikiArticleSnowflake',
        'MovieQwen',
        'MovieMxbai',
    ]:
        """Get the Django model class name."""
        return self.value.model_class_name  # type: ignore

    @property
    def field_name(self) -> Literal['text', 'overview']:
        """Get the vectorized field name."""
        return self.value.field_name  # type: ignore

    @property
    def embedding_model(self) -> str:
        """Get the embedding model name."""
        return self.value.embedding_model

    @property
    def embedding_dimensions(self) -> Literal[384, 1024]:
        """Get the embedding dimensions."""
        return self.value.embedding_dimensions  # type: ignore

    @property
    def dataset(self) -> DatasetConfig:
        """Get the dataset configuration."""
        return self.value.dataset

    @property
    def table_name(self) -> str:
        """Get database table name for this model."""
        try:
            model_class = self.get_model_class()
            return model_class._meta.db_table
        except LookupError:
            # Fallback: construct table name from app_label and model name
            return f"{self.app_label}_{self.model_class_name.lower()}"

    # === Methods ===

    def get_model_class(self) -> "type[Model]":
        """
        Get Django model class from enum.

        Returns:
            Django model class for this vectorizer configuration

        Raises:
            LookupError: If model not found in the configured app
        """
        try:
            return apps.get_model(self.app_label, self.model_class_name)
        except LookupError:
            raise LookupError(
                f"Model '{self.model_class_name}' not found in '{self.app_label}' app"
            )

    # === Class Methods ===

    @classmethod
    def from_key(cls, key: str) -> 'SampleModel':
        """
        Get SampleModel from string key.

        Args:
            key: Vectorizer key ``

        Returns:
            SampleModel enum member

        Raises:
            KeyError: If key not found
        """
        key_lower = key.lower()
        for member in cls:
            if member.key == key_lower:
                return member
        raise KeyError(f"Unknown vectorizer key: '{key}'")

    @classmethod
    def all_keys(cls) -> list[str]:
        """Get all valid vectorizer keys."""
        return [m.key for m in cls]

    @classmethod
    def choices_help(cls) -> str:
        """Generate help text for CLI choices."""
        return ", ".join(cls.all_keys())


__all__ = [
    'SampleModel',
    'DatasetConfig',
    'VectorizerConfig',
    'DATASET_WIKIPEDIA',
    'DATASET_MOVIES',
]
