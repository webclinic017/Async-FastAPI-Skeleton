import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from arq.connections import RedisSettings

REDIS_HOST = os.environ.get("REDIS_HOST", None)
REDIS_PORT = os.environ.get("REDIS_PORT", None)

EMAIL_PORT = os.environ.get("EMAIL_PORT", None)
EMAIL_SERVER = os.environ.get("EMAIL_SERVER", None)
FROM_EMAIL = os.environ.get("FROM_EMAIL", None)

REDIS_SETTINGS = RedisSettings(host=REDIS_HOST, port=REDIS_PORT)

#hardcoded subscribers
SUBSCRIBERS = ["sub1@emailserver.com", "sub2@emailserver.com"]


def create_body(subject: str, body: str) -> str:
    message = MIMEMultipart()

    message["Subject"] = subject
    message["From"] = FROM_EMAIL
    message.attach(MIMEText(body))

    return message.as_string()


async def send_emails(ctx, id: int):
    with smtplib.SMTP(host=EMAIL_SERVER, port=1025) as server:
        server.set_debuglevel(1)
        for to_email in SUBSCRIBERS:
            msg = create_body("Update notification", f"Record with ID {id} was updated")
            server.sendmail(FROM_EMAIL, to_email, msg)


async def startup(ctx):
    pass


async def shutdown(ctx):
    pass


class WorkerSettings:
    functions = [send_emails]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = REDIS_SETTINGS
