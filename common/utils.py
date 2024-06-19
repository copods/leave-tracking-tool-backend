import os
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from email.mime.image import MIMEImage
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection


def send_email(recipients, send_from=None, leave_email_info=None):
    try:
        if not isinstance(recipients, list):
            recipients = [recipients]
        
        parent_dir = os.path.dirname(settings.BASE_DIR)
        logo_path = os.path.join(parent_dir, 'common', 'templates', 'logo.png')
        
        emails = []

        for recipient in recipients:

            recipient_name = f"{recipient['first_name']} {recipient['last_name']}"
            context = { 'recipient_name': recipient_name, }

            if leave_email_info:
                context['subject'] = leave_email_info['subject']
                context['leave_text'] = leave_email_info['leave_text']
                html_file = 'leave_notification_template.html'

            else:
                context['subject'] = 'Your Leave Management Platform Awaits!'
                html_file = 'onboarding_template.html'
                
            html_message = render_to_string(html_file, context)
            plain_message = strip_tags(html_message)  # HTML to plain text

            from_email = send_from['email'] if send_from else "richa@copods.co"
            recipient_list = [recipient['email']]

            email = EmailMultiAlternatives(
                context['subject'],
                plain_message,
                from_email,
                recipient_list
            )
            email.attach_alternative(html_message, "text/html")

            # Attach the logo image
            with open(logo_path, 'rb') as img_file:
                logo_image = MIMEImage(img_file.read())
                logo_image.add_header('Content-ID', '<logo>')  # Match the CID used in the HTML img src
                email.attach(logo_image)

            emails.append(email)

        connection = get_connection()
        connection.send_messages(emails)

    except Exception as e:
        raise e