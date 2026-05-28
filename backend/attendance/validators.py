import os
from django.core.exceptions import ValidationError

MAX_SELFIE_UPLOAD_SIZE = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

def validate_selfie_file(file_obj):
    # 1. Check size (skip if size is missing due to Cloudinary storage)
    if file_obj.size is not None and file_obj.size > MAX_SELFIE_UPLOAD_SIZE:
        raise ValidationError("Selfie image must be 5 MB or smaller.")

    # 2. Extract the file extension
    ext = os.path.splitext(file_obj.name)[1].lower()

    # 3. Skip extension validation if the extension is empty (e.g. Cloudinary dynamic URLs)
    if ext == "":
        return

    # 4. Validate the extension for new uploads
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(f"File extension '{ext}' is not allowed. Allowed extensions are: jpg, jpeg, png, webp.")