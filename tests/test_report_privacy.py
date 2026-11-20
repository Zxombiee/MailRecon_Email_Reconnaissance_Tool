
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mailrecon.report import save

sample_result = {
    "target": "http://127.0.0.1:8080",
    "host": "127.0.0.1",
    "started": "2026-11-20 12:00:00",
    "status": "complete",
    "modules": ["crawl"],
    "pages_crawled": ["home"],
    "emails": {
        "john.smith@example.com": "home"
    },
    "domain_info": {},
    "patterns": {},
    "errors": [],
    "requests_sent": 2,
    "blocked_out_of_scope": 0
}

print("===== MAILRECON PRIVACY TESTING =====")

# TEST 1: Full emails in JSON
files = save(sample_result, "output/test_full_json", "json", show_full=True)
data = json.loads(files[0].read_text(encoding="utf-8"))

assert "john.smith@example.com" in data["emails"]
assert data["masked"] is False

print("PASS: Full email addresses in JSON.")

# TEST 2: Masked emails in JSON
files = save(sample_result, "output/test_masked_json", "json", show_full=False)
data = json.loads(files[0].read_text(encoding="utf-8"))

assert "j***@example.com" in data["emails"]
assert data["masked"] is True

print("PASS: Masked email addresses in JSON.")

# TEST 3: Masked emails in TXT
files = save(sample_result, "output/test_masked_txt", "txt", show_full=False)
content = files[0].read_text(encoding="utf-8")

assert "j***@example.com" in content
assert "john.smith@example.com" not in content

print("PASS: Masked email addresses in TXT.")

print("\n===== ALL PRIVACY TESTS COMPLETED =====")
