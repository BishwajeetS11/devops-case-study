"""Recapture assignment screenshots from live services and local artefacts."""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT / "screenshots"


def fetch_json(url: str):
    with urllib.request.urlopen(url, timeout=10) as resp:
        return json.loads(resp.read().decode())


def fetch_text(url: str) -> str:
    with urllib.request.urlopen(url, timeout=10) as resp:
        return resp.read().decode()


def font(size: int, bold: bool = False):
    names = [
        r"C:\Windows\Fonts\consola.ttf",
        r"C:\Windows\Fonts\CascadiaMono.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ]
    if bold:
        names = [r"C:\Windows\Fonts\consolab.ttf", r"C:\Windows\Fonts\arialbd.ttf"] + names
    for path in names:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def render_terminal(title: str, body: str, outfile: str, width: int = 1400) -> None:
    body_font = font(16)
    title_font = font(18, bold=True)
    lines = []
    for raw in body.splitlines():
        line = raw.rstrip()
        while len(line) > 150:
            lines.append(line[:150])
            line = line[150:]
        lines.append(line)
    if not lines:
        lines = [""]
    height = 72 + len(lines) * 22 + 28
    img = Image.new("RGB", (width, height), "#0b1220")
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, width, 48), fill="#111827")
    draw.ellipse((18, 16, 34, 32), fill="#ef4444")
    draw.ellipse((42, 16, 58, 32), fill="#f59e0b")
    draw.ellipse((66, 16, 82, 32), fill="#22c55e")
    draw.text((108, 14), title, fill="#67e8f9", font=title_font)
    y = 64
    for line in lines:
        draw.text((24, y), line, fill="#e2e8f0", font=body_font)
        y += 22
    img.save(SHOTS / outfile)
    print("wrote", outfile)


def render_json_card(title: str, payload, outfile: str) -> None:
    text = json.dumps(payload, indent=2)
    render_terminal(title, text, outfile, width=1100)


def main() -> None:
    SHOTS.mkdir(exist_ok=True)

    home = fetch_json("http://localhost:5000/")
    health = fetch_json("http://localhost:5000/health")
    data = fetch_json("http://localhost:5000/api/data")
    metrics = fetch_text("http://localhost:5000/metrics")
    interesting = [
        line
        for line in metrics.splitlines()
        if line.startswith("# HELP http_")
        or line.startswith("# TYPE http_")
        or line.startswith("http_")
        or line.startswith("app_info")
        or line.startswith("process_start_time")
    ]
    render_json_card("GET http://localhost:5000/  — Flask service", home, "app_home.png")
    render_json_card("GET http://localhost:5000/health", health, "app_health.png")
    render_json_card("GET http://localhost:5000/api/data", data, "app_api_data.png")
    render_terminal(
        "GET http://localhost:5000/metrics  (Prometheus exposition)",
        "\n".join(interesting),
        "app_metrics.png",
        width=1300,
    )

    render_terminal(
        "kubectl — rolling update v1.0.0 → v2.0.0",
        (SHOTS / "k8s_rollout_status.txt").read_text(encoding="utf-8", errors="replace"),
        "k8s_rollout_status.png",
        width=1500,
    )
    render_terminal(
        "kubectl — rollout undo (rollback to v1.0.0)",
        (SHOTS / "k8s_rollback.txt").read_text(encoding="utf-8", errors="replace"),
        "k8s_rollback.png",
        width=1500,
    )

    html = (SHOTS / "pipeline.html").resolve().as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="msedge")
        page = browser.new_page(viewport={"width": 1600, "height": 900})
        page.goto(html, wait_until="networkidle")
        page.wait_for_timeout(500)
        page.screenshot(path=str(SHOTS / "pipeline_diagram.png"), full_page=False)

        page.set_viewport_size({"width": 1600, "height": 1000})
        page.goto("http://localhost:3000/login", wait_until="networkidle")
        page.fill('input[name="user"]', "admin")
        page.fill('input[name="password"]', "devops123")
        page.click('button[type="submit"]')
        page.wait_for_timeout(2500)
        page.goto(
            "http://localhost:3000/d/devops-case-study-main?"
            "orgId=1&refresh=5s&kiosk",
            wait_until="networkidle",
        )
        page.wait_for_timeout(8000)
        page.screenshot(path=str(SHOTS / "grafana_dashboard.png"), full_page=True)

        page.goto("http://localhost:9090/targets", wait_until="networkidle")
        page.wait_for_timeout(1500)
        page.screenshot(path=str(SHOTS / "prometheus_targets.png"), full_page=True)
        browser.close()

    old_jpg = SHOTS / "pipeline_diagram.jpg"
    if old_jpg.exists():
        old_jpg.unlink()
        print("removed pipeline_diagram.jpg")
    print("screenshots refreshed")


if __name__ == "__main__":
    main()
