
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mailrecon.report import save
import json

sample_result = {
    "target": "http://127.0.0.1:8080",
    "host": "127.0.0.1",
    "started": "2026-11-20 11:00:00",
    "status": "complete",
    "modules": ["crawl", "domain", "patterns"],
    "pages_crawled": ["home", "about"],
    "emails": {
        "john.smith@example.com": "home",
        "mary.jones@gmail.com": "about"
    },
    "domain_info": {},
    "patterns": {},
    "errors": [],
    "requests_sent": 3,
    "blocked_out_of_scope": 0
}

files = save(
    sample_result,
    "output",
    "json",
    show_full=False
)

print("===== JSON REPORT TEST =====")

for file in files:
    print("Generated:", file)

    content = json.loads(
        file.read_text(encoding="utf-8")
    )

    print("\nEmail addresses:")
    for email in content["emails"]:
        print(email)

    print("\nMasking enabled:", content["masked"])

print("\n===== TEST COMPLETED =====")
