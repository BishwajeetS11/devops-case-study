"""Render kubectl command transcripts as terminal-style PNG screenshots."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT / "screenshots"


def render(text: str, filename: str, title: str) -> None:
    font = ImageFont.load_default()
    lines = text.splitlines() or [""]
    width = min(1400, max(900, max(len(line) for line in lines) * 8 + 80))
    height = 70 + len(lines) * 16 + 40
    img = Image.new("RGB", (width, height), "#0b1220")
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, width, 40), fill="#111827")
    draw.text((20, 12), title, fill="#22d3ee", font=font)
    y = 56
    for line in lines:
        draw.text((20, y), line[:180], fill="#e2e8f0", font=font)
        y += 16
    out = SHOTS / filename
    img.save(out)
    print(f"Wrote {out}")


def main():
    render(
        (SHOTS / "k8s_rollout_status.txt").read_text(encoding="utf-8", errors="replace"),
        "k8s_rollout_status.png",
        "kubectl rolling update",
    )
    render(
        (SHOTS / "k8s_rollback.txt").read_text(encoding="utf-8", errors="replace"),
        "k8s_rollback.png",
        "kubectl rollout undo",
    )


if __name__ == "__main__":
    main()
