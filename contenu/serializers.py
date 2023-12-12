from contenu.models import Message
from accounts.models import Recepteur, Emetteur
from rest_framework import serializers
from drf_haystack.serializers import HaystackSerializer
from .search_indexes import ReportIndex

class MessageSerializer(serializers.ModelSerializer):
	"""
	Transforme un objet Message en du json serialisable
	"""
	nom_emetteur = serializers.CharField(max_length=255)
	#emetteur = serializers.StringRelatedField(read_only=True)
	class Meta:
		model = Message
		fields = ['num_recepteur', 'num_emetteur', 'nom_emetteur',
			'installation', 'message']

class ExportSerializer(serializers.Serializer):
	date_debut = serializers.DateField()
	date_fin = serializers.DateField()

class ReportSerializer(HaystackSerializer):
	class Meta:
		index_classes = [ReportIndex]
		fields = ['text', 'num_recepteur', 'recepteur', 'num_emetteur',
			'emetteur', 'installation', 'message', 'date_message', 'id']