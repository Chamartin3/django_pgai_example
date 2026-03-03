"""Seed command - Load Wikipedia data into pgai_example models.

This command follows the Context Architecture pattern:
- Uses ctx.render for all rendering operations
- Uses ctx.helpers for helper functions
- Direct access to SampleModel and Dataset enums
"""
from argparse import ArgumentParser

from django.core.management.base import BaseCommand

from pgai_example.constants import SampleModel
from pgai_example.management.context import ctx
from pgai_example.management.data_models import SeedResultsData, SeedTableResult


def handle_existing_data(
    ctx,
    result: SeedTableResult,
    current_count: int,
    total: int,
    force: bool,
) -> bool:
    """Handle scenario when table already has data.

    Args:
        ctx: Context object
        result: Result object to update if skip/error occurs
        current_count: Current registry count
        total: New total to load
        force: Whether to force replace without prompting

    Returns:
        bool: True if table should be skipped, False to continue loading
    """
    if force:
        # Force replace mode - clear without prompting
        ctx.console.print(
            f"[yellow]Table '{result.table_name}' already has {current_count} registries. "
            f"Replacing with --force flag...[/yellow]"
        )
        if not ctx.helpers.clear_table(result.table_name):
            result.error = "Failed to clear existing data"
            return True
        ctx.console.print(f"[green]✓ Cleared {current_count} registries[/green]")
        return False  # Continue with loading

    # Interactive mode - prompt user via renderer
    option = ctx.render.prompt_seed_options.option
    response = ctx.render.prompt_seed_options.prompt_action(
        variant_key=result.variant_key,
        existing_count=current_count,
        new_total=total,
    )

    if response == option.REPLACE:
        # Clear the table
        if not ctx.helpers.clear_table(result.table_name):
            result.error = "Failed to clear existing data"
            return True
        ctx.render.prompt_seed_options.display_cleared(current_count)
        return False  # Continue with loading

    elif response == option.APPEND:
        ctx.render.prompt_seed_options.display_appending()
        return False  # Continue with loading (append mode)

    else:  # option.SKIP
        ctx.render.prompt_seed_options.display_skipping()
        result.total_loaded = current_count
        result.message = "Skipped"
        return True


def process_sample_model(
    ctx,
    sample_model: SampleModel,
    total: int,
    batch_size: int,
    batches: int,
    append: bool,
    force: bool,
) -> SeedTableResult:
    """Process a single sample model for seeding.

    Args:
        ctx: Context object
        sample_model: Sample model enum instance
        total: Total registries to load
        batch_size: Registries per batch
        batches: Number of batches
        append: Whether to append to existing data
        force: Whether to force replace without prompting

    Returns:
        SeedTableResult: Result with operation outcome and is_skipped flag
    """
    table_name = sample_model.table_name
    dataset = sample_model.dataset
    current_count = ctx.helpers.get_table_row_count(table_name)

    # Create result with common fields
    result = SeedTableResult(
        variant_key=sample_model.key,
        table_name=table_name,
        success=False,
        total_loaded=0,
        existing_count=current_count,
    )

    # Check if table exists
    if not ctx.helpers.check_table_exists(table_name):
        result.error = "Table doesn't exist."
        return result

    # Check if table already has data
    if current_count > 0 and not append:
        should_skip = handle_existing_data(
            ctx=ctx,
            result=result,
            current_count=current_count,
            total=total,
            force=force,
        )
        if should_skip:
            result.is_skipped = True
            return result

    # Load dataset into table
    success, total_loaded, error = ctx.helpers.load_dataset_into_table(
        table_name=table_name,
        dataset_name=dataset.huggingface_name,
        dataset_config=dataset.config,
        field_types=dataset.field_types,
        batches=batches,
        batch_size=batch_size,
    )

    # Update result with loading outcome
    result.success = success
    result.total_loaded = total_loaded
    result.error = error
    result.message = "Added" if success else None

    return result


@ctx.handler
def handle_seed(
    ctx,  # Context injected by decorator
    total: int,
    batch_size: int,
    variant: str,
    append: bool = False,
    force: bool = False,
    **kwargs,
) -> None:
    """Load Wikipedia data into model tables.

    Args:
        total: Total number of registries to load
        batch_size: Number of articles per batch
        variant: Which model variant to seed (from SampleModel keys or 'all')
        append: Whether to append to existing data
        force: Replace existing data without prompting
        **kwargs: Additional arguments (captures verbose from decorator)
    """
    # Calculate number of batches from total and batch_size
    batches = (total + batch_size - 1) // batch_size  # Ceiling division

    # Determine which models to load
    if variant == "all":
        models_to_load = list(SampleModel)
    else:
        # Find matching SampleModel by key
        models_to_load = [m for m in SampleModel if m.key == variant]
        if not models_to_load:
            available = ", ".join(SampleModel.all_keys())
            ctx.render.message.error(
                f"Unknown variant: '{variant}'\n\nAvailable variants: {available}"
            )
            return

    table_results: list[SeedTableResult] = []
    success_count = 0
    skipped_count = 0

    # Load each model's table
    for sample_model in models_to_load:
        result = process_sample_model(
            ctx=ctx,
            sample_model=sample_model,
            total=total,
            batch_size=batch_size,
            batches=batches,
            append=append,
            force=force,
        )

        table_results.append(result)

        if result.is_skipped:
            skipped_count += 1
        elif result.success:
            success_count += 1

    # Prepare data and render
    data = SeedResultsData(
        tables=table_results,
        total=total,
        batch_size=batch_size,
        batches=batches,
        variant=variant,
        success_count=success_count,
        failed_count=len(models_to_load) - success_count - skipped_count,
        skipped_count=skipped_count,
    )
    ctx.render.seed.print(data)


class Command(BaseCommand):
    """Load Wikipedia article data into pgai_example tables."""

    help = "Load Wikipedia article data into pgai_example tables"

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command arguments."""
        parser.add_argument(
            "-t",
            "--total",
            type=int,
            default=1000,
            help="Total number of registries to load (default: 1000)",
        )
        parser.add_argument(
            "-b",
            "--batch-size",
            type=int,
            default=100,
            help="Number of articles per batch (default: 100). Batches will be calculated as ceil(total / batch_size)",
        )
        parser.add_argument(
            "-a",
            "--append",
            action="store_true",
            help="Append to existing data",
        )
        parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help="Replace existing data without prompting",
        )
        # Build choices from SampleModel keys
        model_keys = SampleModel.all_keys()
        choices = model_keys + ["all"]

        parser.add_argument(
            "--variant",
            type=str,
            choices=choices,
            default="all",
            help=f"Which variant to seed: {', '.join(model_keys)}, or all (default: all)",
        )

    def handle(self, *args, **options):
        """Django command entry point."""
        handle_seed(
            total=options["total"],
            batch_size=options["batch_size"],
            variant=options["variant"],
            append=options["append"],
            force=options["force"],
        )
