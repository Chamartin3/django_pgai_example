# Source Generated with Decompyle++ (manually fixed)
# File: data_models.cpython-310.pyc (Python 3.10)

"""Data models for sample commands - TypedDict definitions."""
from dataclasses import dataclass
from enum import Enum
from typing import TypedDict


class VectorizationStatus(Enum):
    """Vectorization status states."""
    NO_VECTORIZER = 'no_vectorizer'
    COMPLETE = 'complete'
    PROCESSING = 'processing'
    ERROR = 'error'


class VectorizationState(Enum):
    """Vectorization completion states."""
    COMPLETE = 'complete'
    PARTIAL = 'partial'
    NONE = 'none'

    @classmethod
    def from_percentage(cls, percentage: float) -> "VectorizationState":
        """Get state from percentage."""
        if percentage == 100:
            return cls.COMPLETE
        elif percentage > 0:
            return cls.PARTIAL
        return cls.NONE


class MessageType(Enum):
    """Message types for message renderer (errors, warnings, info, etc)."""
    INCOMPLETE = 'incomplete'
    NO_RESULTS = 'no_results'
    SUMMARY = 'summary'
    ERROR = 'error'
    WARNING = 'warning'
    SUCCESS = 'success'
    INFO = 'info'


class SeedAction(Enum):
    """Seed command action options for existing data."""
    REPLACE = 'replace'
    APPEND = 'append'
    SKIP = 'skip'


class FieldProgressData(TypedDict):
    """Progress data for a single vectorized field."""
    name: str
    percentage: float
    processed: int
    total: int


class VectorizationStatusData(TypedDict):
    """Vectorization status data structure."""
    status: VectorizationStatus
    overall_percentage: float
    fields: dict
    error: str | None


class ModelConfigData(TypedDict):
    """Model configuration data for info command."""
    embedding_model: str
    dimensions: int
    chunk_size: int
    chunk_overlap: int
    chunking_method: str


class SearchResultData(TypedDict):
    """Search result data structure."""
    pk: int
    title: str
    score: float
    relevance: float
    match_count: int


class ModelDetailsData(TypedDict):
    """Model details for verbose list display."""
    sample_model: str
    model_key: str
    class_name: str
    app_label: str
    table: str
    embedding_model: str
    dimensions: int | str
    field_names: str
    overall_percentage: float
    vectorization_state: VectorizationState
    config_summary: str
    fields: list
    status: VectorizationStatus


class IncompleteVectorizerData(TypedDict):
    """Data for incomplete vectorizer warnings."""
    field: str
    percentage: float
    processed: int
    total: int


class SearchResultsData(TypedDict):
    """Complete search results data."""
    results: list[SearchResultData]
    query: str
    model_name: str
    field: str
    threshold: float | None
    rank_by: str
    total_count: int


class RankingResultsData(TypedDict):
    """Ranking evaluation results data."""
    results: list[dict]
    query: str
    model_name: str
    field: str
    timing_info: dict | None


class ThresholdResultsData(TypedDict):
    """Threshold evaluation results data."""
    thresholds: list[float]
    results: list[dict]


class ModelListData(TypedDict):
    """Models list data structure for list command."""
    models: list[dict]
    total_count: int


class WarningMessageType(TypedDict):
    """Warning message data structure."""
    type: MessageType
    message: str | None


class SearchResultDataExtended(TypedDict):
    """Extended search result data with rank (for display tables)."""
    pk: int
    title: str
    score: float
    relevance: float
    match_count: int
    rank: int


class ChunkMatchData(TypedDict):
    """Single chunk match for display."""
    chunk_id: int
    similarity: float
    text: str


class AggregateStatsData(TypedDict):
    """Aggregated statistics for a document."""
    pk: int
    title: str
    match_count: int
    avg_similarity: float
    best_similarity: float


class EvaluationResultData(TypedDict):
    """Single evaluation test result for display."""
    test_name: str
    result_count: int
    results: list
    timing: float | None
    error: str | None


class VectorizationData(TypedDict):
    """Input data structure for VectorizationStatusRenderer."""
    model_name: str
    status: VectorizationStatus
    overall_percentage: float
    fields: list[FieldProgressData]
    percentage: float | None


class AggregateInput(TypedDict):
    """Input data structure for AggregateRenderer."""
    results: list[AggregateStatsData]
    query: str
    model_name: str
    show_summary: bool


class ChunksInput(TypedDict):
    """Input data for chunks renderer."""
    matches: list[ChunkMatchData]
    document_id: int
    query: str
    order_by: str


class ComparisonData(TypedDict):
    """Data structure for comparison results."""
    results: list
    model_name: str


class CompareInput(TypedDict):
    """Input data for compare renderer."""
    data: ComparisonData
    query: str


class InfoInput(TypedDict):
    """Input data for info renderer."""
    model_name: str
    field_configs: list[ModelConfigData]


class VectorizerInfo(TypedDict):
    """Vectorizer information data."""
    name: str
    status: str
    target_table: str
    source_column: str


@dataclass
class SeedTableResult:
    """Result of seeding a single table."""
    variant_key: str
    table_name: str
    success: bool
    total_loaded: int
    existing_count: int
    is_skipped: bool = False
    error: str | None = None
    message: str | None = None


class SeedResultsData(TypedDict):
    """Complete seed operation results."""
    tables: list[SeedTableResult]
    total: int
    batch_size: int
    batches: int
    variant: str
    success_count: int
    failed_count: int
    skipped_count: int


class AnnotateResultData(TypedDict):
    """Single annotated result for the annotate command."""
    pk: int
    title: str
    score: float


class AnnotateResultsData(TypedDict):
    """Complete annotate command results."""
    results: list[AnnotateResultData]
    query: str
    model_name: str
    field: str
    limit: int


class RankResultData(TypedDict):
    """Single ranked result for the rank command."""
    pk: int
    title: str
    rank: int


class RankResultsData(TypedDict):
    """Complete rank command results."""
    results: list[RankResultData]
    query: str
    model_name: str
    field: str
    limit: int


class StatsRowData(TypedDict):
    """Single row in vectorization stats table."""
    model_name: str
    field_name: str
    total_rows: int
    embedded_rows: int
    percent: float


class StatsData(TypedDict):
    """Complete stats command results."""
    rows: list[StatsRowData]
    variant: str


__all__ = [
    'VectorizationStatus',
    'VectorizationState',
    'MessageType',
    'SeedAction',
    'FieldProgressData',
    'VectorizationStatusData',
    'ModelConfigData',
    'SearchResultData',
    'SearchResultsData',
    'RankingResultsData',
    'ThresholdResultsData',
    'ModelDetailsData',
    'IncompleteVectorizerData',
    'ModelListData',
    'WarningMessageType',
    'SearchResultDataExtended',
    'ChunkMatchData',
    'AggregateStatsData',
    'EvaluationResultData',
    'VectorizationData',
    'AggregateInput',
    'ChunksInput',
    'ComparisonData',
    'CompareInput',
    'InfoInput',
    'VectorizerInfo',
    'SeedTableResult',
    'SeedResultsData',
    'AnnotateResultData',
    'AnnotateResultsData',
    'RankResultData',
    'RankResultsData',
    'StatsRowData',
    'StatsData',
]
