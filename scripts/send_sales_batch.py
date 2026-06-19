#!/usr/bin/env python3
import csv
import os
import smtplib
from email.message import EmailMessage
from pathlib import Path


def build_body(company_name: str, contact_name: str, title: str) -> str:
    greeting = f"{contact_name}様" if contact_name else "ご担当者様"
    context = f"{title}" if title else "ご担当領域"
    return f"""{greeting}

突然のご連絡失礼します。
住宅・建設・リフォームの現場では、提案作成、顧客対応、引き継ぎにかなりの手作業が残っていることが多いと感じています。
私たちranzakuは、その業務をAIで標準化する取り組みを進めています。
{company_name}様の{context}の観点で、もし関心があれば15分だけ現状の運用を伺えればと思っています。
"""


def send_message(to_addr: str, subject: str, body: str) -> None:
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ["SMTP_USER"]
    smtp_pass = os.environ["SMTP_PASS"]
    from_addr = os.environ.get("FROM_ADDR", smtp_user)
    from_name = os.environ.get("FROM_NAME", "Ranzaku")

    message = EmailMessage()
    message["From"] = f"{from_name} <{from_addr}>"
    message["To"] = to_addr
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(message)


def main():
    leads_path = Path(os.environ.get("LEADS_PATH", "07_sales_cs/outreach/leads.private.csv"))
    if not leads_path.exists():
        raise SystemExit(f"Missing {leads_path}")

    with leads_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("status", "").lower() not in {"new", "retry"}:
                continue
            to_addr = row.get("email", "").strip()
            if not to_addr:
                continue
            company_name = row.get("company_name", "").strip()
            contact_name = row.get("contact_name", "").strip()
            title = row.get("title", "").strip()
            subject = "提案作成と引き継ぎの手作業をAIで減らせないかと思い、ご連絡しました"
            body = build_body(company_name, contact_name, title)
            send_message(to_addr, subject, body)


if __name__ == "__main__":
    main()
