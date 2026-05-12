"""Demo command - regenerates USAGE.md at the repo root.

Runs a curated query set across all vectorizer variants and writes a
markdown report that ships with the repo. Re-run after data changes.
"""

from datetime import datetime, timezone
from pathlib import Path

from typer import Option

from pgai_example.management.context import ctx
from pgai_example.management.commands._sample.usage.compare._runner import (
    collect_results,
    collect_timings,
)

CANONICAL_QUERIES = [
    "cooking mice",
    "samurai revenge",
    "hacker breaks into the pentagon",
    "existential dread",
]

OUTPUT_PATH = Path("USAGE.md")


def _md_results_table(data) -> str:
    """Render `CompareModelsData` as a side-by-side markdown table."""
    cols = data["columns"]
    if not cols:
        return "_(no results)_\n"
    headers = ["#"] + [f"{c['variant_key']}<br/>`{c['field']}`" for c in cols]
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("|" + "|".join(["---"] * len(headers)) + "|")
    max_rows = max(len(c["hits"]) for c in cols)
    for i in range(max_rows):
        row = [str(i + 1)]
        for c in cols:
            if i < len(c["hits"]):
                h = c["hits"][i]
                row.append(f"{h['title']} *(`{h['score']:.3f}`)*")
            else:
                row.append("—")
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines) + "\n"


def _md_timing_table(data) -> str:
    rows = data["rows"]
    if not rows:
        return "_(no timings)_\n"
    lines = [
        "| Variant | Field | mean | p50 | p95 | min | max |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        lines.append(
            f"| `{r['variant_key']}` | `{r['field']}` | "
            f"{r['mean_ms']:.1f}ms | {r['p50_ms']:.1f}ms | "
            f"{r['p95_ms']:.1f}ms | {r['min_ms']:.1f}ms | {r['max_ms']:.1f}ms |"
        )
    return "\n".join(lines) + "\n"


def _agreement_note(data) -> str:
    """Identify variants that agree on the top hit."""
    cols = data["columns"]
    tops = {c["variant_key"]: (c["hits"][0]["title"] if c["hits"] else None) for c in cols}
    by_title: dict[str, list[str]] = {}
    for variant_key, title in tops.items():
        if title is None:
            continue
        by_title.setdefault(title, []).append(variant_key)
    biggest = max(by_title.items(), key=lambda kv: len(kv[1]), default=(None, []))
    if biggest[0] is None:
        return "No variant returned results."
    if len(biggest[1]) == len(cols):
        return f"**All variants agree** on top hit: _{biggest[0]}_."
    if len(biggest[1]) >= 2:
        rest = [v for v in tops if v not in biggest[1]]
        return (
            f"**Partial agreement:** {', '.join(f'`{v}`' for v in biggest[1])} "
            f"agree on _{biggest[0]}_; {', '.join(f'`{v}`' for v in rest)} differ."
        )
    return "**Each variant returned a different top hit** — query is on a semantic edge."


def _mermaid_latency_chart(timing) -> str:
    """Bar chart of mean latency per variant for one query."""
    rows = timing["rows"]
    if not rows:
        return ""
    variants = [f'"{r["variant_key"]}"' for r in rows]
    means = [f"{r['mean_ms']:.1f}" for r in rows]
    return (
        "```mermaid\n"
        "xychart-beta\n"
        f'    title "Mean latency per variant (ms) — \\"{timing["query"]}\\""\n'
        f"    x-axis [{', '.join(variants)}]\n"
        '    y-axis "ms"\n'
        f"    bar [{', '.join(means)}]\n"
        "```\n"
    )


def _mermaid_score_chart(results) -> str:
    """Bar chart of top-1 similarity score per variant for one query."""
    cols = results["columns"]
    if not cols:
        return ""
    variants = [f'"{c["variant_key"]}"' for c in cols]
    top_scores = [
        f"{c['hits'][0]['score']:.3f}" if c["hits"] else "0"
        for c in cols
    ]
    return (
        "```mermaid\n"
        "xychart-beta\n"
        f'    title "Top-1 similarity score per variant — \\"{results["query"]}\\""\n'
        f"    x-axis [{', '.join(variants)}]\n"
        '    y-axis "score" 0 --> 1\n'
        f"    bar [{', '.join(top_scores)}]\n"
        "```\n"
    )


def _mermaid_aggregate_latency(timings_per_query: dict[str, dict]) -> str:
    """Bar chart of overall mean latency per variant (averaged across all queries)."""
    if not timings_per_query:
        return ""
    by_variant: dict[str, list[float]] = {}
    for timing in timings_per_query.values():
        for row in timing["rows"]:
            by_variant.setdefault(row["variant_key"], []).append(row["mean_ms"])
    if not by_variant:
        return ""
    variants = list(by_variant.keys())
    means = [sum(v) / len(v) for v in by_variant.values()]
    return (
        "```mermaid\n"
        "xychart-beta\n"
        '    title "Overall mean latency across all queries (ms)"\n'
        f"    x-axis [{', '.join(f'\"{v}\"' for v in variants)}]\n"
        '    y-axis "ms"\n'
        f"    bar [{', '.join(f'{m:.1f}' for m in means)}]\n"
        "```\n"
    )


