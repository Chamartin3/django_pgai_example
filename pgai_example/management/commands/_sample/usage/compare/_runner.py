"""Shared helpers for cross-vectorizer comparison commands."""

import statistics
import time

from pgai_example.management.context import ctx
from pgai_example.management.data_models import (
    CompareModelsData,
    CompareTimingData,
    CompareVariantColumn,
    CompareVariantHit,
    TimingRowData,
)


def collect_results(query: str, limit: int) -> CompareModelsData:
    """Run `find()` for every SampleModel variant and collect top-N hits."""
    columns: list[CompareVariantColumn] = []
    for sample_model in ctx.models.sample_model:
        model_class = sample_model.get_model_class()
        field_name = sample_model.field_name
        accessor = getattr(model_class.similar_in, field_name)
        results = accessor.find(query, limit=limit)
        hits: list[CompareVariantHit] = [
            CompareVariantHit(
                rank=i + 1,
                title=ctx.helpers.extract_title(r.instance),
                score=float(r.score),
            )
            for i, r in enumerate(results)
        ]
        columns.append(
            CompareVariantColumn(
                variant_key=sample_model.key,
                field=field_name,
                hits=hits,
            )
        )
    return CompareModelsData(query=query, limit=limit, columns=columns)


def collect_timings(query: str, runs: int, limit: int) -> CompareTimingData:
    """Benchmark `find()` latency for every SampleModel variant."""
    rows: list[TimingRowData] = []
    for sample_model in ctx.models.sample_model:
        model_class = sample_model.get_model_class()
        field_name = sample_model.field_name
        accessor = getattr(model_class.similar_in, field_name)

        # Warm-up so first-call costs don't dominate.
        accessor.find(query, limit=limit)

        samples_ms: list[float] = []
        for _ in range(runs):
            t0 = time.perf_counter()
            accessor.find(query, limit=limit)
            samples_ms.append((time.perf_counter() - t0) * 1000.0)

        samples_ms.sort()
        rows.append(
            TimingRowData(
                variant_key=sample_model.key,
                field=field_name,
                runs=runs,
                mean_ms=statistics.fmean(samples_ms),
                p50_ms=samples_ms[len(samples_ms) // 2],
                p95_ms=samples_ms[min(len(samples_ms) - 1, int(len(samples_ms) * 0.95))],
                min_ms=samples_ms[0],
                max_ms=samples_ms[-1],
            )
        )
    return CompareTimingData(query=query, runs=runs, rows=rows)
