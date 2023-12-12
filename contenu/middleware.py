import requests
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

class StackOverflowMiddleware(MiddlewareMixin):
	""" 
	classe Middleware pour recuperer les liens d'aide,
	suite a une exception levee
	"""
	def __init__(self, get_response):
		self.get_response = get_response
		self.async_capable = True
		self.async_capable = True
		self.url = 'https://api.stackexchange.com/2.3/search'
		self.headers = { 'User-Agent': 'github.com/paulTchaa8/Dimensionnement' }
		self.params = {
			'order': 'desc',
			'sort': 'votes',
			'site': 'stackoverflow',
			'pagesize': 3,
			'tagged': 'python;django'
		}

	def process_exception(self, request, exception):
		"""Methode appelee lorsqu'une exception est levee"""
		if settings.DEBUG:
			intitle = u'{}: {}'.format(
				exception.__class__.__name__,  str(exception))
			self.params['intitle'] = intitle
			r = requests.get(
				self.url, params=self.params, headers=self.headers)
			questions = r.json()
			print('--------- Liens du bug Middleware ---------')
			for q in questions['items']:
				print(f'titre: {q["title"]}')
				print(f'lien: {q["link"]}\n')
			print('--------- Fin Middleware stackoverflow ---------')
		# on ne perturbe pas le flow normal de la reponse..
		return None