from django.db import models
from django_pgai.fields import VectorizedTextField
from django_pgai.db import SemanticQuerySet


class Movie(models.Model):
    """Movie with four vectorizers over the same `overview` column.

    `overview` is the concrete text column. The remaining three
    ``VectorizedTextField``s are *proxies* (``source_field='overview'``) — no
    extra columns, just additional pgai vectorizers reading the same data.
    """

    title = models.TextField()
    overview = VectorizedTextField(
        vectorizer_name="movie_overview_qwen3",
        embedding_model="qwen3-embedding",
        embedding_dimensions=4096,
        chunk_size=300,
        chunk_overlap=30,
    )
    overview_mxbai = VectorizedTextField(
        vectorizer_name="movie_overview_mxbai",
        source_field="overview",
        embedding_model="mxbai-embed-large:latest",
        embedding_dimensions=1024,
        chunk_size=300,
        chunk_overlap=30,
    )
    overview_minilm = VectorizedTextField(
        vectorizer_name="movie_overview_minilm",
        source_field="overview",
        embedding_model="all-minilm",
        embedding_dimensions=384,
        chunk_size=400,
        chunk_overlap=30,
    )
    overview_snowflake = VectorizedTextField(
        vectorizer_name="movie_overview_snowflake",
        source_field="overview",
        embedding_model="snowflake-arctic-embed",
        embedding_dimensions=1024,
        chunk_size=350,
    )
    genres = models.TextField(blank=True, default="")
    producer = models.TextField(blank=True, default="")
    cast = models.TextField(blank=True, default="")

    objects = SemanticQuerySet.as_manager()

    class Meta:
        verbose_name = "Movie"
        verbose_name_plural = "Movies"

    def __str__(self):
        return self.title
