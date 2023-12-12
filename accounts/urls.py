from django.urls import path, include
from accounts.views import (RecepteurView, ConnexionView, enable_user,
	Logout, ForgotPassword, verify_token, InitPassword)

urlpatterns = [
	path('register', RecepteurView.as_view(), name="register"),
	path('login', ConnexionView.as_view(), name="login"),
	path('logout', Logout.as_view(), name="logout"),
	path(
		'users/enable/<str:reset_token>',
		enable_user, 
		name="enable_user"
	),
	path(
		'forgot-password',
		ForgotPassword.as_view(),
		name="forgot-password"
	),
	path('verify-token', verify_token, name="verify_token"),
	path(
		'reset-password/<str:reset_token>',
		InitPassword.as_view(),
		name="reset-password"
	),
]