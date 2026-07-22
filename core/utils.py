import uuid
from os import path
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

def _generate_filename(filename):
    _, ext = path.splitext(filename)
    return "%s%s" % (uuid.uuid4(), ext)

@deconstructible
class UploadTo:
    def __init__(self, directory):
        self.directory = directory

    def __call__(self, instance, filename):
        return "{dirname}/{filename}".format(
            dirname=self.directory,
            filename=_generate_filename(filename),
        )

@deconstructible
class ValidateFileSize:
    def __init__(self, size_mb):
        self.size_mb = size_mb

    def __call__(self, value):
        file_size = value.size if value else 0
        limit = self.size_mb * 1024 * 1024  # Convert MB to bytes
        if file_size > limit:
            raise ValidationError(
                f"File too large. Max size: {self.size_mb} MB."
            )
