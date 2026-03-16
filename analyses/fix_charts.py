#!/usr/bin/env python3
"""
Regenerate g7_radar (4 communes) and g6_desendettement (4 communes)
with dark-mode-compatible style: transparent bg, lighter text.
Also regenerate all other charts with same style for consistency.
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from pathlib import Path

# ---------------------------------------------------------------------------
# DARK-MODE COMPATIBLE STYLE
# ---------------------------------------------------------------------------
COLOR_HB = '#E63946'       # Rouge - Hénin-Beaumont
COLOR_LIEVIN = '#2A9D8F'   # Vert teal - Liévin
COLOR_CSB = '#457B9D'      # Bleu - Clichy-sous-Bois
COLOR_MONTF = '#9CA3AF'    # Gris - Montfermeil
COLOR_STRATE = '#A8DADC'   # Strate
COLOR_TEXT = '#57534E'      # Stone-600 (visible light & dark)
COLOR_GRID = '#D6D3D1'     # Stone-300
COLOR_ALERT = '#F4A261'
COLOR_SOURCE = '#A8A29E'   # Stone-400

GRAPHS = Path('/root/tawiza-website/analyses/graphs')
GRAPHS.mkdir(parents=True, exist_ok=True)

try:
    from matplotlib.font_manager import fontManager
    inter_available = any('Inter' in f.name for f in fontManager.ttflist)
except Exception:
    inter_available = False

plt.rcParams.update({
    'font.family': 'Inter' if inter_available else 'sans-serif',
    'font.size': 10,
    'axes.facecolor': 'none',
    'figure.facecolor': 'none',
    'axes.edgecolor': COLOR_GRID,
    'axes.labelcolor': COLOR_TEXT,
    'xtick.color': COLOR_TEXT,
    'ytick.color': COLOR_TEXT,
    'text.color': COLOR_TEXT,
    'axes.grid': True,
    'grid.color': COLOR_GRID,
    'grid.linewidth': 0.5,
    'grid.alpha': 0.3,
    'legend.frameon': False,
    'legend.fontsize': 9,
    'axes.spines.top': False,
    'axes.spines.right': False,
})

# ---------------------------------------------------------------------------
# DATA
# ---------------------------------------------------------------------------
ofgl = pd.read_csv('/root/tawiza-website/analyses/data/ofgl_communes_raw.csv')
tfb = pd.read_csv('/root/tawiza-website/analyses/data/tfb_complet_2014_2024.csv')

hb_ofgl = ofgl[ofgl['com_code'] == 62427]
csb_ofgl = ofgl[ofgl['com_code'] == 93014]
lv_ofgl = ofgl[ofgl['com_code'] == 62510]   # Liévin
mf_ofgl = ofgl[ofgl['com_code'] == 93047]   # Montfermeil

years = list(range(2017, 2025))

def get_series(commune_df, agregat):
    sub = commune_df[commune_df['agregat'] == agregat].set_index('exer')['euros_par_habitant']
    return [sub.get(y, np.nan) for y in years]

strate = {
    2017: {'dep_fonct': 1225.9, 'personnel': 746.4, 'equip': 306.4, 'dette': 1100.4,
            'ep_brute': 188.9, 'recettes': 1414.8, 'impots': 824.6, 'dgf': 193.4,
            'annuite': 136.3, 'ep_nette': 85.5},
    2024: {'dep_fonct': 1399.7, 'personnel': 848.8, 'equip': 398.9, 'dette': 998.5,
            'ep_brute': 212.2, 'recettes': 1611.8, 'impots': 989.9, 'dgf': 204.5,
            'annuite': 129.5, 'ep_nette': 110.1},
}

def strate_interp(key):
    v17 = strate[2017][key]
    v24 = strate[2024][key]
    return [v17 + (v24 - v17) * (y - 2017) / 7 for y in years]

def save(fig, name):
    fig.savefig(GRAPHS / f'{name}.png', dpi=300, bbox_inches='tight',
                facecolor='none', transparent=True)
    fig.savefig(GRAPHS / f'{name}.svg', bbox_inches='tight',
                facecolor='none', transparent=True)
    plt.close(fig)
    print(f'  {name} OK')

def add_source(ax, text, y=-0.15):
    ax.annotate(text, xy=(0, y), xycoords='axes fraction',
                fontsize=7, color=COLOR_SOURCE, style='italic')


# ---------------------------------------------------------------------------
# G1 - Taux TFB communal 2018-2024
# ---------------------------------------------------------------------------
def chart_g1():
    tfb_hb = tfb[tfb['code'] == 62427].set_index('year')['taux_tfb_communal'].dropna()
    tfb_csb = tfb[tfb['code'] == 93014].set_index('year')['taux_tfb_communal'].dropna()
    yrs_hb = sorted(tfb_hb.index)
    yrs_csb = sorted(tfb_csb.index)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(yrs_hb, [tfb_hb[y] for y in yrs_hb], 'o-', color=COLOR_HB,
            linewidth=2.2, markersize=5, label='Hénin-Beaumont', zorder=5)
    ax.plot(yrs_csb, [tfb_csb[y] for y in yrs_csb], 's-', color=COLOR_CSB,
            linewidth=2.2, markersize=5, label='Clichy-sous-Bois', zorder=5)
    ax.axvline(x=2021, color=COLOR_ALERT, linewidth=1.5, linestyle='--', alpha=0.8)
    ax.annotate('Transfert TH → TFB', xy=(2021, 62), xytext=(2021.3, 66),
                fontsize=9, color=COLOR_ALERT, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=COLOR_ALERT, lw=1.2))
    for yr, vals, color in [(2018, tfb_hb, COLOR_HB), (2024, tfb_hb, COLOR_HB),
                             (2018, tfb_csb, COLOR_CSB), (2024, tfb_csb, COLOR_CSB)]:
        if yr in vals.index:
            v = vals[yr]
            if color == COLOR_HB:
                voff, ha_val = 6, 'center'
                hoff = 0
            else:
                # CSB: put label below the point with enough clearance
                voff = -12
                ha_val = 'center'
                hoff = 0
            ax.annotate(f'{v:.1f} %', xy=(yr, v), xytext=(hoff, voff),
                        textcoords='offset points', fontsize=8, color=color,
                        fontweight='bold', ha=ha_val, va='bottom')
    ax.set_ylabel('Taux communal TFB (%)')
    ax.set_title('Taux communal de taxe foncière sur le bâti (TFB), 2018-2024',
                 fontsize=12, fontweight='bold', pad=12)
    ax.legend(loc='upper left')
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.0f %%'))
    ax.set_xlim(2017.5, 2024.8)
    ax.set_xticks(range(2018, 2025))
    add_source(ax, 'Source : DGFIP, fichier REI, taux votés 2018-2024')
    fig.tight_layout()
    save(fig, 'g1_taux_tfb')


# ---------------------------------------------------------------------------
# G2a - Dep fonctionnement bassin minier
# ---------------------------------------------------------------------------
def chart_g2a():
    hb_vals = get_series(hb_ofgl, 'Dépenses de fonctionnement')
    lv_vals = get_series(lv_ofgl, 'Dépenses de fonctionnement')
    strate_vals = strate_interp('dep_fonct')

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(years, hb_vals, 'o-', color=COLOR_HB, linewidth=2.2, markersize=5,
            label='Hénin-Beaumont (RN)')
    ax.plot(years, lv_vals, 's-', color=COLOR_LIEVIN, linewidth=2.2, markersize=5,
            label='Liévin (Gauche)')
    ax.plot(years, strate_vals, '--', color=COLOR_STRATE, linewidth=1.8,
            label='Strate 20k-50k hab.')

    for vals, color in [(hb_vals, COLOR_HB), (lv_vals, COLOR_LIEVIN)]:
        ax.annotate(f'{vals[0]:.0f}', xy=(2017, vals[0]), fontsize=8,
                    color=color, fontweight='bold', ha='right',
                    xytext=(-8, 0), textcoords='offset points')
        ax.annotate(f'{vals[-1]:.0f}', xy=(2024, vals[-1]), fontsize=8,
                    color=color, fontweight='bold', ha='left',
                    xytext=(8, 0), textcoords='offset points')

    ax.set_ylabel('€ / habitant')
    ax.set_title('Dépenses de fonctionnement par habitant, 2017-2024',
                 fontsize=12, fontweight='bold', pad=12)
    ax.legend(loc='lower right')
    ax.set_xticks(years)
    add_source(ax, 'Source : OFGL, comptes consolidés des communes, 2017-2024')
    fig.tight_layout()
    save(fig, 'g2a_dep_fonct_bassin')


# ---------------------------------------------------------------------------
# G4a - Investissement bassin minier
# ---------------------------------------------------------------------------
def chart_g4a():
    hb_vals = get_series(hb_ofgl, "Dépenses d'équipement")
    lv_vals = get_series(lv_ofgl, "Dépenses d'équipement")
    strate_vals = strate_interp('equip')

    x = np.array(years)
    width = 0.35
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x - width/2, hb_vals, width, color=COLOR_HB, label='Hénin-Beaumont (RN)',
           edgecolor='white', linewidth=0.5, zorder=3)
    ax.bar(x + width/2, lv_vals, width, color=COLOR_LIEVIN, label='Liévin (Gauche)',
           edgecolor='white', linewidth=0.5, zorder=3)
    ax.plot(x, strate_vals, '--', color=COLOR_STRATE, linewidth=2,
            label='Strate 20k-50k hab.', zorder=4)

    # Add value labels on first and last bars
    for i, yr_idx in enumerate([0, -1]):
        for vals, offset, color in [(hb_vals, -width/2, COLOR_HB), (lv_vals, width/2, COLOR_LIEVIN)]:
            v = vals[yr_idx]
            if not np.isnan(v):
                ax.text(years[yr_idx] + offset, v + 8, f'{v:.0f}',
                        ha='center', va='bottom', fontsize=7.5, color=color, fontweight='bold')

    ax.set_ylabel('€ / habitant')
    ax.set_title("Dépenses d'équipement par habitant, 2017-2024",
                 fontsize=12, fontweight='bold', pad=12)
    ax.set_xticks(years)
    ax.legend(loc='upper left')
    add_source(ax, 'Source : OFGL, comptes consolidés des communes, 2017-2024')
    fig.tight_layout()
    save(fig, 'g4a_invest_bassin')


# ---------------------------------------------------------------------------
# G4b - Investissement IDF
# ---------------------------------------------------------------------------
def chart_g4b():
    csb_vals = get_series(csb_ofgl, "Dépenses d'équipement")
    mf_vals = get_series(mf_ofgl, "Dépenses d'équipement")
    strate_vals = strate_interp('equip')

    x = np.array(years)
    width = 0.35
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x - width/2, csb_vals, width, color=COLOR_CSB, label='Clichy-sous-Bois (Horizons)',
           edgecolor='white', linewidth=0.5, zorder=3)
    ax.bar(x + width/2, mf_vals, width, color=COLOR_MONTF, label='Montfermeil (Droite)',
           edgecolor='white', linewidth=0.5, zorder=3)
    ax.plot(x, strate_vals, '--', color=COLOR_STRATE, linewidth=2,
            label='Strate 20k-50k hab.', zorder=4)

    # Add value labels on first and last bars
    for i, yr_idx in enumerate([0, -1]):
        for vals, offset, color in [(csb_vals, -width/2, COLOR_CSB), (mf_vals, width/2, COLOR_MONTF)]:
            v = vals[yr_idx]
            if not np.isnan(v):
                ax.text(years[yr_idx] + offset, v + 8, f'{v:.0f}',
                        ha='center', va='bottom', fontsize=7.5, color=color, fontweight='bold')

    ax.set_ylabel('€ / habitant')
    ax.set_title("Dépenses d'équipement par habitant, 2017-2024",
                 fontsize=12, fontweight='bold', pad=12)
    ax.set_xticks(years)
    ax.legend(loc='upper right')
    add_source(ax, 'Source : OFGL, comptes consolidés des communes, 2017-2024')
    fig.tight_layout()
    save(fig, 'g4b_invest_idf')


# ---------------------------------------------------------------------------
# G6a - Désendettement bassin minier
# ---------------------------------------------------------------------------
def desendettement(commune_df):
    vals = []
    for y in years:
        dette = commune_df[(commune_df['exer'] == y) &
                           (commune_df['agregat'] == 'Encours de dette')]['montant']
        eb = commune_df[(commune_df['exer'] == y) &
                        (commune_df['agregat'] == 'Epargne brute')]['montant']
        if len(dette) and len(eb) and eb.values[0] > 0:
            vals.append(dette.values[0] / eb.values[0])
        else:
            vals.append(np.nan)
    return vals

def chart_g6a():
    hb_vals = desendettement(hb_ofgl)
    lv_vals = desendettement(lv_ofgl)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axhspan(12, 13,
               alpha=0.15, color=COLOR_ALERT, zorder=1)
    ax.axhline(y=12, color=COLOR_ALERT, linewidth=1.2, linestyle='--', alpha=0.7)
    ax.text(2017.2, 12.3, "Seuil d'alerte (12 ans)", fontsize=8,
            color=COLOR_ALERT, va='bottom')
    ax.plot(years, hb_vals, 'o-', color=COLOR_HB, linewidth=2.2, markersize=5,
            label='Hénin-Beaumont (RN)', zorder=5)
    ax.plot(years, lv_vals, 's-', color=COLOR_LIEVIN, linewidth=2.2, markersize=5,
            label='Liévin (Gauche)', zorder=5)

    for vals, color in [(hb_vals, COLOR_HB), (lv_vals, COLOR_LIEVIN)]:
        ax.annotate(f'{vals[0]:.1f}', xy=(2017, vals[0]), fontsize=8,
                    color=color, fontweight='bold', ha='right',
                    xytext=(-8, 0), textcoords='offset points')
        ax.annotate(f'{vals[-1]:.1f}', xy=(2024, vals[-1]), fontsize=8,
                    color=color, fontweight='bold', ha='left',
                    xytext=(8, 0), textcoords='offset points')

    ax.set_ylabel('Années')
    ax.set_title('Capacité de désendettement, 2017-2024',
                 fontsize=12, fontweight='bold', pad=12)
    ax.set_xticks(years)
    ax.set_ylim(0, 13)
    ax.legend(loc='lower right')
    add_source(ax, 'Source : OFGL, comptes consolidés des communes, calcul dette/épargne brute')
    fig.tight_layout()
    save(fig, 'g6a_desendettement_bassin')


# ---------------------------------------------------------------------------
# G6b - Désendettement IDF
# ---------------------------------------------------------------------------
def chart_g6b():
    csb_vals = desendettement(csb_ofgl)
    mf_vals = desendettement(mf_ofgl)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axhspan(12, 13,
               alpha=0.15, color=COLOR_ALERT, zorder=1)
    ax.axhline(y=12, color=COLOR_ALERT, linewidth=1.2, linestyle='--', alpha=0.7)
    ax.text(2017.2, 12.3, "Seuil d'alerte (12 ans)", fontsize=8,
            color=COLOR_ALERT, va='bottom')
    ax.plot(years, csb_vals, 'o-', color=COLOR_CSB, linewidth=2.2, markersize=5,
            label='Clichy-sous-Bois (Horizons)', zorder=5)
    ax.plot(years, mf_vals, 's-', color=COLOR_MONTF, linewidth=2.2, markersize=5,
            label='Montfermeil (Droite)', zorder=5)

    for vals, color in [(csb_vals, COLOR_CSB), (mf_vals, COLOR_MONTF)]:
        ax.annotate(f'{vals[0]:.1f}', xy=(2017, vals[0]), fontsize=8,
                    color=color, fontweight='bold', ha='right',
                    xytext=(-8, 0), textcoords='offset points')
        ax.annotate(f'{vals[-1]:.1f}', xy=(2024, vals[-1]), fontsize=8,
                    color=color, fontweight='bold', ha='left',
                    xytext=(8, 0), textcoords='offset points')

    ax.set_ylabel('Années')
    ax.set_title('Capacité de désendettement, 2017-2024',
                 fontsize=12, fontweight='bold', pad=12)
    ax.set_xticks(years)
    ax.set_ylim(0, 13)
    ax.legend(loc='lower right')
    add_source(ax, 'Source : OFGL, comptes consolidés des communes, calcul dette/épargne brute')
    fig.tight_layout()
    save(fig, 'g6b_desendettement_idf')


# ---------------------------------------------------------------------------
# G7a - Radar bassin minier (HB vs Liévin)
# ---------------------------------------------------------------------------
def make_radar(ax, communes, colors, markers, labels):
    axes_labels = ['Impôts locaux', 'Dép. fonctionnement', 'Personnel',
                   'Équipement', 'Dette', 'Épargne brute']
    agregats = ['Impôts locaux', 'Dépenses de fonctionnement', 'Frais de personnel',
                "Dépenses d'équipement", 'Encours de dette', 'Epargne brute']
    strate_keys = ['impots', 'dep_fonct', 'personnel', 'equip', 'dette', 'ep_brute']

    def get_2024(commune_df):
        vals = []
        for ag in agregats:
            r = commune_df[(commune_df['exer'] == 2024) & (commune_df['agregat'] == ag)]
            vals.append(r['euros_par_habitant'].values[0] if len(r) else 0)
        return vals

    raw_data = [get_2024(c) for c in communes]
    strate_raw = [strate[2024][k] for k in strate_keys]

    # Normalize
    all_vals = list(zip(*raw_data, strate_raw))
    norms = [[] for _ in communes]
    strate_norm = []
    for i, vals in enumerate(all_vals):
        mn = min(vals) * 0.7
        mx = max(vals) * 1.1
        if mx == mn: mx = mn + 1
        for j in range(len(communes)):
            norms[j].append((vals[j] - mn) / (mx - mn) * 100)
        strate_norm.append((vals[-1] - mn) / (mx - mn) * 100)

    N = len(axes_labels)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]
    for n in norms: n += n[:1]
    strate_norm += strate_norm[:1]

    ax.set_facecolor('none')
    for i, (norm, color, marker, label) in enumerate(zip(norms, colors, markers, labels)):
        ax.plot(angles, norm, f'{marker}-', color=color, linewidth=2, markersize=5, label=label)
        ax.fill(angles, norm, alpha=0.10, color=color)
    ax.plot(angles, strate_norm, '--', color=COLOR_STRATE, linewidth=1.8,
            label='Strate 20k-50k hab.')

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(axes_labels, fontsize=10, fontweight='bold')
    ax.set_ylim(0, 105)
    ax.set_yticklabels([])
    ax.grid(color=COLOR_GRID, linewidth=0.5, alpha=0.3)

    # Value annotations with smart positioning to avoid overlaps
    for i in range(N):
        angle = angles[i]
        # Collect all values at this axis and sort by normalized position
        items = [(j, norms[j][i], raw_data[j][i], colors[j]) for j in range(len(communes))]
        items.sort(key=lambda x: x[1], reverse=True)  # highest first

        # Determine base direction from angle (radial outward)
        deg = np.degrees(angle) % 360
        # Horizontal offset based on which side of the chart
        if deg < 30 or deg > 330:       # right
            base_hoff, ha = 10, 'left'
        elif 150 < deg < 210:           # left
            base_hoff, ha = -10, 'right'
        elif deg <= 150:                # upper half
            base_hoff, ha = 8, 'left'
        else:                           # lower half
            base_hoff, ha = 8, 'left'

        # Stack annotations with enough vertical spacing
        spacing = 12  # pixels between annotations
        start_voff = (len(items) - 1) * spacing / 2
        for rank, (j, norm_val, raw_val, color) in enumerate(items):
            voff = start_voff - rank * spacing
            ax.annotate(f'{raw_val:.0f}', xy=(angle, norm_val),
                        fontsize=7, color=color, fontweight='bold',
                        ha=ha, va='center',
                        xytext=(base_hoff, voff), textcoords='offset points')

def chart_g7a():
    fig, ax = plt.subplots(figsize=(8, 8.5), subplot_kw=dict(polar=True))
    make_radar(ax, [hb_ofgl, lv_ofgl], [COLOR_HB, COLOR_LIEVIN], ['o', 's'],
               ['Hénin-Beaumont (RN)', 'Liévin (Gauche)'])
    ax.set_title('Profil financier comparé 2024 (€/hab)\nBassin minier',
                 fontsize=12, fontweight='bold', pad=20)
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), fontsize=8.5,
              ncol=3, columnspacing=1.5)
    fig.text(0.5, 0.01, 'Source : OFGL, comptes consolidés des communes, 2024',
             ha='center', fontsize=7, color=COLOR_SOURCE, style='italic')
    fig.subplots_adjust(bottom=0.08)
    save(fig, 'g7a_radar_bassin')


def chart_g7b():
    fig, ax = plt.subplots(figsize=(8, 8.5), subplot_kw=dict(polar=True))
    make_radar(ax, [csb_ofgl, mf_ofgl], [COLOR_CSB, COLOR_MONTF], ['o', 's'],
               ['Clichy-sous-Bois (Horizons)', 'Montfermeil (Droite)'])
    ax.set_title('Profil financier comparé 2024 (€/hab)\nSeine-Saint-Denis',
                 fontsize=12, fontweight='bold', pad=20)
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), fontsize=8.5,
              ncol=3, columnspacing=1.5)
    fig.text(0.5, 0.01, 'Source : OFGL, comptes consolidés des communes, 2024',
             ha='center', fontsize=7, color=COLOR_SOURCE, style='italic')
    fig.subplots_adjust(bottom=0.08)
    save(fig, 'g7b_radar_idf')


# ---------------------------------------------------------------------------
# G7 - Radar 4 communes (le profil en un coup d'oeil)
# ---------------------------------------------------------------------------
def chart_g7_all():
    fig, ax = plt.subplots(figsize=(9, 9.5), subplot_kw=dict(polar=True))
    make_radar(ax,
               [hb_ofgl, lv_ofgl, csb_ofgl, mf_ofgl],
               [COLOR_HB, COLOR_LIEVIN, COLOR_CSB, COLOR_MONTF],
               ['o', 's', 'D', '^'],
               ['Hénin-Beaumont (RN)', 'Liévin (Gauche)',
                'Clichy-sous-Bois (Horizons)', 'Montfermeil (Droite)'])
    ax.set_title('Profil financier comparé 2024 (€/hab)\nQuatre communes',
                 fontsize=12, fontweight='bold', pad=20)
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), fontsize=8.5,
              ncol=3, columnspacing=1.2)
    fig.text(0.5, 0.01, 'Source : OFGL, comptes consolidés des communes, 2024',
             ha='center', fontsize=7, color=COLOR_SOURCE, style='italic')
    fig.subplots_adjust(bottom=0.08)
    save(fig, 'g7_radar')


# ---------------------------------------------------------------------------
# G6 - Désendettement 4 communes
# ---------------------------------------------------------------------------
def chart_g6_all():
    hb_vals = desendettement(hb_ofgl)
    lv_vals = desendettement(lv_ofgl)
    csb_vals = desendettement(csb_ofgl)
    mf_vals = desendettement(mf_ofgl)

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.axhspan(12, 13, alpha=0.15, color=COLOR_ALERT, zorder=1)
    ax.axhline(y=12, color=COLOR_ALERT, linewidth=1.2, linestyle='--', alpha=0.7)
    ax.text(2017.2, 12.3, "Seuil d'alerte (12 ans)", fontsize=8,
            color=COLOR_ALERT, va='bottom')

    ax.plot(years, hb_vals, 'o-', color=COLOR_HB, linewidth=2.2, markersize=5,
            label='Hénin-Beaumont (RN)', zorder=5)
    ax.plot(years, lv_vals, 's-', color=COLOR_LIEVIN, linewidth=2.2, markersize=5,
            label='Liévin (Gauche)', zorder=5)
    ax.plot(years, csb_vals, 'D-', color=COLOR_CSB, linewidth=2.2, markersize=5,
            label='Clichy-sous-Bois (Horizons)', zorder=5)
    ax.plot(years, mf_vals, '^-', color=COLOR_MONTF, linewidth=2.2, markersize=5,
            label='Montfermeil (Droite)', zorder=5)

    # Smart end-value annotations: avoid overlaps by sorting and spacing
    end_items = [
        (hb_vals[-1], COLOR_HB, 'HB'),
        (lv_vals[-1], COLOR_LIEVIN, 'LV'),
        (csb_vals[-1], COLOR_CSB, 'CSB'),
        (mf_vals[-1], COLOR_MONTF, 'MF'),
    ]
    end_items.sort(key=lambda x: x[0])
    min_gap = 0.35  # minimum gap in data units
    placed = []
    for val, color, _ in end_items:
        y = val
        for py in placed:
            if abs(y - py) < min_gap:
                y = py + min_gap
        placed.append(y)
        ax.annotate(f'{val:.1f}', xy=(2024, val), fontsize=8,
                    color=color, fontweight='bold', ha='left',
                    xytext=(8, (y - val) * 8), textcoords='offset points')

    ax.set_ylabel('Années')
    ax.set_title('Capacité de désendettement, 2017-2024',
                 fontsize=12, fontweight='bold', pad=12)
    ax.set_xticks(years)
    ax.set_ylim(0, 13)
    ax.legend(loc='lower center', ncol=4, fontsize=7.5,
              bbox_to_anchor=(0.5, -0.18))
    add_source(ax, 'Source : OFGL, comptes consolidés des communes, calcul dette/épargne brute',
               y=-0.22)
    fig.tight_layout(rect=[0, 0.08, 1, 1])
    save(fig, 'g6_desendettement')


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    print('Regénération des graphiques (dark mode compatible)...')
    chart_g1()
    chart_g2a()
    chart_g4a()
    chart_g4b()
    chart_g6a()
    chart_g6b()
    chart_g7a()
    chart_g7b()
    chart_g7_all()
    chart_g6_all()
    print('\nTous les graphiques régénérés (fond transparent, dark/light compatible)')
