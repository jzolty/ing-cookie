from playwright.sync_api import Page, TimeoutError


def open_cookie_settings(page: Page) -> None:
    try:
        page.get_by_role("button", name="Dostosuj").click(timeout=5000)
    except TimeoutError:
        cookie_settings_link = page.get_by_role("link", name="Ustawienia cookie")
        cookie_settings_link.scroll_into_view_if_needed()
        cookie_settings_link.click()


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