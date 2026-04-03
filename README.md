# ING Analytical Cookie Consent Test

This project contains an automated test written in Python using Playwright and pytest.

## Test scope

The automated test verifies the following scenario on `https://www.ing.pl`:

1. Open the ING website
2. Open cookie settings using the `Dostosuj` button
3. Enable `Cookies analityczne`
4. Confirm the selection with `Zaakceptuj zaznaczone`
5. Verify that the expected consent cookies were saved in the browser

## What is verified

The test validates that after accepting analytics cookies, the following cookies are stored in the browser:

- `cookiePolicyGDPR`
- `cookiePolicyGDPR__details`

Additionally, the test verifies that:
- these cookies were not present before consent
- `cookiePolicyGDPR` has the expected value of `3`

## Repeatability

The test is repeatable because it runs in a fresh Playwright browser context each time.  
As a result, every run starts from a clean state, similar to a first visit in incognito mode.

## Technology stack

- Python
- pytest
- Playwright

## Installation

Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```
Install dependencies:

```bash
pip install -r requirements.txt
playwright install
```

## Run test locally

```bash
pytest tests/test_cookie_ing_local.py
```

## Run test in multiple browsers

```bash
pytest tests/test_cookie_ing_local.py --browser chromium --browser firefox --browser webkit
```
## CI pipeline - limitation
The GitHub Actions pipeline is included to demonstrate automated execution in multiple browsers.

During execution on public GitHub runners, the ING website display an anti-bot/security verification page instead of the main page. In that case, the live  test against the production website cannot continue automatically.
The test itself works correctly in a local environment, where the normal cookie consent flow is available.