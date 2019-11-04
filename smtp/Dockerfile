FROM python:3.7-alpine

COPY smtp_debug.py /smtp_debug.py
EXPOSE 1025
CMD python /smtp_debug.py > mail.log