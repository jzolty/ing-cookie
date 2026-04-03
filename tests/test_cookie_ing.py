from pathlib import Path
from playwright.sync_api import Page, BrowserContext, TimeoutError as PlaywrightTimeoutError


RESULTS_DIR = Path("test-results")


def save_debug_artifacts(page: Page, name: str) -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    page.screenshot(path=str(RESULTS_DIR / f"{name}.png"), full_page=True)
    (RESULTS_DIR / f"{name}.html").write_text(page.content(), encoding="utf-8")

    button_texts = page.locator("button").all_text_contents()
    (RESULTS_DIR / f"{name}-buttons.txt").write_text(
        "\n".join(button_texts),
        encoding="utf-8"
    )


def open_cookie_settings(page: Page) -> None:
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)

    save_debug_artifacts(page, "before-opening-cookie-settings")

    # Variant 1: cookie banner button
    banner_button = page.locator("button.js-cookie-policy-settings-button")
    if banner_button.count() > 0:
        banner_button.first.click()
        return

    # Variant 2: footer cookie settings button
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(1000)

    footer_button = page.locator("button.js-cookie-policy-deputed-settings-button")
    if footer_button.count() > 0:
        footer_button.first.click()
        return

    save_debug_artifacts(page, "cookie-settings-not-found")

    raise AssertionError(
        "Could not open cookie settings: neither banner button nor footer button was found."
    )


def test_accept_analytics_cookies(page: Page, context: BrowserContext):
    RESULTS_DIR.mkdir(exist_ok=True)
    context.tracing.start(screenshots=True, snapshots=True, sources=True)

    try:
        page.goto("https://www.ing.pl")
        open_cookie_settings(page)

        save_debug_artifacts(page, "cookie-settings-opened")

        switches = page.get_by_role("switch")
        if switches.count() <= 1:
            save_debug_artifacts(page, "analytics-switch-not-found")
            raise AssertionError("Analytics switch was not found.")

        switches.nth(1).click()

        accept_button = page.get_by_role("button", name="Zaakceptuj zaznaczone")
        if accept_button.count() == 0:
            save_debug_artifacts(page, "accept-button-not-found")
            raise AssertionError("Accept selected button was not found.")

        accept_button.click()

        save_debug_artifacts(page, "after-accepting-cookies")

        cookies_after = context.cookies()

        consent_cookie = next(
            (c for c in cookies_after if c["name"] == "cookiePolicyGDPR"),
            None
        )
        details_cookie = next(
            (c for c in cookies_after if c["name"] == "cookiePolicyGDPR__details"),
            None
        )

        assert consent_cookie is not None, "cookiePolicyGDPR cookie was not found"
        assert details_cookie is not None, "cookiePolicyGDPR__details cookie was not found"
        assert consent_cookie["value"] == "3", "cookiePolicyGDPR has unexpected value"
        assert details_cookie["value"] != "", "cookiePolicyGDPR__details should not be empty"

    finally:
        context.tracing.stop(path=str(RESULTS_DIR / "trace.zip"))