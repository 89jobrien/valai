import smtplib
from email.message import EmailMessage

from loguru import logger
from pydantic import BaseModel, EmailStr, Field

from valai.config import get_settings


class SendEmailArgs(BaseModel):
    """Input model for the send_email tool."""

    recipient: EmailStr = Field(..., description="The email address of the recipient.")
    subject: str = Field(..., description="The subject line of the email.")
    body: str = Field(..., description="The main content/body of the email.")


def send_email(args: SendEmailArgs) -> str:
    """Sends an email to a specified recipient using pre-configured SMTP settings."""
    settings = get_settings()

    required_settings = [
        settings.smtp_host,
        settings.smtp_port,
        settings.smtp_user,
        settings.smtp_password,
    ]
    if not all(required_settings):
        logger.error("SMTP settings are not fully configured.")
        return "Error: SMTP settings are not fully configured. Please contact the administrator."

    msg = EmailMessage()
    msg.set_content(args.body)
    msg["Subject"] = args.subject
    msg["From"] = settings.smtp_user
    msg["To"] = args.recipient

    try:
        logger.info(
            f"Attempting to send email to {args.recipient} via {settings.smtp_host}"
        )
        with smtplib.SMTP_SSL(
            settings.smtp_host, settings.smtp_port, timeout=10
        ) as server:
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
        logger.success(f"Email successfully sent to {args.recipient}.")
        return f"Email successfully sent to {args.recipient}."
    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP authentication failed. Check username/password.")
        return "Error: Email authentication failed. Please check your SMTP credentials."
    except smtplib.SMTPConnectError:
        logger.error(f"Failed to connect to SMTP server at {settings.smtp_host}.")
        return "Error: Could not connect to the email server."
    except smtplib.SMTPServerDisconnected:
        logger.error("SMTP server disconnected unexpectedly.")
        return "Error: The connection to the email server was lost."
    except (TimeoutError, smtplib.SMTPException) as e:
        logger.error(f"A network or SMTP error occurred: {e}")
        return f"A network error occurred while trying to send the email: {e}"
    except Exception as e:
        logger.opt(exception=True).error(
            f"An unexpected error occurred while sending email: {e}"
        )
        return f"An unexpected error occurred: {e}"
