from django.db import models
from django.contrib.auth.models import AbstractBaseUser

# Create your models here.
class Utilisateur(AbstractBaseUser, models.Model):
	name = models.CharField(max_length=255)
	surname = models.CharField(max_length=255, null=True)

class Recepteur(Utilisateur):
	is_receiver = models.BooleanField(default=True)
	email = models.EmailField(max_length=255, unique=True)
	#password = models.CharField(max_length=50)
	phone = models.CharField(max_length=255, null=True)
	created_at = models.DateTimeField(
        db_column="date_creation",
        auto_now_add=True
	)
	is_active = models.BooleanField(default=True)
	is_deleted = models.BooleanField(default=False)
	reset_token = models.CharField(max_length=255, null=True, blank=True)
	date_enregistrement = models.DateTimeField(null=True, blank=True)
	date_expiration_token = models.DateTimeField(null=True, blank=True)
	
	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['password']

	def __str__(self):
		return f'Recepteur {self.name}'

class Emetteur(Utilisateur):
	is_emetteur = models.BooleanField(default=True)
	def __str__(self):
		return f'Emetteur {self.name}'