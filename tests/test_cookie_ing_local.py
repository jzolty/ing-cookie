from playwright.sync_api import Page


def test_accept_analytics_cookies(page: Page, context):
    page.goto("https://www.ing.pl")

    page.get_by_role("button", name="Dostosuj").click()
    page.get_by_role("switch").nth(1).click()
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

    assert consent_cookie is not None, "cookiePolicyGDPR cookie was not found"
    assert details_cookie is not None, "cookiePolicyGDPR__details cookie was not found"
    assert consent_cookie["value"] == "3", "cookiePolicyGDPR has unexpected value"
    assert details_cookie["value"] != "", "cookiePolicyGDPR__details should not be empty"