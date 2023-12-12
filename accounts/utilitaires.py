from django.core.mail import send_mail

# Fonction utilitaire d'envoi d'emails..
def send_all_mail(subject, email_from, recipient_list, html_content, text_content):
    send_mail(subject, None,
    	email_from, recipient_list, html_message=html_content)