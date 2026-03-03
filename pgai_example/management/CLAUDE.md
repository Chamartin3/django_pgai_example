# pgai_example/management - Management Command Architecture

This directory contains Django management commands for the pgai_example app, following the **Context Architecture** pattern for clean separation of concerns.

---

## Context Architecture Pattern

All commands use a centralized `ctx` object that provides access to shared functionality:

```python
from pgai_example.management.context import ctx

# Access renderers for display
ctx.render.search.render_search_results(...)
ctx.render.message.error("Error message")
ctx.render.list.render_models_list(data, verbose=True)

# Access helpers for business logic
model_class = ctx.helpers.get_model_from_string("minilm")
_, incomplete = ctx.helpers.check_vectorization_progress(model_class, "text")
title = ctx.helpers.extract_title(instance)

# Access exceptions for error handling
raise ctx.exceptions.ModelNotFoundError(f"Model '{model}' not found")
raise ctx.exceptions.MissingSimilarInError("Model has no similar_in manager")

# Access models/enums for constants
for sample_model in ctx.models.sample_model:
    state = ctx.models.vectorization_state.from_percentage(percentage)

# Access types for field introspection
if isinstance(field, ctx.types.vectorized_text_field):
    config = field.get_vectorizer_config()
```

### Context Components

| Component | Purpose | Example |
|-----------|---------|---------|
| `ctx.render` | Renderer registry | `ctx.render.search`, `ctx.render.message` |
| `ctx.helpers` | Business logic helpers | `get_model_from_string()`, `extract_title()` |
| `ctx.exceptions` | Custom exceptions | `ModelNotFoundError`, `MissingSimilarInError` |
| `ctx.models` | Model enums/constants | `sample_model`, `vectorization_state` |
| `ctx.types` | Type definitions | `vectorized_text_field`, `search_evaluation` |

---

## Command File Structure

Each command file follows a consistent three-layer pattern:

```python
"""Command description and architecture overview."""

from typer import Argument, Option
from pgai_example.management.context import ctx
from pgai_example.management.data_models import SomeDataClass


# === 1. Handler Function (Entry Point) ===
def handle_command(
    param1: str,
    param2: int = 10,
) -> None:
    """Entry point with error handling and rendering."""
    try:
        # Business logic
        data = prepare_command_data(param1=param1, param2=param2)

        # Display logic
        ctx.render.some_renderer.render(data)

    except ctx.exceptions.SomeError as e:
        ctx.render.message.error(str(e))


# === 2. Business Logic Function ===
def prepare_command_data(
    param1: str,
    param2: int,
) -> SomeDataClass:
    """
    Pure business logic - no rendering, no I/O.

    Returns:
        Typed data structure for rendering

    Raises:
        Appropriate ctx.exceptions on error
    """
    # Query models, transform data, validate
    model_class = ctx.helpers.get_model_from_string(param1)
    # ... business logic ...
    return SomeDataClass(results=results, total=len(results))


# === 3. Typer Adapter Class ===
class SomeCommand:
    """Typer adapter - thin wrapper for CLI integration."""

    @staticmethod
    def command_name(
        param1: str = Argument(..., help="Description"),
        param2: int = Option(10, "--param2", "-p", help="Description"),
    ):
        """Command docstring for --help output."""
        handle_command(param1=param1, param2=param2)


# === Module Export ===
someCommand = SomeCommand()
```

### Layer Responsibilities

| Layer | Responsibility | May Access |
|-------|---------------|------------|
| **Handler** | Error handling, orchestration | ctx.render, ctx.exceptions |
| **Business Logic** | Data preparation, queries | ctx.helpers, ctx.exceptions, ctx.models, ctx.types |
| **Adapter** | CLI argument parsing | Typer only |

---

## Import Rules

### ALWAYS Import

```python
from pgai_example.management.context import ctx
from pgai_example.management.data_models import <DataClass>
```

### NEVER Import Directly

```python
# WRONG - bypass context
from pgai_example.management.helpers.model_helpers import get_model_from_string
from pgai_example.management.renderers.search import SearchRenderer

# RIGHT - use context
ctx.helpers.get_model_from_string(...)
ctx.render.search.render_search_results(...)
```

### Typer Imports (Adapter Only)

```python
from typer import Argument, Option
```

---

## Directory Structure

```
management/
├── CLAUDE.md               # This file
├── __init__.py
├── context.py              # Context object (ctx) definition
├── data_models.py          # TypedDict data structures
├── helpers/                # Business logic helpers
│   ├── __init__.py
│   ├── model_helpers.py    # Model lookup, extraction
│   └── vectorization.py    # Vectorization status checks
├── renderers/              # CLI output components
│   ├── CLAUDE.md           # Renderer architecture docs
│   └── components/         # Individual render components
└── commands/
    ├── sample.py           # Main command entry point
    └── _sample/            # Subcommand modules
        ├── models_command.py
        └── test/
            ├── search.py
            ├── filter.py
            └── eval/
                ├── ranking.py
                └── cutoff.py
```

---

## Data Flow

```
User Input (CLI)
      │
      ▼
┌─────────────────┐
│  Typer Adapter  │  Parse arguments, delegate to handler
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Handler      │  Orchestrate, handle errors
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Business Logic  │  Query models, transform data
└────────┬────────┘
         │
         ▼
   TypedDict Data
         │
         ▼
┌─────────────────┐
│    Renderer     │  Format and display output
└─────────────────┘
         │
         ▼
   Terminal Output
```

---

## Error Handling

Always use context exceptions and render errors via message renderer:

```python
try:
    data = prepare_data(...)
    ctx.render.component.render(data)
except ctx.exceptions.ModelNotFoundError:
    ctx.render.message.error(f"Model '{model}' not found")
except ctx.exceptions.MissingSimilarInError as e:
    ctx.render.message.error(str(e))
except Exception as e:
    ctx.render.message.error(f"Operation failed: {e}")
```

---

## Adding New Commands

1. Create command file in `commands/_sample/` following the three-layer pattern
2. Define TypedDict data structures in `data_models.py` if needed
3. Add renderer methods to appropriate component in `renderers/components/`
4. Wire up in main command file (`sample.py`)
5. Update this CLAUDE.md if introducing new patterns
