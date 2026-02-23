"""Search results renderer."""
from rich.console import Group, RenderableType
from rich.text import Text
from rich.table import Table
from wiki_new.management.data_models import SearchResultsData, SearchResultData
from wiki_new.management.renderers.base import CLIComponent


class SearchRenderer(CLIComponent[SearchResultsData, SearchResultsData]):
    """Renderer for search results."""
    component_name = 'Search Renderer'
    component_key = 'search'

    def render(self, data: SearchResultsData) -> RenderableType:
        """Create Rich renderable from search data."""
        results = data.get('results', [])
        query = data.get('query', '')
        model_name = data.get('model_name', '')

        table = Table(title=f"Search Results for '{query}' ({model_name})")
        table.add_column("ID", style="dim")
        table.add_column("Title")
        table.add_column("Score", justify="right")

        for result in results:
            table.add_row(
                str(result.get('pk', '')),
                str(result.get('title', '')),
                f"{result.get('score', 0):.4f}"
            )

        return table

    def render_search_results(
        self,
        results: list[SearchResultData],
        query: str,
        model_name: str,
        field: str,
        threshold: float | None,
        rank_by: str,
    ) -> None:
        """Render search results."""
        data: SearchResultsData = {
            'results': results,
            'query': query,
            'model_name': model_name,
            'field': field,
            'threshold': threshold,
            'rank_by': rank_by,
            'total_count': len(results),
        }
        self.print(data)
