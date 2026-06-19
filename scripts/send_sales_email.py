#!/usr/bin/env python3
import argparse
import os
import smtplib
from email.message import EmailMessage


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--to", required=True)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--body", required=True)
    args = parser.parse_args()

    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ["SMTP_USER"]
    smtp_pass = os.environ["SMTP_PASS"]
    from_addr = os.environ.get("FROM_ADDR", smtp_user)
    from_name = os.environ.get("FROM_NAME", "Ranzaku")

    message = EmailMessage()
    message["From"] = f"{from_name} <{from_addr}>"
    message["To"] = args.to
    message["Subject"] = args.subject
    message.set_content(args.body)

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(message)


if __name__ == "__main__":
    main()
