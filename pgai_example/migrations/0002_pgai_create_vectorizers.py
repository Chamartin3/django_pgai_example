# Auto-generated migration for 4 field vectorizer(s)
# 
# Set up pgai vectorizer for 4 field(s).
# 
# This migration creates vectorizer(s) that automatically generate
# embeddings for the configured VectorizedTextField(s).
# 
# Generated automatically by makemigrations command.

from django.db import migrations
from django_pgai import db as pgai_db


class Migration(migrations.Migration):

    dependencies = [
        ('pgai_example', '0001_initial'),
        ('django_pgai', '0001_install_extensions'),
    ]

    operations = [
        pgai_db.operations.CreateVectorizer(
            model_name='WikiArticleMiniLM',
            model_table='pgai_example_wikiarticleminilm',
            field_name='text',
            vectorizer_name='pgai_example_wikiarticleminilm_text_vectorizer',
            config={
                    'embedding_provider': 'ollama',
                    'embedding_model': 'all-minilm',
                    'embedding_dimensions': 384,
                    'chunking_method': 'recursive',
                    'chunking_size': 300,
                    'chunking_overlap': 30,
                },
        ),
        pgai_db.operations.CreateVectorizer(
            model_name='WikiArticleSnowflake',
            model_table='pgai_example_wikiarticlesnowflake',
            field_name='text',
            vectorizer_name='pgai_example_wikiarticlesnowflake_text_vectorizer',
            config={
                    'embedding_provider': 'ollama',
                    'embedding_model': 'snowflake-arctic-embed',
                    'embedding_dimensions': 1024,
                    'chunking_method': 'recursive',
                    'chunking_size': 350,
                    'chunking_overlap': 50,
                },
        ),
        pgai_db.operations.CreateVectorizer(
            model_name='MovieQwen',
            model_table='pgai_example_movieqwen',
            field_name='overview',
            vectorizer_name='pgai_example_movieqwen_overview_vectorizer',
            config={
                    'embedding_provider': 'ollama',
                    'embedding_model': 'qwen3-embedding',
                    'embedding_dimensions': 1024,
                    'chunking_method': 'recursive',
                    'chunking_size': 300,
                    'chunking_overlap': 30,
                },
        ),
        pgai_db.operations.CreateVectorizer(
            model_name='MovieMxbai',
            model_table='pgai_example_moviemxbai',
            field_name='overview',
            vectorizer_name='pgai_example_moviemxbai_overview_vectorizer',
            config={
                    'embedding_provider': 'ollama',
                    'embedding_model': 'mxbai-embed-large:latest',
                    'embedding_dimensions': 1024,
                    'chunking_method': 'recursive',
                    'chunking_size': 300,
                    'chunking_overlap': 30,
                },
        ),
    ]
