# pgai_example/management/renderers - CLI Rendering Components

This directory contains CLI rendering components following the **CLIComponent Pattern** - pure presentation logic with strict separation from business operations.

---

## Core Architecture Rules

### Rule 1: Components Only Parse and Render

CLIComponents have **ONE responsibility**: transform data into terminal output.

**Allowed operations:**
- Parse input data into render-ready format
- Create Rich renderables (Table, Panel, Text, etc.)
- Output to console

**FORBIDDEN operations:**
- Query databases
- Make network requests
- Read/write files
- Import Django models
- Call business logic functions
- Modify application state

### Rule 2: Registry-Only Access

Components are **NEVER** instantiated directly. Always access via the registry:

```python
# CORRECT - Via context registry
ctx.render.search.print(data)
ctx.render.message.print(warning_data)

# CORRECT - Via RendererRegistry
from pgai_example.management.renderers import RendererRegistry
registry = RendererRegistry()
registry.search.print(data)

# WRONG - Direct instantiation
from pgai_example.management.renderers.components.search import SearchRenderer
renderer = SearchRenderer()  # NEVER DO THIS
```

### Rule 3: Typed Data Contracts (No Generic Types)

All input/output types must be **TypedDict** - never generic `dict`:

```python
# WRONG - Generic dict type
class BadComponent(CLIComponent[dict, dict]):
    def render(self, data: dict) -> RenderableType:
        ...

# CORRECT - Specific TypedDict types
class SearchRenderer(CLIComponent[SearchResultsData, SearchResultsData]):
    def render(self, data: SearchResultsData) -> RenderableType:
        ...
```

### Rule 4: No Magic Strings

Use **enums** from `data_models.py` instead of literal strings:

```python
# WRONG - Magic string
if msg_type == 'incomplete':
    ...

# CORRECT - Enum value
from pgai_example.management.data_models import MessageType

if msg_type == MessageType.INCOMPLETE:
    ...
```

### Rule 5: TypedDicts in data_models.py

All TypedDict definitions must be **centralized** in `data_models.py`:

```python
# WRONG - Local TypedDict definition
class SearchRenderer(CLIComponent):
    class LocalData(TypedDict):  # NEVER define here
        results: list
        query: str

# CORRECT - Import from data_models
from pgai_example.management.data_models import SearchResultsData

class SearchRenderer(CLIComponent[SearchResultsData, SearchResultsData]):
    ...
```

---

## CLIComponent Architecture

### Class Structure

```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from rich.console import Console, RenderableType

TInput = TypeVar('TInput')
TParsed = TypeVar('TParsed')

class CLIComponent(ABC, Generic[TInput, TParsed]):
    """Abstract base class for CLI rendering components."""

    # Component metadata (REQUIRED for registry)
    component_name: str = ''  # Display name: "Search Renderer"
    component_key: str = ''   # Registry key: "search"

    def __init__(self, console: Console | None = None, **kwargs):
        self.console = console or Console(color_system='256')
        self._config = kwargs

    def _parse(self, data: TInput) -> TParsed:
        """PRIVATE - Transform input to render-ready format."""
        return data  # Default: no transformation

    @abstractmethod
    def render(self, data: TParsed) -> RenderableType:
        """Create Rich renderable from parsed data."""
        pass

    def print(self, data: TInput) -> None:
        """PUBLIC - Main entry point."""
        parsed = self._parse(data)
        rendered = self.render(parsed)
        self.console.print(rendered)
```

### Call Flow

```
External Code (Commands)
        │
        │ calls print(data: TInput)
        ▼
┌───────────────────────────────────────────┐
│              print(data)                  │  PUBLIC entry point
│  1. parsed = self._parse(data)            │
│  2. rendered = self.render(parsed)        │
│  3. self.console.print(rendered)          │
└───────────────────────────────────────────┘
        │                    │
        ▼                    ▼
┌─────────────────┐  ┌─────────────────────┐
│   _parse(data)  │  │  render(parsed)     │
│                 │  │                     │
│ TInput → TParsed│  │ TParsed → Renderable│
│ (PRIVATE)       │  │ (ABSTRACT)          │
└─────────────────┘  └─────────────────────┘
```

