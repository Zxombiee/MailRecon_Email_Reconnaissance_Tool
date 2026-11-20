import re
from collections import Counter


def identify_pattern(email):
    """Identify the structure of an email's local part."""

    if "@" not in email:
        return None

    local_part = email.rsplit("@", 1)[0].lower()

    # first.last
    if re.fullmatch(r"[a-z]+\.[a-z]+", local_part):
        return "{first}.{last}"

    # first_last
    elif re.fullmatch(r"[a-z]+_[a-z]+", local_part):
        return "{first}_{last}"

    # first-last
    elif re.fullmatch(r"[a-z]+-[a-z]+", local_part):
        return "{first}-{last}"

    # first initial + last name
    elif re.fullmatch(r"[a-z]\.[a-z]+", local_part):
        return "{first_initial}.{last}"

    # first name + last initial
    elif re.fullmatch(r"[a-z]+\.[a-z]", local_part):
        return "{first}.{last_initial}"

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
