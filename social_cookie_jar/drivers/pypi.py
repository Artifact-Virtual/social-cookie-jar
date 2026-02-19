"""PyPI driver — check package stats via pypi.org."""

import time
from dataclasses import dataclass
from selenium.webdriver.common.by import By

from . import BaseDriver


@dataclass
class PyPIPackage:
    """A PyPI package."""
    name: str
    version: str = ""
    description: str = ""
    url: str = ""


class PyPIDriver(BaseDriver):
    """PyPI browser driver. Mostly useful for checking stats and managing releases.
    
    NOTE: For publishing packages, use `twine` or `flit` CLI — not browser automation.
    This driver is for reading/checking only.
    """

    PLATFORM = "pypi"
    BASE_URL = "https://pypi.org"
    SESSION_COOKIES = ["session_id"]

    def login(self) -> bool:
        if not self.jar.inject(self.driver, self.PLATFORM, self.BASE_URL):
            print("[pypi] No cookies found. Export them first.")
            return False
        self.driver.get(f"{self.BASE_URL}/manage/projects/")
        time.sleep(5)
        if "/account/login" in self.driver.current_url:
            print("[pypi] Not logged in.")
            return False
        print("[pypi] Logged in via cookies ✓")
        return True

    def check_package(self, name: str) -> PyPIPackage | None:
        """Check a package's info."""
        self.driver.get(f"{self.BASE_URL}/project/{name}/")
        time.sleep(4)
        title = self.driver.title
        body = self.driver.find_element(By.TAG_NAME, "body").text[:1000]
        if "page not found" in body.lower():
            return None
        version_els = self.driver.find_elements(By.CSS_SELECTOR, ".release__version")
        version = version_els[0].text.strip() if version_els else ""
        return PyPIPackage(
            name=name,
            version=version,
            description=body[:200],
            url=f"{self.BASE_URL}/project/{name}/",
        )
