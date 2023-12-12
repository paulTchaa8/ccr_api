from accounts.models import Recepteur
from accounts.serializers import (
	RecepteurSerializer, CheckPhoneSerializer, CheckPasswordSerializer,
	ConnexionSerializer, ForgotPasswordSerializer, VerifyTokenSerializer,
	NewPasswordSerializer)
from hashlib import md5
from uuid import uuid4
import datetime, os, re, threading, pytz
from django.conf import settings
from django.core.mail import BadHeaderError
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .utilitaires import send_all_mail

# Create your views here.
utc = pytz.UTC

class RecepteurView(APIView):
	"""Classe de creation de compte utilisateur"""
	permission_classes = [AllowAny]
	def post(self, request):
		try:
			serializer = RecepteurSerializer(data=request.data)
			check_password = CheckPasswordSerializer(data=request.data)
			if serializer.is_valid(raise_exception=True) \
				and check_password.is_valid(raise_exception=True):
				try:
					user = Recepteur.objects.get(
						email=serializer.validated_data['email'])
					if user.exists():
						return Response({"message": "User already registered!"},
							status=status.HTTP_409_CONFLICT)

				except Recepteur.DoesNotExist:
					# nouveau recepteur, enregistrer
					new = Recepteur.objects.create(
						name=serializer.validated_data['name'],
						surname=serializer.validated_data['surname'],
						email=serializer.validated_data['email'],
						password=md5(
							serializer.validated_data['password'].encode()
							).hexdigest(),
						is_active=False
					)
					# delai validite..
					date_courante = datetime.datetime.now()
					delai_token = datetime.timedelta(hours=1, minutes=00)
					date_expiration = date_courante + delai_token
					new.date_expiration_token = date_expiration

					# code de reinitialisation..
					reset_token = uuid4()
					new.reset_token = reset_token
					new.save()
					
					# envoi d'email Message de bienvenue..
					subject = 'Message de bienvenue'
					val = {
						'url_confirm': request.scheme + '://' + request.get_host() + '/api/users/enable/' + str(reset_token),
						'site_name': 'CCR App',
						'nom': new.name,
						'prenom': new.surname,
	                    'login_url': settings.LOGIN_URL
					}

					html_content = render_to_string(
					    'email/new_user.html', val)
					text_content = strip_tags(html_content)
					email_from = settings.EMAIL_HOST_USER
					recipient_list = [serializer.validated_data['email']]

					# envoi effectif ici..
					thread = threading.Thread(target=send_all_mail, args=(subject, email_from, recipient_list, html_content, text_content))
					thread.start()

					return Response(RecepteurSerializer(new).data,
						status.HTTP_201_CREATED)

		except Exception as e:
			print(f'erreur enregistrement user -> {e}')
			return Response({"message": f"{e}"},
				status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def enable_user(request, reset_token=None):
	"""
	Api d'activation recepteur lorsqu'il confirme son compte
	"""
	try:
		user = Recepteur.objects.get(
			reset_token=reset_token, is_active=False)

		try:
			# je verifie si le delai d'activation n'est pas ecoule..
			current_time = datetime.datetime.now().replace(tzinfo=utc)
			date_expiration_user = user.date_expiration_token.replace(tzinfo=utc)

			if current_time > date_expiration_user:
				# delai ecoule, ne peut plus activer de compte..
				return redirect(settings.LOGIN_URL + '/?status=invalid')
				"""
				return Response({
					"message": "Le délai d'activation de ce compte est écoulé.",
					"statut": 2
					}, status=status.HTTP_400_BAD_REQUEST)
				"""
			# A ce stade, on est dans les temps..
			user.is_active = True
			user.date_expiration_token = None
			user.date_enregistrement = current_time
			user.save()

			return redirect(settings.LOGIN_URL + '/?status=valid')
		except Exception as e:
			# date_expiration_token a None, requete invalide..
			return redirect(settings.LOGIN_URL + '/?status=invalid')

	except Recepteur.DoesNotExist:
		return redirect(settings.LOGIN_URL + '/?status=invalid')


class ConnexionView(APIView):
	""" Classe de connexion a l'application """
	permission_classes = [AllowAny]
	def post(self, request):
		try:
			serializer = ConnexionSerializer(data=request.data)
			serializer.is_valid(raise_exception=True)
			try:
				recepteur = Recepteur.objects.get(
					email=serializer.validated_data['email'],
					password=md5(serializer.validated_data['password'].encode()
						).hexdigest(),
					is_active=True,
					is_deleted=False
				)

			except Recepteur.DoesNotExist:
				return Response(
	                {'message': 'Recepteur inexistant ou non actif.',
	                'statut': 2
	                }, status=status.HTTP_404_NOT_FOUND
            	)
            
			token = Token.objects.get_or_create(user=recepteur)[0]

			return Response({
				"token": token.key,
				"nom": recepteur.name,
				"prenom": recepteur.surname,
				"user_id": recepteur.id,
				"email": recepteur.email
			}, status.HTTP_200_OK)

		except Exception as e:
			print('erreur connex =>', e)
			return Response({
				"message": f"Erreur connexion -> {e}",
				"statut": 2
			}, status=status.HTTP_400_BAD_REQUEST)


class Logout(APIView):
	""" classe de deconnexion """
	permission_classes = [IsAuthenticated]

	def get(self, request, format=None):
		# je supprime le token associe a cet utilisateur..
		try:
			request.user.auth_token.delete()
			return Response({
				"message": "Déconnexion réussie!",
				"statut": 0
			}, status=status.HTTP_200_OK)
		except Exception as e:
			return Response({
				"message": "Utilisateur inexistant!",
				"statut": 2
			}, status=status.HTTP_400_BAD_REQUEST)

class ForgotPassword(APIView):
	permission_classes=[AllowAny]
	def post(self, request):
		try:
			serializer = ForgotPasswordSerializer(data=request.data)
			if serializer.is_valid(raise_exception=True):
				try:
					recepteur = Recepteur.objects.get(
						email=serializer.validated_data['email'],
						is_deleted=False)

				except Recepteur.DoesNotExist:
					return Response({
						"message": "Recepteur inexistant"
						}, status.HTTP_400_BAD_REQUEST)
				
				# duree de validite ..
				date_courante = datetime.datetime.now()
				delai_token = datetime.timedelta(hours=1, minutes=00)
				date_expiration = date_courante + delai_token
				recepteur.date_expiration_token = date_expiration
				# code de reinitialisation..
				reset_token = uuid4()
				recepteur.reset_token = reset_token
				# envoi d'email demande prise en compte..
				subject = 'Mot de passe oublié'
				val = {
					'url_reset': settings.SITE_URL + 'reset-password/?reset_token=' + str(reset_token),
					'site_name': 'CCR App',
					'site_url': settings.SITE_URL
				}

				html_content = render_to_string(
				    'email/forgot_password.html', val)
				text_content = strip_tags(html_content)
				email_from = settings.EMAIL_HOST_USER
				recipient_list = [serializer.validated_data['email']]

				try:
					# envoi effectif ici..
					thread = threading.Thread(
						target=send_all_mail,
						args=(subject, email_from, recipient_list, html_content, text_content))
					thread.start()
					recepteur.save()

					return Response({
						"message": "Demande prise en compte",
						"statut": 0
						}, status=status.HTTP_200_OK)

				except Exception as errconn:
					print("Pb envoi email =>", errconn)
					return Response({
						"message": "Verifiez votre connexion puis reessayez.",
						"statut": 0},
						status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			print('erreur =>', e)
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_token(request):
	""" API de verification du token """
	try:
		serializer = VerifyTokenSerializer(data=request.data)
		if serializer.is_valid(raise_exception=True):
			# je check en BD si un user avec ce token existe..
			try:
				print(serializer.validated_data)
				recep = Recepteur.objects.get(
				reset_token=serializer.validated_data['reset_token'],
				is_deleted=False)
				print('userrrrr', recep)
                
                # je verifie si le delai de reinitialisation n'est pas ecoule..
				current_time = datetime.datetime.now().replace(tzinfo=utc)
				print('redee => ', current_time)
				try:
					date_expiration_user = recep.date_expiration_token.replace(tzinfo=utc)
					if current_time > date_expiration_user:
						# delai ecoule, ne peut plus activer de compte..
						return Response({"message": "Token invalide.", "statut": 1},
                            status=status.HTTP_400_BAD_REQUEST)
				except Exception as e:
					# deja renitialise..
					return Response({
                    "message": "Lien déjà expiré.",
                    "statut": 1}, status=status.HTTP_400_BAD_REQUEST)
				
                # C'est un token valide..
				return Response({"message": "Token valide.", "statut": 0},
					status=status.HTTP_200_OK)

			except Recepteur.DoesNotExist:
				# Token invalide..
				return Response({"message": "Token invalide !", "status": 1},
					status=status.HTTP_400_BAD_REQUEST)
	
	except Exception as e:
		return Response(
			serializer.errors,
			status=status.HTTP_400_BAD_REQUEST)

class InitPassword(APIView):
	""" classe de reinitialisation du mot de passe """
	permission_classes=[AllowAny]
	def post(self, request, reset_token=None):
		try:
			serializer = NewPasswordSerializer(data=request.data)

			if serializer.is_valid(raise_exception=True):
				try:
					user = Recepteur.objects.get(
						reset_token=reset_token,
						is_deleted=False
					)
				except Recepteur.DoesNotExist:
					return Response(
				        {
				            "detail": "Recepteur inexistant ou lien désactivé.",
				            "statut": 2
				        },status=status.HTTP_404_NOT_FOUND)

				# je verifie si le delai de reinitialisation n'est pas ecoule..
				current_time = datetime.datetime.now().replace(tzinfo=utc)

				date_expiration_user = user.date_expiration_token.replace(tzinfo=utc)

				if current_time > date_expiration_user:
					# delai ecoule, ne peut plus activer de compte..
					return Response({
						"message": "Le lien de réinitialisation n'est plus actif.",
						"statut": 2
						}, status=status.HTTP_400_BAD_REQUEST)


				# on est dans les delais ici..
				new_password = serializer.validated_data['new_password']
				confirm_password = serializer.validated_data['confirm_password']
	           	
				if new_password != confirm_password:
					return Response({
					"detail": "The new password and confirm password don't match",
					"statut": 1
						}, status=status.HTTP_400_BAD_REQUEST)

				# on modifie le mot de passe ici ET on active le user...
				user.password = md5(new_password.encode()).hexdigest()
				user.date_expiration_token = None
				user.is_active = True

				user.save()

				del new_password, confirm_password, date_expiration_user, current_time
				#return redirect(settings.LOGIN_URL)
				return Response({"message": "Password changed successfully","statut": 0}, status=status.HTTP_200_OK)

		except Exception as e:
			print('Reinitialisation Err ->', e)
			return Response(
				serializer.errors, status=status.HTTP_400_BAD_REQUEST)
