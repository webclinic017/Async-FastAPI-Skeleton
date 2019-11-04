#!/usr/bin/env python
import smtpd
import asyncore
import logging

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    smtp_server = smtpd.DebuggingServer(('0.0.0.0', 1025),None)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        smtp_server.close()
