"""Browser check of the home-page map. Run against a running server:
    python tests/e2e_map.py http://127.0.0.1:8000
Uses the pre-installed Chromium if /opt/pw-browsers/chromium exists."""
import os
import sys

from playwright.sync_api import sync_playwright

base = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
exe = "/opt/pw-browsers/chromium" if os.path.exists("/opt/pw-browsers/chromium") else None
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe, args=["--no-sandbox"])
    page = b.new_page(viewport={"width": 1366, "height": 800})
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(base + "/")
    active = page.locator("a.prov.is-active")
    n = active.count()
    assert n == 9, f"expected 9 coloured provinces, got {n}"
    assert page.locator("g.prov").count() == 22, "grey provinces should not be links"
    page.locator("a.prov[data-slug='west-azarbaijan']").dispatch_event("click")  # bbox centres overlap for concave provinces
    page.wait_for_selector("[data-p-list] li")
    assert page.locator("[data-p-name]").inner_text() == "آذربایجان غربی"
    assert page.locator("[data-p-list] li").count() == 28
    page.click("[data-p-list] li a >> nth=0")
    page.wait_for_url("**/projects/*/")
    assert page.locator("h1").inner_text().strip()
    page.goto(base + "/")
    page.locator("a.prov[data-slug='fars']").dispatch_event("click")
    page.keyboard.press("Escape")
    assert page.locator("[data-panel]").is_hidden()
    assert not errors, errors
    b.close()
print("e2e map OK")
