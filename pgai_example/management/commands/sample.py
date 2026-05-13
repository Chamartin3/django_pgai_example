"""
Sample command demonstrating pgai_django plugin usage with pgai_example app.

This is an example implementation showing how to use the pgai_django plugin
in a real Django application. The command demonstrates:
- Building apps with VectorizableModel
- Standard Django migration workflow with pgai vectorizers
- Data seeding and cleanup operations
- Integration with pgai management commands

Note: This sample uses pgai_django plugin but the plugin has no knowledge
of this implementation - it's purely a consumer of the plugin's public API.

Command Structure:
    sample
    ├── models [--verbose]          # List available test models
    └── usage                       # Usage commands group
        ├── api                     # One plugin API per command (single variant)
        │   ├── find                # similar_in.<field>.find()
        │   ├── filter              # ORM .filter() + semantic_score()
        │   ├── annotate            # raw semantic_score() expression
        │   └── rank                # objects.semantic_rank() manager method
        └── compare                 # Cross-cutting comparisons
            └── strategies          # Same query, one variant, different knobs
                ├── rank-by         # Compare ranking strategies
                └── threshold       # Compare similarity thresholds
"""

from django_typer.management import TyperCommand, command, group
from typer import Argument, Option

from pgai_example.management.commands._sample.models_command import (
    ModelsCommand,
)

from pathlib import Path

from ._sample.usage import (
    annotate as annotate_adapter,
    cost as cost_adapter,
    demo as demo_adapter,
    filter as filter_adapter,
    find as find_adapter,
    rank as rank_adapter,
    rankByCommand,
    resultsCommand,
    thresholdCommand,
    timeCommand,
)


