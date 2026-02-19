#!/usr/bin/env python3
"""
Social Cookie Jar — CLI interface.

Usage:
    python -m social_cookie_jar <action> <platform> [args...]

Platforms: facebook, twitter, linkedin, reddit, discord, instagram, hackernews, substack, pypi

Actions by platform:
    facebook:    login, feed [group_id], post "text", comment <url> "text", group-comment <gid> <idx> "text"
    twitter:     login, feed, post "text", reply <url> "text", notifications, profile [handle]
    linkedin:    login, feed, post "text", comment <url> "text"
    reddit:      login, feed [subreddit], post <subreddit> "title" ["body"], comment <url> "text"
    discord:     login, read <guild_id> <channel_id>, send <guild_id> <channel_id> "text"
    instagram:   login, feed, comment <url> "text", like <url>
    hackernews:  login, login-creds <user> <pass>, feed [page], submit "title" [--url URL] [--text TEXT], comment <url> "text"
    substack:    login, feed, comment <url> "text"
    pypi:        login, check <package_name>

    export-cookies <platform> --cdp-url URL | --json-file FILE [--cookie-dir DIR]

Examples:
    python -m social_cookie_jar login twitter
    python -m social_cookie_jar post twitter "Hello from an AI agent 🤖"
    python -m social_cookie_jar feed reddit LocalLLaMA
    python -m social_cookie_jar export-cookies facebook --cdp-url http://127.0.0.1:9222
"""

import sys
import argparse

from .drivers.facebook import FacebookDriver
from .drivers.twitter import TwitterDriver
from .drivers.linkedin import LinkedInDriver
from .drivers.reddit import RedditDriver
from .drivers.discord import DiscordDriver
from .drivers.instagram import InstagramDriver
from .drivers.hackernews import HackerNewsDriver
from .drivers.substack import SubstackDriver
from .drivers.pypi import PyPIDriver
from .export import export_from_cdp, export_from_json


DRIVERS = {
    "facebook": FacebookDriver,
    "twitter": TwitterDriver,
    "linkedin": LinkedInDriver,
    "reddit": RedditDriver,
    "discord": DiscordDriver,
    "instagram": InstagramDriver,
    "hackernews": HackerNewsDriver,
    "substack": SubstackDriver,
    "pypi": PyPIDriver,
}


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

    if platform not in DRIVERS:
        print(f"Unknown platform: {platform}")
        print(f"Supported: {', '.join(DRIVERS.keys())}")
        sys.exit(1)

    driver = DRIVERS[platform]()
    try:
        # Login check for all platforms
        if action == "login-creds" and platform == "hackernews":
            driver.login_with_creds(sys.argv[3], sys.argv[4])
            return

        if not driver.login():
            print(f"[{platform}] Not logged in. Export cookies first:")
            print(f"  python -m social_cookie_jar export-cookies {platform} --cdp-url http://127.0.0.1:9222")
            sys.exit(1)

        if action == "login":
            print(f"[{platform}] Session valid ✓")

        # ── Facebook ──
        elif platform == "facebook":
            if action == "feed":
                group_id = sys.argv[3] if len(sys.argv) > 3 else None
                for p in driver.feed(group_id):
                    print(f"\n{'='*60}\nPost {p.index}: {p.text[:200]}")
            elif action == "post":
                driver.post(sys.argv[3])
            elif action == "comment":
                driver.comment(sys.argv[3], sys.argv[4])
            elif action == "group-comment":
                driver.feed(sys.argv[3])
                driver.comment_in_feed(int(sys.argv[4]), sys.argv[5])
            else:
                print(f"Unknown action for facebook: {action}")

        # ── Twitter ──
        elif platform == "twitter":
            if action == "feed":
                for t in driver.feed():
                    print(f"\n{'='*60}\nTweet {t.index}: {t.text[:200]}")
            elif action == "post":
                driver.post(sys.argv[3])
            elif action == "reply":
                driver.reply(sys.argv[3], sys.argv[4])
            elif action == "notifications":
                print(driver.notifications())
            elif action == "profile":
                handle = sys.argv[3] if len(sys.argv) > 3 else "AVA1932509"
                print(driver.profile(handle))
            else:
                print(f"Unknown action for twitter: {action}")

        # ── LinkedIn ──
        elif platform == "linkedin":
            if action == "feed":
                for p in driver.feed():
                    print(f"\n{'='*60}\nPost {p.index}: {p.text[:200]}")
            elif action == "post":
                driver.post(sys.argv[3])
            elif action == "comment":
                driver.comment(sys.argv[3], sys.argv[4])
            else:
                print(f"Unknown action for linkedin: {action}")

        # ── Reddit ──
        elif platform == "reddit":
            if action == "feed":
                sub = sys.argv[3] if len(sys.argv) > 3 else None
                for p in driver.feed(sub):
                    print(f"\n{'='*60}\n{p.title[:200]}")
            elif action == "post":
                body = sys.argv[5] if len(sys.argv) > 5 else ""
                driver.post(sys.argv[3], sys.argv[4], body)
            elif action == "comment":
                driver.comment(sys.argv[3], sys.argv[4])
            else:
                print(f"Unknown action for reddit: {action}")

        # ── Discord ──
        elif platform == "discord":
            if action == "read":
                for m in driver.read_channel(sys.argv[3], sys.argv[4]):
                    print(f"\n{m.text[:200]}")
            elif action == "send":
                driver.send_message(sys.argv[3], sys.argv[4], sys.argv[5])
            else:
                print(f"Unknown action for discord: {action}")

        # ── Instagram ──
        elif platform == "instagram":
            if action == "feed":
                for p in driver.feed():
                    print(f"\n{'='*60}\n{p.text[:200]}")
            elif action == "comment":
                driver.comment(sys.argv[3], sys.argv[4])
            elif action == "like":
                driver.like_post(sys.argv[3])
            else:
                print(f"Unknown action for instagram: {action}")

        # ── Hacker News ──
        elif platform == "hackernews":
            if action == "feed":
                page = sys.argv[3] if len(sys.argv) > 3 else "news"
                for p in driver.feed(page):
                    print(f"  {p.index}. {p.title[:100]}")
            elif action == "submit":
                # submit hackernews "title" [--url URL | --text TEXT]
                title = sys.argv[3]
                url = text = ""
                if "--url" in sys.argv:
                    url = sys.argv[sys.argv.index("--url") + 1]
                if "--text" in sys.argv:
                    text = sys.argv[sys.argv.index("--text") + 1]
                driver.submit(title, url, text)
            elif action == "comment":
                driver.comment(sys.argv[3], sys.argv[4])
            else:
                print(f"Unknown action for hackernews: {action}")

        # ── Substack ──
        elif platform == "substack":
            if action == "feed":
                for p in driver.feed():
                    print(f"\n{'='*60}\n{p.title[:200]}")
            elif action == "comment":
                driver.comment(sys.argv[3], sys.argv[4])
            else:
                print(f"Unknown action for substack: {action}")

        # ── PyPI ──
        elif platform == "pypi":
            if action == "check":
                pkg = driver.check_package(sys.argv[3])
                if pkg:
                    print(f"{pkg.name} v{pkg.version}\n{pkg.description}")
                else:
                    print(f"Package not found: {sys.argv[3]}")
            else:
                print(f"Unknown action for pypi: {action}")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
