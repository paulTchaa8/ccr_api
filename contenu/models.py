from django.db import models
from accounts.models import Recepteur, Emetteur

# Create your models here.
class Message(models.Model):
	"""classe contenant les messages du ccr"""
	num_recepteur = models.CharField(max_length=255)
	recepteur = models.ForeignKey(
		Recepteur,
		on_delete=models.PROTECT,
		null=True
	)
	num_emetteur = models.CharField(max_length=255)
	emetteur = models.ForeignKey(
		Emetteur,
		on_delete=models.PROTECT,
		null=True
	)
	installation = models.CharField(max_length=255)
	message = models.TextField(blank=True, null=True)
	date_message = models.DateTimeField(auto_now_add=True)
	modified_at = models.DateTimeField(null=True)
	modified_by = models.PositiveIntegerField(default=0)