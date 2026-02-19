"""Cookie export utilities — extract cookies from various sources."""

import json
import pickle
from pathlib import Path
from typing import Optional


def export_from_cdp(
    cdp_url: str = "http://127.0.0.1:9222",
    platform: str = "facebook",
    output_dir: str = "./cookies",
    urls: Optional[list[str]] = None,
) -> Path:
    """Export cookies from a Chrome DevTools Protocol endpoint.
    
    Requires `websocket-client` package.
    """
    import websocket
    
    # Platform URL defaults
    platform_urls = {
        "facebook": ["https://www.facebook.com/"],
        "twitter": ["https://x.com/", "https://twitter.com/"],
        "linkedin": ["https://www.linkedin.com/"],
    }
    target_urls = urls or platform_urls.get(platform, [])

    # Get first available page target
    import urllib.request
    tabs = json.loads(urllib.request.urlopen(f"{cdp_url}/json").read())
    page_targets = [t for t in tabs if t.get("type") == "page"]
    if not page_targets:
        raise RuntimeError("No page targets found in Chrome")
    
    ws_url = page_targets[0]["webSocketDebuggerUrl"]
    ws = websocket.create_connection(ws_url, suppress_origin=True)
    
    ws.send(json.dumps({
        "id": 1,
        "method": "Network.getCookies",
        "params": {"urls": target_urls},
    }))
    result = json.loads(ws.recv())
    ws.close()

    cookies = result.get("result", {}).get("cookies", [])
    if not cookies:
        raise RuntimeError(f"No cookies found for {platform}")

    # Convert CDP cookies to Selenium format
    selenium_cookies = []
    for c in cookies:
        sc = {
            "name": c["name"],
            "value": c["value"],
            "domain": c["domain"],
            "path": c.get("path", "/"),
            "secure": c.get("secure", False),
        }
        if c.get("expires", -1) > 0:
            sc["expiry"] = int(c["expires"])
        selenium_cookies.append(sc)

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{platform}.pkl"
    with open(path, "wb") as f:
        pickle.dump(selenium_cookies, f)

    return path


def export_from_json(
    json_file: str,
    platform: str = "facebook",
    output_dir: str = "./cookies",
) -> Path:
    """Export cookies from a JSON file (e.g., from a browser extension).
    
    Expects a list of objects with at least: name, value, domain.
    """
    with open(json_file) as f:
        raw_cookies = json.load(f)

    selenium_cookies = []
    for c in raw_cookies:
        sc = {
            "name": c["name"],
            "value": c["value"],
            "domain": c.get("domain", ""),
            "path": c.get("path", "/"),
            "secure": c.get("secure", False),
        }
        if "expirationDate" in c:
            sc["expiry"] = int(c["expirationDate"])
        elif "expires" in c and c["expires"]:
            sc["expiry"] = int(c["expires"])
        selenium_cookies.append(sc)

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{platform}.pkl"
    with open(path, "wb") as f:
        pickle.dump(selenium_cookies, f)

    return path


def export_from_playwright(
    context,
    platform: str = "facebook",
    output_dir: str = "./cookies",
) -> Path:
    """Export cookies from a Playwright browser context."""
    cookies = context.cookies()

    selenium_cookies = []
    for c in cookies:
        sc = {
            "name": c["name"],
            "value": c["value"],
            "domain": c.get("domain", ""),
            "path": c.get("path", "/"),
            "secure": c.get("secure", False),
        }
        if c.get("expires", -1) > 0:
            sc["expiry"] = int(c["expires"])
        selenium_cookies.append(sc)

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{platform}.pkl"
    with open(path, "wb") as f:
        pickle.dump(selenium_cookies, f)

    return path
