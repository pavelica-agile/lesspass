import getpass
import os
import platform
import sys
import traceback
import signal

from lesspass import exceptions
from lesspass.version import __version__
from lesspass.cli import parse_args
from lesspass.profile import create_profile
from lesspass.password import generate_password
from lesspass.clipboard import copy, get_system_copy_command
from lesspass.fingerprint import getpass_with_fingerprint
from lesspass.connected import (
    save_password_profiles,
    load_password_profiles,
    logout,
    export_passwords,
)
from lesspass.csv_storage import load_profiles, search_profiles, format_profile_display
from lesspass.fzf_selector import select_profile_with_fzf, is_fzf_available

signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))


def main(args=sys.argv[1:]):
    args = parse_args(args)
    if args.clipboard and not get_system_copy_command():
        print(
            "error: To use the option -c (--copy) you need pbcopy on OSX, "
            + "xsel, xclip, or wl-clipboard on Linux, and clip on Windows"
        )
        sys.exit(3)

    if args.save_path:
        return save_password_profiles(args.config_home_path, args.url, args.save_path)

    if args.load_path:
        return load_password_profiles(args.config_home_path, args.url, args.load_path)

    if args.export_file_path:
        return export_passwords(args.config_home_path, args.url, args.export_file_path)

    if args.logout:
        return logout(args.config_home_path)

    # Handle --list command
    if args.list_profiles:
        profiles = load_profiles(args.profiles_path)
        if not profiles:
            print("No profiles found in %s" % args.profiles_path)
            print("Create one by editing the file directly with your editor.")
            return
        print("Saved profiles:")
        print("-" * 80)
        for profile in profiles:
            print(format_profile_display(profile))
        return

    # Profile selection mode
    selected_profile = None
    use_profile_mode = False

    # If no site provided, enter interactive selection mode
    if not args.site and not args.prompt:
        if not os.path.exists(args.profiles_path):
            print("No profiles file found at %s" % args.profiles_path)
            print("Create one with your editor. Example format:")
            print("site,login,lowercase,uppercase,digits,symbols,length,counter,exclude")
            print("github.com,user@email.com,true,true,true,true,16,1,")
            sys.exit(1)

        profiles = load_profiles(args.profiles_path)
        selected_profile = select_profile_with_fzf(profiles)
        if selected_profile is None:
            sys.exit(0)  # User cancelled
        use_profile_mode = True

    # If site provided but no login/master_password, try to match profiles
    elif args.site and not args.login and not args.master_password:
        matches = search_profiles(args.profiles_path, args.site)
        if len(matches) == 1:
            # Exactly one match, use it automatically
            selected_profile = matches[0]
            use_profile_mode = True
            print("Using profile: %s" % format_profile_display(selected_profile), file=sys.stderr)
        elif len(matches) > 1:
            # Multiple matches, let user select
            selected_profile = select_profile_with_fzf(matches)
            if selected_profile is None:
                sys.exit(0)  # User cancelled
            use_profile_mode = True

    if args.prompt:
        if not args.site:
            args.site = getpass.getpass("Site: ")
        if not args.login:
            args.login = getpass.getpass("Login: ")

    # Use selected profile or create from args
    if selected_profile:
        profile = selected_profile
    else:
        if not args.site:
            print("error: argument SITE is required but was not provided.")
            sys.exit(4)
        profile = create_profile(args)

    master_password = args.master_password
    if not master_password:
        prompt = "Master Password: "
        if args.no_fingerprint:
            master_password = getpass.getpass(prompt)
        else:
            master_password = getpass_with_fingerprint(prompt)

    if not master_password:
        print("error: argument MASTER_PASSWORD is required but was not provided")
        sys.exit(5)
    try:
        generated_password = generate_password(profile, master_password)
    except exceptions.ExcludeAllCharsAvailable:
        print("error: you can't exclude all chars available")
        sys.exit(6)

    # Always print password to stdout
    print(generated_password)

    # Auto-copy in profile mode or when --clipboard is specified
    if use_profile_mode or args.clipboard:
        if get_system_copy_command():
            try:
                copy(generated_password)
                print("✓ Copied to clipboard", file=sys.stderr)
            except Exception:
                print("✗ Copy failed", file=sys.stderr)
                if args.clipboard:  # Only show detailed error if explicitly requested
                    print("Can you send us an email at contact@lesspass.com\n", file=sys.stderr)
                    print("-" * 80, file=sys.stderr)
                    print("Object: [LessPass][cli] Copy issue on %s" % platform.system(), file=sys.stderr)
                    print("Hello,", file=sys.stderr)
                    print("I got an issue with LessPass cli software.\n", file=sys.stderr)
                    traceback.print_exc()
                    print("-" * 80, file=sys.stderr)
        elif args.clipboard:
            print("error: No clipboard command available", file=sys.stderr)
            print("Install termux-api for Termux, or xsel/xclip for Linux", file=sys.stderr)


if __name__ == "__main__":
    main()
