"""Social Cookie Jar — Headless social media toolkit for AI agents."""

__version__ = "0.2.0"

from .cookie_jar import CookieJar
from .export import export_from_cdp, export_from_json

from .drivers.facebook import FacebookDriver
from .drivers.twitter import TwitterDriver
from .drivers.linkedin import LinkedInDriver
from .drivers.reddit import RedditDriver
from .drivers.discord import DiscordDriver
from .drivers.instagram import InstagramDriver
from .drivers.hackernews import HackerNewsDriver
from .drivers.substack import SubstackDriver
from .drivers.pypi import PyPIDriver

__all__ = [
    "CookieJar",
    "export_from_cdp",
    "export_from_json",
    # Platform drivers
    "FacebookDriver",
    "TwitterDriver",
    "LinkedInDriver",
    "RedditDriver",
    "DiscordDriver",
    "InstagramDriver",
    "HackerNewsDriver",
    "SubstackDriver",
    "PyPIDriver",
]
