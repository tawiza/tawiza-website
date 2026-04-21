#!/usr/bin/env python3
"""
Record the panoptic methodology HTML reel via Playwright.

Output: ../../preview/exports/panoptic-methodo-reel.mp4
"""

from __future__ import annotations

import http.server
import socketserver
import subprocess
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
HTML_PATH = HERE / "index.html"
OUT_DIR = (HERE.parent.parent / "preview" / "exports").resolve()
OUT_DIR.mkdir(parents=True, exist_ok=True)

FRAMES_DIR = OUT_DIR / "frames"
FRAMES_DIR.mkdir(exist_ok=True)

WIDTH, HEIGHT = 1080, 1920
FPS = 30
DURATION = 40  # secondes
TOTAL_FRAMES = DURATION * FPS
SERVE_PORT = 8899


def start_server():
    """Start a local HTTP server from the website root."""
    site_root = HERE.parent.parent.parent  # tawiza-website root
    handler = lambda *a, **k: http.server.SimpleHTTPRequestHandler(
        *a, directory=str(site_root), **k
    )
    httpd = socketserver.TCPServer(("127.0.0.1", SERVE_PORT), handler)
    th = threading.Thread(target=httpd.serve_forever, daemon=True)
    th.start()
    return httpd


def main():
    for old in FRAMES_DIR.glob("*.png"):
        old.unlink()

    httpd = start_server()
    page_url = f"http://127.0.0.1:{SERVE_PORT}/panoptic/reels/methodo/index.html"
    print(f"Serving at {page_url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--font-render-hinting=none",
                "--disable-font-subpixel-positioning",
            ],
        )
        context = browser.new_context(
            viewport={"width": WIDTH, "height": HEIGHT},
            device_scale_factor=1,
        )
        page = context.new_page()
        page.goto(page_url)
        # Wait for fonts + France data to load
        page.wait_for_load_state("networkidle")
        # Wait for France paths and dots to be injected
        page.wait_for_function(
            "document.querySelectorAll('svg[data-france] circle').length > 500",
            timeout=10000,
        )
        page.wait_for_timeout(300)

        # Inject a control to pause CSS animations and set current time
        # We'll use CDP (Chrome DevTools Protocol) to freeze time
        client = page.context.new_cdp_session(page)
        client.send("Animation.enable")

        # Snapshot approach : pause animations, then scrub using animation.currentTime
        # For each frame i: set animation.currentTime = i / FPS seconds, screenshot

        # Simpler : let animations play, capture at known timestamps via screenshot with
        # playback rate control
        client.send("Animation.setPlaybackRate", {"playbackRate": 0})

        print(f"Capturing {TOTAL_FRAMES} frames @ {FPS} fps")
        for i in range(TOTAL_FRAMES):
            t_ms = i * (1000 / FPS)
            # Seek all animations to t_ms
            page.evaluate(
                """(t) => {
                document.getAnimations().forEach(a => {
                    a.currentTime = t;
                });
            }""",
                t_ms,
            )
            path = FRAMES_DIR / f"f{i:04d}.png"
            page.screenshot(path=str(path), omit_background=False)
            if i % 30 == 0:
                print(f"  frame {i}/{TOTAL_FRAMES} (t={t_ms/1000:.2f}s)")

        browser.close()

    print("\nEncoding MP4 via ffmpeg...")
    import imageio_ffmpeg

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    out_mp4 = OUT_DIR / "panoptic-methodo-reel.mp4"
    subprocess.run(
        [
            ffmpeg, "-y", "-framerate", str(FPS),
            "-i", str(FRAMES_DIR / "f%04d.png"),
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "18", "-preset", "slow",
            "-movflags", "+faststart",
            str(out_mp4),
        ],
        check=True,
    )
    size_mb = out_mp4.stat().st_size / (1024 * 1024)
    print(f"\nDone: {out_mp4} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()
