from haystack import indexes
from .models import Message
from datetime import datetime


class ReportIndex(indexes.SearchIndex, indexes.Indexable):
	text = indexes.CharField(document=True, use_template=True)
	num_recepteur = indexes.CharField(model_attr="num_recepteur")
	recepteur = indexes.CharField(model_attr="recepteur__name")
	num_emetteur = indexes.CharField(model_attr="num_emetteur")
	emetteur = indexes.CharField(model_attr="emetteur__name")
	installation = indexes.CharField(model_attr="installation")
	message = indexes.CharField(model_attr="message", faceted=True)
	id = indexes.IntegerField(model_attr="pk")
	#date_message = indexes.DateTimeField(model_attr="date_message")

	def get_model(self):
		return Message

	def prepare_id(self, obj):
		return obj.id

	def prepare_date_message(self, obj):
		date_str = str(obj.date_message).split('.')[0]
		print(f'1 -> {date_str}')
		#return obj.date_message.strftime('%Y-%m-%d %H:%M:%SZ')
		return datetime.strptime(
			date_str, 
			'%Y-%m-%d %H:%M:%S'
		)
		#return str(obj.date_message)

	def index_queryset(self, using=None):
		"""utilise lorsque l'index est entierement mis a jour"""
		return self.get_model().objects.all().order_by('-id')
