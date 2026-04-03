from playwright.sync_api import Page, TimeoutError


from pathlib import Path
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError


def open_cookie_settings(page: Page) -> None:
    page.wait_for_load_state("domcontentloaded")

    try:
        page.get_by_role("button", name="Dostosuj").click(timeout=10000)
        return
    except PlaywrightTimeoutError:
        pass

    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    try:
        cookie_settings_button = page.get_by_role("button", name="Ustawienia cookie")
        cookie_settings_button.scroll_into_view_if_needed()
        cookie_settings_button.click(timeout=10000)
        return
    except PlaywrightTimeoutError:
        pass

    Path("test-results").mkdir(exist_ok=True)
    page.screenshot(path="test-results/cookie-settings-not-found.png", full_page=True)

    raise AssertionError(
        "Could not open cookie settings: neither 'Dostosuj' button nor "
        "'Ustawienia cookie' button was found."
    )

def test_accept_analytics_cookies(page: Page, context):
    page.goto("https://www.ing.pl")

    cookies_before = context.cookies()
    names_before = [c["name"] for c in cookies_before]

    open_cookie_settings(page)

    page.get_by_role("switch").nth(1).click()
    page.get_by_role("button", name="Zaakceptuj zaznaczone").click()

    cookies_after = context.cookies()
    names_after = [c["name"] for c in cookies_after]

    consent_cookie = next(
        (c for c in cookies_after if c["name"] == "cookiePolicyGDPR"),
        None
    )
    details_cookie = next(
        (c for c in cookies_after if c["name"] == "cookiePolicyGDPR__details"),
        None
    )

    assert "cookiePolicyGDPR" not in names_before, \
        "cookiePolicyGDPR should not be present before consent"
    assert "cookiePolicyGDPR__details" not in names_before, \
        "cookiePolicyGDPR__details should not be present before consent"

    assert "cookiePolicyGDPR" in names_after, \
        "cookiePolicyGDPR was not saved after consent"
    assert "cookiePolicyGDPR__details" in names_after, \
        "cookiePolicyGDPR__details was not saved after consent"

    assert consent_cookie is not None, \
        "cookiePolicyGDPR cookie was not found"
    assert details_cookie is not None, \
        "cookiePolicyGDPR__details cookie was not found"

    assert consent_cookie["value"] == "3", \
        "cookiePolicyGDPR has unexpected value"
    assert details_cookie["value"] != "", \
        "cookiePolicyGDPR__details should not be empty"