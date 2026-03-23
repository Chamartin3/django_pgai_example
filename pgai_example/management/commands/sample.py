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
        ├── search                  # Basic semantic search
        ├── filter                  # Search with filters
        └── eval                    # Evaluation commands
            ├── ranking             # Compare ranking strategies
            └── cutoff              # Compare cutoff values
"""

from django_typer.management import TyperCommand, command, group
from typer import Argument, Option

from pgai_example.management.commands._sample.models_command import (
    ModelsCommand,
)

from ._sample.usage import annotate as annotate_adapter
from ._sample.usage import filter as filter_adapter
from ._sample.usage import rank as rank_adapter
from ._sample.usage import search as search_adapter
from ._sample.usage import stats as stats_adapter
from ._sample.usage.eval import rankingCommand, cutoffCommand


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
        """Usage and evaluation commands."""
        pass

    @usage.command("search")
    def usage_search(
        self,
        query: str = Argument(..., help="Search query string"),
        variant: str = Option(
            "wk-minilm",
            "--variant",
            "-v",
            help="Vectorizer variant: wk-minilm, wk-snow, mv-qwen, mv-mxbai",
        ),
        threshold: float | None = Option(
            None, "--threshold", "-t", help="Similarity threshold (0.0-1.0)"
        ),
        rank_by: str = Option(
            "best", "--rank-by", "-r", help="Ranking: best, relevance, count"
        ),
        limit: int = Option(10, "--limit", "-l", help="Maximum results"),
    ):
        """
        Search for similar instances using the similar_in API.

        Performs semantic search on vectorized text fields and returns
        ranked results based on embedding similarity.

        Examples:
            ./manage.sh sample usage search "machine learning"
            ./manage.sh sample usage search "AI" --variant snowflake --threshold 0.8
            ./manage.sh sample usage search "Python" --limit 20 --rank-by relevance
        """
        return search_adapter.search(
            query=query,
            variant=variant,
            threshold=threshold,
            rank_by=rank_by,
            limit=limit,
        )

    @usage.command("filter")
    def usage_filter(
        self,
        query: str = Argument(..., help="Search query string"),
        variant: str = Option(
            "wk-minilm",
            "--variant",
            "-v",
            help="Vectorizer variant: wk-minilm, wk-snow, mv-qwen, mv-mxbai",
        ),
        threshold: float | None = Option(
            None, "--threshold", "-t", help="Similarity threshold (0.0-1.0)"
        ),
        rank_by: str = Option(
            "best", "--rank-by", "-r", help="Ranking: best, relevance, count"
        ),
        limit: int = Option(10, "--limit", "-l", help="Maximum results"),
    ):
        """
        Search with filters using the similar_in API.

        Performs semantic search with additional filtering capabilities
        on vectorized text fields.

        Examples:
            ./manage.sh sample usage filter "machine learning"
            ./manage.sh sample usage filter "AI" --variant snowflake --threshold 0.75
        """
        return filter_adapter.filter(
            query=query,
            variant=variant,
            threshold=threshold,
            rank_by=rank_by,
            limit=limit,
        )

    @usage.command("annotate")
    def usage_annotate(
        self,
        query: str = Argument(..., help="Search query string"),
        variant: str = Option(
            "wk-minilm",
            "--variant",
            "-v",
            help="Vectorizer variant: wk-minilm, wk-snow, mv-qwen, mv-mxbai",
        ),
        limit: int = Option(10, "--limit", "-l", help="Maximum results"),
    ):
        """
        Annotate queryset with semantic scores (demo of semantic_score expression).

        Examples:
            ./manage.sh sample usage annotate "machine learning"
            ./manage.sh sample usage annotate "AI" --variant wk-snow --limit 20
        """
        return annotate_adapter.annotate(
            query=query,
            variant=variant,
            limit=limit,
        )

    @usage.command("rank")
    def usage_rank(
        self,
        query: str = Argument(..., help="Search query string"),
        variant: str = Option(
            "wk-minilm",
            "--variant",
            "-v",
            help="Vectorizer variant: wk-minilm, wk-snow, mv-qwen, mv-mxbai",
        ),
        limit: int = Option(10, "--limit", "-l", help="Maximum results"),
    ):
        """
        Rank queryset using the semantic_rank manager method.

        Examples:
            ./manage.sh sample usage rank "machine learning"
            ./manage.sh sample usage rank "AI" --variant mv-qwen --limit 5
        """
        return rank_adapter.rank(
            query=query,
            variant=variant,
            limit=limit,
        )

    @usage.command("stats")
    def usage_stats(
        self,
        variant: str = Option(
            "all",
            "--variant",
            "-v",
            help="Vectorizer variant filter (or 'all')",
        ),
    ):
        """
        Show vectorization progress per model and field.

        Examples:
            ./manage.sh sample usage stats
            ./manage.sh sample usage stats --variant wk-minilm
        """
        return stats_adapter.stats(variant=variant)

    # === Eval Sub-group under Usage ===
    @usage.group()
    def eval(self):
        """Evaluation commands for ranking and cutoff values."""
        pass

    @eval.command("ranking")
    def usage_eval_ranking(
        self,
        query: str = Argument(..., help="Search query string"),
        variant: str = Option(
            "wk-minilm",
            "--variant",
            "-v",
            help="Vectorizer variant: wk-minilm, wk-snow, mv-qwen, mv-mxbai",
        ),
        timing: bool = Option(False, "--timing", help="Show timing information"),
        limit: int = Option(5, "--limit", "-l", help="Maximum results per test"),
    ):
        """
        Evaluate different ranking strategies.

        Tests how different ranking approaches (best, relevance, count)
        affect search results for the same query.

        Examples:
            ./manage.sh sample usage eval ranking "machine learning"
            ./manage.sh sample usage eval ranking "AI" --timing --limit 15
        """
        return rankingCommand.ranking(
            query=query,
            variant=variant,
            timing=timing,
            limit=limit,
        )

    @eval.command("cutoff")
    def usage_eval_cutoff(
        self,
        query: str = Argument(..., help="Search query string"),
        variant: str = Option(
            "wk-minilm",
            "--variant",
            "-v",
            help="Vectorizer variant: wk-minilm, wk-snow, mv-qwen, mv-mxbai",
        ),
        custom: str = Option(
            "", "--custom", "-c", help="Custom cutoff values (comma-separated)"
        ),
        timing: bool = Option(False, "--timing", help="Show timing information"),
        limit: int = Option(10, "--limit", "-l", help="Maximum results per test"),
    ):
        """
        Evaluate different similarity cutoff levels.

        Tests how different cutoff values affect search results and
        helps identify optimal cutoff levels for your use case.

        Examples:
            ./manage.sh sample usage eval cutoff "machine learning"
            ./manage.sh sample usage eval cutoff "AI" --custom 0.6,0.7,0.8 --timing
        """
        return cutoffCommand.cutoff(
            query=query,
            variant=variant,
            custom=custom,
            timing=timing,
            limit=limit,
        )
