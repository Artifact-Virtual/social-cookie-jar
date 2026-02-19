"""Reddit driver — post, comment, read feeds via www.reddit.com."""

import time
from dataclasses import dataclass
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from . import BaseDriver


@dataclass
class RedditPost:
    """A Reddit post."""
    index: int
    title: str
    text: str = ""
    subreddit: str = ""
    url: str = ""


class RedditDriver(BaseDriver):
    """Reddit automation via www.reddit.com with cookie-based auth."""

    PLATFORM = "reddit"
    BASE_URL = "https://www.reddit.com"
    SESSION_COOKIES = ["reddit_session", "token_v2"]

    def login(self) -> bool:
        if not self.jar.inject(self.driver, self.PLATFORM, self.BASE_URL):
            print("[reddit] No cookies found. Export them first.")
            return False
        self.driver.get(self.BASE_URL)
        time.sleep(5)
        cookie_names = {c["name"] for c in self.driver.get_cookies()}
        ok = any(n in cookie_names for n in self.SESSION_COOKIES)
        # Check if we see login button (not logged in)
        login_btns = self.driver.find_elements(
            By.CSS_SELECTOR, '[data-testid="login-button"], a[href*="/login"]'
        )
        if login_btns and len(login_btns) > 0:
            ok = False
        print(f"[reddit] {'Logged in via cookies ✓' if ok else 'Not logged in.'}")
        return ok

    def feed(self, subreddit: str | None = None, limit: int = 10) -> list[RedditPost]:
        """Read the home feed or a subreddit."""
        if subreddit:
            self.driver.get(f"{self.BASE_URL}/r/{subreddit}/")
        else:
            self.driver.get(self.BASE_URL)
        time.sleep(6)
        self.driver.execute_script("window.scrollTo(0, 600);")
        time.sleep(3)

        posts_el = self.driver.find_elements(
            By.CSS_SELECTOR,
            'shreddit-post, [data-testid="post-container"], article',
        )
        posts = []
        for i, el in enumerate(posts_el[:limit]):
            text = el.text[:400]
            title = text.split("\n")[0] if text else f"Post {i}"
            posts.append(RedditPost(index=i, title=title, text=text))
        return posts

    def post(self, subreddit: str, title: str, body: str = "") -> bool:
        """Submit a new post to a subreddit."""
        self.driver.get(f"{self.BASE_URL}/r/{subreddit}/submit")
        time.sleep(5)

        # Title field
        title_inputs = self.driver.find_elements(
            By.CSS_SELECTOR,
            'textarea[name="title"], [placeholder*="title" i], '
            'input[aria-label*="Title" i]',
        )
        if not title_inputs:
            print("[reddit] Title field not found")
            return False

        title_inputs[0].click()
        time.sleep(0.3)
        self.paste_text(title_inputs[0], title)
        time.sleep(1)

        # Body
        if body:
            body_boxes = self.driver.find_elements(
                By.CSS_SELECTOR,
                '[role="textbox"][contenteditable="true"], '
                'textarea[name="body"], .DraftEditor-root [contenteditable]',
            )
            if body_boxes:
                body_boxes[0].click()
                time.sleep(0.3)
                self.paste_text(body_boxes[0], body)
                time.sleep(1)

        # Submit
        submit = self.driver.find_elements(
            By.CSS_SELECTOR, 'button[type="submit"], button:has-text("Post")'
        )
        for btn in submit:
            text = btn.text.strip().lower()
            if text in ("post", "submit"):
                btn.click()
                time.sleep(5)
                self.save_cookies()
                print(f"[reddit] Posted: {title[:80]}")
                return True

        print("[reddit] Submit button not found")
        return False

    def comment(self, post_url: str, text: str) -> bool:
        """Comment on a Reddit post by URL."""
        self.driver.get(post_url)
        time.sleep(5)

        boxes = self.driver.find_elements(
            By.CSS_SELECTOR,
            '[role="textbox"][contenteditable="true"], '
            'textarea[name="comment"], .DraftEditor-root [contenteditable]',
        )
        if not boxes:
            # Click "Add a comment" to expand
            add_btns = self.driver.find_elements(
                By.CSS_SELECTOR, '[placeholder*="comment" i]'
            )
            if add_btns:
                add_btns[0].click()
                time.sleep(2)
            boxes = self.driver.find_elements(
                By.CSS_SELECTOR, '[role="textbox"][contenteditable="true"]'
            )

        if not boxes:
            print("[reddit] Comment box not found")
            return False

        box = boxes[0]
        box.click()
        time.sleep(0.5)
        self.paste_text(box, text)
        time.sleep(1)

        submit = self.driver.find_elements(
            By.CSS_SELECTOR, 'button[type="submit"]'
        )
        for btn in submit:
            if "comment" in btn.text.lower():
                btn.click()
                time.sleep(3)
                self.save_cookies()
                print(f"[reddit] Commented: {text[:80]}...")
                return True

        # Fallback: Ctrl+Enter
        box.send_keys(Keys.CONTROL + Keys.RETURN)
        time.sleep(3)
        print(f"[reddit] Commented (Ctrl+Enter): {text[:80]}...")
        return True
