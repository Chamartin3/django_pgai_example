"""Evaluate ranking strategies - eval ranking command.

Architecture:
- handle_ranking(): Entry point handler function
- prepare_ranking_data(): Business logic function
- ranking class: Typer dispatcher adapter (delegates to handle_ranking)
"""

from typer import Argument, Option

from pgai_example.management.context import ctx


# === Handler Function ===
def handle_ranking(
    query: str,
    variant: str,
    timing: bool = False,
    limit: int = 5,
) -> None:
    """Handle ranking command with clean separation."""
    try:
        # Business logic: prepare typed data
        data = prepare_ranking_data(
            query=query,
            variant=variant,
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
        ctx.render.message.error(f"Ranking evaluation failed: {e}")


# === Business Logic Function ===
def prepare_ranking_data(
    query: str,
    variant: str,
    limit: int,
) -> dict:
    """
    Prepare ranking evaluation data (business logic only).

    Args:
        query: Search query string
        variant: Vectorizer variant (e.g., 'minilm', 'movies-qwen')
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
    evaluation = ctx.types.search_evaluation(model_class, field_name=field)
    evaluation.add_preset_find_tests()

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
class RankingCommand:
    """Ranking command adapter for Typer - evaluate ranking strategies."""

    @staticmethod
    def ranking(
        query: str = Argument(..., help="Search query"),
        variant: str = Option(
            "mv-qwen",
            "--variant",
            "-v",
            help="Vectorizer variant: mv-qwen, mv-mxbai, mv-minilm, mv-snowflake",
        ),
        timing: bool = Option(False, "--timing", help="Show timing information"),
        limit: int = Option(5, "--limit", "-l", help="Maximum results per test"),
    ):
        """
        Evaluate different ranking strategies.

        Tests how different ranking approaches (best, relevance, count) affect search results.

        Examples:
            ./manage.sh sample usage eval ranking "machine learning"
            ./manage.sh sample usage eval ranking "AI" --timing --limit 15
        """
        # Delegate to handler
        handle_ranking(
            query=query,
            variant=variant,
            timing=timing,
            limit=limit,
        )


# === Module Export ===
rankingCommand = RankingCommand()
