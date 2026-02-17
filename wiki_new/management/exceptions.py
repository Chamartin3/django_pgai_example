# Source Generated with Decompyle++
# File: exceptions.cpython-312.pyc (Python 3.12)

'''Custom exceptions for sample commands.'''

class SampleCommandError(Exception):
    '''Base exception for sample commands.'''
    pass


class ModelNotFoundError(SampleCommandError):
    '''Model not found.'''
    pass


class MissingSimilarInError(SampleCommandError):
    '''Model missing similar_in manager.'''
    pass


class VectorizationIncompleteError(SampleCommandError):
    '''Vectorization not complete.'''
    pass

__all__ = [
    'SampleCommandError',
    'ModelNotFoundError',
    'MissingSimilarInError',
    'VectorizationIncompleteError']
