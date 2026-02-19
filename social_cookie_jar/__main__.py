#!/usr/bin/env python3
"""
Social Cookie Jar — CLI interface.

Usage:
    python -m social_cookie_jar login facebook
    python -m social_cookie_jar feed facebook [group_id]
    python -m social_cookie_jar post facebook "Hello world"
    python -m social_cookie_jar comment facebook <post_url> "Comment text"
    python -m social_cookie_jar group-comment facebook <group_id> <post_index> "Comment"
    python -m social_cookie_jar export-cookies facebook --cdp-url http://127.0.0.1:9222
    python -m social_cookie_jar export-cookies facebook --json-file cookies.json
"""

import sys
import argparse

from .drivers.facebook import FacebookDriver
from .export import export_from_cdp, export_from_json


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    action = sys.argv[1]
    platform = sys.argv[2]

    # Cookie export (no driver needed)
    if action == "export-cookies":
        parser = argparse.ArgumentParser()
        parser.add_argument("action")
        parser.add_argument("platform")
        parser.add_argument("--cdp-url", default=None)
        parser.add_argument("--json-file", default=None)
        parser.add_argument("--cookie-dir", default="./cookies")
        args = parser.parse_args()

        if args.cdp_url:
            path = export_from_cdp(args.cdp_url, args.platform, args.cookie_dir)
            print(f"Exported cookies to {path}")
        elif args.json_file:
            path = export_from_json(args.json_file, args.platform, args.cookie_dir)
            print(f"Exported cookies to {path}")
        else:
            print("Specify --cdp-url or --json-file")
            sys.exit(1)
        return

    # Platform drivers
    if platform == "facebook":
        driver = FacebookDriver()
        try:
            if not driver.login():
                print("[fb] Not logged in. Export cookies first:")
                print("  python -m social_cookie_jar export-cookies facebook --cdp-url http://127.0.0.1:9222")
                sys.exit(1)

            if action == "login":
                print("[fb] Session valid ✓")
            elif action == "feed":
                group_id = sys.argv[3] if len(sys.argv) > 3 else None
                posts = driver.feed(group_id)
                for p in posts:
                    print(f"\n{'='*60}")
                    print(f"Post {p.index}: {p.text[:200]}")
            elif action == "post":
                driver.post(sys.argv[3])
            elif action == "comment":
                driver.comment(sys.argv[3], sys.argv[4])
            elif action == "group-comment":
                group_id = sys.argv[3]
                post_idx = int(sys.argv[4])
                comment = sys.argv[5]
                driver.feed(group_id)  # Load the feed first
                driver.comment_in_feed(post_idx, comment)
            else:
                print(f"Unknown action: {action}")
                sys.exit(1)
        finally:
            driver.quit()
    else:
        print(f"Platform '{platform}' not yet supported. PRs welcome!")
        sys.exit(1)


if __name__ == "__main__":
    main()
