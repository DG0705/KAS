from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator


MAX_SELFIE_UPLOAD_SIZE = 5 * 1024 * 1024

validate_image_extension = FileExtensionValidator(
    allowed_extensions=["jpg", "jpeg", "png", "webp"]
)


def validate_selfie_file(file_obj):
    validate_image_extension(file_obj)
    if file_obj.size > MAX_SELFIE_UPLOAD_SIZE:
        raise ValidationError("Selfie image must be 5 MB or smaller.")
