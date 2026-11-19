"""Domain Information Gatherer - PLACEHOLDER. Member 3 replaces this file.

Interface that mailrecon.py calls (keep the same name and arguments):

    gather(domain, timeout) -> dict

    Look up MX, SPF (TXT record starting "v=spf1") and DMARC
    (TXT record at _dmarc.<domain>). dnspython is already in requirements.txt.
    Example return value:
        {"mx": ["mail.example.com"], "spf": "v=spf1 ...", "dmarc": "v=DMARC1; p=reject"}
    For an IP address or localhost target, return a note instead of looking up.

This placeholder returns an empty result.
"""


def gather(domain, timeout):
    return {}
