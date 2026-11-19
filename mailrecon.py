#!/usr/bin/env python3
"""MailRecon - Email OSINT Reconnaissance Tool. Entry point and command-line interface."""

import argparse
import sys
from datetime import datetime
from urllib.parse import urlparse

import requests

from mailrecon import (__version__, crawler, domain_info, extractor, http,
                       patterns, report, safety)

ALL_MODULES = ["crawl", "domain", "patterns"]
DEFAULT_TARGET = "http://127.0.0.1:8080"

EXAMPLES = """
examples:
  Scan the local test site (start Member 3's test site first)
    python mailrecon.py

  Crawl up to 10 pages and save only a JSON report
    python mailrecon.py --target http://127.0.0.1:8080 --max-pages 10 --format json

  Only look up MX, SPF and DMARC records for a domain
    python mailrecon.py --target example.com --modules domain

  See what would be sent without sending anything
    python mailrecon.py --target https://example.com --dry-run

  Show full email addresses in the report (masked by default, PDPA 2010)
    python mailrecon.py --show-full

Press Ctrl+C at any time to stop the scan (kill switch). Partial results are saved.
"""


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="mailrecon",
        description="MailRecon - find email addresses published on an authorised website, "
                    "work out the email naming pattern and check the domain's mail records. "
                    "Authorised use only.",
        epilog=EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-t", "--target", default=DEFAULT_TARGET,
                        help=f"website URL or domain to scan (default: {DEFAULT_TARGET})")
    parser.add_argument("-m", "--modules", default=",".join(ALL_MODULES),
                        help="comma-separated modules: crawl,domain,patterns (default: all)")
    parser.add_argument("-s", "--scope-file", default="scope.txt",
                        help="file listing authorised domains/IP ranges (default: scope.txt)")
    parser.add_argument("--max-pages", type=int, default=20,
                        help="maximum pages to crawl, 1-100 (default: 20)")
    parser.add_argument("--delay", type=float, default=1.0,
                        help=f"seconds between requests, minimum {safety.MIN_DELAY} (default: 1.0)")
    parser.add_argument("--timeout", type=float, default=8.0,
                        help="seconds before a request times out (default: 8)")
    parser.add_argument("-o", "--output", default="output",
                        help="folder for reports (default: ./output)")
    parser.add_argument("-f", "--format", choices=["txt", "json", "both"], default="both",
                        help="report format (default: both)")
    parser.add_argument("--show-full", action="store_true",
                        help="show full email addresses instead of masked (j***@example.com)")
    parser.add_argument("--dry-run", action="store_true",
                        help="show the planned requests without sending anything")
    parser.add_argument("--version", action="version", version=f"MailRecon {__version__}")
    args = parser.parse_args(argv)

    args.modules = [m.strip().lower() for m in args.modules.split(",") if m.strip()]
    if not args.modules or any(m not in ALL_MODULES for m in args.modules):
        parser.error(f"unknown or empty module list. Choose from {ALL_MODULES}")
    if args.delay < safety.MIN_DELAY:
        parser.error(f"--delay must be at least {safety.MIN_DELAY} seconds (rate limit)")
    if not 1 <= args.max_pages <= 100:
        parser.error("--max-pages must be between 1 and 100")
    return args


def parse_target(target):
    """Return (start_url, host). A bare domain becomes https://domain/."""
    if "://" not in target:
        target = "https://" + target
    parts = urlparse(target)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        raise ValueError(f"'{target}' is not a valid http/https URL or domain")
    return target, parts.hostname.lower()


def plan_requests(args, url, host):
    """List what the scan will do (shown by --dry-run)."""
    plan = []
    if "crawl" in args.modules:
        plan.append(f"GET robots.txt on {host} and follow its rules")
        plan.append(f"Crawl up to {args.max_pages} pages starting at {url}, only inside scope")
        plan.append("Extract email addresses from each page (no forms, no logins)")
    if "domain" in args.modules:
        plan.append(f"DNS lookups for {host}: MX, SPF (TXT), DMARC (_dmarc TXT)")
    if "patterns" in args.modules:
        plan.append("Analyse the email naming pattern (offline, no requests)")
    return plan


