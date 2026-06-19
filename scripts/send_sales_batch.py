#!/usr/bin/env python3
import argparse
import csv
import os
import re
import smtplib
from dataclasses import dataclass
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Iterable


DEFAULT_LEADS_PATH = Path("07_sales_cs/outreach/leads.private.csv")
DEFAULT_LOG_PATH = Path("07_sales_cs/outreach/send-log.md")


@dataclass(frozen=True)
class Campaign:
    subject_lines: tuple[str, ...]
    opening: str
    value: str
    cta: str
    closing: str


CAMPAIGNS: dict[str, Campaign] = {
    "campaign-001": Campaign(
        subject_lines=(
            "提案作成と引き継ぎの手作業を減らす相談",
            "案件引き継ぎのムダを減らす件",
            "現場の手戻りを減らす運用の相談",
        ),
        opening="住宅・建設・リフォームの現場では、提案作成、案件引き継ぎ、顧客対応の手間が想像以上に積み上がりやすいと見ています。",
        value="ranzakuは、その入口業務をAIで標準化し、担当者ごとのばらつきと手戻りを減らす支援をしています。",
        cta="もし関心があれば、15分だけ現状の運用を伺い、どこで時間と情報が落ちているか整理します。",
        closing="ranzaku",
    ),
    "campaign-002": Campaign(
        subject_lines=(
            "運用の見えない工数を減らす相談",
            "社内調整の手間を軽くする提案",
            "引き継ぎ負荷を下げる件",
        ),
        opening="社内調整や情報の行き違いが増えると、案件は前に進んでいても、裏側の工数だけが膨らみます。",
        value="ranzakuは、会話や資料をそのまま標準化し、隠れた調整コストを減らすための仕組みをつくっています。",
        cta="今の運用で一番詰まりやすい箇所を1つだけ教えていただければ、削れる部分を具体化します。",
        closing="ranzaku",
    ),
    "campaign-003": Campaign(
        subject_lines=(
            "一部の人に依存しない運用について",
            "組織の暗黙知を残す方法",
            "標準化できる業務の相談",
        ),
        opening="会社が伸びるほど、強い個人の判断に依存する部分がボトルネックになりやすくなります。",
        value="ranzakuは、提案や引き継ぎのような繰り返し発生する意思決定を、標準化された運用として残すことを狙っています。",
        cta="いま組織内で一番再現しづらい業務を1つだけ教えてください。",
        closing="ranzaku",
    ),
    "campaign-004": Campaign(
        subject_lines=(
            "提案前の整理作業を軽くする件",
            "設計や提案の下準備を減らす相談",
            "案件ごとの文脈整理を減らす件",
        ),
        opening="設計や提案の現場では、創造より前に発生する整理作業で時間が消えやすいはずです。",
        value="ranzakuは、提案前の情報整理、初期ドラフト、引き継ぎ文の標準化で、本来の業務に集中しやすい状態をつくります。",
        cta="今走っている案件の1本だけで、どこを自動化できるか見ます。",
        closing="ranzaku",
    ),
    "campaign-005": Campaign(
        subject_lines=(
            "営業初動を速くする提案",
            "提案書づくりの手間を減らす件",
            "初回対応の速度を上げる相談",
        ),
        opening="営業現場では、初回対応、ヒアリング整理、提案のたたき台づくりで時間が消えやすいはずです。",
        value="ranzakuは、最初の応答と提案準備を標準化し、返答速度と提案の質を両立する運用を支援します。",
        cta="今の営業フローを1回分だけ見せていただければ、削れる手間を具体化します。",
        closing="ranzaku",
    ),
}


def build_body(row: dict[str, str], campaign_id: str) -> str:
    campaign = CAMPAIGNS[campaign_id]
    contact_name = row.get("contact_name", "").strip()
    greeting = f"{contact_name}様" if contact_name else "ご担当者様"
    company_name = row.get("company_name", "").strip()
    title = row.get("title", "").strip()
    context = f"{company_name}の{title}" if title else f"{company_name}のご担当領域"
    lines = [
        greeting,
        "",
        "突然のご連絡失礼します。",
        campaign.opening,
        campaign.value,
        f"{context}の観点で、{campaign.cta}",
        "",
        campaign.closing,
    ]
    return "\n".join(lines)


def build_subject(row: dict[str, str], campaign_id: str) -> str:
    campaign = CAMPAIGNS[campaign_id]
    company_name = row.get("company_name", "").strip()
    seed = sum(ord(ch) for ch in company_name or row.get("email", ""))
    return campaign.subject_lines[seed % len(campaign.subject_lines)]


def campaign_for_row(row: dict[str, str], default_campaign: str) -> str:
    explicit = row.get("campaign_id", "").strip()
    if explicit and explicit in CAMPAIGNS:
        return explicit
    inferred = re.search(r"(campaign-\d+)", row.get("next_action", ""))
    if inferred and inferred.group(1) in CAMPAIGNS:
        return inferred.group(1)
    return default_campaign if default_campaign in CAMPAIGNS else "campaign-001"


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


def read_leads(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = list(reader.fieldnames or [])
        rows = list(reader)
    return headers, rows


def write_leads(path: Path, headers: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def ensure_headers(headers: list[str], extra: Iterable[str]) -> list[str]:
    result = list(headers)
    for name in extra:
        if name not in result:
            result.append(name)
    return result


def append_log(path: Path, row: dict[str, str], campaign_id: str, subject: str, dry_run: bool) -> None:
    timestamp = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    status = "dry-run" if dry_run else "sent"
    entry = (
        f"- {timestamp} | {status} | {campaign_id} | {row.get('company_name', '').strip()} | "
        f"{row.get('email', '').strip()} | {subject}\n"
    )
    previous = path.read_text(encoding="utf-8") if path.exists() else "# Send Log\n\n"
    if not previous.endswith("\n"):
        previous += "\n"
    path.write_text(previous + entry, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign", default="campaign-001", choices=sorted(CAMPAIGNS))
    parser.add_argument("--leads", default=str(DEFAULT_LEADS_PATH))
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--log", default=str(DEFAULT_LOG_PATH))
    args = parser.parse_args()

    leads_path = Path(args.leads)
    if not leads_path.exists():
        raise SystemExit(f"Missing {leads_path}")

    headers, rows = read_leads(leads_path)
    headers = ensure_headers(headers, ["campaign_id", "sent_at"])

    sent_count = 0
    for row in rows:
        status = row.get("status", "").strip().lower()
        if status not in {"new", "retry"}:
            continue
        to_addr = row.get("email", "").strip()
        if not to_addr:
            continue

        campaign_id = campaign_for_row(row, args.campaign)
        subject = build_subject(row, campaign_id)
        body = build_body(row, campaign_id)

        if args.dry_run:
            print(f"[dry-run] {to_addr} | {campaign_id} | {subject}")
            print(body)
            print("---")
        else:
            send_message(to_addr, subject, body)
            row["status"] = "sent"
            row["campaign_id"] = campaign_id
            row["sent_at"] = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
            sent_count += 1

        append_log(Path(args.log), row, campaign_id, subject, args.dry_run)

        if args.limit and sent_count >= args.limit:
            break

    if not args.dry_run and sent_count:
        write_leads(leads_path, headers, rows)


if __name__ == "__main__":
    main()
