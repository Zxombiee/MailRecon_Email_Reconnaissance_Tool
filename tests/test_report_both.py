
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mailrecon.report import save

sample_result = {
    "target": "http://127.0.0.1:8080",
    "host": "127.0.0.1",
    "started": "2026-11-20 10:00:00",
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

files = save(sample_result, "output", "both")

print("===== BOTH FORMAT TEST =====")

for file in files:
    print("Generated:", file)
    assert Path(file).exists()

assert len(files) == 2
assert any(str(file).endswith(".txt") for file in files)
assert any(str(file).endswith(".json") for file in files)

print("\nPASS: TXT and JSON generated successfully.")
print("===== TEST COMPLETED =====")
