#!/usr/bin/env python3
"""Harvest public contact emails from official pages.

Reads one URL per line from a file or stdin, fetches the page, and emits CSV rows
for any `mailto:` links or email-like strings found in the HTML.

Usage:
  python3 scripts/harvest_public_contacts.py --input urls.txt --output leads.csv
  cat urls.txt | python3 scripts/harvest_public_contacts.py --stdin
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen


EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


class MailtoParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.mailtos: list[str] = []
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag == "a":
            for key, value in attrs:
                if key == "href" and value and value.startswith("mailto:"):
                    self.mailtos.append(value.removeprefix("mailto:").split("?")[0])
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data


@dataclass(frozen=True)
class FoundEmail:
    email: str
    source_url: str
    page_title: str


def fetch(url: str) -> str:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=20) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="ignore")


def harvest(url: str) -> list[FoundEmail]:
    html = fetch(url)
    parser = MailtoParser()
    parser.feed(html)
    title = unescape(parser.title).strip()
    emails = set(parser.mailtos)
    emails.update(EMAIL_RE.findall(html))
    return [FoundEmail(email=e, source_url=url, page_title=title) for e in sorted(emails)]


def read_urls(path: Path | None, stdin_flag: bool) -> list[str]:
    if stdin_flag:
        return [line.strip() for line in sys.stdin if line.strip() and not line.startswith("#")]
    if not path:
        raise SystemExit("--input or --stdin required")
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--stdin", action="store_true")
    args = parser.parse_args()

    urls = read_urls(args.input, args.stdin)
    rows: list[FoundEmail] = []
    for url in urls:
        try:
            rows.extend(harvest(url))
        except Exception as exc:  # noqa: BLE001
            print(f"[skip] {url}: {exc}", file=sys.stderr)

    writer = csv.DictWriter(sys.stdout, fieldnames=["email", "source_url", "page_title"])
    if args.output:
        with args.output.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["email", "source_url", "page_title"])
            writer.writeheader()
            for row in rows:
                writer.writerow(row.__dict__)
    else:
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


if __name__ == "__main__":
    main()
