"""Find command - high-level field-accessor API.

Demonstrates: `Model.similar_in.<field>.find(query, ...)` — the ergonomic
field-accessor API that returns SemanticResult objects with `.score`,
`.relevance`, and `.match_count`.
"""

from typer import Argument, Option

from pgai_example.management.context import ctx
from pgai_example.management.data_models import (
    SearchResultData,
    SearchResultsData,
)


def handle_find(
    query: str,
    variant: str,
    threshold: float | None = None,
    rank_by: str = "best",
    limit: int = 10,
) -> None:
    """Handle find command."""
    try:
        data = prepare_find_data(
            query=query,
            variant=variant,
            threshold=threshold,
            rank_by=rank_by,
            limit=limit,
        )
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
        ctx.render.message.error(f"Find failed: {e}")


def prepare_find_data(
    query: str,
    variant: str,
    threshold: float | None,
    rank_by: str,
    limit: int,
) -> SearchResultsData:
    """Run similar_in.<field>.find() and shape the response."""
    sample_model = ctx.models.sample_model.from_key(variant)
    model_class = sample_model.get_model_class()
    field_name = sample_model.field_name

    if not hasattr(model_class, "similar_in"):
        raise ctx.exceptions.MissingSimilarInError(
            f"Model '{model_class.__name__}' has no similar_in manager"
        )

    ctx.helpers.check_vectorization_progress(model_class, field_name)

    field_accessor = getattr(model_class.similar_in, field_name)
    results = field_accessor.find(
        query,
        limit=limit,
        threshold=threshold,
        rank_by=rank_by,
    )

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


class FindCommand:
    """Typer adapter for the `find` command."""

    @staticmethod
    def find(
        query: str = Argument(..., help="Search query"),
        variant: str = Option(
            "mv-qwen", "--variant", "-v",
            help="Vectorizer variant: mv-qwen, mv-mxbai, mv-minilm, mv-snowflake",
        ),
        threshold: float | None = Option(
            None, "--threshold", "-t", help="Similarity threshold (0.0-1.0)"
        ),
        rank_by: str = Option(
            "best", "--rank-by", "-r", help="Ranking: best, relevance, count"
        ),
        limit: int = Option(10, "--limit", "-l", help="Maximum results"),
    ):
        """Find similar instances via `similar_in.<field>.find()`."""
        handle_find(
            query=query,
            variant=variant,
            threshold=threshold,
            rank_by=rank_by,
            limit=limit,
        )


find = FindCommand()
