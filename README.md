# MailRecon – Email OSINT Reconnaissance Tool

MailRecon is a Python command-line tool for the reconnaissance stage of an authorised penetration test. It crawls a website inside an approved scope, collects the email addresses that are published on it, works out the organisation's email naming pattern, and checks the domain's MX, SPF and DMARC records. The results show how exposed the organisation is to phishing and email spoofing.

> **For authorised testing and education only.** Read the [Legal Disclaimer](#legal-disclaimer) and [Rules of Engagement](#rules-of-engagement-roe) before use.

| | |
|---|---|
| **Course** | IKB31603 Ethical Hacking, UniKL MIIT |
| **Attack category** | 6 – Offensive OSINT |
| **Language** | Python 3.9+ |
| **Licence** | MIT |
| **Team** | [Member 1], [Member 2], [Member 3], [Member 4] |

## Description

<!-- TODO (Member 2): describe the tool, the problem it solves and each module. -->

## Attack lifecycle mapping

<!-- TODO (Member 2): table of lifecycle stage -> what MailRecon does -> module. -->

## Installation

```bash
git clone https://github.com/<your-username>/mailrecon.git
cd mailrecon
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Check that it works:

```bash
python mailrecon.py --help
python -m unittest discover tests
```

## Usage

```bash
# Scan the default target (local test site on http://127.0.0.1:8080)
python mailrecon.py

# Crawl up to 10 pages, save only a JSON report
python mailrecon.py --target http://127.0.0.1:8080 --max-pages 10 --format json

# Only check MX, SPF and DMARC records
python mailrecon.py --target example.com --modules domain

# Dry run: show what would be sent, send nothing
python mailrecon.py --target https://example.com --dry-run

# Show full email addresses (masked by default)
python mailrecon.py --show-full
```

| Option | Meaning | Default |
|---|---|---|
| `-t, --target` | Website URL or domain | `http://127.0.0.1:8080` |
| `-m, --modules` | Any of `crawl,domain,patterns` | all |
| `-s, --scope-file` | File of authorised domains / IP ranges | `scope.txt` |
| `--max-pages` | Pages to crawl (1–100) | `20` |
| `--delay` | Seconds between requests (minimum 1.0) | `1.0` |
| `--timeout` | Request timeout in seconds | `8` |
| `-o, --output` | Folder for reports | `./output` |
| `-f, --format` | `txt`, `json` or `both` | `both` |
| `--show-full` | Show full email addresses instead of `j***@example.com` | off |
| `--dry-run` | Show the plan without sending anything | off |
| `--version` | Show the version | – |

### Safety flow

Every scan goes through these steps in order. If one fails, nothing is sent to the target.

1. **Legal disclaimer** – cites the Computer Crimes Act 1997 and the Personal Data Protection Act 2010. The user must type `I AGREE`.
2. **Scope check** – the target must be listed in `scope.txt` (domain, IP, CIDR range or `*.domain`). If `scope.txt` is missing, only `localhost`, `127.0.0.1`, `::1` and `example.com` are allowed.
3. **Second confirmation** – for any target that is not local or `example.com`, the user must re-type the domain.
4. **Dry run** (optional) – `--dry-run` prints the plan and stops.
5. **Scan** – every request goes through one shared fetcher that re-checks the scope for **each URL**, waits at least 1 second between requests, never follows redirects automatically, and stops at the page limit. Links to other websites are refused and listed in the report under `blocked_out_of_scope`.

### Kill switch

Press **Ctrl+C** at any time during a scan. MailRecon stops immediately, saves the emails found so far (they are saved after every page), and marks the report as `aborted by user (partial results)`.

### Exit codes

| Code | Meaning |
|---|---|
| 0 | Scan completed |
| 1 | Scan finished but some checks failed (for example, the site was offline) |
| 2 | Stopped before scanning: disclaimer refused, target out of scope, or invalid target |
| 130 | Stopped by the kill switch (Ctrl+C) |

## Project structure

```
mailrecon/
├── mailrecon.py         # CLI entry point and scan flow (Member 1)
├── mailrecon/
│   ├── __init__.py      # version (Member 1)
│   ├── safety.py        # disclaimer, scope, rate limiter, kill switch (Member 1)
│   ├── http.py          # scope-enforcing HTTP fetcher (Member 1)
│   ├── crawler.py       # web crawler (Member 2)
│   ├── extractor.py     # email extraction (Member 2)
│   ├── patterns.py      # email pattern analyzer (Member 3)
│   ├── domain_info.py   # MX / SPF / DMARC lookup (Member 3)
│   └── report.py        # report generator and email masking (Member 4)
├── tests/
│   └── test_safety.py   # unit tests for the safety controls
├── scope.txt            # authorised targets
├── requirements.txt
├── LICENSE
└── README.md
```

## Ethical considerations

<!-- TODO (Member 4): each safeguard and why it was chosen, including masking and PDPA. -->
1. Ethical Considerations

MailRecon is created for educational use and approved security investigations. Users need to secure the appropriate authorization from the respective domain owner prior to performing reconnaissance activities.

The tool is intended to gather publicly accessible email addresses and domain details without trying to access private email accounts, send messages, or engage in phishing activities.

Users must ensure their actions adhere to relevant laws and regulations, including the Computer Crimes Act 1997 and the Personal Data Protection Act 2010 (PDPA), when applicable.


2. Privacy Protection and Data Handling

MailRecon implements various strategies to reduce unnecessary exposure of gathered data:

-Default Email Masking:  Email addresses are automatically hidden in produced reports. For instance, john.smith@example.com appears as j***@example.com.

Full Email Display: The --show-full option permits authorized users to reveal entire email addresses when required.

Local Report Storage: Generated TXT and JSON reports are kept locally in the specified output folder.

Timestamped Reports: Each file is given a timestamped name to avoid overwriting current reports.

Duplicate Removal: Duplicate email addresses are deleted to ensure structured and uniform reporting.

Users must limit access to created reports, refrain from unnecessary sharing of collected data, and remove stored information once it is no longer needed.


## Rules of Engagement (RoE)

<!-- TODO (Member 3): authorised scope, time windows, permitted techniques,
     prohibited actions, emergency stop procedure. -->

## Responsible disclosure

<!-- TODO (Member 4): who to report to, when, and how. -->

## Legal disclaimer

MailRecon is provided for education and authorised security testing only.

- **Computer Crimes Act 1997 (Act 563), Malaysia** – unauthorised access to computer material (Section 3), and unauthorised access with intent to commit or facilitate a further offence (Section 4), are offences.
- **Personal Data Protection Act 2010 (Act 709), Malaysia** – an email address that identifies a person is personal data. Collect it only for the authorised assessment, keep it secure, do not disclose it to anyone outside the engagement, and delete it when the engagement ends.

Only scan domains you own or have **written** permission to test. Never use the results for spam, phishing or any other unlawful purpose. Similar laws apply in other countries. The authors accept no liability for misuse or damage caused by this tool. By using MailRecon you confirm that you are authorised to scan every target you choose.

## Limitations

<!-- TODO (Member 3): what MailRecon cannot detect. -->

## Licence

Released under the [MIT License](LICENSE).
