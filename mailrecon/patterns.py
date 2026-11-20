
import re
from collections import Counter


def identify_pattern(email):
    """Identify the structure of an email's local part."""

    if "@" not in email:
        return None

    local_part = email.rsplit("@", 1)[0].lower()

    # First initial + last name (e.g. j.smith)
    if re.fullmatch(r"[a-z]\.[a-z]{2,}", local_part):
        return "{first_initial}.{last}"

    # First name + last initial (e.g. john.s)
    elif re.fullmatch(r"[a-z]{2,}\.[a-z]", local_part):
        return "{first}.{last_initial}"

    # First name + last name (e.g. john.smith)
    elif re.fullmatch(r"[a-z]{2,}\.[a-z]{2,}", local_part):
        return "{first}.{last}"

    # First name + last name separated by underscore
    elif re.fullmatch(r"[a-z]+_[a-z]+", local_part):
        return "{first}_{last}"

    # First name + last name separated by hyphen
    elif re.fullmatch(r"[a-z]+-[a-z]+", local_part):
        return "{first}-{last}"

    return None


def analyse(emails, domain):
    """Analyze email patterns for the specified domain."""

    domain = domain.lower().strip().rstrip(".")
    patterns = Counter()

    for email in emails:
        email = email.strip().lower()

        if "@" not in email:
            continue

        email_domain = email.rsplit("@", 1)[1]

        # Only analyze emails belonging to the target domain
        if email_domain != domain:
            continue

        pattern = identify_pattern(email)

        if pattern:
            patterns[pattern] += 1

    if not patterns:
        return {
            "pattern": "unknown",
            "confidence": 0.0,
            "samples": 0
        }

    # Find the most common pattern
    best_pattern, count = patterns.most_common(1)[0]

    total = sum(patterns.values())
    confidence = count / total

    return {
        "pattern": best_pattern,
        "confidence": round(confidence, 2),
        "samples": count
    }

