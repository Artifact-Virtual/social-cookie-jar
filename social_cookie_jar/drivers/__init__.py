"""Base driver with shared Selenium utilities."""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

from ..cookie_jar import CookieJar


class BaseDriver:
    """Base class for platform-specific drivers."""

    PLATFORM = "base"
    BASE_URL = ""
    SESSION_COOKIES: list[str] = []

    def __init__(
        self,
        cookie_dir: str = "./cookies",
        headless: bool = True,
        user_agent: str = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.6099.109 Safari/537.36"
        ),
        window_size: tuple[int, int] = (1280, 800),
        page_load_timeout: int = 25,
    ):
        self.jar = CookieJar(cookie_dir)
        self.headless = headless
        self.user_agent = user_agent
        self.window_size = window_size
        self.page_load_timeout = page_load_timeout
        self._driver = None

    @property
    def driver(self):
        if self._driver is None:
            self._driver = self._create_driver()
        return self._driver

    def _create_driver(self):
        opts = Options()
        if self.headless:
            opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--disable-extensions")
        opts.add_argument("--disable-notifications")
        opts.add_argument(f"--window-size={self.window_size[0]},{self.window_size[1]}")
        opts.add_argument(f"--user-agent={self.user_agent}")
        d = webdriver.Chrome(options=opts)
        d.set_page_load_timeout(self.page_load_timeout)
        return d

    def login(self) -> bool:
        """Login using saved cookies. Returns True if session is valid."""
        if not self.jar.inject(self.driver, self.PLATFORM, self.BASE_URL):
            return False
        self.driver.refresh()
        time.sleep(3)
        cookie_names = {c["name"] for c in self.driver.get_cookies()}
        return all(name in cookie_names for name in self.SESSION_COOKIES)

    def save_cookies(self):
        """Save current browser cookies to jar."""
        self.jar.save(self.driver.get_cookies(), self.PLATFORM)

    def paste_text(self, element, text: str):
        """Paste text into an element via ClipboardEvent. Instant, no typing."""
        self.driver.execute_script(
            """
            const el = arguments[0];
            el.focus();
            const dt = new DataTransfer();
            dt.setData("text/plain", arguments[1]);
            const evt = new ClipboardEvent("paste", {
                clipboardData: dt, bubbles: true, cancelable: true
            });
            el.dispatchEvent(evt);
            """,
            element,
            text,
        )

    def quit(self):
        """Close the browser."""
        if self._driver:
            self._driver.quit()
            self._driver = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.quit()
