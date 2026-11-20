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

MailRecon is an email reconnaissance tool. It crawls a website that we have permission to test, collects the email addresses published on it, and checks the domain's email security records.

Most phishing attacks start with a list of email addresses. If a company puts staff emails on its website, an attacker can collect them in a few minutes. MailRecon shows the company which addresses are exposed. The company can then remove them, replace them with a contact form or a shared mailbox, and use the results in phishing awareness training.

The tool only reads public web pages and public DNS records. It does not log in, fill in forms, send emails or connect to mail servers.

| Module | File | What it does |
|---|---|---|
| Safety controls | `safety.py`, `http.py` | Shows the legal disclaimer, checks the scope, asks again before scanning a remote target, limits the request rate and handles Ctrl+C. Every request goes through one fetcher that checks the scope again. |
| Web crawler | `crawler.py` | Starts at the target page and follows its links. Obeys `robots.txt`, follows redirects that stay in scope, skips files like images and PDFs, never visits the same page twice and stops at `--max-pages`. Links to other websites are not visited, only listed in the report. |
| Email extractor | `extractor.py` | Uses BeautifulSoup to read the page. Finds normal emails, emails inside `mailto:` links, HTML-encoded emails (`&#64;`) and hidden ones like `ali [at] example [dot] com`. Skips image names that look like emails, such as `logo@2x.png`. |
| Pattern analyzer | `patterns.py` | Works out how the company forms its email addresses, for example `{first}.{last}`, and gives a confidence score. |
| Domain information | `domain_info.py` | Looks up the MX, SPF and DMARC records to see how easy it would be to fake an email from the domain. |
| Report generator | `report.py` | Saves a TXT and JSON report in a local folder named with the date and time. Emails are masked by default (`j***@example.com`). |

## Attack category

MailRecon is in **Category 6: Offensive OSINT**.

OSINT (Open-Source Intelligence) means gathering information from public sources, such as websites and DNS records, without breaking into anything. Offensive OSINT is when that information is gathered the way an attacker would, to plan an attack. In a penetration test, we do this to show the organisation what an attacker could find.

MailRecon fits this category because:

- It only uses public information: web pages anyone can open and public DNS records.
- It does not log in, guess passwords, exploit bugs or send emails.
- What it collects (email addresses, the naming pattern and how easy the domain is to spoof) is exactly what an attacker needs before a phishing attack.

In MITRE ATT&CK, this is the Reconnaissance tactic (TA0043).

## Attack lifecycle mapping

MailRecon covers the reconnaissance stage. Its results can be used in later stages, but the tool does not carry out those stages.

| Lifecycle stage | What MailRecon does | Module | MITRE ATT&CK |
|---|---|---|---|
| 1. Planning and scoping | Reads the allowed targets from `scope.txt` and shows the legal disclaimer. `--dry-run` shows the plan without sending anything. | `safety.py`, `mailrecon.py` | – |
| 2. Passive reconnaissance | Looks up public DNS records (MX, SPF, DMARC). No requests are sent to the target's website. | `domain_info.py` | T1590.002 Gather Victim Network Information: DNS |
| 2. Active reconnaissance | Crawls the in-scope website politely (obeys robots.txt, at most 1 request per second, stops at the page limit) and collects the email addresses on it. | `crawler.py`, `extractor.py` | T1594 Search Victim-Owned Websites; T1589.002 Email Addresses |
| 3. Scanning and enumeration | Works out the email naming pattern, which shows how easily other staff emails could be guessed. | `patterns.py` | T1589.003 Employee Names |
| 4. Gaining access | Not done by MailRecon. The email list and spoofing check show how likely a phishing attack is to work. A real phishing test would need separate permission. | – | T1566 Phishing (input only) |
| 5. Reporting | Saves a masked TXT/JSON report with the page where each email was found and the out-of-scope links that were skipped. | `report.py` | – |

```
Scope & disclaimer ──> Crawl in-scope pages ──> Extract emails ──> Pattern analysis ──┐
        │                                                                             ├──> Masked report
        └──────────────> DNS: MX / SPF / DMARC ──> Spoofing assessment ───────────────┘
```

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

MailRecon is designed for authorised email reconnaissance and security testing only.

Before using this tool, users must follow these rules:

1. Only scan websites and domains that you own or have received written permission to test.
2. Do not scan websites belonging to other individuals or organisations without permission.
3. Do not use MailRecon to collect email addresses for spam, phishing, harassment or other malicious activities.
4. Keep scanning within the authorised scope defined in the scope configuration file.
5. Use reasonable scanning limits and avoid sending excessive requests to the target website.
6. Handle all collected email addresses and scan reports responsibly.
7. Do not publish or share collected information without proper authorisation.

By using MailRecon, users agree to follow these rules and applicable laws, including the Computer Crimes Act 1997 and Personal Data Protection Act 2010 (PDPA) of Malaysia, where applicable.

## Limitations

MailRecon has the following limitations:

1. Email Discovery: The tool can only identify email addresses that are publicly visible on accessible web pages. It cannot discover private or hidden email addresses.
2. Website Access: Some websites may block automated requests or require JavaScript rendering, which may affect email collection.
3. Pattern Analysis: The pattern analyzer only recognises supported email formats, such as `first.last` and `first_last`. Other formats may be classified as unknown.
4. Domain Information: MX, SPF and DMARC results depend on publicly available DNS records. Some domains may not have these records.
5. Localhost and IP Addresses: DNS information gathering is skipped for localhost and IP address targets.
6. Email Masking: Email addresses are masked in reports by default to help protect personal information.
7. Scan Scope: MailRecon only scans targets allowed by its authorised scope configuration.
8. No Guarantee of Accuracy: Results may be incomplete or outdated and should be manually verified before making security decisions.

MailRecon is an educational reconnaissance tool. It is not intended to replace professional security assessments or penetration testing.

## Responsible disclosure

<!-- TODO (Member 4): who to report to, when, and how. -->
3. Responsible Disclosure

When MailRecon detects publicly available information or possible security issues, users must manage the results with care.The subsequent methods are advised:

The following practices are recommended:

1.Report relevant findings to the website owner or authorised security contact.

2.Provide clear and accurate information about the identified findings.

3.Avoid publicly disclosing sensitive information without permission.

4.Do not use collected email addresses for phishing, spam, harassment or other malicious activities.

5.Respect the privacy and confidentiality of individuals whose information appears in the reports.

Responsible disclosure assists organizations in recognizing potential security issues while reducing unnecessary risks to impacted individuals.

## Legal disclaimer

MailRecon is provided for education and authorised security testing only.

- **Computer Crimes Act 1997 (Act 563), Malaysia** – unauthorised access to computer material (Section 3), and unauthorised access with intent to commit or facilitate a further offence (Section 4), are offences.
- **Personal Data Protection Act 2010 (Act 709), Malaysia** – an email address that identifies a person is personal data. Collect it only for the authorised assessment, keep it secure, do not disclose it to anyone outside the engagement, and delete it when the engagement ends.

Only scan domains you own or have **written** permission to test. Never use the results for spam, phishing or any other unlawful purpose. Similar laws apply in other countries. The authors accept no liability for misuse or damage caused by this tool. By using MailRecon you confirm that you are authorised to scan every target you choose.


<!-- TODO (Member 3): what MailRecon cannot detect. -->

## Licence

Released under the [MIT License](LICENSE).
