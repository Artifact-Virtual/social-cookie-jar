"""Twitter/X driver — post, read feed, check notifications via x.com."""

import time
from dataclasses import dataclass
from selenium.webdriver.common.by import By

from . import BaseDriver


@dataclass
class Tweet:
    """A tweet from the timeline."""
    index: int
    text: str
    author: str = ""
    url: str = ""


class TwitterDriver(BaseDriver):
    """Twitter/X automation via x.com with cookie-based auth."""

    PLATFORM = "twitter"
    BASE_URL = "https://x.com"
    SESSION_COOKIES = ["auth_token", "ct0"]

    def login(self) -> bool:
        if not self.jar.inject(self.driver, self.PLATFORM, self.BASE_URL):
            print("[tw] No cookies found. Export them first.")
            return False
        self.driver.get(f"{self.BASE_URL}/home")
        time.sleep(5)
        cookie_names = {c["name"] for c in self.driver.get_cookies()}
        ok = all(n in cookie_names for n in self.SESSION_COOKIES)
        print(f"[tw] {'Logged in via cookies ✓' if ok else 'Cookie session expired.'}")
        return ok

    def feed(self, limit: int = 10) -> list[Tweet]:
        """Read the home timeline."""
        self.driver.get(f"{self.BASE_URL}/home")
        time.sleep(6)
        articles = self.driver.find_elements(
            By.CSS_SELECTOR, 'article[data-testid="tweet"]'
        )
        tweets = []
        for i, art in enumerate(articles[:limit]):
            text = art.text[:400]
            tweets.append(Tweet(index=i, text=text))
        return tweets

    def post(self, text: str) -> bool:
        """Post a tweet from the home timeline composer."""
        self.driver.get(f"{self.BASE_URL}/home")
        time.sleep(6)
        boxes = self.driver.find_elements(
            By.CSS_SELECTOR,
            '[data-testid="tweetTextarea_0"], '
            '[role="textbox"][contenteditable="true"]',
        )
        if not boxes:
            print("[tw] Composer textbox not found")
            return False

        box = boxes[0]
        box.click()
        time.sleep(0.5)
        self.paste_text(box, text)
        time.sleep(2)

        post_btn = self.driver.find_elements(
            By.CSS_SELECTOR,
            '[data-testid="tweetButton"], [data-testid="tweetButtonInline"]',
        )
        if post_btn:
            post_btn[0].click()
            time.sleep(4)
            self.save_cookies()
            print(f"[tw] Posted: {text[:80]}...")
            return True
        print("[tw] Post button not found")
        return False

    def reply(self, tweet_url: str, text: str) -> bool:
        """Reply to a specific tweet."""
        self.driver.get(tweet_url)
        time.sleep(5)
        boxes = self.driver.find_elements(
            By.CSS_SELECTOR, '[data-testid="tweetTextarea_0"]'
        )
        if not boxes:
            boxes = self.driver.find_elements(
                By.CSS_SELECTOR, '[role="textbox"][contenteditable="true"]'
            )
        if not boxes:
            print("[tw] Reply textbox not found")
            return False

        box = boxes[0]
        box.click()
        time.sleep(0.5)
        self.paste_text(box, text)
        time.sleep(2)

        btn = self.driver.find_elements(
            By.CSS_SELECTOR, '[data-testid="tweetButton"]'
        )
        if btn:
            btn[0].click()
            time.sleep(4)
            self.save_cookies()
            print(f"[tw] Replied: {text[:80]}...")
            return True
        print("[tw] Reply button not found")
        return False

    def notifications(self) -> str:
        """Check notifications page."""
        self.driver.get(f"{self.BASE_URL}/notifications")
        time.sleep(5)
        body = self.driver.find_element(By.TAG_NAME, "body").text[:2000]
        return body

    def profile(self, handle: str = "AVA1932509") -> str:
        """View a profile."""
        self.driver.get(f"{self.BASE_URL}/{handle}")
        time.sleep(5)
        body = self.driver.find_element(By.TAG_NAME, "body").text[:2000]
        return body
