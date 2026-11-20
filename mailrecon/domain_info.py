
"""Domain Information Gatherer - Member 3.

Retrieves public MX, SPF and DMARC DNS records.
"""

import ipaddress
import dns.resolver


def is_ip_address(domain):
    """Check whether the target is an IP address."""
    try:
        ipaddress.ip_address(domain)
        return True
    except ValueError:
        return False


def get_txt_records(name, timeout):
    """Retrieve TXT records for a DNS name."""
    try:
        answers = dns.resolver.resolve(
            name,
            "TXT",
            lifetime=timeout
        )

        records = []

        for answer in answers:
            value = b"".join(answer.strings).decode(
                "utf-8", errors="replace"
            )
            records.append(value)

        return records

    except Exception:
        return []


def gather(domain, timeout):
    """Gather MX, SPF and DMARC records."""
    domain = domain.strip().lower().rstrip(".")

    result = {
        "mx": [],
        "spf": "Not found",
        "dmarc": "Not found"
    }

    # Skip DNS lookup for localhost and IP addresses
    if (
        domain == "localhost"
        or domain.endswith(".localhost")
        or is_ip_address(domain)
    ):
        result["note"] = (
            "DNS lookup skipped: target is localhost or an IP address."
        )
        return result

    # Validate timeout
    try:
        timeout = float(timeout)
        if timeout <= 0:
            timeout = 5.0
    except (TypeError, ValueError):
        timeout = 5.0

    # Get MX records
    try:
        answers = dns.resolver.resolve(
            domain,
            "MX",
            lifetime=timeout
        )

        mx_records = sorted(
            answers,
            key=lambda record: record.preference
        )

        null_mx = False

        for record in mx_records:
            exchange = str(record.exchange)

            if exchange == ".":
                null_mx = True
            else:
                result["mx"].append(exchange.rstrip("."))

        if null_mx:
            result["mx_status"] = (
                "Null MX: domain does not accept email"
            )

    except Exception:
        result["mx"] = []

    # Get SPF records
    txt_records = get_txt_records(domain, timeout)

    for record in txt_records:
        if record.lower().startswith("v=spf1"):
            result["spf"] = record
            break

    # Get DMARC records
    dmarc_records = get_txt_records(
        f"_dmarc.{domain}",
        timeout
    )

    for record in dmarc_records:
        if record.lower().startswith("v=dmarc1"):
            result["dmarc"] = record
            break

    return result
