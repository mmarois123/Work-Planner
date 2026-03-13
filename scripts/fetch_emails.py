#!/usr/bin/env python3
"""Fetch unread emails from a Gmail IMAP inbox and output structured JSON.

Used by the /process-email skill to feed forwarded emails into the task pipeline.
Requires a .email-config JSON file with Gmail credentials (see .email-config.example).

Usage:
    python scripts/fetch_emails.py                  # fetch & mark as read
    python scripts/fetch_emails.py --dry-run        # fetch without marking read
    python scripts/fetch_emails.py --limit 5        # fetch at most 5 emails
    python scripts/fetch_emails.py --config PATH    # custom config path
"""

import argparse
import email
import email.header
import email.message
import email.utils
import imaplib
import json
import os
import re
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser

# ---------------------------------------------------------------------------
# HTML → plain text
# ---------------------------------------------------------------------------

class _HTMLToText(HTMLParser):
    """Minimal HTML stripper — keeps text, adds newlines for block tags."""

    _BLOCK_TAGS = {"p", "div", "br", "tr", "li", "h1", "h2", "h3", "h4", "h5", "h6"}

    def __init__(self):
        super().__init__()
        self._parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() in self._BLOCK_TAGS:
            self._parts.append("\n")

    def handle_data(self, data):
        self._parts.append(data)

    def get_text(self) -> str:
        return "".join(self._parts).strip()


def html_to_text(html: str) -> str:
    parser = _HTMLToText()
    parser.feed(html)
    return parser.get_text()


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".email-config")

def load_config(path: str) -> dict:
    if not os.path.isfile(path):
        _error_exit(
            "missing_config",
            f"Config file not found: {path}\n"
            "Copy .email-config.example to .email-config and fill in your Gmail credentials.\n"
            "See the /process-email setup instructions for details.",
        )
    with open(path, encoding="utf-8") as f:
        try:
            cfg = json.load(f)
        except json.JSONDecodeError as exc:
            _error_exit("invalid_config", f"Failed to parse config: {exc}")
    for key in ("email", "app_password", "imap_server", "imap_port"):
        if key not in cfg:
            _error_exit("invalid_config", f"Missing required key '{key}' in config.")
    return cfg


# ---------------------------------------------------------------------------
# IMAP helpers
# ---------------------------------------------------------------------------

BODY_MAX_CHARS = 5000

def connect(cfg: dict) -> imaplib.IMAP4_SSL:
    try:
        conn = imaplib.IMAP4_SSL(cfg["imap_server"], int(cfg["imap_port"]))
    except Exception as exc:
        _error_exit("connection_failed", f"Could not connect to {cfg['imap_server']}: {exc}")
    try:
        conn.login(cfg["email"], cfg["app_password"])
    except imaplib.IMAP4.error as exc:
        _error_exit("auth_failed", f"Authentication failed: {exc}")
    return conn


def fetch_unread(conn: imaplib.IMAP4_SSL, limit: int | None = None, dry_run: bool = False) -> list[dict]:
    conn.select("INBOX")
    status, data = conn.search(None, "UNSEEN")
    if status != "OK":
        return []

    uids = data[0].split()
    if not uids:
        return []

    if limit:
        uids = uids[:limit]

    results = []
    for uid in uids:
        status, msg_data = conn.fetch(uid, "(RFC822)")
        if status != "OK" or not msg_data or not msg_data[0]:
            continue
        raw = msg_data[0][1]
        msg = email.message_from_bytes(raw)
        parsed = _parse_message(msg)
        if parsed:
            results.append(parsed)
            if not dry_run:
                conn.store(uid, "+FLAGS", "\\Seen")

    return results


# ---------------------------------------------------------------------------
# Message parsing
# ---------------------------------------------------------------------------

_FW_RE = re.compile(r"^(fw|fwd|re)\s*:\s*", re.IGNORECASE)

