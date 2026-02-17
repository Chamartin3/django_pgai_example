"""Decorators for management commands."""
from functools import wraps
from typing import Callable

from wiki_new.management.context import ctx


def handle_errors(func: Callable) -> Callable:
    """Decorator to handle exceptions and render errors.

    Catches any exceptions raised by the function and renders them
    using ctx.render.message.error().

    Usage:
        @handle_errors
        def handle_command(...):
            # command logic
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            ctx.render.message.error(str(e))

    return wrapper


def with_context(func: Callable) -> Callable:
    """Decorator to inject ctx as the first argument.

    The decorated function will receive ctx as its first parameter,
    avoiding the need to import ctx at module level.

    Usage:
        @with_context
        def handle_command(ctx, arg1, arg2, ...):
            ctx.render.seed.print(data)
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(ctx, *args, **kwargs)

    return wrapper


def command_handler(func: Callable) -> Callable:
    """Combined decorator for command handlers.

    Provides both error handling and context injection.

    Usage:
        @command_handler
        def handle_command(ctx, ...):
            # command logic with ctx injected
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(ctx, *args, **kwargs)
        except Exception as e:
            ctx.render.message.error(str(e))

    return wrapper
