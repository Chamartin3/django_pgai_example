# Source Generated with Decompyle++
# File: context.cpython-310.pyc (Python 3.10)

'''
CLI Context - Single source of truth for all external imports.

This module provides a single `ctx` object that contains ALL external dependencies
used by management commands. Commands should ONLY import from:
1. This context module (ctx object)
2. data_models module (for type hints only)
3. typer (for Option, Argument decorators)

Usage in commands:
    from wiki_new.management.context import ctx
    from wiki_new.management.data_models import SearchResultsData  # type hints only

    # Use ctx for everything else:
    ctx.render.build.render_build_start(app_label)
    ctx.render.message.error("Error message")
    ctx.get_model_from_string("minilm")
    ctx.SampleModel.WIKI_MINILM

Architecture:
- Context Injection: All dependencies accessed through ctx
- No direct imports: Commands don\'t import external modules directly
- Centralized rendering: All UI rendering goes through ctx.render
- Type-safe: Context class provides proper type hints
'''
from __future__ import annotations

from django_pgai.config import ConfigField
from django_pgai.evaluation import FilterEvaluation, SearchEvaluation
from django_pgai.models import Vectorizer
from django_pgai.pgai_fields import VectorizedTextField
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from wiki_new.management.data_models import (
    MessageType,
    VectorizationState,
    VectorizationStatus,
)
from wiki_new.management import exceptions as _exceptions_module
from wiki_new.management.exceptions import MissingSimilarInError, ModelNotFoundError
from wiki_new.management.helpers.field_config import extract_field_config
from wiki_new.management.helpers.model_helpers import (
    extract_title,
    get_model_app_label,
    get_model_table_name,
)
from wiki_new.management.helpers.seed import (
    check_table_exists,
    load_dataset_into_table,
)
from wiki_new.management.helpers.vectorization import (
    check_vectorization_progress,
    get_vectorization_status,
)
from wiki_new.management.models import Dataset, SampleModel, get_model_from_string
from wiki_new.management.renderers import CLIComponentRegistry, CLIRenderer


class _ModelsNamespace:
    """Namespace for model enums and constants."""

    @property
    def sample_model(self):
        return SampleModel

    @property
    def dataset(self):
        return Dataset

    @property
    def vectorization_state(self):
        return VectorizationState

    @property
    def vectorization_status(self):
        return VectorizationStatus


class _HelpersNamespace:
    """Namespace for helper functions."""

    @staticmethod
    def get_model_from_string(model_key):
        return get_model_from_string(model_key)

    @staticmethod
    def get_vectorization_status(model_class):
        return get_vectorization_status(model_class)

    @staticmethod
    def check_vectorization_progress(model_class, field):
        return check_vectorization_progress(model_class, field)

    @staticmethod
    def extract_field_config(field):
        return extract_field_config(field)

    @staticmethod
    def extract_title(instance):
        return extract_title(instance)

    @staticmethod
    def get_model_table_name(model_class):
        return get_model_table_name(model_class)

    @staticmethod
    def get_model_app_label(model_class):
        return get_model_app_label(model_class)

    @staticmethod
    def check_table_exists(table_name):
        return check_table_exists(table_name)

    @staticmethod
    def load_dataset_into_table(table_name, dataset_name, dataset_config, field_types, batches, batch_size):
        return load_dataset_into_table(table_name, dataset_name, dataset_config, field_types, batches, batch_size)


class _TypesNamespace:
    """Namespace for type definitions."""

    @property
    def vectorized_text_field(self):
        return VectorizedTextField

    @property
    def config_field(self):
        return ConfigField

    @property
    def search_evaluation(self):
        return SearchEvaluation

    @property
    def filter_evaluation(self):
        return FilterEvaluation

    @property
    def vectorizer(self):
        return Vectorizer


