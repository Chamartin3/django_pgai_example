"""Search command - semantic search via similar_in API."""

from typer import Argument, Option

from pgai_example.management.context import ctx
from pgai_example.management.data_models import (
    SearchResultData,
    SearchResultsData,
)


# === Handler Function ===
def handle_search(
    query: str,
    variant: str,
    threshold: float | None = None,
    rank_by: str = "best",
    limit: int = 10,
) -> None:
    """Handle search command with clean separation."""
    try:
        # Business logic: prepare typed data
        data = prepare_search_data(
            query=query,
            variant=variant,
            threshold=threshold,
            rank_by=rank_by,
            limit=limit,
        )

        # Display logic: render using registry
        ctx.render.search.render_search_results(
            results=data["results"],
            query=data["query"],
            model_name=data["model_name"],
            field=data["field"],
            threshold=data["threshold"],
            rank_by=data["rank_by"],
        )

    except KeyError:
        available = ", ".join(ctx.models.sample_model.all_keys())
        ctx.render.message.error(
            f"Unknown variant: '{variant}'\n\nAvailable variants: {available}"
        )
    except ctx.exceptions.MissingSimilarInError as e:
        ctx.render.message.error(str(e))
    except Exception as e:
        ctx.render.message.error(f"Search failed: {e}")


# === Business Logic Function ===
def prepare_search_data(
    query: str,
    variant: str,
    threshold: float | None,
    rank_by: str,
    limit: int,
) -> SearchResultsData:
    """
    Prepare search data (business logic only).

    Args:
        query: Search query string
        variant: Vectorizer variant (e.g., 'minilm', 'movies-qwen')
        threshold: Similarity threshold
        rank_by: Ranking strategy
        limit: Maximum results

    Returns:
        SearchResultsData with typed structure

    Raises:
        KeyError: If variant not found
        MissingSimilarInError: If model has no similar_in manager
    """
    # Get sample model from variant key
    sample_model = ctx.models.sample_model.from_key(variant)
    model_class = sample_model.get_model_class()
    field_name = sample_model.field_name

    # Validate similar_in manager exists
    if not hasattr(model_class, "similar_in"):
        raise ctx.exceptions.MissingSimilarInError(
            f"Model '{model_class.__name__}' has no similar_in manager"
        )

    # Check vectorization progress via context helpers (non-blocking)
    _, incomplete = ctx.helpers.check_vectorization_progress(model_class, field_name)
    # Note: incomplete vectorizers are handled by renderer as warnings

    # Execute search
    field_accessor = getattr(model_class.similar_in, field_name)
    results = field_accessor.find(
        query,
        limit=limit,
        threshold=threshold,
        rank_by=rank_by,
    )

    # Transform to typed data structure
    search_results: list[SearchResultData] = [
        SearchResultData(
            pk=result.instance.pk,
            title=ctx.helpers.extract_title(result.instance),
            score=result.score,
            relevance=result.relevance,
            match_count=result.match_count,
        )
        for result in results
    ]

    return SearchResultsData(
        results=search_results,
        query=query,
        model_name=model_class.__name__,
        field=field_name,
        threshold=threshold,
        rank_by=rank_by,
        total_count=len(search_results),
    )


# === Helper Functions ===
# Moved to helpers/model_helpers.py - imported from context


# === Typer Command Class (Adapter) ===
class SearchCommand:
    """Search command adapter for Typer - semantic search via similar_in API."""

    @staticmethod
    def search(
        query: str = Argument(..., help="Search query"),
        variant: str = Option(
            "wk-minilm",
            "--variant",
            "-v",
            help="Vectorizer variant: wk-minilm, wk-snow, mv-qwen, mv-mxbai",
        ),
        threshold: float | None = Option(
            None, "--threshold", "-t", help="Similarity threshold (0.0-1.0)"
        ),
        rank_by: str = Option(
            "best", "--rank-by", "-r", help="Ranking: best, relevance, count"
        ),
        limit: int = Option(10, "--limit", "-l", help="Maximum results"),
    ):
        """Search for similar instances using the similar_in API."""
        # Delegate to handler
        handle_search(
            query=query,
            variant=variant,
            threshold=threshold,
            rank_by=rank_by,
            limit=limit,
        )


# === Module Export ===
search = SearchCommand()
