"""Cost benchmark - captures static cost metrics per vectorizer variant.

Measures per variant:
  - Embedding model name + dimensions + Ollama on-disk size
  - Embedding store target table + row count + total relation size on disk
  - Embed-only latency via direct Ollama /api/embeddings call

Emits JSON to the ``--output`` path for downstream documentation rendering.
"""

import json
import os
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from django.db import connection
from typer import Option

from pgai_example.management.context import ctx


OLLAMA_HOST = os.environ["OLLAMA_HOST"]


# Short, fixed probe text. Keeps embed-only timing comparable across runs.
PROBE_TEXT = (
    "A retired hitman seeks revenge against the gangsters who killed his dog "
    "and stole his car."
)


def _ollama_models() -> dict[str, dict]:
    """Return Ollama model metadata keyed by model name (and bare-name alias)."""
    r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=10)
    r.raise_for_status()
    out: dict[str, dict] = {}
    for m in r.json().get("models", []):
        out[m["name"]] = m
        bare = m["name"].split(":", 1)[0]
        out.setdefault(bare, m)
    return out


def _embed_timing(model: str, runs: int) -> dict:
    """Time direct Ollama /api/embeddings calls. One warm-up, then `runs` timed."""
    url = f"{OLLAMA_HOST}/api/embeddings"
    payload = {"model": model, "prompt": PROBE_TEXT}

    requests.post(url, json=payload, timeout=120).raise_for_status()

    samples_ms: list[float] = []
    for _ in range(runs):
        t0 = time.perf_counter()
        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()
        samples_ms.append((time.perf_counter() - t0) * 1000.0)
    samples_ms.sort()
    return {
        "runs": runs,
        "mean_ms": statistics.fmean(samples_ms),
        "p50_ms": samples_ms[len(samples_ms) // 2],
        "p95_ms": samples_ms[min(len(samples_ms) - 1, int(len(samples_ms) * 0.95))],
        "min_ms": samples_ms[0],
        "max_ms": samples_ms[-1],
    }


def _vectorizer_tables() -> dict[str, dict]:
    """Map vectorizer name -> {target_table, source_table, view}."""
    out: dict[str, dict] = {}
    with connection.cursor() as cur:
        cur.execute(
            "SELECT name, source_table, target_table, view FROM ai.vectorizer_status"
        )
        for name, source_table, target_table, view in cur.fetchall():
            out[name] = {
                "source_table": source_table,
                "target_table": target_table,
                "view": view,
            }
    return out


def _table_stats(qualified: str) -> dict:
    """Return rows + on-disk size (bytes) for ``schema.table``."""
    with connection.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) FROM {qualified}")
        rows = cur.fetchone()[0]
        cur.execute("SELECT pg_total_relation_size(%s)", [qualified])
        size_bytes = cur.fetchone()[0]
    return {"rows": rows, "size_bytes": int(size_bytes)}


def collect_cost(runs: int) -> dict:
    ollama_index = _ollama_models()
    vectorizers = _vectorizer_tables()
    variants: list[dict] = []

    for sm in ctx.models.sample_model:
        cfg = sm.value
        # vectorizer name follows convention movie_overview_{tag}
        # match via field_name → vectorizer name suffix
        suffix_map = {
            "overview": "movie_overview_qwen3",
            "overview_mxbai": "movie_overview_mxbai",
            "overview_minilm": "movie_overview_minilm",
            "overview_snowflake": "movie_overview_snowflake",
        }
        vec_name = suffix_map.get(cfg.field_name)
        vec_meta = vectorizers.get(vec_name, {})

        target_table = vec_meta.get("target_table")
        table_stats = _table_stats(target_table) if target_table else None

        ollama_meta = ollama_index.get(cfg.embedding_model) or ollama_index.get(
            cfg.embedding_model.split(":", 1)[0]
        ) or {}

        embed_timing = _embed_timing(cfg.embedding_model, runs=runs)

        variants.append({
            "key": cfg.key,
            "description": cfg.description,
            "field_name": cfg.field_name,
            "embedding_model": cfg.embedding_model,
            "embedding_dimensions": cfg.embedding_dimensions,
            "vectorizer_name": vec_name,
            "target_table": target_table,
            "ollama_model_size_bytes": int(ollama_meta.get("size", 0)),
            "ollama_model_digest": ollama_meta.get("digest"),
            "embedding_store": table_stats,
            "embed_timing_ms": embed_timing,
        })

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ollama_host": OLLAMA_HOST,
        "probe_text": PROBE_TEXT,
        "runs": runs,
        "variants": variants,
    }


def handle_cost(runs: int, output: Path) -> None:
    try:
        data = collect_cost(runs=runs)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(data, indent=2), encoding="utf-8")
        ctx.render.message.success(
            f"Wrote {output} ({len(data['variants'])} variants, {runs} embed runs each)"
        )
    except Exception as e:
        ctx.render.message.error(f"Cost benchmark failed: {e}")


class CostCommand:
    """Typer adapter for `usage compare cost`."""

    @staticmethod
    def cost(
        output: Path = Option(
            ..., "--output", "-o",
            help="Output JSON path for the cost report",
        ),
        runs: int = Option(5, "--runs", "-n", help="Embed-only timed runs per variant"),
    ):
        """Benchmark static costs (model size, index size, embed latency)."""
        handle_cost(runs=runs, output=output)


cost = CostCommand()