### Type Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `TInput` | Raw input data type received by `print()` | `SearchResultsData` |
| `TParsed` | Prepared data type passed to `render()` | `SearchResultsData` |

When `TInput == TParsed`, the default `_parse()` returns data unchanged.

---

## Component Metadata

Every component must define two metadata attributes:

```python
class SearchRenderer(CLIComponent[SearchResultsData, SearchResultsData]):
    component_name = 'Search Renderer'  # Human-readable name
    component_key = 'search'            # Registry access key
```

| Attribute | Purpose | Example |
|-----------|---------|---------|
| `component_name` | Display name for debugging/logs | `'Search Renderer'` |
| `component_key` | Registry access key (unique) | `'search'` |

The registry validates that all `component_key` values are unique.

---

## Registry System

### SampleRendererRegistry (Enum)

Maps enum entries to component classes with lazy loading:

```python
class SampleRendererRegistry(Enum):
    SEARCH = 'search.SearchRenderer'
    MESSAGE = 'message.MessageRenderer'
    LIST = 'list.ListRenderer'
    # ...

    @property
    def cls(self):
        """Lazy-load component class."""
        if self._cls is None:
            mod = importlib.import_module(
                f'.components.{self._module}',
                package='pgai_example.management.renderers'
            )
            self._cls = getattr(mod, self._class_name)
        return self._cls
```

### RendererRegistry (Dynamic Access)

Provides attribute-based access to cached component instances:

```python
class RendererRegistry:
    console = Console(color_system='256')  # Shared console

    def __getattr__(self, name: str):
        """Get renderer by component_key."""
        all_renderers = SampleRendererRegistry.all()
        if name not in all_renderers:
            raise AttributeError(f"Unknown renderer key '{name}'")
        if name not in self._cache:
            self._cache[name] = all_renderers[name](self.console)
        return self._cache[name]
```

### Usage

```python
# In commands via context
ctx.render.search.print(search_data)
ctx.render.message.print(warning_data)
ctx.render.list.print(model_list_data)

# Direct registry access
from pgai_example.management.renderers import RendererRegistry
registry = RendererRegistry()
registry.search.print(search_data)

# Get all available keys
from pgai_example.management.renderers import SampleRendererRegistry
all_keys = SampleRendererRegistry.all().keys()
# {'search', 'message', 'list', 'info', 'compare', ...}
```

---

## Creating New Components

### Step 1: Define TypedDict in data_models.py

```python
# pgai_example/management/data_models.py

class MyFeatureInput(TypedDict):
    """Input data for MyFeature renderer."""
    items: list[ItemData]
    title: str
    show_details: bool
```

### Step 2: Create Component File

```python
# pgai_example/management/renderers/components/my_feature.py

"""My feature renderer."""
from rich.console import RenderableType
from rich.table import Table
from pgai_example.management.data_models import MyFeatureInput
from pgai_example.management.renderers.base import CLIComponent


class MyFeatureRenderer(CLIComponent[MyFeatureInput, MyFeatureInput]):
    """Renderer for my feature display."""
    component_name = 'My Feature Renderer'
    component_key = 'my_feature'

    def render(self, data: MyFeatureInput) -> RenderableType:
        """Create Rich table from feature data."""
        items = data.get('items', [])
        title = data.get('title', '')

        table = Table(title=title)
        table.add_column("ID", style="dim")
        table.add_column("Name")

        for item in items:
            table.add_row(
                str(item.get('id', '')),
                str(item.get('name', '')),
            )

        return table
```

### Step 3: Register Component

```python
# pgai_example/management/renderers/registry.py

class SampleRendererRegistry(Enum):
    # ... existing entries ...
    MY_FEATURE = 'my_feature.MyFeatureRenderer'  # ADD THIS
```

### Step 4: Use in Commands

```python
# In command handler
data: MyFeatureInput = {
    'items': items,
    'title': 'My Feature Results',
    'show_details': True,
}
ctx.render.my_feature.print(data)
```

---

## Available Components

| Key | Class | Purpose |
|-----|-------|---------|
| `search` | `SearchRenderer` | Search results table |
| `eval` | `EvalRenderer` | Evaluation results |
| `list` | `ListRenderer` | Model list table |
| `message` | `MessageRenderer` | Errors, warnings, info, status |
| `seed` | `SeedRenderer` | Seed data loading progress |

