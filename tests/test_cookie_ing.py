from playwright.sync_api import Page


def open_cookie_settings(page: Page) -> None:
    page.wait_for_load_state("domcontentloaded")

    
    if page.locator("button:has-text('Dostosuj')").count() > 0:
        page.locator("button:has-text('Dostosuj')").click()
        return

    
    if page.locator("button.js-cookie-policy-deputed-settings-button").count() > 0:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.locator("button.js-cookie-policy-deputed-settings-button").click()
        return

    # print("No cookie banner or cookie settings button found - continuing test")


def test_accept_analytics_cookies(page: Page, context):
    page.goto("https://www.ing.pl")

    open_cookie_settings(page)

    if page.get_by_role("switch").count() > 1:
        page.get_by_role("switch").nth(1).click()

    if page.get_by_role("button", name="Zaakceptuj zaznaczone").count() > 0:
        page.get_by_role("button", name="Zaakceptuj zaznaczone").click()

    cookies_after = context.cookies()

    consent_cookie = next(
        (c for c in cookies_after if c["name"] == "cookiePolicyGDPR"),
        None
    )
    details_cookie = next(
        (c for c in cookies_after if c["name"] == "cookiePolicyGDPR__details"),
        None
    )

    assert consent_cookie is not None, \
        "cookiePolicyGDPR cookie was not found"
    assert details_cookie is not None, \
        "cookiePolicyGDPR__details cookie was not found"

    assert consent_cookie["value"] == "3", \
        "cookiePolicyGDPR has unexpected value"
    assert details_cookie["value"] != "", \
        "cookiePolicyGDPR__details should not be empty"