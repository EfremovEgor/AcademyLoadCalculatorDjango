from django.forms import ValidationError


def validate_file_extension(value):
    if not value.name.endswith(".json"):
        raise ValidationError("Only .json file is accepted")