---

## TypedDict Types Reference

Import from `pgai_example.management.data_models`:

### Input Types (for TInput)

| TypedDict | Used By | Description |
|-----------|---------|-------------|
| `SearchResultsData` | SearchRenderer | Search results with metadata |
| `ModelListData` | ListRenderer | Model list |
| `WarningMessageType` | MessageRenderer | Warning/error messages |
| `dict` | EvalRenderer, SeedRenderer | Generic evaluation and seed data |

### Enum Types

| Enum | Values | Usage |
|------|--------|-------|
| `MessageType` | `INCOMPLETE`, `NO_RESULTS`, `SUMMARY`, `ERROR`, `WARNING`, `SUCCESS`, `INFO` | Message type selection |
| `VectorizationStatus` | `NO_VECTORIZER`, `COMPLETE`, `PROCESSING`, `ERROR` | Status indicator |
| `VectorizationState` | `COMPLETE`, `PARTIAL`, `NONE` | Completion state |

---

## Directory Structure

```
renderers/
├── CLAUDE.md               # This file
├── __init__.py             # Exports RendererRegistry, SampleRendererRegistry
├── base.py                 # CLIComponent abstract base class
├── registry.py             # Registry definitions
└── components/
    ├── __init__.py
    ├── search.py           # SearchRenderer
    ├── eval.py             # EvalRenderer
    ├── list.py             # ListRenderer
    ├── message.py          # MessageRenderer
    └── seed.py             # SeedRenderer
```

---

## Styling Guidelines

### Colors

| Element | Style |
|---------|-------|
| Errors | `[bold red]` |
| Warnings | `[yellow]` |
| Success | `[green]` |
| Dim/secondary | `[dim]` |
| Emphasis | `[bold]` |
| Model names | `[cyan]` |
| Field names | `[magenta]` |

### Tables

```python
table = Table(
    title="Title",
    show_header=True,
    header_style="bold",
    border_style="dim",
)
```

### Panels

```python
Panel(content, title="Title", border_style="blue")
```

---

## Testing Components

Components are pure functions - easy to test:

```python
from io import StringIO
from rich.console import Console
from pgai_example.management.renderers.components.search import SearchRenderer
from pgai_example.management.data_models import SearchResultsData

def test_search_renderer():
    # Capture output
    output = StringIO()
    console = Console(file=output, force_terminal=True)

    renderer = SearchRenderer(console=console)

    data: SearchResultsData = {
        'results': [
            {'pk': 1, 'title': 'Test', 'score': 0.95, 'relevance': 0.9, 'match_count': 3},
        ],
        'query': 'test query',
        'model_name': 'TestModel',
        'field': 'text',
        'threshold': None,
        'rank_by': 'best',
        'total_count': 1,
    }

    renderer.print(data)

    result = output.getvalue()
    assert 'Test' in result
    assert '0.95' in result
```

---

## Common Mistakes

### Mistake 1: Business Logic in Render

```python
# WRONG
def render(self, data):
    model = Model.objects.get(pk=data['pk'])  # DATABASE QUERY!
    return Table(...)

# CORRECT
def render(self, data):
    # Data already fetched and passed in
    return Table(...)
```

### Mistake 2: Generic Dict Types

```python
# WRONG
class MyRenderer(CLIComponent[dict, dict]):
    ...

# CORRECT
class MyRenderer(CLIComponent[MyInputData, MyInputData]):
    ...
```

### Mistake 3: Magic Strings

```python
# WRONG
if data['type'] == 'incomplete':
    ...

# CORRECT
from pgai_example.management.data_models import MessageType
if data['type'] == MessageType.INCOMPLETE:
    ...
```

### Mistake 4: Direct Instantiation

```python
# WRONG
renderer = SearchRenderer()
renderer.print(data)

# CORRECT
ctx.render.search.print(data)
```

### Mistake 5: Local TypedDict

```python
# WRONG - In component file
class LocalData(TypedDict):
    items: list

# CORRECT - In data_models.py
# Then import: from pgai_example.management.data_models import LocalData
```
