from django.core.exceptions import ValidationError

MAX_RESUME_MB = 5


def validate_resume_size(f):
    if f.size > MAX_RESUME_MB * 1024 * 1024:
        raise ValidationError(f"حجم فایل نباید بیشتر از {MAX_RESUME_MB} مگابایت باشد.")
