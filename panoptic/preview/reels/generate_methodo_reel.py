#!/usr/bin/env python3
"""
panoptic - reel methodologie (Instagram Reel, 1080x1920, 18s, 30 FPS)

Raconte en 18 secondes comment on a crose 4 registres publics pour compter
626 projets agrivoltaiques - hook, ampilement des sources, diagramme de
Venn, carte France, appel au code ouvert, end card.

Generation: pur Python + Pillow + imageio/ffmpeg. Aucun service tiers.

Usage:
    python3 generate_methodo_reel.py

Sortie:
    ../exports/panoptic-methodo-reel.mp4 (ignored par git)
"""

from __future__ import annotations

import math
import random
from pathlib import Path

import imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# =========================================================================
# CONFIG
# =========================================================================

WIDTH, HEIGHT = 1080, 1920
FPS = 30
TOTAL_DURATION = 18.0  # secondes

HERE = Path(__file__).resolve().parent
OUT_DIR = (HERE.parent / "exports").resolve()
OUT_DIR.mkdir(exist_ok=True)
OUTPUT = OUT_DIR / "panoptic-methodo-reel.mp4"

# Scenes cumulatives (nom, debut_s, fin_s)
SCENES = [
    ("hero",  0.0,  1.8),
    ("stack", 1.8,  4.8),
    ("venn",  4.8,  8.5),
    ("map",   8.5, 12.5),
    ("code",  12.5, 15.5),
    ("end",   15.5, 18.0),
]

# Palette Tawiza (reprise du design system)
INK      = (26, 22, 18)
INK_SOFT = (58, 52, 44)
INK_MUTE = (122, 110, 94)
CREAM    = (250, 245, 239)
CREAM_D  = (243, 235, 221)
OCRE     = (180, 83, 9)
TERRE    = (193, 85, 77)
FORET    = (45, 106, 79)

# Fonts - on detecte les chemins via fc-match puis fallback sur les env vars
# INSTRUMENT_SERIF_TTF / JETBRAINS_MONO_TTF / JETBRAINS_MONO_MEDIUM_TTF
import os
import subprocess


def _find_font(family: str, style: str = "Regular") -> str | None:
    """Resout un chemin TTF/OTF via fc-match. Retourne None si absent."""
    try:
        out = subprocess.check_output(
            ["fc-match", "-f", "%{file}", f"{family}:style={style}"],
            text=True, stderr=subprocess.DEVNULL,
        ).strip()
        return out if out and out.endswith((".ttf", ".otf")) else None
    except Exception:
        return None


FONT_SERIF_PATH = os.environ.get("INSTRUMENT_SERIF_TTF") or \
    _find_font("Instrument Serif") or \
    _find_font("DejaVu Serif")
FONT_SERIF_IT_PATH = os.environ.get("INSTRUMENT_SERIF_IT_TTF") or \
    _find_font("Instrument Serif", "Italic") or \
    _find_font("DejaVu Serif", "Italic")
FONT_MONO_PATH = os.environ.get("JETBRAINS_MONO_TTF") or \
    _find_font("JetBrainsMono Nerd Font Mono") or \
    _find_font("DejaVu Sans Mono")
FONT_MONO_MEDIUM_PATH = os.environ.get("JETBRAINS_MONO_MEDIUM_TTF") or \
    _find_font("JetBrainsMono Nerd Font Mono", "Medium") or \
    FONT_MONO_PATH

for _fp, _name in [
    (FONT_SERIF_PATH, "Instrument Serif (Regular)"),
    (FONT_SERIF_IT_PATH, "Instrument Serif (Italic)"),
    (FONT_MONO_PATH, "JetBrains Mono (Regular)"),
    (FONT_MONO_MEDIUM_PATH, "JetBrains Mono (Medium)"),
]:
    if not _fp:
        raise RuntimeError(
            f"Font manquante: {_name}. Exporte la variable d'env "
            f"correspondante ou installe la via fontconfig."
        )


def serif(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_SERIF_PATH, size)


def serif_italic(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_SERIF_IT_PATH, size)


