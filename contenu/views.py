import datetime, pytz, psycopg2, csv, os, xlsxwriter
from accounts.models import Recepteur, Emetteur

from contenu.models import Message
from contenu.serializers import MessageSerializer, ExportSerializer

from django.conf import settings
from django.http import HttpResponse
from django.db import transaction, DatabaseError
from django.shortcuts import get_object_or_404

from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, action

from drf_haystack.viewsets import HaystackViewSet
from .serializers import ReportSerializer

utc = pytz.UTC
# Create your views here.
class MessageView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request):
		serializer = MessageSerializer(data=request.data)
		try:
			if serializer.is_valid(raise_exception=True):
				# check if the emetter is already stored..
				try:
					emetteur = Emetteur.objects.get(
						name=serializer.validated_data['nom_emetteur'])
				except Exception as vf:
					print('new emetter =>', vf)
					emetteur = Emetteur.objects.create(
						name=serializer.validated_data['nom_emetteur']
					)

				# now can save the new message..
				msg = Message.objects.create(
					num_recepteur=serializer.validated_data['num_recepteur'],
					recepteur=request.user,
					num_emetteur=serializer.validated_data['num_emetteur'],
					emetteur=emetteur,
					installation=serializer.validated_data['installation'],
					message=serializer.validated_data['message']
				)
				print('new msg => ', msg)
				#message = serializer.save(recepteur=request.user, emetteur=emetteur)
				liste = []
				messages = Message.objects.all().order_by('-id')
				for message in messages:
					rep = {}
					rep['id'] = message.id
					rep['num_recepteur'] = message.num_recepteur
					rep['recepteur'] = message.recepteur.name
					rep['num_emetteur'] = message.num_emetteur
					rep['emetteur'] = message.emetteur.name
					rep['installation'] = message.installation
					rep['message'] = message.message
					rep['date_message'] = message.date_message
					rep['modified_at'] = message.modified_at
					#rep.update(MessageSerializer(message).data)
					liste.append(rep)
				return Response(liste, status=status.HTTP_201_CREATED)
		except Exception as e:
			print('Save msg error => ', e)
			return Response(serializer.errors,
				status=status.HTTP_400_BAD_REQUEST)

	def put(self, request, id):
		""" Modifier un message """
		try:
			msg = Message.objects.get(pk=int(id))
		except Message.DoesNotExist:
			return Response({"message": "Message introuvable."},
				status=status.HTTP_404_NOT_FOUND)
		serializer = MessageSerializer(data=request.data)
		if serializer.is_valid(raise_exception=True):
			try:
				emetteur = Emetteur.objects.get(
					name=serializer.validated_data['nom_emetteur'])
			except Exception as vf:
				print('new emetter PUT =>', vf)
				emetteur = Emetteur.objects.create(
					name=serializer.validated_data['nom_emetteur']
				)
			try:
				with transaction.atomic():
					msg.num_recepteur = serializer.validated_data['num_recepteur']
					msg.num_emetteur = serializer.validated_data['num_emetteur']
					msg.emetteur = emetteur
					msg.installation = serializer.validated_data['installation']
					msg.message = serializer.validated_data['message']
					msg.modified_at = datetime.datetime.now().replace(tzinfo=utc)
					msg.modified_by = request.user.id
					msg.save()
				# sauvegarde ok, rendre le message..
				rep = {}
				rep['id'] = msg.id
				rep['num_recepteur'] = msg.num_recepteur
				rep['recepteur'] = msg.recepteur.name
				rep['num_emetteur'] = msg.num_emetteur
				rep['emetteur'] = msg.emetteur.name
				rep['installation'] = msg.installation
				rep['message'] = msg.message
				rep['date_message'] = msg.date_message
				rep['modified_at'] = msg.modified_at
				rep['modified_by'] = Recepteur.objects.get(pk=int(msg.modified_by)).name
				return Response(rep, status=status.HTTP_200_OK)
			except DatabaseError as d:
				print('err modif msg => ', d)
				return Response({'message': f"err modif msg {d}"},
					status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		return Response(serializer.error,
			status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request, id):
		""" Supprimer un message """
		try:
			msg = Message.objects.get(pk=int(id))
		except Message.DoesNotExist:
			return Response({"message": "Message introuvable."},
				status=status.HTTP_404_NOT_FOUND)
		# proceed to the deletion..
		msg.delete()
		return Response({"message": "Suppression OK"},
			status=status.HTTP_200_OK)

	def get(self, request, id):
		"""Details sur un message"""
		try:
			msg = Message.objects.get(pk=int(id))
		except Message.DoesNotExist:
			return Response({"message": "Message introuvable."},
				status=status.HTTP_404_NOT_FOUND)
		# details..
		rep = {}
		rep['id'] = msg.id
		rep['num_emetteur'] = msg.num_emetteur
		rep['emetteur'] = msg.emetteur.name
		rep['num_recepteur'] = msg.num_recepteur
		rep['recepteur'] = msg.recepteur.name
		rep['installation'] = msg.installation
		rep['message'] = msg.message
		rep['date_message'] = msg.date_message
		rep['modified_at'] = msg.modified_at
		rep['modified_by'] = Recepteur.objects.get(
			pk=msg.modified_by).name if msg.modified_by > 0 else None
		return Response(rep, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def liste_messages(request):
	liste = []
	messages = Message.objects.all().order_by('-id')
	for message in messages:
		rep = {}
		rep['id'] = message.id
		rep['num_emetteur'] = message.num_emetteur
		rep['emetteur'] = message.emetteur.name
		rep['num_recepteur'] = message.num_recepteur
		rep['recepteur'] = message.recepteur.name
		rep['installation'] = message.installation
		rep['message'] = message.message
		rep['date_message'] = message.date_message
		rep['modified_at'] = message.modified_at
		liste.append(rep)
	return Response(liste, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_info_recepteur(request):
	"""Recupere les donnees du user en cours"""
	recepteur = request.user
	rep = {}
	rep['id'] = recepteur.id
	rep['nom'] = recepteur.name
	rep['prenom'] = recepteur.surname
	rep['email'] = recepteur.email
	rep['telephone'] = recepteur.phone
	rep['date_inscription'] = recepteur.date_enregistrement
	return Response(rep, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_data_recepteur(request):
	"""change the current user's data"""
	recepteur = request.user
	try:
		with transaction.atomic():
			recepteur.name = request.data['nom']
			recepteur.surname = request.data['prenom']
			recepteur.phone = request.data['phone']
			recepteur.save()
			rep = {}
			rep['id'] = recepteur.id
			rep['nom'] = recepteur.name
			rep['prenom'] = recepteur.surname
			rep['email'] = recepteur.email
			rep['telephone'] = recepteur.phone
			rep['date_inscription'] = recepteur.date_enregistrement
			return Response(rep, status=status.HTTP_200_OK)
	except DatabaseError as e:
		print('err change recp => ', e)
		return Response({'message': f'Erreur profile -> {e}'},
			status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def export_message(request):
	"""Api d'export de messages version excel"""
	try:
		serializer = ExportSerializer(data=request.data)
		if serializer.is_valid(raise_exception=True):
			# A ce stade on fetch les messages..
			date_debut = serializer.validated_data['date_debut']
			date_fin = serializer.validated_data['date_fin']
			messages = Message.objects.filter(
				date_message__lte=date_fin,
				date_message__gte=date_debut
			).order_by('-date_message')
			repertoire = f'{settings.MEDIA_ROOT}'.replace('\\', '/')
			if not os.path.exists(repertoire):
				os.makedirs(repertoire, exist_ok=True)
			nom_fichier = 'report_message.xlsx'
			chemin_file = f'{repertoire}/{nom_fichier}'
			workbook = xlsxwriter.Workbook(chemin_file)
			worksheet = workbook.add_worksheet('messages')
			worksheet.write(0, 0, 'Numero Recepteur')
			worksheet.write(0, 1, 'Recepteur')
			worksheet.write(0, 2, 'Numero Emetteur')
			worksheet.write(0, 3, 'Emetteur')
			worksheet.write(0, 4, 'Installation')
			worksheet.write(0, 5, 'Message')
			worksheet.write(0, 6, 'Date enregistrement')
			worksheet.write(0, 7, 'Date modification')
			worksheet.write(0, 8, 'Modifie par')
		
			ligne = 1
			colonne = 0
			for msg in messages:
				recepteur = msg.recepteur.name
				emetteur = msg.emetteur.name
				modifier = Recepteur.objects.get(pk=msg.modified_by).name if msg.modified_by > 0 else None
				worksheet.write(ligne, colonne, msg.num_recepteur)
				worksheet.write(ligne, colonne+1, recepteur)
				worksheet.write(ligne, colonne+2, str(msg.num_emetteur))
				worksheet.write(ligne, colonne+3, emetteur)
				worksheet.write(ligne, colonne+4, msg.installation)
				worksheet.write(ligne, colonne+5, msg.message)
				worksheet.write(ligne, colonne+6, msg.date_message.strftime('%d/%m/%Y %X') if msg.date_message is not None else msg.date_message)
				worksheet.write(ligne, colonne+7, msg.modified_at.strftime('%d/%m/%Y %X') if msg.modified_at is not None else msg.modified_at)
				worksheet.write(ligne, colonne+8, modifier)
				ligne += 1

			workbook.close()
			# Tu vas renvoyer le lien d'acces au fichier au web...
			path_file = os.path.join(
				f'{request.scheme}://',
				request.get_host(),
				f'media/{nom_fichier}'
			).replace('\\', '/')
			return Response(
				{'chemin_fichier': path_file}, status=status.HTTP_200_OK)
	except Exception as ed:
		print('what the hell => ', ed)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MessageViewSet(viewsets.ViewSet):
	""" Test viewset sur le modele Message """
	permission_classes = [IsAuthenticated]
	queryset = Message.objects.all().order_by('-id')
	serializer_class = MessageSerializer
		
	def list(self, request):
		serializer = self.serializer_class(self.queryset, many=True)
		return Response(serializer.data)

	@action(detail=False, methods=['GET'])
	def custom_get_emetteur(self, request, pk=None):
		message = get_object_or_404(queryset, pk=1)
		emetteur = Emetteur.objects.get(pk=message.emetteur.pk)
		print('bato =>', emetteur)


class ReportView(HaystackViewSet):
	index_models = [Message]
	serializer_class = ReportSerializer