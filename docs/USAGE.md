# Usage Guide: Semantic Search Mechanisms with `django-pgai`

In `django-pgai`, semantic search is a Django ORM feature. You declare a
`VectorizedTextField`. The plugin owns the embedding lifecycle. You query
it through normal Django expressions: `.filter()`, `.annotate()`, manager
methods.

As a consequence, the tuning surface is small and local. Swapping an
embedding model is a one line change. Adjusting thresholds, ranking
strategies, or blending multiple models is also a one line change.

Two surfaces matter:

1. The four query mechanisms: `find()`, `semantic_score()`, `semantic_rank()`,
   and `.filter()` + `semantic_score()`. Pick by call site ergonomics.
2. The knobs each mechanism exposes: `threshold`, `rank_by`, multi field
   rank, weighted blends. Each one is a lever for tuning precision, recall,
   or score distribution.

Cross model comparison is covered in [`MODEL_COMPARISON.md`](MODEL_COMPARISON.md).

Examples are driven by the `sample usage` CLI against the `Movie` model.
The mechanisms are not repo specific. Every CLI call resolves to one
Django ORM expression you can paste into any project.

The example model (`Movie`, with four vectorizers over a single `overview`
column) is defined in the project [README](../README.md#the-model--one-source-column-four-embeddings-zero-glue-code).
The mechanisms work identically on any of the four vectorizers. The
`--variant` flag on the CLI picks which one. All examples use the same
query (`"samurai revenge"`) and the same variant (`mv-snowflake`) for
read across.

---

## Mechanism 1. `similar_in.<field>.find()`

**API.** `Model.similar_in.<field>.find(query, limit=N, threshold=…, rank_by=…)`
returns a `list[SemanticResult]`. Each result exposes `.score`, `.relevance`,
`.match_count`, and `.instance`. This is the friendliest entry point: no
ORM ceremony, just a query and a top N list.

```python
results = Movie.similar_in.overview_snowflake.find(
    "samurai revenge", limit=5,
)
for r in results:
    print(r.score, r.instance.title)
```

**CLI demo.**

```bash
$ ./manage.sh sample usage api find "samurai revenge" -v mv-snowflake -l 5
```

```text
 ID   Title              Score
 646  Hero               0.7516
 785  47 Ronin           0.7490
 5    Furious 7          0.7460
 175  The Last Samurai   0.7459
 198  The Wolverine      0.7446
```

Four out of five top hits are on topic samurai or revenge films. Reach for
`find()` when the call site doesn't need to participate in a larger
QuerySet pipeline.

---

## Mechanism 2. `semantic_score()` annotation

**API.** `semantic_score(field, query)` is a Django ORM expression. It
returns the similarity score as an annotated column on a plain QuerySet,
which you then order or slice yourself. This is the lowest level
mechanism. Everything else in the plugin is built on top of it.

```python
from django_pgai.db.semantic_search.expressions import semantic_score

qs = (
    Movie.objects
    .annotate(score=semantic_score("overview_snowflake", "samurai revenge"))
    .order_by("-score")[:5]
)
for m in qs:
    print(m.score, m.title)
```

**CLI demo.**

```bash
$ ./manage.sh sample usage api annotate "samurai revenge" -v mv-snowflake -l 5
```

The result set matches `find()`: same scores, same order. `find()` is
implemented as exactly this annotation. Use this mechanism when you need
to do something the higher level APIs don't expose, such as blending two
score columns into a weighted sum (see Mechanism 8) or applying arithmetic
to the score before ordering.

---

## Mechanism 3. `objects.semantic_rank()`

**API.** `Model.objects.semantic_rank(query, fields=[…])` returns a
`QuerySet` already annotated with `semantic_score` and pre ordered by it.
The result is a normal Django QuerySet. You can `.filter()`, `.values()`,
`.iterator()`, paginate it, hand it to DRF, anything.

```python
qs = (
    Movie.objects
    .semantic_rank("samurai revenge", fields=["overview_snowflake"])[:5]
)
```

**CLI demo.**

```bash
$ ./manage.sh sample usage api rank "samurai revenge" -v mv-snowflake -l 5
```

Same five movies as `find()`, but now with a chainable handle. Reach for
this mechanism when the search result has to flow through existing ORM
code that expects a QuerySet, not a list of result objects (serializers,
admin actions, view mixins).

---

## Mechanism 4. `.filter()` + `semantic_score()`

**API.** Compose any standard Django `.filter()` with `semantic_score()`.
The structured predicate narrows the candidate set. The semantic score
re ranks the survivors. This is the workhorse mechanism for production
search where "find something relevant and matching these constraints" is
the real requirement.

```python
qs = (
    Movie.objects
    .filter(genres__icontains="Action")
    .annotate(score=semantic_score("overview_snowflake", "samurai revenge"))
    .order_by("-score")[:5]
)
```

**CLI demo.**

```bash
$ ./manage.sh sample usage api filter "samurai revenge" -v mv-snowflake -g Action -l 5
```

The candidate set shrinks to Action tagged movies before the vector
comparison runs, so this is cheaper than ranking the whole table and
post filtering. pgvector only computes similarity on the rows that survive
the structured predicate. Use this mechanism whenever you have any
structured constraint (tenant, status, region, tag) that can prune the
candidate set.

---

## Mechanism 5. Threshold cutoff

**API.** Passing `threshold=` to `find()` (or applying a `score__gte`
filter to a `semantic_rank()` queryset) drops results below a cutoff.
The cutoff is per model. An absolute score that's "strong" on one
vectorizer is "noise" on another.

```python
results = Movie.similar_in.overview_snowflake.find(
    "samurai revenge", threshold=0.74, limit=10,
)
```

**CLI demo.**

```bash
$ ./manage.sh sample usage api find "samurai revenge" -v mv-snowflake -t 0.74 -l 10
```

To find the right cutoff for a variant, sweep it:

```bash
$ ./manage.sh sample usage compare strategies threshold "samurai revenge" -v mv-snowflake
```

This evaluates three cutoff bands (high ≥0.85, medium ≥0.70, low ≥0.55)
on a single variant and shows which results survive each. The visible gap
between the last relevant hit and the first irrelevant one is where the
threshold belongs.

Typical bands per variant (from the canonical query runs):

| Variant | Top 1 (clear query) | Noise floor |
|---|---|---|
| `mv-snowflake` | ~0.75 | ~0.65 |
| `mv-mxbai` | ~0.60 to 0.67 | ~0.50 |
| `mv-qwen` | ~0.55 to 0.60 | ~0.45 |
| `mv-minilm` | ~0.45 to 0.48 | ~0.30 |

A `threshold=0.55` keeps almost everything on `mv-snowflake` but cuts
deeply on `mv-minilm`. **Calibrate per model, never globally.**

---

## Mechanism 6. Ranking strategy (`rank_by`)

**API.** When a document chunks into multiple pieces, multiple chunks can
match the query. `rank_by=` controls how those per chunk scores collapse
into a single document score:

| Strategy | Document score is | Best for |
|---|---|---|
| `best` *(default)* | the highest single chunk similarity | Short queries, distinctive matches |
| `relevance` | best score × number of matching chunks (weighted) | Long queries where breadth matters |
| `count` | number of chunks above the threshold | "How saturated is this document with the topic?" |

```python
results = Movie.similar_in.overview_snowflake.find(
    "existential dread", rank_by="relevance", limit=5,
)
```

**CLI demo.**

```bash
$ ./manage.sh sample usage compare strategies rank-by "existential dread" -v mv-mxbai
```

This runs the same query three times against the same variant, once per
strategy, and shows how the top N reshuffles. In practice **`best` is the
right default**. Use `relevance` for multi clause queries. Pair `count`
with a `--threshold` to ask "documents where at least N chunks score above X."

---

## Mechanism 7. Cross model comparison

**API.** Call any of mechanisms 1 to 4 in a loop, once per vectorizer
field. The `compare models` CLI commands do exactly this. They are
convenience wrappers around repeated `find()` calls, not a separate plugin
API.

**CLI demos.**

```bash
$ ./manage.sh sample usage compare models results "samurai revenge" -l 5
$ ./manage.sh sample usage compare models time    "samurai revenge" -n 5
```

The first prints a side by side table. The second runs a warm latency
benchmark per variant. For `"samurai revenge"` the top 3 hits look like:

| # | `mv-qwen` | `mv-mxbai` | `mv-minilm` | `mv-snowflake` |
|---|---|---|---|---|
| 1 | Unforgiven *(0.568)* | 47 Ronin *(0.670)* | Licence to Kill *(0.458)* | Hero *(0.752)* |
| 2 | Shrek Forever After *(0.560)* | The Last Samurai *(0.650)* | The Last Samurai *(0.441)* | 47 Ronin *(0.749)* |
| 3 | The Notebook *(0.556)* | Princess Mononoke *(0.633)* | 47 Ronin *(0.440)* | Furious 7 *(0.746)* |

Three of four vectorizers return on topic top 3 hits. `mv-qwen` returns
unrelated titles despite comparable absolute scores, a reminder that
scores aren't comparable across models. Use this mechanism when you don't
yet know which vectorizer fits your corpus.

For the full canonical sweep (4 queries × 4 variants × N runs each):

```bash
$ ./manage.sh sample usage compare demo --output <path/to/usage.md>
```

`--output` is required and takes the markdown path. A JSON sibling is
written next to it (same path with the `.json` extension). See
[`MODEL_COMPARISON.md`](MODEL_COMPARISON.md) for the analysis built from
those numbers.

---

## Mechanism 8. Combining multiple models

**API, variant A: pass several fields to `semantic_rank()`.** The plugin
runs each field's similarity and combines them internally.

```python
qs = Movie.objects.semantic_rank(
    "cooking mice",
    fields=["overview_snowflake", "overview_mxbai"],
)[:10]
```

**API, variant B: blend `semantic_score()` annotations by hand.** Useful
when you want explicit weights or to mix in non semantic signals (recency,
popularity).

```python
from django.db.models import F
from django_pgai.db.semantic_search.expressions import semantic_score

qs = (
    Movie.objects
    .annotate(
        s_snow=semantic_score("overview_snowflake", "cooking mice"),
        s_mxbai=semantic_score("overview_mxbai", "cooking mice"),
    )
    .annotate(blended=0.6 * F("s_snow") + 0.4 * F("s_mxbai"))
    .order_by("-blended")[:10]
)
```

Why bother. On semantically ambiguous queries the four vectorizers
disagree on the top hit. For `"cooking mice"` the top hit is _Stuart Little_
under `mv-snowflake`, _Stuart Little 2_ under `mv-mxbai`, and _Ratatouille_
under both `mv-minilm` and `mv-qwen`. A blended ranker rewards documents
that score well under multiple models, which is a stronger relevance signal
than either model alone.

---

## What gives the best results

Across the four canonical queries (from the `compare demo` JSON output):

- **`mv-snowflake`** (`snowflake-arctic-embed`). Highest absolute top 1
  scores and the widest gap to the noise floor. Easiest to threshold.
  Best default.
- **`mv-mxbai`** (`mxbai-embed-large`). Close second on quality, around
  10× faster than `mv-qwen`. Strong fallback.
- **`mv-minilm`** (`all-MiniLM-L6-v2`). Compressed score range, but
  surfaces the right films on concrete queries. Pick for latency critical
  paths.
- **`mv-qwen`** (`qwen3-embedding`). Slowest and worst on these short
  English overviews. Try it only after measuring on your own corpus.
  Qwen3's strengths are long documents and multilingual queries, neither
  of which apply here.

See [`MODEL_COMPARISON.md`](MODEL_COMPARISON.md) for the full cost and
benefit breakdown with charts.

---

## Reproducing the numbers

Bring the stack up and seed the dataset:

```bash
docker compose up -d
./manage.sh migrate
./setup.sh build                    # seeds 1000 movies + vectorizes all four variants
```

Two ways to reproduce the comparison numbers in this doc.

**Per query evaluation.** Run one query against all variants. Use this to
spot check a query you care about, or to reproduce the top 3 table in
Mechanism 7 for `"samurai revenge"`:

```bash
./manage.sh sample usage compare models results "samurai revenge" -l 5
./manage.sh sample usage compare models time    "samurai revenge" -n 5
```

**Full canonical sweep.** Run the fixed query set against all variants
and write the persisted report. Both commands take `--output` as a
required parameter:

```bash
./manage.sh sample usage compare cost --output <path/to/cost.json>
./manage.sh sample usage compare demo --output <path/to/usage.md>
```

`compare demo` also writes a JSON sibling next to the markdown file
(same path with the `.json` extension).
