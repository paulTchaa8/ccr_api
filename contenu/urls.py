from django.urls import path, include
from accounts.views import (RecepteurView, ConnexionView)
from contenu.views import (MessageView, liste_messages, ReportView,
	get_info_recepteur, change_data_recepteur, export_message,MessageViewSet)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('liste/messages', MessageViewSet, basename="messageviewset")
router.register('reports', ReportView, basename="reportview")

urlpatterns = [
	path('message', MessageView.as_view(), name="message"),
	path('messages', liste_messages, name="messages"),
	path('messages/<int:id>', MessageView.as_view(), name="message_id"),
	path('accounts/me', get_info_recepteur, name="get_info_recepteur"),
	path('accounts/change',
		change_data_recepteur, name="change_data_recepteur"),
	path('messages/export',
		export_message, name="export_message"),
] + router.urls