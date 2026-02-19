"""Instagram driver — post, read feed, comment via instagram.com."""

import time
from dataclasses import dataclass
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from . import BaseDriver


@dataclass
class InstaPost:
    """An Instagram post."""
    index: int
    text: str
    author: str = ""
    url: str = ""


class InstagramDriver(BaseDriver):
    """Instagram automation via www.instagram.com with cookie-based auth.
    
    NOTE: Instagram heavily rate-limits and detects automation.
    Use sparingly. For business accounts, prefer Meta Business Suite.
    """

    PLATFORM = "instagram"
    BASE_URL = "https://www.instagram.com"
    SESSION_COOKIES = ["sessionid", "ds_user_id"]

    def login(self) -> bool:
        if not self.jar.inject(self.driver, self.PLATFORM, self.BASE_URL):
            print("[ig] No cookies found. Export them first.")
            return False
        self.driver.get(self.BASE_URL)
        time.sleep(5)
        cookie_names = {c["name"] for c in self.driver.get_cookies()}
        ok = all(n in cookie_names for n in self.SESSION_COOKIES)
        if "/accounts/login" in self.driver.current_url:
            ok = False
        print(f"[ig] {'Logged in via cookies ✓' if ok else 'Cookie session expired.'}")
        return ok

    def feed(self, limit: int = 10) -> list[InstaPost]:
        """Read the home feed."""
        self.driver.get(self.BASE_URL)
        time.sleep(6)
        articles = self.driver.find_elements(By.CSS_SELECTOR, "article")
        posts = []
        for i, art in enumerate(articles[:limit]):
            text = art.text[:400]
            posts.append(InstaPost(index=i, text=text))
        return posts

    def comment(self, post_url: str, text: str) -> bool:
        """Comment on a post by URL."""
        self.driver.get(post_url)
        time.sleep(5)
        textareas = self.driver.find_elements(
            By.CSS_SELECTOR,
            'textarea[aria-label*="comment" i], textarea[placeholder*="comment" i]',
        )
        if not textareas:
            print("[ig] Comment box not found")
            return False
        ta = textareas[0]
        ta.click()
        time.sleep(0.5)
        ta.send_keys(text)
        time.sleep(1)
        post_btns = self.driver.find_elements(By.CSS_SELECTOR, 'button[type="submit"]')
        for btn in post_btns:
            if btn.text.strip().lower() == "post":
                btn.click()
                time.sleep(3)
                self.save_cookies()
                print(f"[ig] Commented: {text[:80]}...")
                return True
        print("[ig] Post button not found")
        return False

    def like_post(self, post_url: str) -> bool:
        """Like a post by URL."""
        self.driver.get(post_url)
        time.sleep(5)
        like_btns = self.driver.find_elements(By.CSS_SELECTOR, '[aria-label="Like"]')
        if like_btns:
            like_btns[0].click()
            time.sleep(1)
            print("[ig] Liked post")
            return True
        print("[ig] Like button not found")
        return False
