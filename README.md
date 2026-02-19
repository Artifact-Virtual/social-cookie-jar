# 🍪 Social Cookie Jar

Headless social media automation toolkit for AI agents. Cookie-based auth, paste-and-send pattern, zero typing detection.

## Supported Platforms

| Platform | Feed | Post | Comment | Reply | Like |
|----------|------|------|---------|-------|------|
| Facebook | ✅ | ✅ | ✅ | — | — |
| Twitter/X | ✅ | ✅ | — | ✅ | — |
| LinkedIn | ✅ | ✅ | ✅ | — | — |
| Reddit | ✅ | ✅ | ✅ | — | — |
| Discord | ✅ | — | — | — | — |
| Instagram | ✅ | — | ✅ | — | ✅ |
| Hacker News | ✅ | ✅ | ✅ | — | — |
| Substack | ✅ | — | ✅ | — | — |
| PyPI | — | — | — | — | — |

## How It Works

1. **Login once** in a real browser (or use the CDP cookie export)
2. **Export cookies** to a pickle/JSON file
3. **Selenium loads cookies** — no login flow, no 2FA, no CAPTCHA
4. **Paste-and-send** — text is pasted via `ClipboardEvent`, not typed character by character. Instant and indistinguishable from human behavior.

## Install

```bash
pip install social-cookie-jar
# or
pip install -e .
```

Requires: Python 3.10+, Chrome/Chromium, ChromeDriver

## Quick Start

### Export cookies from a running browser (CDP)

```python
from social_cookie_jar import export_from_cdp

# From an OpenClaw/Playwright/Puppeteer browser with CDP enabled
export_from_cdp("ws://127.0.0.1:9222/devtools/page/TARGET_ID", "facebook", "./cookies")
```

### Use a driver

```python
from social_cookie_jar import TwitterDriver

with TwitterDriver(cookie_dir="./cookies") as tw:
    if tw.login():
        tw.post("Hello from an AI agent 🤖")
        
        for tweet in tw.feed():
            print(tweet.text[:100])
        
        tw.reply("https://x.com/user/status/123", "Great thread!")
```

### CLI

```bash
# Login check
python -m social_cookie_jar login twitter

# Post
python -m social_cookie_jar post twitter "Hello world"
python -m social_cookie_jar post facebook "My first post"

# Read feeds
python -m social_cookie_jar feed reddit LocalLLaMA
python -m social_cookie_jar feed hackernews

# Comment
python -m social_cookie_jar comment facebook https://fb.com/post/123 "Nice post!"
python -m social_cookie_jar reply twitter https://x.com/user/status/123 "Interesting!"

# Submit to HN
python -m social_cookie_jar submit hackernews "Show HN: My Project" --url https://myproject.com

# Export cookies
python -m social_cookie_jar export-cookies facebook --cdp-url ws://127.0.0.1:9222/devtools/page/ID
python -m social_cookie_jar export-cookies twitter --json-file cookies.json
```

## Architecture

```
social_cookie_jar/
├── __init__.py          # Package exports
├── __main__.py          # CLI entry point
├── cookie_jar.py        # CookieJar — save/load/inject cookies (pickle + JSON)
├── export.py            # CDP, Playwright, JSON, Netscape cookie import
└── drivers/
    ├── __init__.py      # BaseDriver — shared Selenium utilities + paste pattern
    ├── facebook.py      # FacebookDriver
    ├── twitter.py       # TwitterDriver
    ├── linkedin.py      # LinkedInDriver
    ├── reddit.py        # RedditDriver
    ├── discord.py       # DiscordDriver
    ├── instagram.py     # InstagramDriver
    ├── hackernews.py    # HackerNewsDriver
    ├── substack.py      # SubstackDriver
    └── pypi.py          # PyPIDriver
```

### Key Design Decisions

- **Cookie-based auth** — no passwords stored or typed into browsers. Export cookies once from a real session, reuse forever (until they expire).
- **Paste, don't type** — `ClipboardEvent` paste is instant and bypasses typing-speed heuristics. This is how humans actually work (Ctrl+V).
- **Platform-specific drivers** — each platform has its own CSS selectors and flow. No generic "just find a textbox" approach.
- **Headless by default** — no GUI needed. Perfect for servers, CI, AI agent runtimes.

## Cookie Refresh

Cookies expire (typically 30-90 days). When they do:

1. Login manually in a regular browser
2. Re-export cookies: `python -m social_cookie_jar export-cookies <platform> --cdp-url <url>`
3. Selenium picks up new cookies automatically

## For AI Agents

This toolkit is designed for AI agents that need social media presence. See `llms.txt` in this repo for AI-specific guidance.

**Separation pattern:** Use your host browser for human accounts, and Social Cookie Jar (Selenium) for the agent's own accounts. Never mix sessions.

## License

MIT — see [LICENSE](LICENSE)
