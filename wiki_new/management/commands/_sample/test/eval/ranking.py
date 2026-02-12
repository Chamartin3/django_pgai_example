"""Evaluate ranking strategies - eval ranking command.

Architecture:
- handle_ranking(): Entry point handler function
- prepare_ranking_data(): Business logic function
- ranking class: Typer dispatcher adapter (delegates to handle_ranking)
"""

from typer import Argument, Option

from wiki_new.management.context import ctx


# === Handler Function ===
def handle_ranking(
    query: str,
    model: str,
    field: str = "text",
    timing: bool = False,
    limit: int = 10,
) -> None:
    """Handle ranking command with clean separation."""
    try:
        # Business logic: prepare typed data
        data = prepare_ranking_data(
            query=query,
            model=model,
            field=field,
            limit=limit,
        )

        # Display warnings for incomplete vectorizers
        if data.get("incomplete_vectorizers"):
            ctx.render.message.render_incomplete_vectorizers(
                data["model_name"], data["incomplete_vectorizers"]
            )

        # Display logic: render using registry eval renderer
        ctx.render.eval.print(data["results_data"])

    except ctx.exceptions.ModelNotFoundError:
        ctx.render.message.error(f"Model '{model}' not found")
    except Exception as e:
        ctx.render.message.error(f"Ranking evaluation failed: {e}")


# === Business Logic Function ===
def prepare_ranking_data(
    query: str,
    model: str,
    field: str,
    limit: int,
) -> dict:
    """
    Prepare ranking evaluation data (business logic only).

    Args:
        query: Search query string
        model: Model identifier
        field: Field to search
        limit: Maximum results per test

    Returns:
        dict with results_data, model_name, and incomplete_vectorizers

    Raises:
        ModelNotFoundError: If model not found
    """
    # Get model class via context helpers
    model_class = ctx.helpers.get_model_from_string(model)
    if not model_class:
        raise ctx.exceptions.ModelNotFoundError(f"Model '{model}' not found")

    # Check vectorization progress via context helpers
    _, incomplete_vectorizers = ctx.helpers.check_vectorization_progress(model_class, field)

    # Create evaluation
    evaluation = ctx.types.SearchEvaluation(model_class, field_name=field)
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
        model: str = Option(
            "minilm",
            "--model",
            "-m",
            help="Model: minilm, hybrid, nomic, mxbai, snowflake",
        ),
        field: str = Option(
            "text", "--field", "-f", help="Field to search: text, summary"
        ),
        timing: bool = Option(False, "--timing", help="Show timing information"),
        limit: int = Option(10, "--limit", "-l", help="Maximum results per test"),
    ):
        """
        Evaluate different ranking strategies.

        Tests how different ranking approaches (best, relevance, count) affect search results.

        Examples:
            ./manage.sh sample test ranking "machine learning"
            ./manage.sh sample test ranking "AI" --timing --limit 15
        """
        # Delegate to handler
        handle_ranking(
            query=query,
            model=model,
            field=field,
            timing=timing,
            limit=limit,
        )


# === Module Export ===
rankingCommand = RankingCommand()
