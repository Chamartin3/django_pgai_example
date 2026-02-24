"""Seed command - Load Wikipedia data into wiki_new models.

This command follows the Context Architecture pattern:
- Uses ctx.render for all rendering operations
- Uses ctx.helpers for helper functions
- Direct access to SampleModel and Dataset enums
"""
from django.core.management.base import BaseCommand

from wiki_new.management.data_models import SeedResultsData, SeedTableResult
from wiki_new.management.decorators import command_handler
from wiki_new.management.models import Dataset, SampleModel, MODEL_DATASET_MAP


@command_handler
def handle_seed(
    ctx,  # Context injected by decorator
    batches: int,
    batch_size: int,
    model_choice: str,
    append: bool = False,
) -> None:
    """Load Wikipedia data into model tables.

    Args:
        batches: Number of batches to load
        batch_size: Number of articles per batch
        model_choice: Which model(s) to seed ('minilm', 'snowflake', or 'all')
        append: Whether to append to existing data (unused currently)
    """
    # Determine which models to load
    if model_choice == "all":
        models_to_load = list(SampleModel)
    else:
        models_to_load = [m for m in SampleModel if m.key == model_choice]

    table_results: list[SeedTableResult] = []
    success_count = 0

    # Load each model's table
    for sample_model in models_to_load:
        table_name = sample_model.table_name
        dataset = MODEL_DATASET_MAP.get(sample_model, Dataset.WIKIPEDIA)

        # Check if table exists
        if not ctx.helpers.check_table_exists(table_name):
            table_results.append({
                'table_name': table_name,
                'success': False,
                'total_loaded': 0,
                'error': f"Table doesn't exist. Run: ./setup.sh build --skip-seed",
            })
            continue

        # Load dataset into table
        success, total_loaded, error = ctx.helpers.load_dataset_into_table(
            table_name=table_name,
            dataset_name=dataset.huggingface_name,
            dataset_config=dataset.config,
            field_types=dataset.field_types,
            batches=batches,
            batch_size=batch_size,
        )

        table_results.append({
            'table_name': table_name,
            'success': success,
            'total_loaded': total_loaded,
            'error': error,
        })

        if success:
            success_count += 1

    # Prepare data and render
    data = SeedResultsData(
        tables=table_results,
        batches=batches,
        batch_size=batch_size,
        model_choice=model_choice,
        total_per_model=batches * batch_size,
        success_count=success_count,
        failed_count=len(models_to_load) - success_count,
    )
    ctx.render.seed.print(data)


class Command(BaseCommand):
    """Load Wikipedia article data into wiki_new tables."""

    help = "Load Wikipedia article data into wiki_new tables"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--batches",
            type=int,
            default=10,
            help="Number of batches to load (default: 10)",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=100,
            help="Number of articles per batch (default: 100)",
        )
        parser.add_argument(
            "--append",
            action="store_true",
            help="Append to existing data",
        )
        parser.add_argument(
            "--model",
            type=str,
            choices=["minilm", "snowflake", "all"],
            default="all",
            help="Which model(s) to seed: minilm, snowflake, or all (default: all)",
        )

    def handle(self, *args, **options):
        """Django command entry point."""
        handle_seed(
            batches=options["batches"],
            batch_size=options["batch_size"],
            model_choice=options["model"],
            append=options["append"],
        )
