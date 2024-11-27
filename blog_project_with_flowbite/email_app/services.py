from concurrent.futures import ThreadPoolExecutor
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from utils.herlpers import pro_print


class EmailService:
    # Create a thread pool with max workers
    _executor = ThreadPoolExecutor(max_workers=3)

    @staticmethod
    def send_email(subject, template_name, context, recipient_list):
        """
        Send email using a template
        """
        template_path = f"email_app/emails/{template_name}"
        html_message = render_to_string(template_path, context)

        def send_email_task():
            try:
                send_mail(
                    subject=subject,
                    message="",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=recipient_list,
                    html_message=html_message,
                    fail_silently=False,
                )
                return True
            except Exception as error:
                pro_print(error, f"Email sending failed: {str(error)}")
                return False

        # Submit task to thread poll instead of creating new thread
        EmailService._executor.submit(send_email_task)
        return True

    @classmethod
    def send_welcome_email(cls, user_email, username):
        """
        Send welcome email to new users
        """
        return cls.send_email(
            subject="Welcome to Zenset!",
            template_name="welcome.html",
            context={"username": username},
            recipient_list=[user_email],
        )

    @classmethod
    def send_notification_email(cls, user_email, notification_type, **kwargs):
        """
        Send notification emails ( Comments, follow, etc, )
        """
        return cls.send_email(
            subject=f"New {notification_type} on Zenset",
            template_name="notification.html",
            context=kwargs,
            recipient_list=[user_email],
        )

    @classmethod
    def send_password_reset_email(cls, user_email, reset_link, **kwargs):
        """
        Send email to reset password
        """
        kwargs["reset_link"] = reset_link

        return cls.send_email(
            f"Recover Your Zenset Password",
            template_name="pass_reset.html",
            context=kwargs,
            recipient_list=[user_email],
        )
