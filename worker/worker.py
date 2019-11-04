import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from arq.connections import RedisSettings

REDIS_HOST = os.environ.get("REDIS_HOST", None)
REDIS_PORT = os.environ.get("REDIS_PORT", None)

EMAIL_PORT = os.environ.get("EMAIL_PORT", None)
EMAIL_SERVER = os.environ.get("EMAIL_SERVER", None)
FROM_EMAIL = os.environ.get("FROM_EMAIL", None)

REDIS_SETTINGS = RedisSettings(host=REDIS_HOST, port=REDIS_PORT)

SUBSCRIBERS = ["sub1@emailserver.com", "sub2@emailserver.com"]


def create_body(subject: str, body: str) -> str:
    """Creates an email body with the preset email sender
    Args:
        subject: Subject of the email
        body: Contents of the email

    Returns: Constructed message as a string
    """
    message = MIMEMultipart()

    message["Subject"] = subject
    message["From"] = FROM_EMAIL
    message.attach(MIMEText(body))

    return message.as_string()


async def send_emails(ctx, id: int):
    """Sends update alerts to the subscribed emails that a particular record has been updated
    Args:
        ctx: Context for the enqueued task
        id: ID of the record that was updated
    """
    server = ctx['server']

    for to_email in SUBSCRIBERS:
        msg = create_body(
            "Update notification",
            f"Record with ID {id} was updated")
        server.sendmail(FROM_EMAIL, to_email, msg)


async def startup(ctx):
    """Function to run on worker startup
    Args:
        ctx: Context for the enqueued task
    """
    ctx['server'] = smtplib.SMTP(host=EMAIL_SERVER, port=1025)
    ctx['server'].set_debuglevel(1)


async def shutdown(ctx):
    """Function to run on worker startup
    Args:
        ctx: Context for the enqueued task
    """
    await ctx['server'].close()


class WorkerSettings:
    """Settings for the Arq worker to use when running jobs"""
    functions = [send_emails]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = REDIS_SETTINGS
