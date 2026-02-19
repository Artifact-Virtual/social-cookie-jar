"""Discord driver — post messages, read channels via discord.com."""

import time
from dataclasses import dataclass
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from . import BaseDriver


@dataclass
class DiscordMessage:
    """A Discord message."""
    index: int
    text: str
    author: str = ""


class DiscordDriver(BaseDriver):
    """Discord automation via discord.com with cookie-based auth.
    
    NOTE: Discord is aggressive about bot detection. Use sparingly.
    For bots, prefer the Discord API (discord.js / discord.py) over browser automation.
    This driver is for personal account interaction only.
    """

    PLATFORM = "discord"
    BASE_URL = "https://discord.com"
    SESSION_COOKIES = ["__dcfduid", "__sdcfduid"]

    def login(self) -> bool:
        if not self.jar.inject(self.driver, self.PLATFORM, self.BASE_URL):
            print("[discord] No cookies found. Export them first.")
            return False
        self.driver.get(f"{self.BASE_URL}/channels/@me")
        time.sleep(6)
        # Check if redirected to login
        if "/login" in self.driver.current_url:
            print("[discord] Cookie session expired.")
            return False
        print("[discord] Logged in via cookies ✓")
        return True

    def read_channel(self, guild_id: str, channel_id: str, limit: int = 20) -> list[DiscordMessage]:
        """Read messages from a channel."""
        self.driver.get(f"{self.BASE_URL}/channels/{guild_id}/{channel_id}")
        time.sleep(5)

        msg_els = self.driver.find_elements(
            By.CSS_SELECTOR, '[id^="chat-messages-"]'
        )
        messages = []
        for i, el in enumerate(msg_els[-limit:]):
            text = el.text[:400]
            messages.append(DiscordMessage(index=i, text=text))
        return messages

    def send_message(self, guild_id: str, channel_id: str, text: str) -> bool:
        """Send a message to a channel."""
        self.driver.get(f"{self.BASE_URL}/channels/{guild_id}/{channel_id}")
        time.sleep(5)

        boxes = self.driver.find_elements(
            By.CSS_SELECTOR, '[role="textbox"][contenteditable="true"]'
        )
        if not boxes:
            print("[discord] Message box not found")
            return False

        box = boxes[0]
        box.click()
        time.sleep(0.3)
        self.paste_text(box, text)
        time.sleep(1)
        box.send_keys(Keys.RETURN)
        time.sleep(2)
        self.save_cookies()
        print(f"[discord] Sent: {text[:80]}...")
        return True
