"""Annotate command - semantic score annotation demo."""

from django_pgai.db.semantic_search.expressions import semantic_score
from typer import Argument, Option

from pgai_example.management.context import ctx
from pgai_example.management.data_models import (
    AnnotateResultData,
    AnnotateResultsData,
)


def handle_annotate(
    query: str,
    variant: str,
    limit: int,
) -> None:
    """Handle annotate command."""
    try:
        data = prepare_annotate_data(
            query=query,
            variant=variant,
            limit=limit,
        )

        ctx.render.annotate.print(data)

    except KeyError:
        available = ", ".join(ctx.models.sample_model.all_keys())
        ctx.render.message.error(
            f"Unknown variant: '{variant}'\n\nAvailable variants: {available}"
        )
    except Exception as e:
        ctx.render.message.error(f"Annotate failed: {e}")


def prepare_annotate_data(
    query: str,
    variant: str,
    limit: int,
) -> AnnotateResultsData:
    """Prepare annotate data (business logic)."""
    sample_model = ctx.models.sample_model.from_key(variant)
    model_class = sample_model.get_model_class()
    field_name = sample_model.field_name

    # NOTE: Thiss sohudl not anotate itself but it should be using the SemanticSearchQuerySet.
    # Que queryst annotates the score This is just for demo purposes.

    qs = model_class.objects.annotate(score=semantic_score(field_name, query)).order_by(
        "-score"
    )[:limit]

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
        query=query,
        model_name=model_class.__name__,
        field=field_name,
        limit=limit,
    )


class AnnotateCommand:
    """Annotate command adapter for Typer."""

    @staticmethod
    def annotate(
        query: str = Argument(..., help="Search query"),
        variant: str = Option(
            "mv-qwen",
            "--variant",
            "-v",
            help="Vectorizer variant: mv-qwen, mv-mxbai, mv-minilm, mv-snowflake",
        ),
        limit: int = Option(10, "--limit", "-l", help="Maximum results"),
    ):
        """Annotate queryset with semantic scores."""
        handle_annotate(
            query=query,
            variant=variant,
            limit=limit,
        )


annotate = AnnotateCommand()
