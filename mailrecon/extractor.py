"""Email Extraction - PLACEHOLDER. Member 2 replaces this file.

Interface that mailrecon.py calls (keep the same name and arguments):

    extract_emails(text) -> set of email address strings

    Should find: plain emails, mailto: links, and obfuscated forms
    such as "ali [at] example [dot] com".

This placeholder only finds plain emails.
"""

import re

PLAIN_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def extract_emails(text):
    return set(PLAIN_EMAIL.findall(text or ""))
