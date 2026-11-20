
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mailrecon.report import save

sample_result = {
    "target": "http://127.0.0.1:8080",
    "host": "127.0.0.1",
    "started": "2026-11-20 10:00:00",
    "status": "complete",
    "pages_crawled": ["home", "about"],
    "requests_sent": 3,
    "emails": {
        "john.smith@example.com": "home",
        "mary.jones@gmail.com": "about"
    },
    "errors": []
}

files = save(
    sample_result,
    "output",
    "txt",
    show_full=False
)

print("Generated files:")

for file in files:
    print(file)
    print("\nReport content:")
    print(file.read_text(encoding="utf-8"))
