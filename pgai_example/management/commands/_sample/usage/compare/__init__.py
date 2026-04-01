"""Cross-cutting comparison commands.

- `models/`     - same query across all vectorizer variants
- `strategies/` - same query across different strategies on one variant
- `demo`        - regenerates DEMONSTRATION.md from canonical query set
"""
from .demo import demo
from .models import resultsCommand, timeCommand

__all__ = ["demo", "resultsCommand", "timeCommand"]
