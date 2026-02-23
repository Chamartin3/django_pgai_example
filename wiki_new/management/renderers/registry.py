"""Component registry for CLI renderers.

Usage:
    from wiki_new.management.renderers import RendererRegistry

    registry = RendererRegistry()
    registry.search.print(data)
    registry.message.error("Error message")
"""
import importlib
from enum import Enum
from rich.console import Console
from .base import CLIComponent


class SampleRendererRegistry(Enum):
    """Registry of available CLI rendering components.

    Enum values are string paths in format: "module.ClassName"
    """
    SEARCH = 'search.SearchRenderer'
    EVAL = 'eval.EvalRenderer'
    LIST = 'list.ListRenderer'
    MESSAGE = 'message.MessageRenderer'
    SEED = 'seed.SeedRenderer'

    def __init__(self, component_path: str):
        """Initialize registry entry with component path."""
        self._module, self._class_name = component_path.rsplit('.', 1)
        self._cls = None

    @property
    def cls(self):
        """Get the component class (lazy loaded)."""
        if self._cls is None:
            mod = importlib.import_module(
                f'.components.{self._module}',
                package='wiki_new.management.renderers'
            )
            self._cls = getattr(mod, self._class_name)
        if self._cls is None:
            raise RuntimeError(f'Failed to load component class {self._class_name}')
        return self._cls

    @property
    def display_name(self) -> str:
        """Get display name from component class metadata."""
        return self.cls.component_name

    @property
    def module(self) -> str:
        """Get module name."""
        return self._module

    @property
    def class_name(self) -> str:
        """Get class name."""
        return self._class_name

    def create(self, console: Console | None = None, **kwargs):
        """Create an instance of the component."""
        return self.cls(console=console, **kwargs)

    @classmethod
    def _validate_keys(cls) -> dict:
        """Validate that all component keys are unique."""
        seen_keys = {}
        for entry in cls:
            key = entry.cls.component_key
            if key in seen_keys:
                raise ValueError(
                    f"Duplicate component key '{key}' found in registry. "
                    f"Components {seen_keys[key]} and {entry.name} both use the same key."
                )
            seen_keys[key] = entry.name
        return seen_keys

    @classmethod
    def all(cls) -> dict:
        """Get all available renderers indexed by component key."""
        cls._validate_keys()
        renderers = {}
        for entry in cls:
            key = entry.cls.component_key
            renderers[key] = entry.cls
        return renderers


class RendererRegistry:
    """Dynamic renderer registry with attribute-based access.

    Usage:
        registry = RendererRegistry()
        registry.search.print(data)
        registry.message.error("Error")
    """
    console = Console(color_system='256')

    def __init__(self):
        """Initialize registry."""
        self._cache = {}

    def __getattr__(self, name: str):
        """Get renderer instance by component key (cached)."""
        if name.startswith('_'):
            raise AttributeError(f"No private attribute '{name}'")
        all_renderers = SampleRendererRegistry.all()
        if name not in all_renderers:
            available_keys = ', '.join(sorted(all_renderers.keys()))
            raise AttributeError(f"Unknown renderer key '{name}'. Available keys: {available_keys}")
        if name not in self._cache:
            renderer_class = all_renderers[name]
            self._cache[name] = renderer_class(self.console)
        return self._cache[name]

    def get_renderer(self, key: str, **kwargs):
        """Get a new renderer instance with optional configuration (not cached)."""
        all_renderers = SampleRendererRegistry.all()
        if key not in all_renderers:
            available_keys = ', '.join(sorted(all_renderers.keys()))
            raise KeyError(f"Unknown renderer key '{key}'. Available keys: {available_keys}")
        renderer_class = all_renderers[key]
        return renderer_class(self.console, **kwargs)


# Aliases for easier access
CLIComponentRegistry = SampleRendererRegistry
CLIRenderer = RendererRegistry
