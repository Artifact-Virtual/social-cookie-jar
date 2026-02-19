"""Substack driver — read, comment via substack.com."""

import time
from dataclasses import dataclass
from selenium.webdriver.common.by import By

from . import BaseDriver


@dataclass
class SubstackPost:
    """A Substack post."""
    index: int
    title: str
    text: str = ""
    url: str = ""


class SubstackDriver(BaseDriver):
    """Substack automation via substack.com with cookie-based auth.
    
    NOTE: Substack uses magic link (email) auth. Export cookies after
    clicking the magic link in your email.
    """

    PLATFORM = "substack"
    BASE_URL = "https://substack.com"
    SESSION_COOKIES = ["substack.sid"]

    def login(self) -> bool:
        if not self.jar.inject(self.driver, self.PLATFORM, self.BASE_URL):
            print("[substack] No cookies found. Export them first.")
            return False
        self.driver.get(self.BASE_URL)
        time.sleep(5)
        cookie_names = {c["name"] for c in self.driver.get_cookies()}
        ok = any("sid" in n.lower() for n in cookie_names)
        # Check if we see the dashboard or user menu
        body = self.driver.find_element(By.TAG_NAME, "body").text[:500]
        if "sign in" in body.lower() and "dashboard" not in body.lower():
            ok = False
        print(f"[substack] {'Logged in via cookies ✓' if ok else 'Not logged in.'}")
        return ok

    def feed(self, limit: int = 10) -> list[SubstackPost]:
        """Read the home feed / inbox."""
        self.driver.get(f"{self.BASE_URL}/inbox")
        time.sleep(5)
        articles = self.driver.find_elements(By.CSS_SELECTOR, "article, [class*='post-preview']")
        posts = []
        for i, art in enumerate(articles[:limit]):
            text = art.text[:400]
            title = text.split("\n")[0] if text else f"Post {i}"
            posts.append(SubstackPost(index=i, title=title, text=text))
        return posts

    def comment(self, post_url: str, text: str) -> bool:
        """Comment on a Substack post."""
        self.driver.get(post_url)
        time.sleep(5)
        # Scroll to comments
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.8);")
        time.sleep(2)

        boxes = self.driver.find_elements(
            By.CSS_SELECTOR,
            '[role="textbox"][contenteditable="true"], '
            'textarea[placeholder*="comment" i], '
            '.ProseMirror[contenteditable="true"]',
        )
        if not boxes:
            print("[substack] Comment box not found")
            return False
        box = boxes[0]
        box.click()
        time.sleep(0.5)
        self.paste_text(box, text)
        time.sleep(1)

        submit = self.driver.find_elements(
            By.CSS_SELECTOR, 'button[class*="comment"]'
        )
        for btn in submit:
            if "post" in btn.text.lower() or "reply" in btn.text.lower():
                btn.click()
                time.sleep(3)
                self.save_cookies()
                print(f"[substack] Commented: {text[:80]}...")
                return True
        print("[substack] Submit button not found")
        return False
