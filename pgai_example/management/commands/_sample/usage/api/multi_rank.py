"""Rank command - semantic_rank queryset demo."""

from typer import Argument, Option

from pgai_example.management.context import ctx
from pgai_example.management.data_models import (
    RankResultData,
    RankResultsData,
)


def handle_rank(
    query: str,
    variant: str,
    limit: int,
) -> None:
    """Handle rank command."""
    try:
        data = prepare_rank_data(
            query=query,
            variant=variant,
            limit=limit,
        )

        ctx.render.rank.print(data)

    except KeyError:
        available = ", ".join(ctx.models.sample_model.all_keys())
        ctx.render.message.error(
            f"Unknown variant: '{variant}'\n\nAvailable variants: {available}"
        )
    except Exception as e:
        ctx.render.message.error(f"Rank failed: {e}")


def prepare_rank_data(
    query: str,
    variant: str,
    limit: int,
) -> RankResultsData:
    """Prepare rank data (business logic)."""
    sample_model = ctx.models.sample_model.from_key(variant)
    model_class = sample_model.get_model_class()
    field_name = sample_model.field_name

    qs = model_class.objects.semantic_rank(query, fields=[field_name])[:limit]

    results: list[RankResultData] = [
        RankResultData(
            pk=instance.pk,
            title=ctx.helpers.extract_title(instance),
            rank=idx,
        )
        for idx, instance in enumerate(qs, 1)
    ]

    return RankResultsData(
        results=results,
        query=query,
        model_name=model_class.__name__,
        field=field_name,
        limit=limit,
    )


class RankCommand:
    """Rank command adapter for Typer."""

    @staticmethod
    def rank(
        query: str = Argument(..., help="Search query"),
        variant: str = Option(
            "mv-qwen",
            "--variant",
            "-v",
            help="Vectorizer variant: mv-qwen, mv-mxbai, mv-minilm, mv-snowflake",
        ),
        limit: int = Option(10, "--limit", "-l", help="Maximum results"),
    ):
        """Rank queryset using multi-field semantic score."""
        handle_rank(
            query=query,
            variant=variant,
            limit=limit,
        )


rank = RankCommand()