class Command(TyperCommand):
    help = "Sample commands demonstrating pgai_django usage with pgai_example app"

    # === Models Command ===
    @command()
    def models(
        self,
        verbose: bool = Option(
            False, "--verbose", "-v", help="Show detailed configuration"
        ),
    ):
        """
        List all available test models with their configurations.

        Shows each model variant with embedding details, dimensions, provider,
        chunking strategy, and vectorization status. Model keys are enhanced
        to include dimension information for easy identification.

        Model Keys:
            minilm    - all-MiniLM-L6-v2 (384d) - Fast, general purpose
            hybrid    - Combined MiniLM + Nomic (768d) - Multi-model ensemble
            nomic     - nomic-embed-text (768d) - High quality general
            mxbai     - mixedbread-ai/mxbai-embed-large-1 (1024d) - Best quality
            snowflake - snowflake-arctic-embed-m (768d) - Enterprise grade

        Examples:
            ./manage.sh sample models                        # Basic table view
            ./manage.sh sample models --verbose              # Detailed config
        """
        return ModelsCommand.list_models(verbose=verbose)

    # === Usage Group ===
    @group()
    def usage(self):
        """Usage examples and cross-cutting comparisons."""
        pass

    # --- api/ subgroup: one plugin API per command ---
    @usage.group()
    def api(self):
        """Single-API demos (one plugin entry point per command)."""
        pass

    @api.command("find")
    def usage_api_find(
        self,
        query: str = Argument(..., help="Search query string"),
        variant: str = Option(
            "mv-qwen", "--variant", "-v",
            help="Vectorizer variant: mv-qwen, mv-mxbai, mv-minilm, mv-snowflake",
        ),
        threshold: float | None = Option(
            None, "--threshold", "-t", help="Similarity threshold (0.0-1.0)"
        ),
        rank_by: str = Option(
            "best", "--rank-by", "-r", help="Ranking: best, relevance, count"
        ),
        limit: int = Option(10, "--limit", "-l", help="Maximum results"),
    ):
        """Find similar instances via `similar_in.<field>.find()`."""
        return find_adapter.find(
            query=query, variant=variant, threshold=threshold,
            rank_by=rank_by, limit=limit,
        )

    @api.command("filter")
    def usage_api_filter(
        self,
        query: str = Argument(..., help="Search query string"),
        variant: str = Option(
            "mv-qwen", "--variant", "-v",
            help="Vectorizer variant: mv-qwen, mv-mxbai, mv-minilm, mv-snowflake",
        ),
        genre: str = Option(
            "Action", "--genre", "-g",
            help="Filter by genre (icontains match on movie.genres)",
        ),
        limit: int = Option(10, "--limit", "-l", help="Maximum results"),
    ):
        """ORM `.filter()` + `semantic_score()` — structured filter + semantic rank."""
        return filter_adapter.filter(
            query=query, variant=variant, genre=genre, limit=limit,
        )

    @api.command("annotate")
    def usage_api_annotate(
        self,
        query: str = Argument(..., help="Search query string"),
        variant: str = Option(
            "mv-qwen", "--variant", "-v",
            help="Vectorizer variant: mv-qwen, mv-mxbai, mv-minilm, mv-snowflake",
        ),
        limit: int = Option(10, "--limit", "-l", help="Maximum results"),
    ):
        """Raw `semantic_score()` ORM expression on a plain queryset."""
        return annotate_adapter.annotate(
            query=query, variant=variant, limit=limit,
        )

    @api.command("rank")
    def usage_api_rank(
        self,
        query: str = Argument(..., help="Search query string"),
        variant: str = Option(
            "mv-qwen", "--variant", "-v",
            help="Vectorizer variant: mv-qwen, mv-mxbai, mv-minilm, mv-snowflake",
        ),
        limit: int = Option(10, "--limit", "-l", help="Maximum results"),
    ):
        """Manager method `objects.semantic_rank()` — chainable QuerySet."""
        return rank_adapter.rank(
            query=query, variant=variant, limit=limit,
        )

    # --- compare/ subgroup: cross-cutting comparisons ---
    @usage.group()
    def compare(self):
        """Cross-cutting comparison commands."""
        pass

    @compare.group()
    def models(self):
        """Same query, all vectorizer variants."""
        pass

    @models.command("results")
    def usage_compare_models_results(
        self,
        query: str = Argument(..., help="Search query"),
        limit: int = Option(5, "--limit", "-l", help="Top-N per variant"),
    ):
        """Side-by-side top-N across all variants."""
        return resultsCommand.results(query=query, limit=limit)

    @models.command("time")
    def usage_compare_models_time(
        self,
        query: str = Argument(..., help="Search query"),
        runs: int = Option(5, "--runs", "-n", help="Warm timed runs per variant"),
        limit: int = Option(10, "--limit", "-l", help="Top-N per call"),
    ):
        """Latency benchmark per variant (mean/p50/p95)."""
        return timeCommand.time(query=query, runs=runs, limit=limit)

    @compare.command("cost")
    def usage_compare_cost(
        self,
        output: Path = Option(
            ..., "--output", "-o",
            help="Output JSON path for the cost report",
        ),
        runs: int = Option(5, "--runs", "-n", help="Embed-only timed runs per variant"),
    ):
        """Static cost benchmark: model size, index size, embed latency."""
        return cost_adapter.cost(runs=runs, output=output)

    @compare.command("demo")
    def usage_compare_demo(
        self,
        output: Path = Option(
            ..., "--output", "-o",
            help="Output markdown path (a JSON sibling is also written)",
        ),
        queries: str = Option(
            "cooking mice,samurai revenge,hacker breaks into the pentagon,existential dread",
            "--queries", "-q", help="Comma-separated list of queries",
        ),
        limit: int = Option(5, "--limit", "-l", help="Top-N per variant"),
        runs: int = Option(5, "--runs", "-n", help="Timed runs per variant"),
    ):
        """Run canonical queries; write raw JSON + markdown report."""
        return demo_adapter.demo(
            queries=queries, limit=limit, runs=runs, output=output,
        )

    @compare.group()
    def strategies(self):
        """Same query, one variant, different strategies."""
        pass

    @strategies.command("rank-by")
    def usage_compare_strategies_rank_by(
        self,
        query: str = Argument(..., help="Search query string"),
        variant: str = Option(
            "mv-qwen", "--variant", "-v",
            help="Vectorizer variant: mv-qwen, mv-mxbai, mv-minilm, mv-snowflake",
        ),
        timing: bool = Option(False, "--timing", help="Show timing information"),
        limit: int = Option(5, "--limit", "-l", help="Maximum results per test"),
    ):
        """Compare ranking strategies (best/relevance/count) on one variant."""
        return rankByCommand.ranking(
            query=query, variant=variant, timing=timing, limit=limit,
        )

    @strategies.command("threshold")
    def usage_compare_strategies_threshold(
        self,
        query: str = Argument(..., help="Search query string"),
        variant: str = Option(
            "mv-qwen", "--variant", "-v",
            help="Vectorizer variant: mv-qwen, mv-mxbai, mv-minilm, mv-snowflake",
        ),
        custom: str = Option(
            "", "--custom", "-c", help="Custom threshold values (comma-separated)"
        ),
        timing: bool = Option(False, "--timing", help="Show timing information"),
        limit: int = Option(10, "--limit", "-l", help="Maximum results per test"),
    ):
        """Compare similarity thresholds on one variant."""
        return thresholdCommand.cutoff(
            query=query, variant=variant, custom=custom, timing=timing, limit=limit,
        )
