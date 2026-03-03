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
    from pgai_example.management.context import ctx
    from pgai_example.management.data_models import SearchResultsData  # type hints only

    # Use ctx for everything else:
    ctx.render.build.render_build_start(app_label)
    ctx.render.message.error("Error message")
    ctx.get_model_from_string("minilm")
    ctx.SampleModel.WIKI_MINILM

Architecture:
- Context Injection: All dependencies accessed through ctx
- No direct imports: Commands don\'t import external modules directly
- Centralized rendering: All UI rendering goes through ctx.render
- Decorator support: Command handlers with error handling and verbose tracebacks
- Type-safe: Context class provides proper type hints

Command Handler Decorator:
    @ctx.handler
    def my_command(ctx, arg: str, **kwargs):
        # ctx is injected, verbose flag extracted from kwargs
        # errors are handled automatically
        pass
'''
from __future__ import annotations

import sys
import traceback
from functools import wraps
from typing import Callable

from django_pgai.config import ConfigField
from django_pgai.evaluation import FilterEvaluation, SearchEvaluation
from django_pgai.models import Vectorizer
from django_pgai.pgai_fields import VectorizedTextField
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pgai_example.management.data_models import (
    MessageType,
    VectorizationState,
    VectorizationStatus,
)
from pgai_example.management import exceptions as _exceptions_module
from pgai_example.management.exceptions import SampleCommandError
from pgai_example.management.helpers.field_config import extract_field_config
from pgai_example.management.helpers.model_helpers import (
    extract_title,
    get_model_app_label,
    get_model_table_name,
)
from pgai_example.management.helpers.seed import (
    check_table_exists,
    load_dataset_into_table,
    get_table_row_count,
    clear_table,
)
from pgai_example.management.helpers.vectorization import (
    check_vectorization_progress,
    get_vectorization_status,
)
from pgai_example.constants import SampleModel
from pgai_example.management.renderers import CLIComponentRegistry, CLIRenderer


class _ModelsNamespace:
    """Namespace for model enums and constants."""

    @property
    def sample_model(self):
        return SampleModel

    @property
    def vectorization_state(self):
        return VectorizationState

    @property
    def vectorization_status(self):
        return VectorizationStatus


class _HelpersNamespace:
    """Namespace for helper functions."""

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

    @staticmethod
    def get_table_row_count(table_name):
        return get_table_row_count(table_name)

    @staticmethod
    def clear_table(table_name):
        return clear_table(table_name)


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


class CommandDecorators:
    """
    Decorator utilities for command handlers.

    Provides context injection and error handling decorators that can be
    used individually or combined via the command_handler method.
    """

    def __init__(self, ctx_instance):
        """Initialize with reference to parent context instance."""
        self._ctx = ctx_instance

    def inject_context(self, func: Callable) -> Callable:
        """
        Decorator to inject ctx as the first argument to a function.

        The decorated function will receive ctx as its first parameter,
        avoiding the need to import ctx at module level.

        Args:
            func: Function to decorate

        Returns:
            Wrapped function with ctx injected as first argument
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(self._ctx, *args, **kwargs)
        return wrapper

    def error_printing(self, func: Callable) -> Callable:
        """
        Decorator to handle exceptions and render errors with optional verbose output.

        This decorator:
        1. Expects ctx as the first argument (use with inject_context)
        2. Catches all exceptions
        3. Renders custom SampleCommandError exceptions with specific formatting
        4. Extracts verbose flag from kwargs (if present)
        5. Shows full traceback when verbose=True is passed via kwargs
        6. Uses ctx.render.message.error() for all error rendering

        Args:
            func: Function to decorate (must accept ctx as first arg and **kwargs)

        Returns:
            Wrapped function with error handling
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract verbose flag if it exists
            verbose = kwargs.get('verbose', False)

            # Extract ctx from first argument (injected by inject_context)
            ctx = args[0] if args else self._ctx

            try:
                return func(*args, **kwargs)

            except SampleCommandError as e:
                # Handle custom command errors with structured formatting
                error_type = type(e).__name__
                error_msg = str(e)

                if verbose:
                    # Show detailed traceback
                    tb = traceback.format_exc()
                    full_msg = f"[bold red]{error_type}[/bold red]: {error_msg}\n\n{tb}"
                    ctx.render.message.error(full_msg)
                else:
                    # Show concise error message
                    ctx.render.message.error(f"{error_type}: {error_msg}")

            except Exception as e:
                # Handle unexpected errors
                error_type = type(e).__name__
                error_msg = str(e)

                if verbose:
                    # Show full traceback for debugging
                    tb = traceback.format_exc()
                    full_msg = f"[bold red]Unexpected {error_type}[/bold red]: {error_msg}\n\n{tb}"
                    ctx.render.message.error(full_msg)
                else:
                    # Show basic error info
                    ctx.render.message.error(f"Unexpected error: {error_msg}")

        return wrapper

    def command_handler(self, func: Callable) -> Callable:
        """
        Combined decorator for command handlers.

        Provides both context injection and error handling in one decorator.
        This is equivalent to:
            @error_printing
            @inject_context
            def my_command(ctx, ...):
                ...

        Args:
            func: Function to decorate

        Returns:
            Wrapped function with context injection and error handling
        """
        return self.error_printing(self.inject_context(func))


class CLIContext:
    '''
    Typed context object containing all dependencies for CLI commands.

    This class provides a single, type-safe interface to all external
    dependencies. Commands should only import this context object.

    Attributes:
        render: CLIRenderer instance for all rendering operations
        console: Shared Rich Console instance
        handler: Decorator method for command handlers
        helpers: Utility functions for business logic
        models: Model enums and constants
        types: Type definitions for Django PGAI
        exceptions: Custom exception classes

    Usage:
        from pgai_example.management.context import ctx

        # Rendering
        ctx.render.build.render_build_start("pgai_example")
        ctx.render.message.error("Something went wrong")

        # Helpers
        model_class = ctx.get_model_from_string("minilm")

        # Handler decorator
        @ctx.handler
        def my_command(ctx, query: str, **kwargs):
            # ctx injected, verbose from kwargs, errors handled
            pass
    '''

    def __init__(self):
        '''Initialize context with all dependencies.'''
        self._render = CLIRenderer()
        self._models = _ModelsNamespace()
        self._helpers = _HelpersNamespace()
        self._types = _TypesNamespace()
        self._command_decorators = CommandDecorators(self)


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

    def handler(self, func: Callable) -> Callable:
        '''
        Decorator for command handlers with context injection and error handling.

        This is the recommended decorator for all command handler functions.
        It combines context injection and comprehensive error handling.

        Usage:
            @ctx.handler
            def handle_search(ctx, query: str, **kwargs):
                # ctx is automatically injected
                # verbose flag extracted from kwargs
                # errors are caught and formatted
                model = ctx.helpers.get_model_from_string(query)
                ctx.render.search.render_results(model)

        Features:
            - Injects ctx as first argument automatically
            - Extracts verbose flag from kwargs (defaults to False)
            - Catches SampleCommandError and renders with type name
            - Catches generic exceptions as "Unexpected error"
            - Shows full traceback when verbose=True passed via kwargs
            - All errors rendered via ctx.render.message.error()

        Args:
            func: Function to decorate (must accept ctx as first arg and **kwargs)

        Returns:
            Wrapped function with context injection and error handling
        '''
        return self._command_decorators.command_handler(func)

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
