"""Search command - semantic search via similar_in API."""

from typer import Argument, Option

from wiki_new.management.context import ctx
from wiki_new.management.data_models import (
    SearchResultData,
    SearchResultsData,
)


# === Handler Function ===
def handle_search(
    query: str,
    model: str,
    field: str = "text",
    threshold: float | None = None,
    rank_by: str = "best",
    limit: int = 10,
) -> None:
    """Handle search command with clean separation."""
    try:
        # Business logic: prepare typed data
        data = prepare_search_data(
            query=query,
            model=model,
            field=field,
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

    except ctx.exceptions.ModelNotFoundError:
        ctx.render.message.error(f"Model '{model}' not found")
    except ctx.exceptions.MissingSimilarInError as e:
        ctx.render.message.error(str(e))
    except Exception as e:
        ctx.render.message.error(f"Search failed: {e}")


# === Business Logic Function ===
def prepare_search_data(
    query: str,
    model: str,
    field: str,
    threshold: float | None,
    rank_by: str,
    limit: int,
) -> SearchResultsData:
    """
    Prepare search data (business logic only).

    Args:
        query: Search query string
        model: Model identifier
        field: Field to search
        threshold: Similarity threshold
        rank_by: Ranking strategy
        limit: Maximum results

    Returns:
        SearchResultsData with typed structure

    Raises:
        ModelNotFoundError: If model not found
        MissingSimilarInError: If model has no similar_in manager
    """
    # Get model class via context helpers
    model_class = ctx.helpers.get_model_from_string(model)
    if not model_class:
        raise ctx.exceptions.ModelNotFoundError(f"Model '{model}' not found")

    # Validate similar_in manager exists
    if not hasattr(model_class, "similar_in"):
        raise ctx.exceptions.MissingSimilarInError(
            f"Model '{model_class.__name__}' has no similar_in manager"
        )

    # Check vectorization progress via context helpers (non-blocking)
    _, incomplete = ctx.helpers.check_vectorization_progress(model_class, field)
    # Note: incomplete vectorizers are handled by renderer as warnings

    # Execute search
    field_accessor = getattr(model_class.similar_in, field)
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
        field=field,
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
        model: str = Option(
            "minilm",
            "--model",
            "-m",
            help="Model: minilm, hybrid, nomic, mxbai, snowflake",
        ),
        field: str = Option(
            "text", "--field", "-f", help="Field to search: text, summary"
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
            model=model,
            field=field,
            threshold=threshold,
            rank_by=rank_by,
            limit=limit,
        )


# === Module Export ===
search = SearchCommand()
