"""Filter command - structured ORM filter combined with semantic ranking.

Demonstrates: composing a normal Django `.filter()` (here: `genres__icontains`)
with the `semantic_score()` expression, then ordering by similarity. This is
the only usage command that mixes structured filtering with semantic ranking.
"""

from django_pgai.db.semantic_search.expressions import semantic_score
from typer import Argument, Option

from pgai_example.management.context import ctx
from pgai_example.management.data_models import (
    AnnotateResultData,
    AnnotateResultsData,
)


def handle_filter(
    query: str,
    variant: str,
    genre: str,
    limit: int,
) -> None:
    """Handle filter command."""
    try:
        data = prepare_filter_data(
            query=query,
            variant=variant,
            genre=genre,
            limit=limit,
        )
        ctx.render.annotate.print(data)
    except KeyError:
        available = ", ".join(ctx.models.sample_model.all_keys())
        ctx.render.message.error(
            f"Unknown variant: '{variant}'\n\nAvailable variants: {available}"
        )
    except Exception as e:
        ctx.render.message.error(f"Filter failed: {e}")


def prepare_filter_data(
    query: str,
    variant: str,
    genre: str,
    limit: int,
) -> AnnotateResultsData:
    """Filter by genre, annotate semantic score, order by score."""
    sample_model = ctx.models.sample_model.from_key(variant)
    model_class = sample_model.get_model_class()
    field_name = sample_model.field_name

    qs = (
        model_class.objects
        .filter(genres__icontains=genre)
        .annotate(score=semantic_score(field_name, query))
        .order_by("-score")[:limit]
    )

    results: list[AnnotateResultData] = [
        AnnotateResultData(
            pk=instance.pk,
            title=ctx.helpers.extract_title(instance),
            score=float(instance.score),
        )
        for instance in qs
    ]

    return AnnotateResultsData(
        results=results,
        query=f"{query}  (genre~={genre!r})",
        model_name=model_class.__name__,
        field=field_name,
        limit=limit,
    )


class FilterCommand:
    """Typer adapter for the `filter` command."""

    @staticmethod
    def filter(
        query: str = Argument(..., help="Search query"),
        variant: str = Option(
            "mv-qwen", "--variant", "-v",
            help="Vectorizer variant: mv-qwen, mv-mxbai, mv-minilm, mv-snowflake",
        ),
        genre: str = Option(
            "Action", "--genre", "-g",
            help="Filter by genre (icontains match on movie.genres)",
        ),
        limit: int = Option(10, "--limit", "-l", help="Maximum results"),
    ):
        """Combine an ORM filter with semantic ranking."""
        handle_filter(
            query=query,
            variant=variant,
            genre=genre,
            limit=limit,
        )


filter = FilterCommand()
