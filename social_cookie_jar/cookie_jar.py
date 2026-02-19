"""Cookie jar management — load, save, validate cookies."""

import pickle
import json
from pathlib import Path
from typing import Optional


class CookieJar:
    """Manages browser cookies for social platforms."""

    def __init__(self, cookie_dir: str = "./cookies"):
        self.cookie_dir = Path(cookie_dir)
        self.cookie_dir.mkdir(parents=True, exist_ok=True)

    def save(self, cookies: list[dict], platform: str, fmt: str = "pkl") -> Path:
        """Save cookies to disk."""
        path = self.cookie_dir / f"{platform}.{fmt}"
        if fmt == "pkl":
            with open(path, "wb") as f:
                pickle.dump(cookies, f)
        elif fmt == "json":
            with open(path, "w") as f:
                json.dump(cookies, f, indent=2)
        else:
            raise ValueError(f"Unknown format: {fmt}")
        return path

    def load(self, platform: str) -> Optional[list[dict]]:
        """Load cookies from disk. Tries pkl first, then json."""
        for fmt in ("pkl", "json"):
            path = self.cookie_dir / f"{platform}.{fmt}"
            if path.exists():
                if fmt == "pkl":
                    with open(path, "rb") as f:
                        return pickle.load(f)
                else:
                    with open(path) as f:
                        return json.load(f)
        return None

    def has_session(self, platform: str, required_cookies: list[str]) -> bool:
        """Check if saved cookies contain required session cookies."""
        cookies = self.load(platform)
        if not cookies:
            return False
        cookie_names = {c["name"] for c in cookies}
        return all(name in cookie_names for name in required_cookies)

    def inject(self, driver, platform: str, domain: str) -> bool:
        """Load cookies and inject them into a Selenium driver."""
        cookies = self.load(platform)
        if not cookies:
            return False
        driver.get(domain)
        import time
        time.sleep(1)
        injected = 0
        for cookie in cookies:
            try:
                driver.add_cookie(cookie)
                injected += 1
            except Exception:
                pass
        return injected > 0