def _clean_subject(subject_raw: str | None) -> str:
    if not subject_raw:
        return "(no subject)"
    # Decode RFC2047 encoded words
    parts = email.header.decode_header(subject_raw)
    decoded = []
    for part, charset in parts:
        if isinstance(part, bytes):
            decoded.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            decoded.append(part)
    subject = " ".join(decoded).strip()
    # Strip forwarding prefixes (possibly chained)
    while _FW_RE.match(subject):
        subject = _FW_RE.sub("", subject, count=1).strip()
    return subject or "(no subject)"


def _get_body(msg: email.message.Message) -> str:
    """Extract plain text body, falling back to stripped HTML."""
    if msg.is_multipart():
        plain = None
        html = None
        for part in msg.walk():
            ct = part.get_content_type()
            if ct == "text/plain" and plain is None:
                plain = part.get_payload(decode=True)
            elif ct == "text/html" and html is None:
                html = part.get_payload(decode=True)
        if plain:
            charset = msg.get_content_charset() or "utf-8"
            return plain.decode(charset, errors="replace")[:BODY_MAX_CHARS]
        if html:
            charset = msg.get_content_charset() or "utf-8"
            return html_to_text(html.decode(charset, errors="replace"))[:BODY_MAX_CHARS]
        return ""
    else:
        payload = msg.get_payload(decode=True)
        if payload is None:
            return ""
        charset = msg.get_content_charset() or "utf-8"
        ct = msg.get_content_type()
        text = payload.decode(charset, errors="replace")
        if ct == "text/html":
            text = html_to_text(text)
        return text[:BODY_MAX_CHARS]


# Patterns to detect the original sender in forwarded email bodies
_FROM_LINE_PATTERNS = [
    re.compile(r"^From:\s*(.+)", re.MULTILINE),
    re.compile(r"^-+\s*Forwarded message\s*-+.*?From:\s*(.+)", re.MULTILINE | re.DOTALL),
]

def _detect_original_sender(body: str, envelope_from: str) -> dict:
    """Try to extract original sender from forwarding headers in body."""
    for pat in _FROM_LINE_PATTERNS:
        m = pat.search(body[:2000])  # only scan first 2000 chars
        if m:
            raw = m.group(1).strip()
            name, addr = email.utils.parseaddr(raw)
            if name or addr:
                return {"name": name or None, "email": addr or None}
    # Fall back to envelope From
    name, addr = email.utils.parseaddr(envelope_from)
    return {"name": name or None, "email": addr or None}


def _parse_message(msg: email.message.Message) -> dict | None:
    subject = _clean_subject(msg.get("Subject"))
    from_header = msg.get("From", "")
    date_header = msg.get("Date", "")
    body = _get_body(msg)
    original_sender = _detect_original_sender(body, from_header)

    # Parse date
    parsed_date = email.utils.parsedate_to_datetime(date_header) if date_header else None
    iso_date = parsed_date.isoformat() if parsed_date else None

    return {
        "subject": subject,
        "from": from_header,
        "original_sender_name": original_sender["name"],
        "original_sender_email": original_sender["email"],
        "date": iso_date,
        "body": body,
    }


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def _error_exit(code: str, message: str):
    json.dump({"error": code, "message": message, "emails": [], "count": 0}, sys.stdout, indent=2)
    sys.stdout.write("\n")
    sys.exit(1)


def _output(emails: list[dict]):
    json.dump({"count": len(emails), "emails": emails}, sys.stdout, indent=2)
    sys.stdout.write("\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Fetch unread emails from Gmail IMAP inbox.")
    parser.add_argument("--dry-run", action="store_true", help="Fetch without marking as read")
    parser.add_argument("--limit", type=int, default=None, help="Max emails to fetch")
    parser.add_argument("--config", type=str, default=DEFAULT_CONFIG_PATH, help="Path to config JSON")
    args = parser.parse_args()

    cfg = load_config(args.config)
    conn = connect(cfg)
    try:
        emails = fetch_unread(conn, limit=args.limit, dry_run=args.dry_run)
    finally:
        try:
            conn.logout()
        except Exception:
            pass

    _output(emails)


if __name__ == "__main__":
    main()
