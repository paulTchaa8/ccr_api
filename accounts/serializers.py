from accounts.models import Recepteur, Emetteur
import re
from django.core.exceptions import ValidationError
from rest_framework import serializers

def validate_password(password):
    """Docstring for function."""
    if len(password) < 8:
        raise ValidationError(
            _("The password must be at least 8 characters"),
            code='password_no_length')

    if not re.findall('\d', password):
        raise ValidationError(
            _("The password must contain at least 1 digit, 0-9."),
            code='password_no_number',
        )

    if not re.findall('[A-Z]', password):
        raise ValidationError(
            _("The password must contain at least 1 uppercase letter, A-Z."),
            code='password_no_upper',
        )

    if not re.findall('[a-z]', password):
        raise ValidationError(
            _("The password must contain at least 1 lowercase letter, a-z."),
            code='password_no_lower',
        )

    if not re.findall('[()[\]{}|\\`~!@#$%^&*_\-+=;:\'",<>./?]', password):
        raise ValidationError(
            _("The password must contain at least 1 symbol: " +
              "()[]{}|\`~!@#$%^&*_-+=;:'\",<>./?"),
            code='password_no_symbol',
        )

    return password


def validate_phone(phone):
    """Fonction de validation du phone number."""
    if not re.findall("^+[0-9]{6,}", phone):
        raise ValidationError(
            "The phone must start with + and contain at least 5 digits."
        )

    return phone

class CheckPhoneSerializer(serializers.Serializer):
    """checke la validite du phone field."""
    phone = serializers.CharField(
        max_length=50,
        validators=[validate_phone]
    )

class CheckPasswordSerializer(serializers.Serializer):
	password = serializers.CharField(
		max_length=50,
		validators=[validate_password]
	)

class RecepteurSerializer(serializers.ModelSerializer):
	"""
	Transforme l'objet Recepteur en du json serialisable
	"""
	class Meta:
		model = Recepteur
		fields = ['id', 'name', 'surname', 'email', 'password']

class ConnexionSerializer(serializers.Serializer):
    """ Valider password et email """
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=255)

class ForgotPasswordSerializer(serializers.Serializer):
    """Docstring for class."""
    email = serializers.EmailField(max_length=255)

class NewPasswordSerializer(serializers.Serializer):
    """Docstring for class."""
    new_password = serializers.CharField(
        max_length=100,
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(
        max_length=100,
        validators=[validate_password]
    )


class VerifyTokenSerializer(serializers.Serializer):
    """ Convertit la donnee en du json approprie """
    reset_token = serializers.CharField(max_length=255)