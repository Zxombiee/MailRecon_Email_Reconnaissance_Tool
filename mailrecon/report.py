
"""MailRecon Report Generator - Member 4.

Generates TXT and JSON reports.
Email addresses are masked by default unless show_full=True.
"""

import json
import re
import uuid
from pathlib import Path
from datetime import datetime


def mask(email):
    """Mask the local part of an email address."""

    if not isinstance(email, str) or email.count("@") != 1:
        return "[invalid email]"

    local, domain = email.split("@", 1)

    if not local or not domain:
        return "[invalid email]"

    return f"{local[0]}***@{domain}"


def _emails(result, show_full=False):
    """Prepare email records while preserving masking collisions."""

    original = result.get("emails", {})
    output = {}

    for email, page in sorted(original.items()):
        label = email if show_full else mask(email)

        base = label
        counter = 2

        while label in output:
            label = f"{base} [{counter}]"
            counter += 1

        output[label] = page

    return output


def _format_section(title, content):
    """Format information for the TXT report."""

    lines = [f"\n{title}:", "-" * 45]

    if not content:
        lines.append("No information available.")

    elif isinstance(content, dict):
        for key, value in content.items():
            lines.append(f"{key}: {value}")

    elif isinstance(content, list):
        for item in content:
            lines.append(str(item))

    else:
        lines.append(str(content))

    return lines


def print_report(result, show_full=False):
    """Display scan results in the terminal."""

    emails = _emails(result, show_full)

    print("\n========== MAILRECON REPORT ==========")
    print("Target:", result.get("target", "Unknown"))
    print("Host:", result.get("host", "Unknown"))
    print("Scan Date:", result.get("started", "Unknown"))
    print("Status:", result.get("status", "Unknown"))
    print("Modules:", result.get("modules", []))
    print("Pages Crawled:", len(result.get("pages_crawled", [])))
    print("Requests Sent:", result.get("requests_sent", 0))
    print("Blocked Out-of-Scope:",
          result.get("blocked_out_of_scope", 0))

    print("\nCOLLECTED EMAILS:")

    if emails:
        for email, page in sorted(emails.items()):
            print(f"{email} (found on {page})")
    else:
        print("No email addresses found.")

    print("\nDOMAIN INFORMATION:")
    print(json.dumps(result.get("domain_info", {}),
                     indent=4, default=str))

    print("\nEMAIL PATTERNS:")
    print(json.dumps(result.get("patterns", {}),
                     indent=4, default=str))

    print("\nERRORS:")

    errors = result.get("errors", [])

    if errors:
        for error in errors:
            print("-", error)
    else:
        print("No errors found.")

    print("\n======================================")


def save(result, output_dir, fmt, show_full=False):
    """Save reports in TXT, JSON or both formats."""

    if fmt not in ("txt", "json", "both"):
        raise ValueError("Format must be txt, json or both.")

    stamp = re.sub(r"\D", "", str(result.get("started", "")))

    if not stamp:
        stamp = datetime.now().strftime("%Y%m%d%H%M%S")

    host = re.sub(
        r"[^A-Za-z0-9.-]",
        "_",
        str(result.get("host", "unknown"))
    )

    folder = Path(output_dir) / f"{host}_{stamp}"
    folder.mkdir(parents=True, exist_ok=True)

    emails = _emails(result, show_full)

    data = dict(result)
    data["emails"] = emails
    data["masked"] = not show_full
    data["email_count"] = len(result.get("emails", {}))

    saved_files = []

    # Generate a unique identifier to prevent overwriting.
    unique_id = uuid.uuid4().hex[:8]

    # TXT REPORT
    if fmt in ("txt", "both"):

        lines = [
            "========== MAILRECON SCAN REPORT ==========",
            "",
            f"Target: {result.get('target', 'Unknown')}",
            f"Host: {result.get('host', 'Unknown')}",
            f"Scan Date: {result.get('started', 'Unknown')}",
            f"Status: {result.get('status', 'Unknown')}",
            f"Modules: {result.get('modules', [])}",
            f"Pages Crawled: {len(result.get('pages_crawled', []))}",
            f"Requests Sent: {result.get('requests_sent', 0)}",
            f"Blocked Out-of-Scope: {result.get('blocked_out_of_scope', 0)}",
            f"Total Emails: {data['email_count']}",
            f"Email Masking Enabled: {not show_full}",
        ]

        lines.extend(_format_section("COLLECTED EMAILS", [
            f"{email} (found on {page})"
            for email, page in sorted(emails.items())
        ]))

        lines.extend(_format_section(
            "PAGES CRAWLED",
            result.get("pages_crawled", [])
        ))

        lines.extend(_format_section(
            "DOMAIN INFORMATION",
            result.get("domain_info", {})
        ))

        lines.extend(_format_section(
            "EMAIL PATTERNS",
            result.get("patterns", {})
        ))

        lines.extend(_format_section(
            "ERRORS",
            result.get("errors", [])
        ))

        lines.append("\n============================================")

        txt_path = folder / f"mailrecon_report_{unique_id}.txt"

        txt_path.write_text(
            "\n".join(lines),
            encoding="utf-8"
        )

        saved_files.append(txt_path)

    # JSON REPORT
    if fmt in ("json", "both"):

        json_path = folder / f"mailrecon_report_{unique_id}.json"

        json_path.write_text(
            json.dumps(data, indent=4, default=str),
            encoding="utf-8"
        )

        saved_files.append(json_path)

    return saved_files
