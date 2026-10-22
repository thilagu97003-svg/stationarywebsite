import re

from django.core.exceptions import ValidationError


class LetterAndNumberValidator:
    """Password must have at least one letter and one number."""

    def validate(self, password, user=None):
        if not re.search(r"[A-Za-z]", password):
            raise ValidationError("Password must contain at least one letter.", code="password_no_letter")
        if not re.search(r"\d", password):
            raise ValidationError("Password must contain at least one number.", code="password_no_number")

    def get_help_text(self):
        return "Your password must contain at least one letter and one number."