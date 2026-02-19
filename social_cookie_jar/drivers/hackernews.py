"""Hacker News driver — submit, comment, read via news.ycombinator.com."""

import time
from dataclasses import dataclass
from selenium.webdriver.common.by import By

from . import BaseDriver


@dataclass
class HNPost:
    """A Hacker News post."""
    index: int
    title: str
    url: str = ""
    points: int = 0
    comments: int = 0


class HackerNewsDriver(BaseDriver):
    """Hacker News automation via news.ycombinator.com with cookie-based auth."""

    PLATFORM = "hackernews"
    BASE_URL = "https://news.ycombinator.com"
    SESSION_COOKIES = ["user"]

    def login(self) -> bool:
        if not self.jar.inject(self.driver, self.PLATFORM, self.BASE_URL):
            print("[hn] No cookies found. Export them first.")
            return False
        self.driver.get(self.BASE_URL)
        time.sleep(3)
        cookie_names = {c["name"] for c in self.driver.get_cookies()}
        ok = "user" in cookie_names
        # Check for login link
        body = self.driver.find_element(By.TAG_NAME, "body").text
        if "login" in body[:200].lower() and "logout" not in body[:200].lower():
            ok = False
        print(f"[hn] {'Logged in via cookies ✓' if ok else 'Not logged in.'}")
        return ok

    def login_with_creds(self, username: str, password: str) -> bool:
        """Login with username/password (HN supports this directly)."""
        self.driver.get(f"{self.BASE_URL}/login")
        time.sleep(3)
        inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="text"], input[type="password"]')
        if len(inputs) < 2:
            print("[hn] Login form not found")
            return False
        inputs[0].clear()
        inputs[0].send_keys(username)
        inputs[1].clear()
        inputs[1].send_keys(password)
        submit = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="submit"]')
        if submit:
            submit[0].click()
            time.sleep(3)
            self.save_cookies()
            body = self.driver.find_element(By.TAG_NAME, "body").text
            ok = "logout" in body[:300].lower()
            print(f"[hn] {'Login successful ✓' if ok else 'Login failed.'}")
            return ok
        return False

    def feed(self, page: str = "news", limit: int = 30) -> list[HNPost]:
        """Read front page or other pages (newest, ask, show)."""
        self.driver.get(f"{self.BASE_URL}/{page}")
        time.sleep(3)
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".athing")
        posts = []
        for i, row in enumerate(rows[:limit]):
            title_el = row.find_elements(By.CSS_SELECTOR, ".titleline a")
            title = title_el[0].text if title_el else f"Post {i}"
            url = title_el[0].get_attribute("href") if title_el else ""
            posts.append(HNPost(index=i, title=title, url=url))
        return posts

    def submit(self, title: str, url: str = "", text: str = "") -> bool:
        """Submit a new post."""
        self.driver.get(f"{self.BASE_URL}/submit")
        time.sleep(3)
        inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[name="title"]')
        if not inputs:
            print("[hn] Submit form not found")
            return False
        inputs[0].clear()
        inputs[0].send_keys(title)

        if url:
            url_input = self.driver.find_elements(By.CSS_SELECTOR, 'input[name="url"]')
            if url_input:
                url_input[0].clear()
                url_input[0].send_keys(url)
        elif text:
            text_input = self.driver.find_elements(By.CSS_SELECTOR, 'textarea[name="text"]')
            if text_input:
                text_input[0].clear()
                text_input[0].send_keys(text)

        submit = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="submit"]')
        if submit:
            submit[0].click()
            time.sleep(3)
            self.save_cookies()
            print(f"[hn] Submitted: {title[:80]}")
            return True
        return False

    def comment(self, item_url: str, text: str) -> bool:
        """Comment on a post or reply to a comment."""
        self.driver.get(item_url)
        time.sleep(3)
        textareas = self.driver.find_elements(By.CSS_SELECTOR, 'textarea[name="text"]')
        if not textareas:
            print("[hn] Comment box not found")
            return False
        textareas[0].clear()
        textareas[0].send_keys(text)
        time.sleep(0.5)
        submit = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="submit"]')
        if submit:
            submit[0].click()
            time.sleep(3)
            self.save_cookies()
            print(f"[hn] Commented: {text[:80]}...")
            return True
        return False
