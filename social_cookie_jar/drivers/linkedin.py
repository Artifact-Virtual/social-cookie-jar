"""LinkedIn driver — post, read feed, comment via linkedin.com."""

import time
from dataclasses import dataclass
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from . import BaseDriver


@dataclass
class LinkedInPost:
    """A LinkedIn feed post."""
    index: int
    text: str
    author: str = ""


class LinkedInDriver(BaseDriver):
    """LinkedIn automation via www.linkedin.com with cookie-based auth."""

    PLATFORM = "linkedin"
    BASE_URL = "https://www.linkedin.com"
    SESSION_COOKIES = ["li_at"]

    def login(self) -> bool:
        if not self.jar.inject(self.driver, self.PLATFORM, self.BASE_URL):
            print("[li] No cookies found. Export them first.")
            return False
        self.driver.get(f"{self.BASE_URL}/feed/")
        time.sleep(5)
        cookie_names = {c["name"] for c in self.driver.get_cookies()}
        ok = "li_at" in cookie_names
        # Check for auth wall
        if "/login" in self.driver.current_url or "/authwall" in self.driver.current_url:
            ok = False
        print(f"[li] {'Logged in via cookies ✓' if ok else 'Cookie session expired.'}")
        return ok

    def feed(self, limit: int = 10) -> list[LinkedInPost]:
        """Read the main feed."""
        self.driver.get(f"{self.BASE_URL}/feed/")
        time.sleep(6)
        # Scroll to load
        self.driver.execute_script("window.scrollTo(0, 800);")
        time.sleep(3)

        posts_el = self.driver.find_elements(
            By.CSS_SELECTOR, '[data-urn*="activity"], .feed-shared-update-v2'
        )
        posts = []
        for i, el in enumerate(posts_el[:limit]):
            text = el.text[:400]
            posts.append(LinkedInPost(index=i, text=text))
        return posts

    def post(self, text: str) -> bool:
        """Create a new post."""
        self.driver.get(f"{self.BASE_URL}/feed/")
        time.sleep(5)

        # Click "Start a post" button
        starters = self.driver.find_elements(
            By.CSS_SELECTOR,
            'button.share-box-feed-entry__trigger, '
            '[aria-label*="Start a post"], '
            '[class*="share-box"] button',
        )
        if starters:
            starters[0].click()
            time.sleep(3)

        # Find the textbox
        boxes = self.driver.find_elements(
            By.CSS_SELECTOR,
            '[role="textbox"][contenteditable="true"], '
            '.ql-editor[contenteditable="true"]',
        )
        if not boxes:
            print("[li] Composer textbox not found")
            return False

        box = boxes[0]
        box.click()
        time.sleep(0.5)
        self.paste_text(box, text)
        time.sleep(2)

        # Click Post button
        post_btn = self.driver.find_elements(
            By.CSS_SELECTOR,
            'button.share-actions__primary-action, '
            'button[aria-label*="Post" i]',
        )
        if post_btn:
            post_btn[0].click()
            time.sleep(4)
            self.save_cookies()
            print(f"[li] Posted: {text[:80]}...")
            return True
        print("[li] Post button not found")
        return False

    def comment(self, post_url: str, text: str) -> bool:
        """Comment on a LinkedIn post by URL."""
        self.driver.get(post_url)
        time.sleep(5)

        # Click comment button to open box
        comment_btns = self.driver.find_elements(
            By.CSS_SELECTOR, 'button[aria-label*="Comment" i]'
        )
        if comment_btns:
            comment_btns[0].click()
            time.sleep(2)

        boxes = self.driver.find_elements(
            By.CSS_SELECTOR,
            '[role="textbox"][contenteditable="true"], '
            '.ql-editor[contenteditable="true"]',
        )
        if not boxes:
            print("[li] Comment box not found")
            return False

        box = boxes[-1]
        box.click()
        time.sleep(0.5)
        self.paste_text(box, text)
        time.sleep(1)

        # Submit
        submit = self.driver.find_elements(
            By.CSS_SELECTOR,
            'button.comments-comment-box__submit-button, '
            'button[aria-label*="Post comment" i]',
        )
        if submit:
            submit[0].click()
            time.sleep(3)
            self.save_cookies()
            print(f"[li] Commented: {text[:80]}...")
            return True

        # Fallback: Ctrl+Enter
        box.send_keys(Keys.CONTROL + Keys.RETURN)
        time.sleep(3)
        self.save_cookies()
        print(f"[li] Commented (Ctrl+Enter): {text[:80]}...")
        return True
