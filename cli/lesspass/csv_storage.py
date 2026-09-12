import csv
import os


def _parse_bool(value):
    """Parse string to boolean"""
    if isinstance(value, bool):
        return value
    return value.lower() in ("true", "1", "yes", "y")


def _parse_int(value, default=None):
    """Parse string to int with default"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def load_profiles(csv_path):
    """
    Load all profiles from CSV file.

    Returns:
        list: List of profile dictionaries
    """
    if not os.path.exists(csv_path):
        return []

    profiles = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            profile = {
                "site": row.get("site", ""),
                "login": row.get("login", ""),
                "lowercase": _parse_bool(row.get("lowercase", "true")),
                "uppercase": _parse_bool(row.get("uppercase", "true")),
                "digits": _parse_bool(row.get("digits", "true")),
                "symbols": _parse_bool(row.get("symbols", "true")),
                "length": _parse_int(row.get("length"), 16),
                "counter": _parse_int(row.get("counter"), 1),
                "exclude": row.get("exclude", ""),
            }
            profiles.append(profile)

    return profiles


def search_profiles(csv_path, pattern):
    """
    Search profiles by site name (case-insensitive substring match).

    Args:
        csv_path: Path to CSV file
        pattern: Search pattern

    Returns:
        list: Matching profiles
    """
    all_profiles = load_profiles(csv_path)
    if not pattern:
        return all_profiles

    pattern_lower = pattern.lower()
    return [p for p in all_profiles if pattern_lower in p["site"].lower()]


def format_profile_display(profile):
    """
    Format profile for display in fzf or list.

    Returns:
        str: Formatted profile line
    """
    chars = ""
    if profile["lowercase"]:
        chars += "l"
    if profile["uppercase"]:
        chars += "u"
    if profile["digits"]:
        chars += "d"
    if profile["symbols"]:
        chars += "s"

    exclude_info = f" exclude:{profile['exclude']}" if profile['exclude'] else ""

    return f"{profile['site']:<30} │ {profile['login']:<25} │ L:{profile['length']:<2} C:{profile['counter']:<2} │ {chars}{exclude_info}"
