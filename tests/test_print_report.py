
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mailrecon.report import print_report

sample_result = {
    "target": "http://127.0.0.1:8080",
    "host": "127.0.0.1",
    "started": "2026-11-20 10:00:00",
    "status": "complete",
    "modules": ["crawl", "domain", "patterns"],

    "pages_crawled": [
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8080/about"
    ],

    "emails": {
        "john.smith@example.com": "home",
        "mary.jones@gmail.com": "about"
    },

    "domain_info": {
        "mx": [],
        "spf": "Not found",
        "dmarc": "Not found",
        "note": "DNS lookup skipped: target is localhost."
    },

    "patterns": {
        "pattern": "unknown",
        "confidence": 0.0,
        "samples": 0
    },

    "errors": [],
    "requests_sent": 3,
    "blocked_out_of_scope": 0
}

print_report(sample_result, show_full=False)
