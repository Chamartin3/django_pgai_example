"""Models command - show all available test models with configuration.

Architecture:
- handle_models(): Entry point handler function
- prepare_models_data(): Business logic function
- models class: Typer dispatcher adapter (delegates to handle_models)

This command follows the Context Architecture pattern:
- Uses ctx.render for all rendering operations
- Uses ctx.helpers for helper functions
- Uses ctx exceptions for error handling
- Clean separation between business logic and display logic
"""

from typer import Option

from wiki_new.management.context import ctx
from wiki_new.management.data_models import ModelListData


# === Handler Function ===
def handle_models(
    verbose: bool = False,
) -> None:
    """Handle models command with clean separation.

    Args:
        verbose: Whether to show detailed configuration
    """
    try:
        # Business logic: prepare typed data
        data = prepare_models_data()

        # Display logic: render using registry
        ctx.render.list.render_models_list(data, verbose=verbose)

    except Exception as e:
        ctx.render.message.error(str(e))


# === Business Logic Function ===
def prepare_models_data() -> ModelListData:
    """
    Prepare models list data (business logic only).

    Returns:
        ModelListData with typed structure containing all model information
    """
    models_data = []

    for sample_model in ctx.models.sample_model:
        try:
            # Get model class directly from enum
            model_class = sample_model.get_model_class()

            # Get vectorization status via context helpers
            status = ctx.helpers.get_vectorization_status(model_class)

            # Get embedding configuration from the first vectorized field
            vectorized_fields = [
                field
                for field in model_class._meta.get_fields()
                if isinstance(field, ctx.types.vectorized_text_field)
            ]

            if not vectorized_fields:
                continue

            # Get config from first field
            first_field = vectorized_fields[0]
            config = first_field.get_vectorizer_config()

            if not config:
                continue

            config_dict = config.to_dict()
            embedding_model = config_dict.get(
                ctx.types.config_field.EMBEDDING_MODEL.value, "unknown"
            )
            dimensions = config_dict.get(
                ctx.types.config_field.EMBEDDING_DIMENSIONS.value, "unknown"
            )

            # Get all field names
            field_names = ", ".join(f.name for f in vectorized_fields)

            # Determine vectorization state from percentage
            percentage = status["overall_percentage"]
            state = ctx.models.vectorization_state.from_percentage(percentage)

            # Build field data for verbose mode
            fields_data = []
            for field in vectorized_fields:
                field_config = field.get_vectorizer_config()
                if not field_config:
                    continue

                field_config_dict = field_config.to_dict()

                # Get field-specific vectorization status
                field_status_data = status["fields"].get(field.name)
                if field_status_data:
                    field_status = {
                        "percentage": field_status_data["percentage"],
                        "processed": field_status_data["processed"],
                        "total": field_status_data["total"],
                    }
                else:
                    field_status = {"percentage": 0.0, "processed": 0, "total": 0}

                fields_data.append(
                    {
                        "name": field.name,
                        "config": field_config_dict,
                        "percentage": field_status["percentage"],
                        "processed": field_status["processed"],
                        "total": field_status["total"],
                    }
                )

            models_data.append(
                {
                    "sample_model": sample_model.name,
                    "model_key": sample_model.key,
                    "class_name": model_class.__name__,
                    "app_label": model_class._meta.app_label,
                    "table": model_class._meta.db_table,
                    "embedding_model": embedding_model,
                    "dimensions": dimensions,
                    "field_names": field_names,
                    "overall_percentage": percentage,
                    "vectorization_state": state,
                    "config_summary": sample_model.description,
                    "fields": fields_data,
                }
            )

        except (LookupError, AttributeError):
            continue

    return ModelListData(
        models=models_data,
        total_count=len(models_data),
    )


# === Typer Adapter Class ===
class ModelsCommand:
    """Models command adapter for Typer - lists available test models."""

    @staticmethod
    def list_models(
        verbose: bool = Option(
            False, "--verbose", "-v", help="Show detailed configuration"
        ),
    ):
        """
        List all available test models with their configurations.

        Shows each model variant with embedding details, dimensions, and
        available vectorized fields.

        Model Keys:
            minilm    - all-MiniLM-L6-v2 (384d) - Fast, general purpose
            hybrid    - Combined MiniLM + Nomic (768d) - Multi-model ensemble
            nomic     - nomic-embed-text (768d) - High quality general
            mxbai     - mixedbread-ai/mxbai-embed-large-1 (1024d) - Best quality
            snowflake - snowflake-arctic-embed-m (768d) - Enterprise grade

        Examples:
            ./manage.sh cmd sample models list
            ./manage.sh cmd sample models list --verbose
            ./manage.sh cmd sample models list -v
        """
        handle_models(verbose=verbose)
