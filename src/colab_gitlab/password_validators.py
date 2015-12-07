
from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _


def min_length(password):
    if len(password) < 8:
        raise ValidationError(_('Password must have at least 8 characters.'))
