"""Compare time - latency benchmark across vectorizer variants."""

from typer import Argument, Option

from pgai_example.management.context import ctx
from pgai_example.management.commands._sample.usage.compare._runner import (
    collect_timings,
)


def handle_time(query: str, runs: int, limit: int) -> None:
    try:
        data = collect_timings(query=query, runs=runs, limit=limit)
        ctx.render.compare_timing.print(data)
    except Exception as e:
        ctx.render.message.error(f"Compare time failed: {e}")


class CompareTimeCommand:
    """Typer adapter for `compare models time`."""

    @staticmethod
    def time(
        query: str = Argument(..., help="Search query"),
        runs: int = Option(5, "--runs", "-n", help="Timed runs per variant (warm)"),
        limit: int = Option(10, "--limit", "-l", help="Top-N per call"),
    ):
        """Benchmark `.find()` latency per variant (warm runs, mean/p50/p95)."""
        handle_time(query=query, runs=runs, limit=limit)


timeCommand = CompareTimeCommand()
