"""Facebook driver — post, comment, read feeds via www.facebook.com."""

import time
from dataclasses import dataclass
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from . import BaseDriver


@dataclass
class Post:
    """A Facebook post."""
    index: int
    text: str
    permalink: str = ""
    author: str = ""

    def is_relevant(self, *keywords: str) -> bool:
        """Check if post text contains any of the keywords."""
        text_lower = self.text.lower()
        return any(kw.lower() in text_lower for kw in keywords)


class FacebookDriver(BaseDriver):
    """Facebook automation via www.facebook.com with cookie-based auth."""

    PLATFORM = "facebook"
    BASE_URL = "https://www.facebook.com"
    SESSION_COOKIES = ["c_user", "xs"]

    def login(self) -> bool:
        """Login using saved cookies."""
        if not self.jar.inject(self.driver, self.PLATFORM, self.BASE_URL):
            print("[fb] No cookies found. Export them first (see README).")
            return False

        # Verify session by visiting profile
        self.driver.get(f"{self.BASE_URL}/me")
        time.sleep(4)
        cookie_names = {c["name"] for c in self.driver.get_cookies()}
        logged_in = all(name in cookie_names for name in self.SESSION_COOKIES)
        if logged_in:
            print("[fb] Logged in via cookies ✓")
        else:
            print("[fb] Cookie session expired. Re-export cookies.")
        return logged_in

    def feed(self, group_id: str | None = None, limit: int = 10) -> list[Post]:
        """Read the home feed or a group feed."""
        if group_id:
            self.driver.get(f"{self.BASE_URL}/groups/{group_id}/")
        else:
            self.driver.get(self.BASE_URL)
        time.sleep(7)

        # Scroll to load posts
        self.driver.execute_script("window.scrollTo(0, 600);")
        time.sleep(3)

        # Extract body text and split into post sections
        body = self.driver.find_element(By.TAG_NAME, "body").text
        
        # Find comment-related aria-labels to identify post boundaries
        comment_boxes = self.driver.find_elements(
            By.CSS_SELECTOR,
            'div[role="textbox"][aria-label*="comment" i], '
            'div[role="textbox"][aria-label*="answer" i]',
        )

        posts = []
        for i, box in enumerate(comment_boxes[:limit]):
            # Walk up to find the post container
            try:
                article = box.find_element(By.XPATH, "./ancestor::div[@role='article']")
                text = article.text[:500]
            except Exception:
                text = f"(post {i} — text extraction failed)"

            posts.append(Post(index=i, text=text))

        return posts

    def post(self, text: str, profile_id: str | None = None) -> bool:
        """Post to own timeline."""
        if profile_id:
            self.driver.get(f"{self.BASE_URL}/profile.php?id={profile_id}")
        else:
            self.driver.get(f"{self.BASE_URL}/me")
        time.sleep(5)

        # Click composer
        composers = self.driver.find_elements(By.CSS_SELECTOR, "[aria-label]")
        for c in composers:
            if "mind" in (c.get_attribute("aria-label") or "").lower():
                c.click()
                time.sleep(3)
                break

        textboxes = self.driver.find_elements(
            By.CSS_SELECTOR, '[contenteditable="true"][role="textbox"]'
        )
        if not textboxes:
            print("[fb] Could not find composer textbox")
            return False

        textboxes[0].click()
        time.sleep(0.5)
        self.paste_text(textboxes[0], text)
        time.sleep(2)

        # Click Post
        buttons = self.driver.find_elements(By.CSS_SELECTOR, '[aria-label="Post"]')
        if buttons:
            buttons[0].click()
            time.sleep(3)
            self.save_cookies()
            print(f"[fb] Posted: {text[:80]}...")
            return True

        print("[fb] Post button not found")
        return False

    def comment(self, post_url: str, text: str) -> bool:
        """Comment on a post by URL."""
        self.driver.get(post_url)
        time.sleep(6)

        boxes = self.driver.find_elements(
            By.CSS_SELECTOR, '[contenteditable="true"][role="textbox"]'
        )
        if not boxes:
            # Try clicking Comment button first
            btns = self.driver.find_elements(
                By.CSS_SELECTOR, '[aria-label*="comment" i]'
            )
            for btn in btns:
                if "leave" in (btn.get_attribute("aria-label") or "").lower():
                    btn.click()
                    time.sleep(2)
                    break
            boxes = self.driver.find_elements(
                By.CSS_SELECTOR, '[contenteditable="true"][role="textbox"]'
            )

        if not boxes:
            print("[fb] No comment box found")
            return False

        box = boxes[-1]
        box.click()
        time.sleep(0.5)
        self.paste_text(box, text)
        time.sleep(1)
        box.send_keys(Keys.RETURN)
        time.sleep(2)
        self.save_cookies()
        print(f"[fb] Commented: {text[:80]}...")
        return True

    def comment_in_feed(self, post_index: int, text: str) -> bool:
        """Comment on the nth post in the currently loaded feed.
        
        Call feed() first to load the page, then use this.
        """
        boxes = self.driver.find_elements(
            By.CSS_SELECTOR,
            'div[role="textbox"][aria-label*="comment" i], '
            'div[role="textbox"][aria-label*="answer" i]',
        )
        if post_index >= len(boxes):
            print(f"[fb] Post {post_index} out of range ({len(boxes)} available)")
            return False

        box = boxes[post_index]
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", box
        )
        time.sleep(1)
        box.click()
        time.sleep(0.5)
        self.paste_text(box, text)
        time.sleep(1)
        box.send_keys(Keys.RETURN)
        time.sleep(2)
        self.save_cookies()
        print(f"[fb] Commented on post {post_index}: {text[:80]}...")
        return True
