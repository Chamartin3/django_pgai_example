"""Helper functions for seed operations."""
import json
from django.db import connection


def check_table_exists(table_name: str) -> bool:
    """Check if a table exists in the database.

    Args:
        table_name: Name of the table to check

    Returns:
        bool: True if table exists, False otherwise
    """
    with connection.cursor() as cur:
        cur.execute(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = %s
            );
            """,
            [table_name],
        )
        return cur.fetchone()[0]


def get_table_row_count(table_name: str) -> int:
    """Get the number of rows in a table.

    Args:
        table_name: Name of the table to check

    Returns:
        int: Number of rows in the table, 0 if table doesn't exist
    """
    try:
        with connection.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            return cur.fetchone()[0]
    except Exception:
        return 0


def clear_table(table_name: str) -> bool:
    """Clear all data from a table.

    Args:
        table_name: Name of the table to clear

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with connection.cursor() as cur:
            cur.execute(f"TRUNCATE TABLE {table_name} CASCADE")
        connection.commit()
        return True
    except Exception as e:
        print(f"Error clearing table {table_name}: {e}")
        return False


def load_dataset_into_table(
    table_name: str,
    dataset_name: str,
    dataset_config: str,
    field_types: dict[str, str],
    batches: int,
    batch_size: int,
) -> tuple[bool, int, str | None]:
    """Load dataset into a PostgreSQL table using pgai.load_dataset.

    Args:
        table_name: Target table name
        dataset_name: HuggingFace dataset identifier
        dataset_config: Dataset configuration/version
        field_types: Field type mappings
        batches: Number of batches to load
        batch_size: Number of records per batch

    Returns:
        tuple: (success: bool, total_loaded: int, error: str | None)
    """
    statement = """
        SELECT ai.load_dataset(
            %s, %s,
            table_name=>%s,
            if_table_exists=>'append',
            field_types=>%s::jsonb,
            batch_size=>%s,
            max_batches=>%s
        );
    """

    try:
        with connection.cursor() as cur:
            cur.execute(
                statement,
                [
                    dataset_name,
                    dataset_config,
                    table_name,
                    json.dumps(field_types),
                    batch_size,
                    batches,
                ],
            )
        connection.commit()
        total_loaded = batches * batch_size
        return (True, total_loaded, None)
    except Exception as e:
        return (False, 0, str(e))
