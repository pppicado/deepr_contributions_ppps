from playwright.sync_api import Page, expect, sync_playwright
import time
import pytest
import os

# To run this test:
# 1. Ensure backend is running: uvicorn deepr.backend.main:app --port 8000
# 2. Ensure frontend is running: npm run dev -- --port 3000
# 3. pytest tests/test_frontend.py

@pytest.mark.skip(reason="Requires running frontend and backend servers")
def test_ensemble_ui_flow():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. Login
        page.goto("http://localhost:3000")
        page.get_by_placeholder("test@example.com").fill("test@example.com")
        page.get_by_role("button", name="Login / Create Account").click()

        # Wait for navigation
        page.wait_for_url("http://localhost:3000/", timeout=5000)

        # 2. Setup API Key if needed
        # Check if we need to setup settings (simplification: assume we do or force it)
        page.goto("http://localhost:3000/settings")

        # Check if login redirected us back to login (session issue)
        if "/login" in page.url:
             pytest.fail("Login failed or session lost")

        # Set Key
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            pytest.fail("OPENROUTER_API_KEY environment variable not set")
        page.get_by_label("API Key").fill(api_key)
        page.get_by_role("button", name="Save Configuration").click()

        expect(page.get_by_text("API Key saved successfully!")).to_be_visible(timeout=5000)

        # 3. Go to Council
        page.goto("http://localhost:3000/")

        # 4. Select Ensemble
        page.get_by_label("Ensemble").check()
        expect(page.get_by_label("Ensemble")).to_be_checked()

        # 5. Run Prompt
        page.get_by_placeholder("Enter your research question or topic...").fill("Testing Ensemble Flow")
        page.get_by_text("Start Research").click()

        # 6. Verify Execution
        expect(page.get_by_text("Initializing...")).to_be_visible()
        expect(page.get_by_text("All models are researching in parallel...", exact=False)).to_be_visible(timeout=30000)

def test_superchat_ui_flow():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. Login
        page.goto("http://localhost:3000")
        page.get_by_placeholder("test@example.com").fill("test_sc@example.com")
        page.get_by_role("button", name="Login / Create Account").click()

        # Wait for navigation
        page.wait_for_url("http://localhost:3000/", timeout=10000)

        # 2. Setup API Key if needed
        page.goto("http://localhost:3000/settings")

        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPEN_ROUTER_KEY")
        if not api_key:
            pytest.skip("OPENROUTER_API_KEY environment variable not set")

        # Always set key to be sure
        page.get_by_label("API Key").fill(api_key)
        page.get_by_role("button", name="Save Configuration").click()
        expect(page.get_by_text("API Key saved successfully!")).to_be_visible(timeout=5000)

        # 3. Go to SuperChat
        page.click("a[href='/super-chat']")
        page.wait_for_url("http://localhost:3000/super-chat")
        page.reload() # Ensure clean state

        # 4. Start Session
        page.fill("textarea", "Tell me a short joke")
        # Ensure button enabled
        expect(page.get_by_role("button", name="Start Session")).to_be_enabled()
        page.get_by_role("button", name="Start Session").click()

        # 5. Verify Streaming
        expect(page.get_by_text("SuperChat Session")).to_be_visible()
        expect(page.get_by_text("You")).to_be_visible()
        expect(page.get_by_text("Tell me a short joke")).to_be_visible()

        # Wait for completion (input placeholder changes back)
        expect(page.get_by_placeholder("Type a message to continue...")).to_be_visible(timeout=40000)

        # 6. Follow up
        page.fill("textarea", "Explain it.")
        # Click the send button (icon)
        # It's inside the input area.
        # Locator by role button? There might be others.
        # The button has Send icon.
        # We can select by order or class.
        # Or `page.get_by_role("button").last`?
        # The sidebar buttons are links (nav).
        # Settings has button? No we are on SuperChat page.
        # Only button is Send button.
        page.locator("div.fixed button").click()

        expect(page.get_by_text("Explain it.")).to_be_visible()
        expect(page.get_by_placeholder("Type a message to continue...")).to_be_visible(timeout=40000)

        # 7. Check History
        page.click("a[href='/history']")
        # Should see "Tell me a short joke"
        expect(page.get_by_text("Tell me a short joke", exact=False)).to_be_visible()
        # Should see "SuperChat" badge
        expect(page.get_by_text("SuperChat")).to_be_visible()
