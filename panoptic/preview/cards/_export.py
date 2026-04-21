#!/usr/bin/env python3
"""
Export all card-m-X.html to PNG at 1080x1350 retina 2x.
Serves via local HTTP so the shared eye.js fetch works.
"""

from __future__ import annotations

import http.server
import socketserver
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
OUT = (HERE.parent / "exports").resolve()
OUT.mkdir(parents=True, exist_ok=True)
SITE_ROOT = HERE.parent.parent.parent  # tawiza-website root
PORT = 8776


def start_server():
    handler = lambda *a, **k: http.server.SimpleHTTPRequestHandler(
        *a, directory=str(SITE_ROOT), **k
    )
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), handler)
    th = threading.Thread(target=httpd.serve_forever, daemon=True)
    th.start()
    return httpd


def main():
    cards = sorted(HERE.glob("card-m-*.html"))
    print(f"Exporting {len(cards)} cards")
    httpd = start_server()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1080, "height": 1350},
            device_scale_factor=2,
        )
        page = context.new_page()

        for card in cards:
            rel = card.relative_to(SITE_ROOT)
            url = f"http://127.0.0.1:{PORT}/{rel}"
            page.goto(url)
            page.wait_for_load_state("networkidle")
            # Wait for eye injection
            page.wait_for_function(
                "document.querySelectorAll('.eye-watcher svg').length > 0",
                timeout=5000,
            )
            page.wait_for_timeout(200)
            out = OUT / f"panoptic-methodo-{card.stem.split('-')[-1]}.png"
            page.screenshot(path=str(out), full_page=False,
                            clip={"x": 0, "y": 0, "width": 1080, "height": 1350})
            print(f"  {out.name} ({out.stat().st_size // 1024} kB)")

        browser.close()

    print(f"\nDone -> {OUT}")


if __name__ == "__main__":
    main()
