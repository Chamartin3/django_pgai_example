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
    key: str                      # "mv-qwen", "mv-mxbai", ...
    description: str              # Human-readable
    app_label: str                # "pgai_example"
    model_class_name: str         # "Movie"
    field_name: str               # "overview", "overview_mxbai", ...
    embedding_model: str          # "qwen3-embedding"
    embedding_dimensions: int     # 384, 1024
    dataset: DatasetConfig


DATASET_MOVIES = DatasetConfig(
    huggingface_name='Cohere/movies',
    config=None,
    field_types={},
    description='Cohere movies dataset with titles, overviews, genres, cast',
)


class SampleModel(Enum):
    """Single source of truth for all vectorizer configurations.

    Every entry shares ``model_class_name='Movie'`` and differs only in
    ``field_name`` — each field on ``Movie`` is its own vectorizer over the
    shared ``overview`` column (via the proxy ``source_field='overview'``).
    """

    MOVIES_QWEN = VectorizerConfig(
        key='mv-qwen',
        description='qwen3-embedding (1024d) — concrete column vectorizer',
        app_label='pgai_example',
        model_class_name='Movie',
        field_name='overview',
        embedding_model='qwen3-embedding',
        embedding_dimensions=1024,
        dataset=DATASET_MOVIES,
    )

    MOVIES_MXBAI = VectorizerConfig(
        key='mv-mxbai',
        description='mxbai-embed-large (1024d) — proxy over overview',
        app_label='pgai_example',
        model_class_name='Movie',
        field_name='overview_mxbai',
        embedding_model='mxbai-embed-large:latest',
        embedding_dimensions=1024,
        dataset=DATASET_MOVIES,
    )

    MOVIES_MINILM = VectorizerConfig(
        key='mv-minilm',
        description='all-MiniLM-L6-v2 (384d) — proxy over overview',
        app_label='pgai_example',
        model_class_name='Movie',
        field_name='overview_minilm',
        embedding_model='all-minilm',
        embedding_dimensions=384,
        dataset=DATASET_MOVIES,
    )

    MOVIES_SNOWFLAKE = VectorizerConfig(
        key='mv-snowflake',
        description='snowflake-arctic-embed (1024d) — proxy over overview',
        app_label='pgai_example',
        model_class_name='Movie',
        field_name='overview_snowflake',
        embedding_model='snowflake-arctic-embed',
        embedding_dimensions=1024,
        dataset=DATASET_MOVIES,
    )

    # === Property Accessors ===

    @property
    def key(self) -> str:
        return self.value.key

    @property
    def description(self) -> str:
        return self.value.description

    @property
    def app_label(self) -> str:
        return self.value.app_label

    @property
    def model_class_name(self) -> Literal['Movie']:
        return self.value.model_class_name  # type: ignore

    @property
    def field_name(self) -> Literal[
        'overview', 'overview_mxbai', 'overview_minilm', 'overview_snowflake'
    ]:
        return self.value.field_name  # type: ignore

    @property
    def embedding_model(self) -> str:
        return self.value.embedding_model

    @property
    def embedding_dimensions(self) -> Literal[384, 1024]:
        return self.value.embedding_dimensions  # type: ignore

    @property
    def dataset(self) -> DatasetConfig:
        return self.value.dataset

    @property
    def table_name(self) -> str:
        """Database table name for this vectorizer's source model."""
        try:
            return self.get_model_class()._meta.db_table
        except LookupError:
            return f"{self.app_label}_{self.model_class_name.lower()}"

    # === Methods ===

    def get_model_class(self) -> "type[Model]":
        try:
            return apps.get_model(self.app_label, self.model_class_name)
        except LookupError:
            raise LookupError(
                f"Model '{self.model_class_name}' not found in '{self.app_label}' app"
            )

    # === Class Methods ===

    @classmethod
    def from_key(cls, key: str) -> 'SampleModel':
        key_lower = key.lower()
        for member in cls:
            if member.key == key_lower:
                return member
        raise KeyError(f"Unknown vectorizer key: '{key}'")

    @classmethod
    def all_keys(cls) -> list[str]:
        return [m.key for m in cls]

    @classmethod
    def choices_help(cls) -> str:
        return ", ".join(cls.all_keys())


__all__ = [
    'SampleModel',
    'DatasetConfig',
    'VectorizerConfig',
    'DATASET_MOVIES',
]