def _fastest(timing) -> str:
    rows = timing["rows"]
    if not rows:
        return ""
    fastest = min(rows, key=lambda r: r["mean_ms"])
    slowest = max(rows, key=lambda r: r["mean_ms"])
    ratio = slowest["mean_ms"] / fastest["mean_ms"] if fastest["mean_ms"] > 0 else 0
    return (
        f"Fastest: `{fastest['variant_key']}` "
        f"({fastest['mean_ms']:.1f}ms mean). Slowest: `{slowest['variant_key']}` "
        f"({slowest['mean_ms']:.1f}ms, {ratio:.1f}× slower)."
    )


def generate(queries: list[str], limit: int, runs: int) -> str:
    """Build the full USAGE.md content."""
    parts: list[str] = []
    parts.append("# USAGE.md\n")
    parts.append(
        "_Auto-generated by `./manage.sh sample usage compare demo`. "
        "Shows how different vectorizers respond to the same query._\n"
    )
    parts.append(
        f"Generated: `{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}`\n"
    )
    parts.append("## Setup\n")
    parts.append(
        "- Dataset: `Cohere/movies` (1,000 rows)\n"
        "- Model: `Movie` with four vectorizers over the same `overview` column:\n"
        "  - `mv-qwen` — `qwen3-embedding` (4096d)\n"
        "  - `mv-mxbai` — `mxbai-embed-large` (1024d)\n"
        "  - `mv-minilm` — `all-MiniLM-L6-v2` (384d)\n"
        "  - `mv-snowflake` — `snowflake-arctic-embed` (1024d)\n"
        "- API used: `Model.similar_in.<field>.find(query, limit=N)`\n"
    )

    timings_per_query: dict[str, dict] = {}
    for query in queries:
        results_data = collect_results(query=query, limit=limit)
        timing_data = collect_timings(query=query, runs=runs, limit=limit)
        timings_per_query[query] = timing_data

        parts.append(f"## Query: _\"{query}\"_\n")
        parts.append("### Top hits per variant\n")
        parts.append(_md_results_table(results_data))
        parts.append("\n### Top-1 similarity score\n")
        parts.append(_mermaid_score_chart(results_data))
        parts.append("\n### Latency\n")
        parts.append(_md_timing_table(timing_data))
        parts.append("\n")
        parts.append(_mermaid_latency_chart(timing_data))
        parts.append("\n### Takeaway\n")
        parts.append("- " + _agreement_note(results_data) + "\n")
        parts.append("- " + _fastest(timing_data) + "\n")

    parts.append("## Overall performance\n")
    parts.append(_mermaid_aggregate_latency(timings_per_query))
    parts.append("\n## Recommendations\n")
    parts.append(
        "- **Pick by latency**: small queries (chat UI, autocomplete) → `mv-minilm`. "
        "Heavy ranking (offline batch) → `mv-qwen` for best semantic recall.\n"
        "- **Pick by agreement**: when 3+ variants agree on top hit, the result is "
        "robust; tune `--threshold` upward to suppress weak matches.\n"
        "- **Pick by spread**: when each variant returns different titles, the query "
        "is semantically ambiguous — consider rephrasing or using `rank-by relevance` "
        "to weight by per-hit match count.\n"
    )
    return "".join(parts)


def handle_demo(queries: list[str], limit: int, runs: int, output: Path) -> None:
    try:
        content = generate(queries=queries, limit=limit, runs=runs)
        output.write_text(content, encoding="utf-8")
        ctx.render.message.success(f"Wrote {output} ({len(content):,} bytes)")
    except Exception as e:
        ctx.render.message.error(f"Demo failed: {e}")


class DemoCommand:
    """Typer adapter for `compare demo`."""

    @staticmethod
    def demo(
        queries: str = Option(
            ",".join(CANONICAL_QUERIES),
            "--queries", "-q",
            help="Comma-separated list of queries",
        ),
        limit: int = Option(5, "--limit", "-l", help="Top-N hits per variant"),
        runs: int = Option(5, "--runs", "-n", help="Timed runs per variant"),
        output: Path = Option(
            OUTPUT_PATH, "--output", "-o", help="Output markdown path"
        ),
    ):
        """Run canonical queries across all variants; write USAGE.md."""
        query_list = [q.strip() for q in queries.split(",") if q.strip()]
        handle_demo(queries=query_list, limit=limit, runs=runs, output=output)


demo = DemoCommand()
