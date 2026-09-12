import shutil
import subprocess
import sys

from lesspass.csv_storage import format_profile_display


def is_fzf_available():
    """Check if fzf is installed"""
    return shutil.which("fzf") is not None


def select_profile_with_fzf(profiles):
    """
    Display profiles in fzf for interactive selection.

    Args:
        profiles: List of profile dictionaries

    Returns:
        dict: Selected profile, or None if cancelled
    """
    if not profiles:
        print("No profiles found.", file=sys.stderr)
        return None

    if not is_fzf_available():
        print("Error: fzf is not installed.", file=sys.stderr)
        print("Install with: pkg install fzf", file=sys.stderr)
        return None

    # Format profiles for display
    lines = [format_profile_display(p) for p in profiles]

    # Call fzf
    try:
        result = subprocess.run(
            [
                "fzf",
                "--height=40%",
                "--reverse",
                "--header=Select a profile (ESC to cancel)",
                "--border",
                "--prompt=Profile> ",
            ],
            input="\n".join(lines),
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            # User cancelled (ESC or Ctrl+C)
            return None

        # Parse the selection - find which profile was selected
        selected_line = result.stdout.strip()
        for i, line in enumerate(lines):
            if line == selected_line:
                return profiles[i]

        return None

    except FileNotFoundError:
        print("Error: fzf is not installed.", file=sys.stderr)
        print("Install with: pkg install fzf", file=sys.stderr)
        return None
    except KeyboardInterrupt:
        return None
