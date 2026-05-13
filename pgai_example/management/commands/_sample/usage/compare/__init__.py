"""Cross-cutting comparison commands.

- `models/`     - same query across all vectorizer variants
- `strategies/` - same query across different strategies on one variant
- `demo`        - canonical query set -> $BENCHMARKS_DIR/usage.{md,json}
- `cost`        - static cost benchmark -> $BENCHMARKS_DIR/cost.json
"""
from .cost import cost
from .demo import demo
from .models import resultsCommand, timeCommand

__all__ = ["cost", "demo", "resultsCommand", "timeCommand"]
