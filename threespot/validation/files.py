from functools import partial

from django import forms
from django.conf import settings
from django.core.files.images import get_image_dimensions

from threespot.text import get_readable_file_size

def validate_file_size(file, max_size_kb=1024, label='file'):
    """
    Validates the size of a file, raises a ValidationError for files
    that are too large.
    """
    max_size_bytes = (max_size_kb * 1024)
    if file.size > max_size_bytes:
        fs = get_readable_file_size(max_size_bytes)
        raise forms.ValidationError, (
            "At %s, this %s is too large. %s is the maximum size "
            "allowed for any %s."
        ) % (
            get_readable_file_size(file.size),
            label,
            get_readable_file_size(max_size_bytes),
            label,
        )

# A common use-case, planned for:
validate_image_size = partial(validate_file_size, label='image')

def validate_image_dimensions(image_file, required_width, required_height):
    """
    Validates the dimensions, raises a ValidationErrror for images
    that are too large.
    """
    width, height = get_image_dimensions(image_file)
    if width != required_width or height != required_height:
        raise forms.ValidationError, (
            "Images must be %d pixels wide and %d pixels high; This "
            "image is %d pixels wide and %d pixels high."
        ) % (required_width, required_height, width, height)