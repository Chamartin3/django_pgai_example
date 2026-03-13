"""Stats command - vectorization progress per model/field."""

from django.db import connection

from typer import Option

from pgai_example.management.context import ctx
from pgai_example.management.data_models import (
    StatsData,
    StatsRowData,
)


def handle_stats(
    variant: str,
) -> None:
    """Handle stats command."""
    try:
        data = prepare_stats_data(variant=variant)
        ctx.render.stats.print(data)

    except Exception as e:
        ctx.render.message.error(f"Stats failed: {e}")


def prepare_stats_data(variant: str) -> StatsData:
    """Prepare stats data (business logic)."""
    rows: list[StatsRowData] = []

    for sample_model in ctx.models.sample_model:
        try:
            model_class = sample_model.get_model_class()
            table_name = model_class._meta.db_table

            for field in model_class._meta.get_fields():
                if not isinstance(field, ctx.types.vectorized_text_field):
                    continue

                field_name = field.name
                total_rows = model_class.objects.count()
                embedding_table = f"{table_name}_{field_name}_embedding_store"
                embedded_rows = _count_distinct_embedded(embedding_table)
                percent = (embedded_rows / total_rows * 100.0) if total_rows > 0 else 0.0

                rows.append(
                    StatsRowData(
                        model_name=model_class.__name__,
                        field_name=field_name,
                        total_rows=total_rows,
                        embedded_rows=embedded_rows,
                        percent=percent,
                    )
                )
        except Exception:
            continue

    return StatsData(rows=rows, variant=variant)


def _count_distinct_embedded(embedding_table: str) -> int:
    """Count distinct source documents with at least one embedding chunk."""
    try:
        with connection.cursor() as cur:
            cur.execute(
                f"SELECT COUNT(DISTINCT source_pk) FROM {embedding_table}"
            )
            return cur.fetchone()[0]
    except Exception:
        return 0


class StatsCommand:
    """Stats command adapter for Typer."""

    @staticmethod
    def stats(
        variant: str = Option(
            "all",
            "--variant",
            "-v",
            help="Vectorizer variant filter (or 'all')",
        ),
    ):
        """Show vectorization progress per model and field."""
        handle_stats(variant=variant)


stats = StatsCommand()
