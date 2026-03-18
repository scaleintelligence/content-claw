"""
Shared browser management for Content Claw.

Uses Driver.dev (Browser Cash) cloud browsers by default.
Falls back to local Playwright if Driver.dev is unavailable.

Usage:
    from browser import create_browser, create_browser_context

    with create_browser(cookie_path="creds/reddit-cookies.json") as page:
        page.goto("https://reddit.com")

Environment:
    DRIVER_API_KEY - Required for cloud browsers. Set in .env file.
    Falls back to local Playwright if not set or if cloud session fails.
"""

import json
import os
import sys
from contextlib import contextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

STEALTH_INIT = "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
DEFAULT_VIEWPORT = {"width": 1280, "height": 800}
LOCAL_BROWSER_ARGS = ["--disable-blink-features=AutomationControlled", "--no-sandbox"]

DRIVER_API_URL = "https://api.driver.dev/v1/browser/session"


def load_cookies(context, cookie_path: str | None):
    """Load cookies into a browser context if path exists."""
    if cookie_path and Path(cookie_path).exists():
        cookies = json.loads(Path(cookie_path).read_text())
        context.add_cookies(cookies)


def _create_driver_session() -> dict | None:
    """Create a cloud browser session via Driver.dev. Returns session info or None."""
    api_key = os.getenv("DRIVER_API_KEY")
    if not api_key:
        return None

    try:
        import httpx
        resp = httpx.post(
            DRIVER_API_URL,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"type": "hosted"},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return {
            "session_id": data.get("sessionId", ""),
            "cdp_url": data.get("cdpUrl", ""),
        }
    except Exception:
        return None


def _stop_driver_session(session_id: str):
    """Stop a Driver.dev cloud browser session."""
    api_key = os.getenv("DRIVER_API_KEY")
    if not api_key or not session_id:
        return
    try:
        import httpx
        httpx.delete(
            f"{DRIVER_API_URL}?sessionId={session_id}",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10,
        )
    except Exception:
        pass


@contextmanager
def _driver_browser(cookie_path: str | None = None):
    """Connect to a Driver.dev cloud browser via CDP."""
    from playwright.sync_api import sync_playwright

    session = _create_driver_session()
    if not session or not session["cdp_url"]:
        raise RuntimeError("Driver.dev session creation failed")

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(session["cdp_url"])
        try:
            context = browser.contexts[0] if browser.contexts else browser.new_context(
                user_agent=USER_AGENT,
                viewport=DEFAULT_VIEWPORT,
                locale="en-US",
            )
            load_cookies(context, cookie_path)
            page = context.pages[0] if context.pages else context.new_page()
            page.add_init_script(STEALTH_INIT)
            yield page
        finally:
            browser.close()
            _stop_driver_session(session["session_id"])


@contextmanager
def _driver_browser_context(cookie_path: str | None = None):
    """Connect to Driver.dev and yield (page, context, browser)."""
    from playwright.sync_api import sync_playwright

    session = _create_driver_session()
    if not session or not session["cdp_url"]:
        raise RuntimeError("Driver.dev session creation failed")

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(session["cdp_url"])
        try:
            context = browser.contexts[0] if browser.contexts else browser.new_context(
                user_agent=USER_AGENT,
                viewport=DEFAULT_VIEWPORT,
                locale="en-US",
            )
            load_cookies(context, cookie_path)
            page = context.pages[0] if context.pages else context.new_page()
            page.add_init_script(STEALTH_INIT)
            yield page, context, browser
        finally:
            browser.close()
            _stop_driver_session(session["session_id"])


@contextmanager
def _local_browser(cookie_path: str | None = None):
    """Launch a local Playwright browser."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=LOCAL_BROWSER_ARGS)
        context = browser.new_context(
            user_agent=USER_AGENT,
            viewport=DEFAULT_VIEWPORT,
            locale="en-US",
        )
        load_cookies(context, cookie_path)
        page = context.new_page()
        page.add_init_script(STEALTH_INIT)
        try:
            yield page
        finally:
            context.close()
            browser.close()


@contextmanager
def _local_browser_context(cookie_path: str | None = None):
    """Launch a local Playwright browser and yield (page, context, browser)."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=LOCAL_BROWSER_ARGS)
        context = browser.new_context(
            user_agent=USER_AGENT,
            viewport=DEFAULT_VIEWPORT,
            locale="en-US",
        )
        load_cookies(context, cookie_path)
        page = context.new_page()
        page.add_init_script(STEALTH_INIT)
        try:
            yield page, context, browser
        finally:
            context.close()
            browser.close()


@contextmanager
def create_browser(cookie_path: str | None = None):
    """Create a browser page. Tries Driver.dev first, falls back to local Playwright.

    Usage:
        with create_browser(cookie_path="creds/reddit-cookies.json") as page:
            page.goto("https://reddit.com")
    """
    try:
        with _driver_browser(cookie_path) as page:
            yield page
            return
    except Exception:
        pass

    with _local_browser(cookie_path) as page:
        yield page


@contextmanager
def create_browser_context(cookie_path: str | None = None):
    """Create a browser and yield (page, context, browser).
    Tries Driver.dev first, falls back to local Playwright.

    Usage:
        with create_browser_context(cookie_path) as (page, context, browser):
            page.goto("https://reddit.com")
    """
    try:
        with _driver_browser_context(cookie_path) as result:
            yield result
            return
    except Exception:
        pass

    with _local_browser_context(cookie_path) as result:
        yield result