def check_authorisation(args):
    """Run every safety gate. Returns (url, host, scope), or None to stop."""
    if not safety.show_disclaimer():
        print("[x] Disclaimer not accepted. Exiting without scanning.")
        return None
    try:
        url, host = parse_target(args.target)
    except ValueError as error:
        print(f"[x] {error}")
        return None
    scope = safety.load_scope(args.scope_file)
    if not safety.in_scope(host, scope):
        print(f"[x] '{host}' is NOT in the authorised scope ({args.scope_file}).")
        print("    Add it to the scope file only if you have written permission.")
        return None
    if not safety.confirm_remote_target(host):
        print("[x] Domain confirmation failed. Exiting without scanning.")
        return None
    print(f"[+] Target {host} is in scope.")
    return url, host, scope


def run_crawl(args, url, fetcher, result):
    """Crawl page by page. Emails are saved after every page, so the
    kill switch never loses what was already found."""
    print(f"[*] Crawling {url} (max {args.max_pages} pages)")
    for page_url, html in crawler.crawl(url, fetcher, args.max_pages):
        result["pages_crawled"].append(page_url)
        for email in extractor.extract_emails(html):
            result["emails"].setdefault(email.lower(), page_url)
        print(f"    [{len(result['pages_crawled'])}] {page_url} "
              f"- {len(result['emails'])} unique email(s) so far")


def run_modules(args, url, host, fetcher, result):
    """Run each selected module. One broken module must not stop the others."""
    steps = [
        ("crawl", lambda: run_crawl(args, url, fetcher, result)),
        ("domain", lambda: result.update(domain_info=domain_info.gather(host, args.timeout))),
        ("patterns", lambda: result.update(patterns=patterns.analyse(list(result["emails"]), host))),
    ]
    for name, run in steps:
        if name not in args.modules:
            continue
        if name == "domain":
            print(f"[*] Looking up mail records for {host}")
        if name == "patterns":
            print("[*] Analysing email patterns")
        try:
            run()
        except safety.OutOfScope as error:
            result["errors"].append(f"{name}: stopped - {error}")
        except requests.RequestException as error:
            result["errors"].append(f"{name} failed: could not connect ({error.__class__.__name__})")
        except (OSError, ValueError) as error:
            result["errors"].append(f"{name} failed: {error.__class__.__name__}: {error}")


def main(argv=None):
    args = parse_args(argv)
    print(f"\nMailRecon v{__version__} - Email OSINT Reconnaissance Tool")

    # 1-3. Disclaimer, scope and confirmation: nothing is sent before these pass.
    checked = check_authorisation(args)
    if checked is None:
        return 2
    url, host, scope = checked

    # 4. Dry run: show the plan and stop.
    if args.dry_run:
        print("\n[DRY RUN] Nothing was sent. The scan would do this:")
        for number, step in enumerate(plan_requests(args, url, host), 1):
            print(f"  {number}. {step}")
        print(f"  Delay between requests: {args.delay}s. Reports would go to ./{args.output}/")
        return 0

    # 5. Scan with the kill switch armed.
    limiter = safety.RateLimiter(args.delay)
    # +1 request allowed for robots.txt
    fetcher = http.Fetcher(scope, limiter, args.timeout, max_requests=args.max_pages + 1)
    result = {
        "target": url, "host": host,
        "started": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "complete", "modules": args.modules,
        "pages_crawled": [], "emails": {},          # email -> page where it was first seen
        "domain_info": {}, "patterns": {}, "errors": [],
    }
    safety.install_kill_switch()
    try:
        run_modules(args, url, host, fetcher, result)
    except safety.ScanAborted:
        result["status"] = "aborted by user (partial results)"
        print("\n[!] Kill switch: scan stopped. Saving what was collected so far.")
    finally:
        safety.remove_kill_switch()

    if result["errors"] and result["status"] == "complete":
        result["status"] = "incomplete (some checks failed)"
    result["requests_sent"] = limiter.count
    result["blocked_out_of_scope"] = fetcher.blocked

    # 6. Report (Member 4): masked by default, saved locally only.
    print()
    report.print_report(result, show_full=args.show_full)
    saved = report.save(result, args.output, args.format, show_full=args.show_full)
    print("\n[+] Report saved locally:")
    for path in saved:
        print(f"    {path}")

    if result["status"].startswith("aborted"):
        return 130
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
