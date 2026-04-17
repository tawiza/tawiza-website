"""Injects Tawiza fonts, analytics, and return bar into marimo WASM exports.

Run by .github/workflows/notebooks.yml after marimo export, or locally before
commit. Idempotent: skips already-branded files.
"""

from __future__ import annotations

import re
from pathlib import Path

INJECTION = """<!-- tawiza-branding -->
    <!-- R16 doctrine : fonts self-hosted (pas de tracking Google Fonts). -->
    <link rel="stylesheet" href="/assets/fonts/tawiza-fonts.css">
    <link rel="icon" type="image/x-icon" href="/favicon.ico">
    <!-- R16 doctrine : pas d'extraction via tracking. Pas de flag pageview-props ici
         pour ne pas logger les query strings des URLs de partage de simulateur. -->
    <script defer data-domain="tawiza.fr" data-api="https://t.tawiza.fr/api/event" src="https://t.tawiza.fr/js/script.outbound-links.js"></script>
    <style>
        body { font-family: "Inter", system-ui, sans-serif !important; }
        h1, h2, h3, h4 { font-family: "El Messiri", serif !important; }
        .tawiza-bar {
            position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
            background: #fafaf9; border-bottom: 1px solid rgba(29,53,87,.15);
            padding: 8px 20px; font-family: "Inter", sans-serif; font-size: 13px;
            color: #1D3557; display: flex; justify-content: space-between; align-items: center;
            gap: 8px;
        }
        .tawiza-bar a { color: #b45309; text-decoration: none; font-weight: 600; }
        .tawiza-bar a:hover { text-decoration: underline; }
        body > div:first-of-type { padding-top: 42px !important; }

        /* === Mobile (R32 accessibilité étendue, pénètre shadow DOM marimo) === */
        @media (max-width: 640px) {
            /* Bannière haute compacte */
            .tawiza-bar { font-size: 11px !important; padding: 6px 10px !important; }
            .tawiza-bar > span:last-child { display: none !important; }
            body > div:first-of-type { padding-top: 36px !important; }

            /* Global : empêcher débordement horizontal */
            html, body { overflow-x: hidden !important; max-width: 100vw !important; }
            #root, #root > *, .ProseMirror, marimo-cell-output, marimo-cell {
                max-width: 100% !important;
                box-sizing: border-box !important;
            }

            /* Touch targets - cible les custom elements marimo ET leur contenu */
            marimo-button, marimo-button button,
            marimo-slider, marimo-slider input,
            marimo-dropdown, marimo-dropdown select,
            button, a.skip-link, [role="button"] {
                min-height: 44px !important;
            }
            marimo-slider { display: block !important; padding: 8px 0 !important; }
            marimo-slider input[type="range"] { height: 28px !important; }

            /* Cards dashboard (mo.Html avec role=status) : 2 par ligne */
            div[role="status"] {
                min-width: calc(50% - 4px) !important;
                flex: 1 1 calc(50% - 4px) !important;
                max-width: calc(50% - 4px) !important;
            }

            /* Graphiques Plotly : responsive obligatoire */
            .plotly-graph-div, .js-plotly-plot, .plot-container {
                max-width: 100% !important;
                width: 100% !important;
                overflow-x: auto !important;
            }
            .svg-container { max-width: 100% !important; }

            /* Scorecard + alertes : padding réduit */
            section[role="region"], div[role="region"] { padding: 14px !important; }

            /* Voix dense */
            figure[role="figure"] {
                margin: 8px 0 !important;
                padding: 10px 14px !important;
            }

            /* Grid scorecard : 2 colonnes */
            [role="region"] > div[style*="grid-template-columns"] {
                grid-template-columns: repeat(2, 1fr) !important;
            }

            /* Tableau chronique événements : scroll horizontal si overflow */
            table { font-size: 11px !important; width: 100% !important; }
            table td { padding: 4px 6px !important; }

            /* Images et iframes : responsive */
            img, iframe { max-width: 100% !important; height: auto !important; }

            /* Texte général plus respirant */
            p, li { line-height: 1.6 !important; }
        }

        /* === Très petit mobile (iPhone SE, Galaxy Fold plié) === */
        @media (max-width: 380px) {
            .tawiza-bar { font-size: 10px !important; padding: 5px 8px !important; }
            div[role="status"] {
                min-width: 100% !important;
                flex: 1 1 100% !important;
                max-width: 100% !important;
            }
            /* Grid scorecard final : 1 colonne pour pas écraser */
            [role="region"] > div[style*="grid-template-columns"] {
                grid-template-columns: 1fr !important;
            }
            /* Scorecard titre plus petit */
            [role="region"] h2 { font-size: 18px !important; }
        }

        /* === Grand desktop : max-width pour pas être noyé dans un écran 4K === */
        @media (min-width: 1400px) {
            body > div:first-of-type { max-width: 1200px; margin: 0 auto; }
        }
    </style>
"""

BANNER = (
    '<div class="tawiza-bar">'
    '<span><a href="/">Tawiza</a> &middot; <a href="/notebooks/">Notebooks</a></span>'
    "<span>Modifie les valeurs, l'analyse se recalcule</span>"
    "</div>"
)


def brand(html_path: Path) -> bool:
    html = html_path.read_text(encoding="utf-8")
    if "tawiza-branding" in html:
        return False
    html = html.replace("</head>", INJECTION + "\n</head>")
    html = re.sub(r"(<body[^>]*>)", r"\1" + BANNER, html, count=1)
    html_path.write_text(html, encoding="utf-8")
    return True


def main() -> int:
    root = Path("notebooks")
    if not root.exists():
        print("No notebooks/ directory.")
        return 0
    for html_file in root.glob("*/index.html"):
        if brand(html_file):
            print(f"  branded: {html_file}")
        else:
            print(f"  skip (already branded): {html_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
