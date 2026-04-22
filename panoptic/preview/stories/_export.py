#!/usr/bin/env python3
"""Export story-1.html + story-2.html → PNG 1080x1920 pour IG story.

Usage :
    python _export.py

Requires playwright + chromium installed :
    pip install playwright && playwright install chromium

Sortie : panoptic/public/stories/story-{1,2}.png
"""

from __future__ import annotations

import http.server
import socketserver
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
SITE_ROOT = HERE.parent.parent  # panoptic/
OUT = SITE_ROOT / "public" / "stories"
OUT.mkdir(parents=True, exist_ok=True)

PORT = 8791


def start_server():
    handler = lambda *a, **k: http.server.SimpleHTTPRequestHandler(
        *a, directory=str(SITE_ROOT.parent), **k  # tawiza-website root
    )
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), handler)
    th = threading.Thread(target=httpd.serve_forever, daemon=True)
    th.start()
    return httpd


def main() -> None:
    srv = start_server()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            ctx = browser.new_context(
                viewport={"width": 1080, "height": 1920},
                device_scale_factor=2,  # retina
            )
            page = ctx.new_page()

            for num in (1, 2):
                url = f"http://127.0.0.1:{PORT}/panoptic/preview/stories/story-{num}.html"
                page.goto(url, wait_until="networkidle")
                png = OUT / f"story-{num}.png"
                page.screenshot(path=str(png), omit_background=False)
                print(f"✓ {png} ({png.stat().st_size // 1024} KB)")

            browser.close()
    finally:
        srv.shutdown()


if __name__ == "__main__":
    main()
