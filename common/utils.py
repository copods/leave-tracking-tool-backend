from django.conf import settings
from django.template import Context, Template
from django.core.mail import EmailMultiAlternatives, get_connection
from django.utils.html import strip_tags
from email.mime.image import MIMEImage
import os

def send_email(recipients, subject, template_name, context, send_from=None, app_name=None):
    try:
        if not isinstance(recipients, list):
            recipients = [recipients]

        from_email = send_from['email'] if send_from else "kalash.bhagwat@copods.co"
        parent_dir = os.path.dirname(settings.BASE_DIR)
        logo_path = os.path.join(parent_dir, 'common', 'templates', 'logo.png')

        emails = []

        for recipient in recipients:
            recipient_name = f"{recipient['first_name']} {recipient['last_name']}"
            context['recipient_name'] = recipient_name

            template_path = os.path.join(parent_dir, app_name, 'templates', template_name)

            # Read template content from the specified file path
            with open(template_path, 'r') as template_file:
                template_content = template_file.read()

            template = Template(template_content)

            html_message = template.render(Context(context))
            plain_message = strip_tags(html_message)

            recipient_list = [recipient['email']]

            email = EmailMultiAlternatives(
                subject,
                plain_message,
                from_email,
                recipient_list
            )
            email.attach_alternative(html_message, "text/html")

            with open(logo_path, 'rb') as img_file:
                logo_image = MIMEImage(img_file.read())
                logo_image.add_header('Content-ID', '<logo>')
                email.attach(logo_image)

            emails.append(email)

        connection = get_connection()
        connection.send_messages(emails)

    except Exception as e:
        raise e