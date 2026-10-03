"""Capture Grafana dashboard and Prometheus targets screenshots."""

from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT / "screenshots"
SHOTS.mkdir(exist_ok=True)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1600, "height": 1000})

        page.goto("http://localhost:3000/login", wait_until="networkidle")
        page.fill('input[name="user"]', "admin")
        page.fill('input[name="password"]', "devops123")
        page.click('button[type="submit"]')
        page.wait_for_url("**/", timeout=20000)

        page.goto(
            "http://localhost:3000/d/devops-case-study-main/devops-case-study-app-dashboard?orgId=1&refresh=5s",
            wait_until="networkidle",
        )
        page.wait_for_timeout(8000)
        page.screenshot(path=str(SHOTS / "grafana_dashboard.png"), full_page=True)

        page.goto("http://localhost:9090/targets", wait_until="networkidle")
        page.wait_for_timeout(2000)
        page.screenshot(path=str(SHOTS / "prometheus_targets.png"), full_page=True)

        browser.close()
        print("Saved grafana_dashboard.png and prometheus_targets.png")


if __name__ == "__main__":
    main()
