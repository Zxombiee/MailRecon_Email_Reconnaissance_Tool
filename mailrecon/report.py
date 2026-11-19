"""Report Generator - PLACEHOLDER. Member 4 replaces this file.

Interface that mailrecon.py calls (keep the same names and arguments):

    print_report(result, show_full)               show the result in the terminal
    save(result, output_dir, fmt, show_full) -> list of saved file paths

    result keys: target, host, started, status, modules, pages_crawled,
                 emails (dict: email -> page where first seen), domain_info,
                 patterns, errors, requests_sent, blocked_out_of_scope
    fmt is "txt", "json" or "both". Save ONLY inside output_dir.
    Emails MUST be masked (j***@example.com) unless show_full is True.

This placeholder masks emails and saves a basic JSON file so the tool
can be tested end to end.
"""

import json
import re
from pathlib import Path


def mask(email):
    local, _, domain = email.partition("@")
    return f"{local[:1]}***@{domain}"


def _emails(result, show_full):
    return {(e if show_full else mask(e)): page for e, page in result["emails"].items()}


def print_report(result, show_full=False):
    print(f"Target: {result['target']}  Status: {result['status']}")
    print(f"Pages crawled: {len(result['pages_crawled'])}  "
          f"Requests sent: {result['requests_sent']}")
    for email, page in sorted(_emails(result, show_full).items()):
        print(f"  {email}  (found on {page})")
    for error in result["errors"]:
        print(f"[ERROR] {error}")


def save(result, output_dir, fmt, show_full=False):
    stamp = re.sub(r"\D", "", result["started"])
    host = re.sub(r"[^A-Za-z0-9.-]", "_", result["host"])
    folder = Path(output_dir) / f"{host}_{stamp}"
    folder.mkdir(parents=True, exist_ok=True)
    data = dict(result, emails=_emails(result, show_full), masked=not show_full)
    path = folder / "mailrecon_report.json"
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return [path]