def mono(size: int, medium: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_MONO_MEDIUM_PATH if medium else FONT_MONO_PATH
    return ImageFont.truetype(path, size)


# =========================================================================
# HELPERS - easing et interpolations
# =========================================================================

def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


def ease_in_out_cubic(t: float) -> float:
    if t < 0.5:
        return 4 * t * t * t
    return 1 - pow(-2 * t + 2, 3) / 2


def ease_out_cubic(t: float) -> float:
    return 1 - pow(1 - t, 3)


def ease_out_quart(t: float) -> float:
    return 1 - pow(1 - t, 4)


def color_lerp(c1, c2, t: float):
    return tuple(int(round(lerp(a, b, t))) for a, b in zip(c1, c2))


def fade_rgb(rgb, alpha: float):
    """Fade RGB vers CREAM (utile pour faire apparaitre du texte)."""
    return color_lerp(CREAM, rgb, clamp(alpha))


def with_alpha(rgb, alpha: float):
    """(r,g,b) -> (r,g,b,a)"""
    return (*rgb, int(round(255 * clamp(alpha))))


# =========================================================================
# 3AYNE EYE - geometrie pixel art
# =========================================================================

# ViewBox 40x16 - chaque tuple = (x, y, w, h)
EYE_LASHES_TOP = [(8, 0, 1, 2), (14, 0, 1, 2), (20, 0, 1, 2),
                  (26, 0, 1, 2), (32, 0, 1, 2)]

EYE_LID_TOP = [(6, 3, 1, 1), (7, 2, 2, 1), (9, 2, 4, 1), (13, 2, 4, 1),
               (17, 2, 6, 1), (23, 2, 4, 1), (27, 2, 4, 1), (31, 2, 2, 1),
               (33, 3, 1, 1)]

EYE_SCLERA = [(8, 4, 24, 8), (9, 3, 22, 1), (9, 12, 22, 1), (11, 13, 18, 1)]

EYE_IRIS = [(15, 4, 10, 1), (14, 5, 12, 1), (13, 6, 14, 1), (13, 7, 14, 1),
            (13, 8, 14, 1), (13, 9, 14, 1), (14, 10, 12, 1), (15, 11, 10, 1)]

EYE_IRIS_INNER = [(16, 5, 8, 1), (15, 6, 10, 1), (15, 7, 10, 1),
                  (15, 8, 10, 1), (15, 9, 10, 1), (16, 10, 8, 1)]

EYE_PUPIL = [(18, 6, 4, 4)]
EYE_HIGHLIGHT_A = [(18, 6, 1, 1)]
EYE_HIGHLIGHT_B = [(19, 6, 1, 1)]  # 55 % opacity

EYE_LID_BOTTOM = [(8, 13, 2, 1), (10, 14, 20, 1), (30, 13, 2, 1)]


def draw_eye(img: Image.Image, cx: float, cy: float, width: int,
             variant: str = "avatar", pupil_dx: float = 0.0,
             pupil_dy: float = 0.0, closed: float = 0.0) -> None:
    """
    Dessine l'oeil 3AYNE centre sur (cx, cy), largeur 'width' px.
    variant: 'avatar' (fond ocre, iris noir, pupille ocre) ou
             'panoptic' (fond crème, iris noir, pupille ocre).
    pupil_dx/dy: deplacement pupille en unites viewBox (max ~2.5).
    closed: 0=oeil ouvert, 1=oeil ferme (paupiere descend).
    """
    scale = width / 40.0
    height_px = 16 * scale
    x0 = cx - width / 2
    y0 = cy - height_px / 2

    # Choix palette
    if variant == "avatar":
        c_ink = INK
        c_sclera = CREAM
        c_iris = INK
        c_iris_inner = INK_SOFT
        c_pupil = OCRE
        c_highlight = CREAM
    else:  # "panoptic"
        c_ink = INK
        c_sclera = CREAM
        c_iris = INK
        c_iris_inner = INK_SOFT
        c_pupil = OCRE
        c_highlight = CREAM

    # Dessine sur un calque separe pour permettre l'alpha
    layer = Image.new("RGBA", (width + 2, int(height_px + 2)), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    def rects(items, color, dx_u=0.0, dy_u=0.0, opacity=1.0):
        col = (*color, int(round(255 * opacity)))
        for (rx, ry, rw, rh) in items:
            x1 = (rx + dx_u) * scale
            y1 = (ry + dy_u) * scale
            x2 = x1 + rw * scale
            y2 = y1 + rh * scale
            d.rectangle([x1, y1, x2, y2], fill=col)

    rects(EYE_LASHES_TOP, c_ink)
    rects(EYE_LID_TOP, c_ink)
    rects(EYE_SCLERA, c_sclera)
    rects(EYE_IRIS, c_iris)
    rects(EYE_IRIS_INNER, c_iris_inner)
    rects(EYE_PUPIL, c_pupil, dx_u=pupil_dx, dy_u=pupil_dy)
    rects(EYE_HIGHLIGHT_A, c_highlight, dx_u=pupil_dx, dy_u=pupil_dy)
    rects(EYE_HIGHLIGHT_B, c_highlight, dx_u=pupil_dx, dy_u=pupil_dy,
          opacity=0.55)
    rects(EYE_LID_BOTTOM, c_ink)

    # Paupiere de clignement : rect noir qui descend depuis le haut
    if closed > 0:
        lid_h = 10 * closed * scale
        d.rectangle([6 * scale, 2 * scale, 34 * scale, 2 * scale + lid_h],
                    fill=(*c_ink, 255))

    img.paste(layer, (int(x0), int(y0)), layer)


# =========================================================================
# FRANCE - outline simplifie (~13 points, hexagone stylise)
# =========================================================================

# Coordonnees lat/lon approx des contours (sens horaire depuis Dunkerque)
FRANCE_POINTS_LATLON = [
    (51.0, 2.4),    # Dunkerque
    (50.6, 3.1),    # Lille
    (49.2, 5.5),    # Metz
    (48.6, 7.8),    # Strasbourg
    (47.0, 7.2),    # Jura
    (45.0, 7.0),    # Briancon
    (43.7, 7.3),    # Nice
    (43.3, 5.4),    # Marseille
    (43.1, 3.0),    # Narbonne
    (42.6, 2.0),    # Pyrenees Est
    (43.0, -1.5),   # Pyrenees Ouest
    (45.7, -1.2),   # La Rochelle
    (48.4, -4.8),   # Brest
    (49.6, -1.3),   # Cherbourg
    (50.8, 1.6),    # Calais
]


def france_polygon(cx: float, cy: float, width: int, height: int):
    """Convertit les lat/lon en points (x,y) canvas."""
    lats = [p[0] for p in FRANCE_POINTS_LATLON]
    lons = [p[1] for p in FRANCE_POINTS_LATLON]
    lat_min, lat_max = min(lats), max(lats)
    lon_min, lon_max = min(lons), max(lons)
    # Rapport d'aspect France (approximatif)
    lon_range = lon_max - lon_min
    lat_range = lat_max - lat_min
    # Scale pour tenir dans (width, height)
    aspect = lon_range / lat_range
    target_aspect = width / height
    if aspect > target_aspect:
        # Limite par largeur
        scale_lon = width / lon_range
        scale_lat = scale_lon
    else:
        scale_lat = height / lat_range
        scale_lon = scale_lat

    pts = []
    for (la, lo) in FRANCE_POINTS_LATLON:
        x = cx + (lo - (lon_min + lon_max) / 2) * scale_lon
        y = cy - (la - (lat_min + lat_max) / 2) * scale_lat  # y inverse
        pts.append((x, y))
    return pts


# =========================================================================
# UTILS DESSIN
# =========================================================================

def new_frame(bg=CREAM) -> Image.Image:
    return Image.new("RGB", (WIDTH, HEIGHT), bg)


def text_centered(draw: ImageDraw.ImageDraw, text: str, y: int,
                  font, color=INK, line_spacing: float = 1.15) -> int:
    """Dessine texte centre horizontalement. Retourne y du bas."""
    lines = text.split("\n")
    line_heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_heights.append(bbox[3] - bbox[1])
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        x = (WIDTH - w) / 2
        draw.text((x, y), line, font=font, fill=color)
        y += int(line_heights[i] * line_spacing)
    return y


def text_left(draw: ImageDraw.ImageDraw, text: str, x: int, y: int,
              font, color=INK) -> None:
    draw.text((x, y), text, font=font, fill=color)


# =========================================================================
# SCENE 1 - HERO (0.0 - 1.8s)
# =========================================================================

def scene_hero(t: float) -> Image.Image:
    """t: 0..1 dans la scene.
    - fond ocre
    - eye scale in (0 -> 1) avec ease_out_cubic sur premiere moitie
    - titre apparait fade in sur seconde moitie
    """
    img = new_frame(bg=OCRE)
    draw = ImageDraw.Draw(img)

    # Oeil
    eye_t = clamp(t * 2.0)  # apparait sur premiere moitie
    eye_scale = ease_out_cubic(eye_t)
    eye_width = int(lerp(80, 700, eye_scale))
    if eye_width > 40:
        # Petite poursuite du regard cosmetique
        px = math.sin(t * 4) * 0.4
        py = math.cos(t * 3) * 0.3
        draw_eye(img, WIDTH / 2, HEIGHT * 0.38, eye_width,
                 variant="avatar", pupil_dx=px, pupil_dy=py)

    # Titre (apparait a t=0.4, fin_fade a t=0.95)
    title_t = clamp((t - 0.4) / 0.5)
    title_t_eased = ease_out_quart(title_t)
    if title_t > 0:
        alpha = int(title_t_eased * 255)
        # Gros titre serif
        title = "la methodologie"
        font_title = serif(130)
        layer = Image.new("RGBA", (WIDTH, 260), (0, 0, 0, 0))
        dl = ImageDraw.Draw(layer)
        bbox = dl.textbbox((0, 0), title, font=font_title)
        w = bbox[2] - bbox[0]
        dl.text(((WIDTH - w) / 2, 40), title, font=font_title,
                fill=(*CREAM, alpha))
        # sous-titre mono
        sub = "> comment on a compte 626 projets"
        font_sub = mono(34)
        bbox2 = dl.textbbox((0, 0), sub, font=font_sub)
        w2 = bbox2[2] - bbox2[0]
        dl.text(((WIDTH - w2) / 2, 190), sub, font=font_sub,
                fill=(*CREAM, int(alpha * 0.82)))
        img.paste(layer, (0, int(HEIGHT * 0.60)), layer)

    return img


# =========================================================================
# SCENE 2 - STACK (1.8 - 4.8s) : empilement des 4 registres
# =========================================================================

REGISTERS = [
    ("ADEME",              "raccordés",            OCRE,  237),
    ("projets-environnement", "en instruction",    TERRE, 78),
    ("MRAe",               "avis autorité",        FORET, 311),
    ("CNPrV",              "contestations",        INK,   133),
]


def scene_stack(t: float) -> Image.Image:
    """4 cartes s'empilent une par une, chacune avec un badge couleur."""
    img = new_frame(bg=CREAM)
    draw = ImageDraw.Draw(img)

    # Titre du haut
    title = "aucun registre ne voit tout"
    font_title = serif(88)
    bbox = draw.textbbox((0, 0), title, font=font_title)
    w = bbox[2] - bbox[0]
    draw.text(((WIDTH - w) / 2, 200), title, font=font_title, fill=INK)

    sub = "# chacun voit un bout du pipeline"
    font_sub = mono(30)
    bbox2 = draw.textbbox((0, 0), sub, font=font_sub)
    w2 = bbox2[2] - bbox2[0]
    draw.text(((WIDTH - w2) / 2, 330), sub, font=font_sub, fill=INK_SOFT)

    # 4 cartes
    card_top_start = 500
    card_h = 230
    gap = 30
    card_w = WIDTH - 200

    per_card_t = 1.0 / 4.0  # chaque carte prend 1/4 du temps

    for i, (name, tag, color, count) in enumerate(REGISTERS):
        # Apparition card i entre t = i/4 et t = i/4 + per_card_t
        local_t = clamp((t - i * per_card_t) / per_card_t)
        if local_t <= 0:
            continue
        eased = ease_out_cubic(local_t)
        y = card_top_start + i * (card_h + gap)
        offset_y = int(lerp(40, 0, eased))
        alpha = int(lerp(0, 255, eased))

        card_layer = Image.new("RGBA", (card_w + 12, card_h + 12),
                               (0, 0, 0, 0))
        dl = ImageDraw.Draw(card_layer)
        # Ombre decalee
        dl.rectangle([6, 6, card_w + 6, card_h + 6], fill=(*INK, alpha))
        # Carte crème
        dl.rectangle([0, 0, card_w, card_h], fill=(*CREAM_D, alpha),
                     outline=(*INK, alpha), width=2)
        # Badge couleur
        dl.rectangle([20, 20, 120, card_h - 20], fill=(*color, alpha))
        # Titre registre
        f_name = serif(70)
        dl.text((160, 50), name, font=f_name, fill=(*INK, alpha))
        # Tag
        f_tag = mono(28)
        dl.text((160, 135), tag, font=f_tag, fill=(*INK_SOFT, alpha))
        # Count a droite
        f_count = serif(110)
        count_s = f"{count}"
        bbox_c = dl.textbbox((0, 0), count_s, font=f_count)
        cw = bbox_c[2] - bbox_c[0]
        dl.text((card_w - cw - 40, 30), count_s, font=f_count,
                fill=(*INK, alpha))
        # Label "projets"/"avis" sous le count
        f_lab = mono(22)
        lbl = "contestations" if i == 3 else "entrées"
        bbox_l = dl.textbbox((0, 0), lbl, font=f_lab)
        lw = bbox_l[2] - bbox_l[0]
        dl.text((card_w - lw - 40, 160), lbl, font=f_lab,
                fill=(*INK_SOFT, alpha))

        img.paste(card_layer, (100, y + offset_y), card_layer)

    return img


# =========================================================================
# SCENE 3 - VENN (4.8 - 8.5s) : diagramme de Venn 4 cercles
# =========================================================================

def scene_venn(t: float) -> Image.Image:
    """4 cercles qui se reunissent pour former un Venn, puis highlight center."""
    img = new_frame(bg=CREAM)
    draw = ImageDraw.Draw(img)

    # Titre haut
    title = "on croise"
    font_t = serif(100)
    bbox = draw.textbbox((0, 0), title, font=font_t)
    draw.text(((WIDTH - (bbox[2] - bbox[0])) / 2, 180), title, font=font_t,
              fill=INK)

    # Centre du Venn
    cx, cy = WIDTH / 2, HEIGHT * 0.50
    radius = 280

    # 4 cercles - position finale en cercle autour de cx,cy
    # angles : 135, 45, 315, 225 (haut-G, haut-D, bas-D, bas-G)
    angles_deg = [135, 45, -45, -135]
    final_offset = 180  # distance centre -> centre cercle

    # Position initiale (cercles écartés) et finale (cercles qui se touchent)
    separation_t = ease_in_out_cubic(clamp(t * 2.0))  # 0->1 sur premiere moitie
    # init_offset_mult = 2.2 -> final_offset_mult = 1.0
    offset_mult = lerp(2.2, 1.0, separation_t)

    circles_info = []
    names = ["ADEME", "projets-env", "MRAe", "CNPrV"]
    colors = [OCRE, TERRE, FORET, INK]

    venn_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    vd = ImageDraw.Draw(venn_layer)

    for i, ang in enumerate(angles_deg):
        rad = math.radians(ang)
        ox = cx + math.cos(rad) * final_offset * offset_mult
        oy = cy - math.sin(rad) * final_offset * offset_mult
        circles_info.append((ox, oy, colors[i], names[i]))
        # Alpha = 0.38 pour voir les intersections
        alpha = 96
        vd.ellipse([ox - radius, oy - radius, ox + radius, oy + radius],
                   fill=(*colors[i], alpha))

    img.paste(venn_layer, (0, 0), venn_layer)

    # Labels autour
    f_label = mono(30, medium=True)
    for (ox, oy, col, nm) in circles_info:
        # Position label = cercle position + decalage vers exterieur
        rad = math.atan2(cy - oy, ox - cx)
        lx = ox + math.cos(rad) * (radius + 60)
        ly = oy - math.sin(rad) * (radius + 60)
        bbox_l = draw.textbbox((0, 0), nm, font=f_label)
        lw = bbox_l[2] - bbox_l[0]
        lh = bbox_l[3] - bbox_l[1]
        draw.text((lx - lw / 2, ly - lh / 2), nm, font=f_label, fill=col)

    # Highlight central sur seconde moitie (t > 0.5)
    highlight_t = clamp((t - 0.5) * 2.0)
    if highlight_t > 0:
        he = ease_out_quart(highlight_t)
        # Petit cercle noir au centre + texte
        r2 = int(lerp(0, 80, he))
        if r2 > 0:
            draw.ellipse([cx - r2, cy - r2, cx + r2, cy + r2],
                         fill=INK, outline=OCRE, width=4)

        if highlight_t > 0.3:
            text_t = clamp((highlight_t - 0.3) / 0.7)
            alpha = int(text_t * 255)
            # "21 projets visibles dans 2+ registres"
            big = "21"
            f_big = serif(200)
            bbox_b = draw.textbbox((0, 0), big, font=f_big)
            bw = bbox_b[2] - bbox_b[0]
            tlayer = Image.new("RGBA", (WIDTH, 400), (0, 0, 0, 0))
            td = ImageDraw.Draw(tlayer)
            td.text(((WIDTH - bw) / 2, 0), big, font=f_big,
                    fill=(*INK, alpha))
            sub = "projets visibles dans 2+ registres"
            f_sub = mono(30)
            bbox_s = td.textbbox((0, 0), sub, font=f_sub)
            sw = bbox_s[2] - bbox_s[0]
            td.text(((WIDTH - sw) / 2, 220), sub, font=f_sub,
                    fill=(*INK_SOFT, alpha))
            pct = "3,3 % du total"
            f_pct = mono(28)
            bbox_p = td.textbbox((0, 0), pct, font=f_pct)
            pw = bbox_p[2] - bbox_p[0]
            td.text(((WIDTH - pw) / 2, 260), pct, font=f_pct,
                    fill=(*OCRE, alpha))
            img.paste(tlayer, (0, int(HEIGHT * 0.73)), tlayer)

    return img


# =========================================================================
# SCENE 4 - MAP (8.5 - 12.5s) : carte France + points disperses
# =========================================================================

# Points pre-calcules pour eviter du random a chaque frame
_map_points = None


def _seed_map_points(n=300, seed=42):
    """Genere des points dans le polygone France. Cache."""
    global _map_points
    random.seed(seed)
    # Pour simplifier, on genere dans le bounding box puis on garde ceux
    # qui sont a l'interieur du polygone (point-in-polygon simple)
    map_cx, map_cy = WIDTH / 2, HEIGHT * 0.52
    poly = france_polygon(map_cx, map_cy, WIDTH - 260, int(HEIGHT * 0.52))
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    pts = []
    tries = 0
    while len(pts) < n and tries < n * 8:
        tries += 1
        x = random.uniform(xmin, xmax)
        y = random.uniform(ymin, ymax)
        if _point_in_polygon(x, y, poly):
            # couleur aleatoire dans palette + index d'apparition 0..1
            col_choice = random.choice([OCRE, TERRE, FORET, INK])
            order = random.random()
            pts.append((x, y, col_choice, order))
    _map_points = (pts, poly)


def _point_in_polygon(x, y, poly):
    n = len(poly)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi):
            inside = not inside
        j = i
    return inside


def scene_map(t: float) -> Image.Image:
    img = new_frame(bg=CREAM)
    draw = ImageDraw.Draw(img)

    if _map_points is None:
        _seed_map_points()

    pts, poly = _map_points
    map_cx, map_cy = WIDTH / 2, HEIGHT * 0.52

    # Dessiner polygone France en traits noirs epais
    # Avec un fade-in sur t < 0.15
    poly_alpha = int(clamp(t / 0.15) * 255)
    poly_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    pd = ImageDraw.Draw(poly_layer)
    pd.line(poly + [poly[0]], fill=(*INK, poly_alpha), width=4)
    img.paste(poly_layer, (0, 0), poly_layer)

    # Titre haut
    title = "626 projets"
    font_t = serif(110)
    bbox = draw.textbbox((0, 0), title, font=font_t)
    draw.text(((WIDTH - (bbox[2] - bbox[0])) / 2, 200), title, font=font_t,
              fill=INK)
    sub = "> disperses sur 96 departements"
    font_s = mono(28)
    bbox2 = draw.textbbox((0, 0), sub, font=font_s)
    draw.text(((WIDTH - (bbox2[2] - bbox2[0])) / 2, 350), sub, font=font_s,
              fill=INK_SOFT)

    # Points apparaissent progressivement selon leur 'order'
    # Un point apparait quand t >= point.order * 0.85 (laisse 15% pour le fade-in du polygone avant les points)
    reveal_progress = clamp((t - 0.15) / 0.70)
    for (px, py, col, order) in pts:
        if order <= reveal_progress:
            # Appliquer un leger "pop" anim sur 0.1s autour de l'apparition
            local = clamp((reveal_progress - order) / 0.05) if order > reveal_progress - 0.05 else 1.0
            r = 5 + int(local * 3)
            draw.ellipse([px - r, py - r, px + r, py + r], fill=col)

    # Legende en bas
    legend_y = int(HEIGHT * 0.87)
    draw.line([(100, legend_y), (WIDTH - 100, legend_y)],
              fill=(*INK_SOFT, 255), width=1)
    lt = mono(24)
    draw.text((100, legend_y + 20), "ADEME · projets-env · MRAe · CNPrV",
              font=lt, fill=INK_SOFT)
    draw.text((100, legend_y + 60), "chaque point = un projet croise",
              font=lt, fill=INK_MUTE)

    return img


# =========================================================================
# SCENE 5 - CODE (12.5 - 15.5s) : github + URL + license
# =========================================================================

def scene_code(t: float) -> Image.Image:
    """Fond noir, texte crème façon terminal."""
    img = new_frame(bg=INK)
    draw = ImageDraw.Draw(img)

    # Fond : legers traces code en transparence
    # (skip pour simplicite)

    # Lignes de code qui apparaissent en sequence
    lines = [
        ("$ git clone github.com/tawiza/panoptic", mono(30), OCRE, 0.0),
        ("", None, None, 0.0),
        ("> tout le code est ouvert.", serif_italic(58), CREAM, 0.15),
        ("> license AGPL-3.0.", serif_italic(58), CREAM, 0.25),
        ("", None, None, 0.0),
        ("  tu peux refaire.", mono(34), CREAM, 0.40),
        ("  tu peux corriger.", mono(34), CREAM, 0.50),
        ("  tu peux forker.", mono(34), CREAM, 0.60),
        ("", None, None, 0.0),
        ("$ panoptic.tawiza.fr", mono(34, medium=True), OCRE, 0.78),
    ]

    y = 420
    for (text, font, color, start_t) in lines:
        if font is None:
            y += 40
            continue
        if t < start_t:
            continue
        alpha_t = clamp((t - start_t) / 0.12)
        alpha = int(ease_out_quart(alpha_t) * 255)
        slide_y = int((1 - ease_out_quart(alpha_t)) * 20)
        layer = Image.new("RGBA", (WIDTH, 120), (0, 0, 0, 0))
        dl = ImageDraw.Draw(layer)
        bbox = dl.textbbox((0, 0), text, font=font)
        lh = bbox[3] - bbox[1] + 30
        dl.text((120, 0), text, font=font, fill=(*color, alpha))
        img.paste(layer, (0, y + slide_y), layer)
        y += lh

    return img


# =========================================================================
# SCENE 6 - END (15.5 - 18.0s) : oeil wink + wordmark
# =========================================================================

def scene_end(t: float) -> Image.Image:
    img = new_frame(bg=OCRE)
    draw = ImageDraw.Draw(img)

    # Oeil qui wink une fois a t=0.3
    closed = 0.0
    if 0.25 < t < 0.55:
        # Rapide descente puis remontee
        local = (t - 0.25) / 0.30
        if local < 0.5:
            closed = local * 2.0
        else:
            closed = (1 - local) * 2.0
    draw_eye(img, WIDTH / 2, HEIGHT * 0.38, 600, variant="avatar",
             closed=closed)

    # Wordmark sous l'oeil
    text_t = clamp(t * 2.0)
    alpha = int(ease_out_quart(text_t) * 255)

    layer = Image.new("RGBA", (WIDTH, 500), (0, 0, 0, 0))
    dl = ImageDraw.Draw(layer)

    # "tawiza"
    wm = "tawiza"
    f_wm = serif(150)
    bbox = dl.textbbox((0, 0), wm, font=f_wm)
    dl.text(((WIDTH - (bbox[2] - bbox[0])) / 2, 0), wm, font=f_wm,
            fill=(*CREAM, alpha))

    # "panoptic - un regard sur l'agrivoltaïsme"
    sub = "panoptic - un regard sur l'agrivoltaïsme"
    f_sub = mono(30)
    bbox2 = dl.textbbox((0, 0), sub, font=f_sub)
    dl.text(((WIDTH - (bbox2[2] - bbox2[0])) / 2, 200), sub, font=f_sub,
            fill=(*CREAM, int(alpha * 0.82)))

    # Call to action DM
    cta = "> un tuyau ? DM ou mail."
    f_cta = mono(32, medium=True)
    bbox3 = dl.textbbox((0, 0), cta, font=f_cta)
    dl.text(((WIDTH - (bbox3[2] - bbox3[0])) / 2, 310), cta, font=f_cta,
            fill=(*CREAM, alpha))

    img.paste(layer, (0, int(HEIGHT * 0.63)), layer)

    return img


# =========================================================================
# DISPATCHER + MAIN LOOP
# =========================================================================

SCENE_RENDERERS = {
    "hero":  scene_hero,
    "stack": scene_stack,
    "venn":  scene_venn,
    "map":   scene_map,
    "code":  scene_code,
    "end":   scene_end,
}


def render_frame(time_s: float) -> np.ndarray:
    """Trouve la scene courante, calcule t normalise, appelle le renderer."""
    for (name, t_start, t_end) in SCENES:
        if t_start <= time_s < t_end:
            local_t = (time_s - t_start) / (t_end - t_start)
            img = SCENE_RENDERERS[name](local_t)
            return np.array(img)
    # Fin : scene 'end' a t=1
    img = scene_end(1.0)
    return np.array(img)


def main():
    n_frames = int(TOTAL_DURATION * FPS)
    print(f"Rendering {n_frames} frames @ {FPS} fps -> {OUTPUT}")

    # Pre-seed les points de la carte
    _seed_map_points()

    # imageio writer h264
    with imageio.get_writer(
        str(OUTPUT),
        fps=FPS,
        codec="libx264",
        quality=8,
        macro_block_size=1,  # permet 1080x1920 sans warnings de pad
        pixelformat="yuv420p",
    ) as writer:
        for i in range(n_frames):
            time_s = i / FPS
            frame = render_frame(time_s)
            writer.append_data(frame)
            if i % 30 == 0:
                print(f"  frame {i}/{n_frames} ({time_s:.2f}s)")

    size_mb = OUTPUT.stat().st_size / (1024 * 1024)
    print(f"\nDone: {OUTPUT} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()
