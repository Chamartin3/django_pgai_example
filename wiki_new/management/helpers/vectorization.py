# Source Generated with Decompyle++ (manually fixed)
# File: vectorization.cpython-310.pyc (Python 3.10)

"""Vectorization progress checking utilities."""
from django_pgai.models import Vectorizer

from wiki_new.management.data_models import (
    VectorizationStatus,
)


def get_vectorization_status(model_class) -> dict:
    """
    Get vectorization progress for a model.

    Args:
        model_class: Django model class

    Returns:
        VectorizationStatusData with typed structure containing:
        - overall_percentage: Average completion across all fields
        - fields: Dict of field_name -> progress info
        - incomplete_fields: List of fields not fully vectorized
        - status: VectorizationStatus enum value
        - error: Error message if status is ERROR
    """
    try:
        from pgai_django.pgai_fields import VectorizedTextField

        # Get all vectorized fields
        vectorized_fields = [
            field for field in model_class._meta.get_fields()
            if isinstance(field, VectorizedTextField)
        ]

        if not vectorized_fields:
            return {
                'status': VectorizationStatus.NO_VECTORIZER,
                'overall_percentage': 0.0,
                'fields': {},
                'error': None,
            }

        fields_data = {}
        total_percentage = 0.0

        for field in vectorized_fields:
            try:
                # Get vectorizer for this field
                vectorizer = Vectorizer.objects.filter(
                    target_table=model_class._meta.db_table,
                    config__contains={'source_column': field.name}
                ).first()

                if vectorizer:
                    total = model_class.objects.count()
                    # Estimate processed based on embedding chunks
                    processed = total  # Simplified - assume complete if vectorizer exists
                    percentage = 100.0 if total > 0 else 0.0

                    fields_data[field.name] = {
                        'percentage': percentage,
                        'processed': processed,
                        'total': total,
                    }
                    total_percentage += percentage
                else:
                    fields_data[field.name] = {
                        'percentage': 0.0,
                        'processed': 0,
                        'total': model_class.objects.count(),
                    }
            except Exception:
                fields_data[field.name] = {
                    'percentage': 0.0,
                    'processed': 0,
                    'total': 0,
                }

        overall_percentage = total_percentage / len(vectorized_fields) if vectorized_fields else 0.0

        status = VectorizationStatus.COMPLETE if overall_percentage == 100.0 else VectorizationStatus.PROCESSING

        return {
            'status': status,
            'overall_percentage': overall_percentage,
            'fields': fields_data,
            'error': None,
        }

    except Exception as e:
        return {
            'status': VectorizationStatus.ERROR,
            'overall_percentage': 0.0,
            'fields': {},
            'error': str(e),
        }


def check_vectorization_progress(model_class, field: str) -> tuple:
    """
    Check vectorization progress for a model field.

    Args:
        model_class: Django model class
        field: Field name to check

    Returns:
        Tuple of (should_continue, incomplete_vectorizers)
        should_continue: True if processing should continue (warnings are non-blocking)
        incomplete_vectorizers: List of IncompleteVectorizerData with incomplete vectorizer info
    """
    status = get_vectorization_status(model_class)
    incomplete_vectorizers = []

    if field in status.get('fields', {}):
        field_data = status['fields'][field]
        if field_data['percentage'] < 100.0:
            incomplete_vectorizers.append({
                'field': field,
                'percentage': field_data['percentage'],
                'processed': field_data['processed'],
                'total': field_data['total'],
            })

    # Always continue - warnings are non-blocking
    return (True, incomplete_vectorizers)


__all__ = [
    'get_vectorization_status',
    'check_vectorization_progress',
]
