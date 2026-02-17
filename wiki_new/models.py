from django.db import models
from django_pgai.pgai_fields import VectorizedTextField


class WikiArticleMiniLM(models.Model):
    url = models.TextField(default="")
    title = models.TextField()
    text = VectorizedTextField(
        embedding_model='all-minilm',
        embedding_dimensions=384,
        chunking_type='recursive',
        chunk_size=300,
        chunk_overlap=30,
    )

    class Meta:
        verbose_name = "Wiki Article (MiniLM)"
        verbose_name_plural = "Wiki Articles (MiniLM)"

    def __str__(self):
        return self.title


class WikiArticleSnowflake(models.Model):
    url = models.TextField(default="")
    title = models.TextField()
    text = VectorizedTextField(
        embedding_model='snowflake-arctic-embed',
        embedding_dimensions=1024,
        chunking_type='recursive',
        chunk_size=350,
        chunk_overlap=50,
    )

    class Meta:
        verbose_name = "Wiki Article (Snowflake)"
        verbose_name_plural = "Wiki Articles (Snowflake)"

    def __str__(self):
        return self.title
