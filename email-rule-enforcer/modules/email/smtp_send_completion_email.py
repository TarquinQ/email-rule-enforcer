from modules.email.smtp_send import send_email_from_config
from modules.email.make_new_emails import new_email_nonmultipart


def smtp_send_completion_email(config, display_body):

    if (False and config['send_notification_email_on_completion']):
        # Build Email
        email_to_send = new_email_forward(
            new_email_nonmultipart(
                email_from=config['smtp_forward_from'],
                email_to=action_to_perform.email_recipients,
                subject='FWD: ' + email_to_validate['subject'],
                bodytext="Forwarded Email Attached",
                email_to_attach=email_to_attach
            )
        )
        send_email_from_config(config, email_to_send)
