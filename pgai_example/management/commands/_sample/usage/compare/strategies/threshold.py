"""Evaluate cutoff filtering - eval cutoff command.

Architecture:
- handle_cutoff(): Entry point handler function
- prepare_cutoff_data(): Business logic function
- CutoffCommand class: Typer dispatcher adapter (delegates to handle_cutoff)
"""

from typer import Argument, Option

from pgai_example.management.context import ctx


# === Handler Function ===
def handle_cutoff(
    query: str,
    variant: str,
    custom: str | None = None,
    timing: bool = False,
    limit: int = 5,
) -> None:
    """Handle cutoff command with clean separation."""
    try:
        # Business logic: prepare typed data
        data = prepare_cutoff_data(
            query=query,
            variant=variant,
            custom=custom,
            limit=limit,
        )

        # Display warnings for incomplete vectorizers
        if data.get("incomplete_vectorizers"):
            ctx.render.message.render_incomplete_vectorizers(
                data["model_name"], data["incomplete_vectorizers"]
            )

        # Display logic: render using registry eval renderer
        ctx.render.eval.print(data["results_data"])

    except KeyError:
        available = ", ".join(ctx.models.sample_model.all_keys())
        ctx.render.message.error(
            f"Unknown variant: '{variant}'\n\nAvailable variants: {available}"
        )
    except Exception as e:
        ctx.render.message.error(f"Cutoff evaluation failed: {e}")


# === Business Logic Function ===
def prepare_cutoff_data(
    query: str,
    variant: str,
    custom: str | None,
    limit: int,
) -> dict:
    """
    Prepare cutoff evaluation data (business logic only).

    Args:
        query: Search query string
        variant: Vectorizer variant (e.g., 'minilm', 'movies-qwen')
        custom: Custom cutoff values (comma-separated)
        limit: Maximum results per test

    Returns:
        dict with results_data, model_name, and incomplete_vectorizers

    Raises:
        KeyError: If variant not found
    """
    # Get sample model from variant key
    sample_model = ctx.models.sample_model.from_key(variant)
    model_class = sample_model.get_model_class()
    field = sample_model.field_name

    # Check vectorization progress via context helpers
    _, incomplete_vectorizers = ctx.helpers.check_vectorization_progress(model_class, field)

    # Create evaluation
    evaluation = ctx.types.filter_evaluation(model_class, field_name=field, query=query)
    evaluation.add_preset_tests()

    # Add custom cutoff values if specified
    if custom:
        custom_cutoffs = [float(t.strip()) for t in custom.split(",")]
        for cutoff in custom_cutoffs:
            evaluation.add_custom_test(cutoff)

    # Run tests
    evaluation.run(query=query, limit=limit)

    # Get structured data for rendering
    results_data = evaluation.get_results_data()

    return {
        "results_data": results_data,
        "model_name": model_class.__name__,
        "incomplete_vectorizers": incomplete_vectorizers,
    }


# === Typer Adapter Class ===
class CutoffCommand:
    """Cutoff command adapter for Typer - evaluate similarity cutoff levels."""

    @staticmethod
    def cutoff(
        query: str = Argument(..., help="Search query"),
        variant: str = Option(
            "mv-qwen",
            "--variant",
            "-v",
            help="Vectorizer variant: mv-qwen, mv-mxbai, mv-minilm, mv-snowflake",
        ),
        custom: str = Option(
            None, "--custom", "-c", help="Custom cutoff values (comma-separated)"
        ),
        timing: bool = Option(False, "--timing", help="Show timing information"),
        limit: int = Option(5, "--limit", "-l", help="Maximum results per test"),
    ):
        """
        Evaluate different similarity cutoff levels.

        Tests how different cutoff values affect search results.

        Examples:
            ./manage.sh sample usage eval cutoff "machine learning"
            ./manage.sh sample usage eval cutoff "AI" --custom 0.6,0.7,0.8 --timing
        """
        # Delegate to handler
        handle_cutoff(
            query=query,
            variant=variant,
            custom=custom,
            timing=timing,
            limit=limit,
        )


# === Module Export ===
thresholdCommand = CutoffCommand()
