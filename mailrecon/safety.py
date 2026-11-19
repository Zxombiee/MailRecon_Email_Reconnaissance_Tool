"""Ethical controls (Member 1): legal disclaimer, scope check,
target confirmation, rate limiter and kill switch."""

import ipaddress
import signal
import time
from pathlib import Path

DISCLAIMER = """
================================= LEGAL DISCLAIMER =================================
 MailRecon is for AUTHORISED security testing and education only.

 Computer Crimes Act 1997 (Act 563), Malaysia:
   - Section 3: unauthorised access to computer material is an offence.
   - Section 4: unauthorised access with intent to commit a further offence.

 Personal Data Protection Act 2010 (Act 709), Malaysia:
   - Email addresses that identify a person are PERSONAL DATA.
   - Collect them only for the authorised assessment, keep them secure,
     do not share them, and delete them when the engagement ends.

 Only scan domains that you own, or that you have WRITTEN permission to test.
 Never use the results for spam, phishing or any other unlawful purpose.
 You are fully responsible for how you use this tool.
=====================================================================================
"""

# Targets that are always safe to scan. Used when scope.txt is missing.
SAFE_HOSTS = {"localhost", "127.0.0.1", "::1", "example.com"}

# The rate limit cannot be set lower than this from the command line.
MIN_DELAY = 1.0


class ScanAborted(Exception):
    """Raised when the user presses Ctrl+C (kill switch)."""


class OutOfScope(Exception):
    """Raised when any part of the tool tries to contact a host outside the scope."""


def _ask(prompt, ask):
    """Ask a question; no keyboard input (e.g. piped from /dev/null) counts as 'no'."""
    try:
        return ask(prompt).strip()
    except EOFError:
        return ""


def show_disclaimer(ask=input):
    """Print the disclaimer and require the user to type I AGREE."""
    print(DISCLAIMER)
    answer = _ask('Type "I AGREE" to confirm you are authorised to scan the target: ', ask)
    return answer.upper() == "I AGREE"


def load_scope(scope_file):
    """Read the authorised scope file: one hostname, IP, CIDR range or *.domain per line.

    If the file does not exist, only the safe local/test hosts are allowed.
    """
    path = Path(scope_file)
    if not path.exists():
        return sorted(SAFE_HOSTS)
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip().lower()
        if line:
            entries.append(line)
    return entries


def in_scope(host, entries):
    """Return True if host matches a hostname, wildcard, IP or CIDR range in the scope."""
    host = (host or "").lower().rstrip(".")
    if not host:
        return False
    try:
        host_ip = ipaddress.ip_address(host)
    except ValueError:
        host_ip = None

    for entry in entries:
        if entry == host:
            return True
        # "*.lab.local" allows sub-domains such as hr.lab.local
        if entry.startswith("*.") and host.endswith(entry[1:]):
            return True
        if host_ip is not None:
            try:
                if host_ip in ipaddress.ip_network(entry, strict=False):
                    return True
            except ValueError:
                continue    # entry is a hostname, not an IP range
    return False


def confirm_remote_target(host, ask=input):
    """Second confirmation for any target that is not a safe local/test host."""
    if host.lower() in SAFE_HOSTS:
        return True
    print(f"\n[!] '{host}' is not a local/test target.")
    typed = _ask("    Re-type the domain to confirm you have written authorisation: ", ask)
    return typed.lower() == host.lower()


class RateLimiter:
    """Waits between requests so the scan never floods the target."""

    def __init__(self, delay_seconds):
        self.delay = max(MIN_DELAY, delay_seconds)
        self.last_request = 0.0
        self.count = 0

    def wait(self):
        gap = time.monotonic() - self.last_request
        if self.count and gap < self.delay:
            time.sleep(self.delay - gap)
        self.last_request = time.monotonic()
        self.count += 1


def _on_ctrl_c(signum, frame):
    raise ScanAborted()


def install_kill_switch():
    """Ctrl+C stops the scan cleanly instead of crashing with a traceback."""
    signal.signal(signal.SIGINT, _on_ctrl_c)


def remove_kill_switch():
    """After the scan, a second Ctrl+C works normally again."""
    signal.signal(signal.SIGINT, signal.default_int_handler)