class CLIContext:
    '''
    Typed context object containing all dependencies for CLI commands.

    This class provides a single, type-safe interface to all external
    dependencies. Commands should only import this context object.

    Attributes:
        render: CLIRenderer instance for all rendering operations
        console: Shared Rich Console instance

    Usage:
        from wiki_new.management.context import ctx

        ctx.render.build.render_build_start("wiki_new")
        ctx.render.message.error("Something went wrong")
        model_class = ctx.get_model_from_string("minilm")
    '''

    def __init__(self):
        '''Initialize context with all dependencies.'''
        self._render = CLIRenderer()
        self._models = _ModelsNamespace()
        self._helpers = _HelpersNamespace()
        self._types = _TypesNamespace()


    def render(self):
        '''CLIRenderer instance for all rendering operations.'''
        return self._render

    render = property(render)

    def console(self):
        '''Shared Rich Console instance.'''
        return CLIRenderer.console

    console = property(console)

    def Console(self):
        '''Rich Console class.'''
        return Console

    Console = property(Console)

    def Panel(self):
        '''Rich Panel class.'''
        return Panel

    Panel = property(Panel)

    def Table(self):
        '''Rich Table class.'''
        return Table

    Table = property(Table)

    def Text(self):
        '''Rich Text class.'''
        return Text

    Text = property(Text)

    def Vectorizer(self):
        '''PGAI Vectorizer model class.'''
        return Vectorizer

    Vectorizer = property(Vectorizer)

    def VectorizedTextField(self):
        '''PGAI VectorizedTextField class.'''
        return VectorizedTextField

    VectorizedTextField = property(VectorizedTextField)

    def ConfigField(self):
        '''PGAI ConfigField enum.'''
        return ConfigField

    ConfigField = property(ConfigField)

    def SearchEvaluation(self):
        '''SearchEvaluation class.'''
        return SearchEvaluation

    SearchEvaluation = property(SearchEvaluation)

    def FilterEvaluation(self):
        '''FilterEvaluation class.'''
        return FilterEvaluation

    FilterEvaluation = property(FilterEvaluation)

    def CLIComponentRegistry(self):
        '''CLIComponentRegistry enum for introspection.'''
        return CLIComponentRegistry

    CLIComponentRegistry = property(CLIComponentRegistry)

    def VectorizationStatus(self):
        '''VectorizationStatus enum.'''
        return VectorizationStatus

    VectorizationStatus = property(VectorizationStatus)

    def VectorizationState(self):
        '''VectorizationState enum.'''
        return VectorizationState

    VectorizationState = property(VectorizationState)

    def MessageType(self):
        '''MessageType enum.'''
        return MessageType

    MessageType = property(MessageType)

    def SampleModel(self):
        '''SampleModel enum.'''
        return SampleModel

    SampleModel = property(SampleModel)

    def ModelNotFoundError(self):
        '''ModelNotFoundError exception class.'''
        return ModelNotFoundError

    ModelNotFoundError = property(ModelNotFoundError)

    def MissingSimilarInError(self):
        '''MissingSimilarInError exception class.'''
        return MissingSimilarInError

    MissingSimilarInError = property(MissingSimilarInError)

    def exceptions(self):
        '''Exceptions module namespace.'''
        return _exceptions_module

    exceptions = property(exceptions)

    def models(self):
        '''Models namespace with enums and constants.'''
        return self._models

    models = property(models)

    def helpers(self):
        '''Helpers namespace with utility functions.'''
        return self._helpers

    helpers = property(helpers)

    def types(self):
        '''Types namespace with type definitions.'''
        return self._types

    types = property(types)

    def get_model_from_string(self, model_key):
        '''Get Django model class from string key.'''
        return get_model_from_string(model_key)


    def get_vectorization_status(self, model_class):
        '''Get vectorization status for a model.'''
        return get_vectorization_status(model_class)


    def check_vectorization_progress(self, model_class, field):
        '''Check vectorization progress for a model field.'''
        return check_vectorization_progress(model_class, field)


    def extract_field_config(self, field):
        '''Extract configuration from a VectorizedTextField.'''
        return extract_field_config(field)


    def extract_title(self, instance):
        '''Extract title from a model instance.'''
        return extract_title(instance)


    def get_model_table_name(self, model_class):
        '''Get database table name for a model.'''
        return get_model_table_name(model_class)


    def get_model_app_label(self, model_class):
        '''Get app label for a model.'''
        return get_model_app_label(model_class)


ctx = CLIContext()
__all__ = [
    'ctx',
    'CLIContext']
