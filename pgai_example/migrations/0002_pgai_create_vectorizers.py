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
        ('django_pgai', '0001_pgai_system_tables'),
    ]

    operations = [
        pgai_db.operations.CreateVectorizer(
            model_name='Movie',
            model_table='pgai_example_movie',
            field_name='overview',
            vectorizer_name='movie_overview_qwen3',
            config={
                    'embedding_provider': 'ollama',
                    'embedding_model': 'qwen3-embedding',
                    'embedding_dimensions': 4096,
                    'chunking_size': 300,
                    'chunking_overlap': 30,
                },
        ),
        pgai_db.operations.CreateVectorizer(
            model_name='Movie',
            model_table='pgai_example_movie',
            field_name='overview_mxbai',
            vectorizer_name='movie_overview_mxbai',
            config={
                    'embedding_provider': 'ollama',
                    'embedding_model': 'mxbai-embed-large:latest',
                    'embedding_dimensions': 1024,
                    'chunking_size': 300,
                    'chunking_overlap': 30,
                },
            source_column='overview',
        ),
        pgai_db.operations.CreateVectorizer(
            model_name='Movie',
            model_table='pgai_example_movie',
            field_name='overview_minilm',
            vectorizer_name='movie_overview_minilm',
            config={
                    'embedding_provider': 'ollama',
                    'embedding_model': 'all-minilm',
                    'embedding_dimensions': 384,
                    'chunking_size': 400,
                    'chunking_overlap': 30,
                },
            source_column='overview',
        ),
        pgai_db.operations.CreateVectorizer(
            model_name='Movie',
            model_table='pgai_example_movie',
            field_name='overview_snowflake',
            vectorizer_name='movie_overview_snowflake',
            config={
                    'embedding_provider': 'ollama',
                    'embedding_model': 'snowflake-arctic-embed',
                    'embedding_dimensions': 1024,
                    'chunking_size': 350,
                },
            source_column='overview',
        ),
    ]
