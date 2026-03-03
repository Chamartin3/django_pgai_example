"""List renderer for model listings."""
from rich.console import Group, RenderableType
from rich.text import Text
from rich.table import Table
from pgai_example.management.data_models import ModelListData
from pgai_example.management.renderers.base import CLIComponent


class ListRenderer(CLIComponent[ModelListData, ModelListData]):
    """Renderer for model list display."""
    component_name = 'List Renderer'
    component_key = 'list'

    def render(self, data: ModelListData) -> RenderableType:
        """Create Rich renderable from list data."""
        models = data.get('models', [])

        table = Table(title="Available Models")
        table.add_column("Key", style="cyan")
        table.add_column("Model")
        table.add_column("Embedding")
        table.add_column("Dimensions", justify="right")
        table.add_column("Status")

        for model in models:
            table.add_row(
                str(model.get('model_key', '')),
                str(model.get('class_name', '')),
                str(model.get('embedding_model', '')),
                str(model.get('dimensions', '')),
                str(model.get('vectorization_state', '')),
            )

        return table

    def render_models_list(self, data: ModelListData, verbose: bool = False) -> None:
        """Render models list."""
        self.print(data)
