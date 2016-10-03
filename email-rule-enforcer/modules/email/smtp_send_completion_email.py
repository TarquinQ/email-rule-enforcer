from modules.email.smtp_send import send_email_from_config
from modules.email.make_new_emails import new_email_nonmultipart


def smtp_send_completion_email(config, display_body):
    if (config['send_notification_email_on_completion']):
        email_details = config['notification_email_on_completion']

        email_to_send = new_email_nonmultipart(
            email_from=config['smtp_forward_from'],
            email_to=email_details.recipients,
            subject=email_details.subject,
            bodytext=email_details.body_prefix + '\n\n' + display_body,
        )

        send_email_from_config(config, email_to_send)

