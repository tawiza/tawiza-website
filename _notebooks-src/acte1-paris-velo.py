# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = [
#     "marimo",
#     "plotly",
# ]
# ///

"""acte1_slider_budget v7 — Simulateur Tawiza Paris vélo 2026-2031.

v7 : refactor CFG/MOTEUR phase 1. Une cellule `__config_cfg()` contient TOUTES
les données spécifiques Paris vélo. Les cellules `__constants`, `__state`,
`__fetch_trame` lisent depuis CFG. Pour un nouveau territoire : cloner ce
fichier et modifier seulement `__config_cfg()`. La logique moteur (voix,
twists, verdicts, couplages) sera factorisée en v8.

v6 → v7 : changements structurels uniquement, aucune régression fonctionnelle.

Historique :
- v6 : presets, arrondissements, provocation events, 5 voix, twists, spirale
       live, radar, branches narratives, URL partage.
- v6.1 : corrections Vigie (Plausible R16, disclaimer R23).
- v7 : extraction CFG (ce fichier).

Nommage Tawiza : "la Trame" (pas "observatoire").
Règle marimo : variables internes préfixées `_`.

LICENCE R23 (non-partisanerie)
──────────────────────────────
Ce notebook est distribué par Tawiza avec clause de non-partisanerie.
Les forks modifiant les règles pour favoriser une ligne politique (retrait
de Hamide, trucage coefficients, palmarès municipaux, détournement électoral)
doivent explicitement renoncer au nom "Tawiza", à la doctrine 31 règles,
au mythe Tisserand-Cartographe, et à toute référence à tawiza.fr.
"""

import marimo

__generated_with = "0.9.0"
app = marimo.App(
    width="medium",
    app_title="Tawiza — Simulateur Paris vélo 2026-2031",
)


@app.cell
def _():
    import marimo as mo
    return (mo,)


# =============================================================================
# ====== CFG — seule cellule à modifier pour adapter à un autre territoire ====
# =============================================================================

@app.cell
def __config_cfg():
    """Config spécifique Paris vélo 2026-2031. Clone du notebook pour autre
    territoire = modifier UNIQUEMENT cette cellule. Le reste du moteur lit CFG.

    Structure documentée dans `notebooks/_template/simulateur_moteur.py`.
    """
    CFG = {
        # === Identité territoriale ===
        "territoire_slug": "paris-velo-2026",
        "territoire_label": "Paris vélo",
        "periode_label": "2026-2031",
        "annee_depart": 2026,
        "annee_fin": 2031,
        "budget_plafond_meur": 80,

        # === Objectif simulé ===
        "objectif_km": 180,
        "cout_moyen_km_meur": 1.4,

        # === État initial (alimente mo.state) ===
        "etat_initial": {
            "km_realises": 72,
            "dette_mdeur": 9.4,
            "notation": "AA-",
            "usage_index": 100,
            "lobby_cyclo": 1.0,
            "capital_politique": 100,
        },

        # === Trame (snapshot inline) ===
        "trame": {
            "updated_at": "2026-04-17",
            "valid_until": "2027-12-31",
            "n_signaux": 12,
            "signaux_critiques": [
                {"id": "plf_2026_velo", "etat": "🔴",
                 "label": "Budget vélo national PLF 2026",
                 "lecture": "Sénat a rescapé à 50 M€ vs 250 M€ initiaux"},
                {"id": "bp_paris_velo_2026", "etat": "🔴",
                 "label": "BP Paris — Plan Vélo 2026",
                 "lecture": "20 M€ constatés, seuil 30 M€"},
            ],
            "boucle_active": "Spirale du désengagement (2 signaux rouges sur chaîne de 4)",
            "backtest": {"vu_juste": 4, "total": 6, "latence_moyenne_mois": 22.7},
            "doctrine_version": "31-règles",
        },

        # === Événements aléatoires/forçables ===
        "events_base": [
            # Les probabilités peuvent être modulées par l'état de la Trame
            # via des clés 'proba_if_plf_rouge' / 'proba_if_bp_rouge' (optionnel)
            {"id": "canicule", "label": "Canicule majeure, pic d'usage vélo",
             "effet": {"usage_index": +15}, "proba": 0.3},
            {"id": "moodys_warning", "label": "Moody's passe Paris sous surveillance",
             "effet": {"notation_risk": +1, "dette_cout": +0.3},
             "proba": 0.2, "proba_if_bp_rouge": 0.35},
            {"id": "election_nationale", "label": "Élection : nouveau rapport à l'État",
             "effet": {}, "proba": 0.2},
            {"id": "accident_grave", "label": "Accident cycliste mortel rue de Rivoli",
             "effet": {"capital_politique": -10, "usage_index": -8}, "proba": 0.15},
            {"id": "greve_livreurs", "label": "Grève des livreurs vélo — saturation",
             "effet": {"lobby_cyclo": -0.2}, "proba": 0.15},
            {"id": "cper_avenant", "label": "Avenant CPER IDF — Paris arrache 50 M€",
             "effet": {"budget_bonus": +50, "capital_politique": +10},
             "proba": 0.15, "proba_if_plf_rouge": 0.05},
            {"id": "tempete_financiere", "label": "Choc obligataire — coût dette",
             "effet": {"dette_cout": +0.5}, "proba": 0.1},
        ],

        # === Périmètres géographiques (5 zones Paris) ===
        "arrondissements": {
            "tous_paris": {"label": "Tout Paris (standard)", "cout_mult": 1.0,
                           "concert_requise": 3,
                           "description": "Calibrage standard sur l'ensemble"},
            "centre_1_4": {"label": "Centre (1er-4e) — dense, patrimoine", "cout_mult": 1.6,
                           "concert_requise": 6,
                           "description": "Rues étroites, ABF, commerçants nombreux, coût +60%"},
            "est_11_12_20": {"label": "Est populaire (11e-12e-20e)", "cout_mult": 0.9,
                             "concert_requise": 4,
                             "description": "Axes larges, concertation sociale importante"},
            "ouest_16_17": {"label": "Ouest aisé (16e-17e)", "cout_mult": 1.2,
                            "concert_requise": 7,
                            "description": "Coûts +20%, opposition politique haute"},
            "periph_18_19": {"label": "Périphérie (18e-19e)", "cout_mult": 0.75,
                             "concert_requise": 3,
                             "description": "Axes larges, coûts −25%, concertation plus facile"},
        },

        # === Presets politiques (6 configs) ===
        "presets": {
            "libre": {"label": "Mode libre (curseurs à toi)",
                      "v": (20, 15, 20, 2)},
            "ecolo_visionnaire": {"label": "Maire écolo visionnaire (45/15/15/5)",
                                  "v": (45, 15, 15, 5)},
            "gestionnaire_prudent": {"label": "Gestionnaire prudent (18/18/20/4)",
                                     "v": (18, 18, 20, 4)},
            "austerite_crc": {"label": "Austérité CRC-compatible (10/12/15/1)",
                              "v": (10, 12, 15, 1)},
            "priorite_commerce": {"label": "Priorité commerçants (15/20/20/5, concertation haute)",
                                  "v": (15, 20, 20, 5)},
            "jo_bis": {"label": "Ambition JO bis (50/10/10/2 — tout sur pistes)",
                       "v": (50, 10, 10, 2)},
        },

        # === Labels UI leviers ===
        "leviers_labels": [
            "Pistes neuves (M€)",
            "Maintenance réseau (M€)",
            "Contribution Agemob/Vélib (M€)",
            "Concertation + accessibilité (M€)",
        ],
    }
    return (CFG,)


@app.cell
def __fetch_trame(CFG):
    """Snapshot de la Trame lu depuis CFG (v7 refactor)."""
    trame = CFG["trame"]
    return (trame,)


@app.cell
def __a11y_styles(mo):
    """R32 P1.7 — styles d'accessibilité injectés une fois au chargement.

    - .sr-only : masque visuellement tout en restant annonçable par les lecteurs d'écran.
    - :focus-visible : contour orange Tawiza 3px sur tous les interactifs (R32).
    - .tawiza-skip-link : skip-link visible uniquement au focus clavier.
    """
    mo.Html("""
    <style>
      .sr-only {
        position: absolute !important;
        width: 1px !important;
        height: 1px !important;
        padding: 0 !important;
        margin: -1px !important;
        overflow: hidden !important;
        clip: rect(0, 0, 0, 0) !important;
        white-space: nowrap !important;
        border: 0 !important;
      }
      /* R32 P1.7 — focus visible renforcé, palette Tawiza */
      a:focus-visible,
      button:focus-visible,
      input:focus-visible,
      select:focus-visible,
      textarea:focus-visible,
      [role="button"]:focus-visible,
      [tabindex]:focus-visible,
      .marimo-ui-dropdown:focus-visible,
      marimo-slider:focus-visible,
      marimo-button:focus-visible,
      marimo-dropdown:focus-visible {
        outline: 3px solid #b45309 !important;
        outline-offset: 2px !important;
        border-radius: 3px;
      }
    </style>
    """)
    return


@app.cell
def __header(mo, trame):
    mo.Html(f"""
    <div style="background: linear-gradient(135deg, #fafaf9, #fff); padding: 24px 28px;
         border-radius: 10px; border-left: 6px solid #b45309; margin-bottom: 20px;">
      <h1 style="font-family: El Messiri, serif; font-size: 28px; color: #1D3557;
           font-weight: 700; margin: 0 0 8px 0;">
        Simulateur Paris vélo 2026-2031
      </h1>
      <div style="font-size: 14px; color: #6C757D; line-height: 1.6;">
        <b>Tu pilotes la Ville pendant 5 ans.</b> Charge un preset politique ou répartis
        librement 80 M€ entre 4 leviers. Provoque les événements pour tester les crises.
        Joue avec les 5 voix qui réagissent à tes choix.
      </div>
      <div style="margin-top: 14px; padding: 10px 14px; background: #fff; border-radius: 4px;
           border: 1px solid #e9ecef; font-size: 12px; color: #6C757D;
           font-family: JetBrains Mono, monospace;">
        <b style="color: #b45309;">⧖ La Trame, dernière lecture :</b>
        {trame['updated_at']} · valid jusqu'au {trame['valid_until']} ·
        <b>{trame['n_signaux']}</b> fils suivis · doctrine {trame['doctrine_version']} ·
        <a href="/methode/" style="color: #b45309;">lire la méthode</a>
      </div>
    </div>
    """)
    return


@app.cell
def __carte_signaux(mo, trame):
    _critiques_html = ""
    for _s in trame.get("signaux_critiques", []):
        _critiques_html += (
            f'<div style="padding: 10px 14px; background: #fff; border-left: 3px solid #C1554D; '
            f'border-radius: 3px; margin-bottom: 8px;">'
            f'<div style="font-size: 13px; color: #1D3557;"><b>{_s["etat"]} {_s["label"]}</b></div>'
            f'<div style="font-size: 12px; color: #6C757D; margin-top: 2px;">{_s["lecture"]}</div>'
            f'</div>'
        )

    _boucle = trame.get("boucle_active", "")
    _boucle_html = ""
    if _boucle:
        _boucle_html = (
            f'<div style="padding: 10px 14px; background: #C1554D15; border: 1px dashed #C1554D; '
            f'border-radius: 4px; margin-top: 10px;">'
            f'<div style="font-size: 12px; color: #C1554D; font-weight: 600;">⚠ Boucle cumulative active</div>'
            f'<div style="font-size: 12px; color: #1D3557; margin-top: 4px;">{_boucle}</div>'
            f'</div>'
        )

    _bt = trame.get("backtest", {})
    _bt_html = ""
    if _bt:
        _bt_html = (
            f'<div style="padding: 10px 14px; background: #fafaf9; border-left: 3px solid #457B9D; '
            f'border-radius: 3px; margin-top: 10px; font-size: 12px; color: #1D3557;">'
            f'<b>Backtest rétrospectif</b> — {_bt["vu_juste"]}/{_bt["total"]} fils vus juste, '
            f'latence moyenne {_bt["latence_moyenne_mois"]} mois. '
            f'<span style="color: #6C757D;">(Ces chiffres ne seront jamais optimisés — R20)</span>'
            f'</div>'
        )

    mo.Html(f"""
    <details style="margin: 16px 0;">
      <summary style="cursor: pointer; font-family: El Messiri, serif; font-size: 17px;
               color: #1D3557; padding: 10px 14px; background: #fafaf9; border-radius: 4px;">
        <b>📍 État actuel du terrain</b> — ce que la Trame Tawiza voit aujourd'hui
      </summary>
      <div style="padding: 14px 4px;">
        <div style="font-size: 12px; color: #6C757D; margin-bottom: 10px;">
          Le simulateur démarre avec ces valeurs réelles. Le monde simulé hérite du monde observé.
        </div>
        {_critiques_html}
        {_boucle_html}
        {_bt_html}
      </div>
    </details>
    """)
    return


@app.cell
def __state(mo, CFG):
    _init = CFG["etat_initial"]
    _annee_init = CFG["annee_depart"]
    get_state, set_state = mo.state({
        "annee": _annee_init,
        "km_realises": _init["km_realises"],
        "dette_mdeur": _init["dette_mdeur"],
        "notation": _init["notation"],
        "usage_index": _init["usage_index"],
        "lobby_cyclo": _init["lobby_cyclo"],
        "capital_politique": _init["capital_politique"],
        "historique": [
            {"annee": _annee_init - 1, "km": _init["km_realises"],
             "dette": _init["dette_mdeur"], "budget_vote": 20,
             "event": "État initial"},
        ],
        "events_tires": [],
        "forced_event": None,
        # v6 — Branches narratives
        "ans_capital_bas": 0,
        "ans_concert_elevee": 0,
        "branche_active": None,
        "cumul_concertation": 0,
    })
    return get_state, set_state


@app.cell
def __constants(CFG, trame):
    """Lecture depuis CFG + modulation des events par l'état de la Trame."""
    OBJECTIF_KM = CFG["objectif_km"]
    COUT_MOYEN_KM_MEUR = CFG["cout_moyen_km_meur"]
    ANNEE_FIN = CFG["annee_fin"]
    ARRONDISSEMENTS = CFG["arrondissements"]
    PRESETS = CFG["presets"]

    # Modulation des probabilités selon signaux critiques de la Trame
    _critiques_ids = {_s["id"] for _s in trame.get("signaux_critiques", [])}
    _plf_rouge = "plf_2026_velo" in _critiques_ids
    _bp_rouge = "bp_paris_velo_2026" in _critiques_ids

    EVENTS = []
    for _ev in CFG["events_base"]:
        _proba = _ev["proba"]
        if _bp_rouge and "proba_if_bp_rouge" in _ev:
            _proba = _ev["proba_if_bp_rouge"]
        elif _plf_rouge and "proba_if_plf_rouge" in _ev:
            _proba = _ev["proba_if_plf_rouge"]
        EVENTS.append({"id": _ev["id"], "label": _ev["label"],
                       "effet": _ev["effet"], "proba": _proba})
    return ANNEE_FIN, ARRONDISSEMENTS, COUT_MOYEN_KM_MEUR, EVENTS, OBJECTIF_KM, PRESETS


@app.cell
def __arrondissement_ui(mo, ARRONDISSEMENTS):
    # Pattern robuste : liste de labels + reverse lookup dans cellule séparée
    _labels = [_v["label"] for _v in ARRONDISSEMENTS.values()]
    arrondissement_ui = mo.ui.dropdown(
        options=_labels,
        value=_labels[0],
        label="🗺️ Périmètre géographique",
    )
    return (arrondissement_ui,)


@app.cell
def __arrondissement(arrondissement_ui, ARRONDISSEMENTS):
    """Reverse lookup : label visible → internal key."""
    arrondissement = next(
        (_k for _k, _v in ARRONDISSEMENTS.items() if _v["label"] == arrondissement_ui.value),
        list(ARRONDISSEMENTS.keys())[0],
    )
    return (arrondissement,)


@app.cell
def __arrondissement_display(mo, arrondissement_ui, arrondissement, ARRONDISSEMENTS):
    _info = ARRONDISSEMENTS[arrondissement]
    _mult = _info["cout_mult"]
    _couleur = "#C1554D" if _mult > 1.2 else "#A8832E" if _mult > 1.0 else "#2D6A4F"

    # R32 P1.2 — aide contextuelle pour lecteur d'écran (aria-describedby)
    _aide_arr = (
        f"Choisir un périmètre géographique parmi 5 options. "
        f"Sélection actuelle : {_info['label']}. {_info['description']}. "
        f"Coût par kilomètre multiplié par {_mult:.2f}, concertation utile "
        f"à partir de {_info['concert_requise']} millions d'euros."
    )
    mo.Html(
        f'<p id="arr-help" class="sr-only" '
        f'style="position:absolute;left:-10000px;top:auto;width:1px;height:1px;overflow:hidden;">'
        f'{_aide_arr}</p>'
    )
    mo.hstack([arrondissement_ui], justify="start")
    mo.Html(f"""
    <div role="note" aria-describedby="arr-help"
         style="margin-top: 6px; padding: 8px 14px; background: #fafaf9; border-left: 3px solid {_couleur};
         border-radius: 3px; font-size: 12px; color: #6C757D;">
      <b style="color: #1D3557;">{_info['label']}</b> · coût/km ×{_mult:.2f} · concertation utile ≥ {_info['concert_requise']} M€<br/>
      <i>{_info['description']}</i>
    </div>
    """)
    return


@app.cell
def __preset_ui(mo, PRESETS):
    _labels = [_v["label"] for _v in PRESETS.values()]
    preset_ui = mo.ui.dropdown(
        options=_labels,
        value=_labels[0],
        label="🎭 Scénario politique préconfiguré",
    )
    return (preset_ui,)


@app.cell
def __preset(preset_ui, PRESETS):
    """Reverse lookup."""
    preset = next(
        (_k for _k, _v in PRESETS.items() if _v["label"] == preset_ui.value),
        list(PRESETS.keys())[0],
    )
    return (preset,)


@app.cell
def __preset_display(mo, preset_ui, preset, PRESETS):
    # R32 P1.2 — aide contextuelle pour lecteur d'écran (aria-describedby)
    _p = PRESETS[preset]
    _v = _p["v"]
    _aide_preset = (
        f"Scénario politique préconfiguré. Sélection actuelle : {_p['label']}. "
        f"Répartition des 4 leviers : pistes {_v[0]} M€, maintenance {_v[1]} M€, "
        f"Vélib {_v[2]} M€, concertation {_v[3]} M€. "
        f"Ce choix charge automatiquement les 4 sliders budget."
    )
    mo.Html(
        f'<p id="preset-help" class="sr-only" '
        f'style="position:absolute;left:-10000px;top:auto;width:1px;height:1px;overflow:hidden;">'
        f'{_aide_preset}</p>'
    )
    mo.hstack([preset_ui], justify="start")
    return


@app.cell
def __levers_ui(mo, get_state, preset, PRESETS):
    _etat = get_state()
    _annee = _etat["annee"]
    _v = PRESETS[preset]["v"]  # preset est une internal key (string)

    pistes = mo.ui.slider(
        start=0, stop=80, value=_v[0], step=2,
        label=f"[Année {_annee}] Pistes neuves (M€)", show_value=True,
    )
    maintenance = mo.ui.slider(
        start=0, stop=40, value=_v[1], step=1,
        label=f"[Année {_annee}] Maintenance réseau (M€)", show_value=True,
    )
    velib = mo.ui.slider(
        start=0, stop=40, value=_v[2], step=1,
        label=f"[Année {_annee}] Contribution Agemob/Vélib (M€)", show_value=True,
    )
    concertation = mo.ui.slider(
        start=0, stop=10, value=_v[3], step=0.5,
        label=f"[Année {_annee}] Concertation + accessibilité (M€)", show_value=True,
    )
    return concertation, maintenance, pistes, velib


@app.cell
def __levers_display(mo, pistes, maintenance, velib, concertation):
    _total = pistes.value + maintenance.value + velib.value + concertation.value

    if _total > 80:
        _couleur, _msg = "#C1554D", f"⚠ Dépassement : {_total:.0f} M€ sur 80 M€ plafond"
    elif _total < 60:
        _couleur, _msg = "#A8832E", f"🟡 Sous-allocation : {_total:.0f} M€ (tu laisses du budget)"
    else:
        _couleur, _msg = "#2D6A4F", f"✓ Allocation : {_total:.0f} M€ / 80 M€"

    # R32 P1.3 — live region qui annonce le total à chaque mouvement de slider
    _live_msg = (
        f"Pistes : {pistes.value:.0f} M€ sur 80 plafond. "
        f"Maintenance : {maintenance.value:.0f} M€. "
        f"Vélib : {velib.value:.0f} M€. "
        f"Concertation : {concertation.value:.1f} M€. "
        f"Total alloué : {_total:.0f} M€ sur 80."
    )

    mo.vstack([
        pistes, maintenance, velib, concertation,
        mo.Html(f'<div style="color:{_couleur}; font-weight:600; margin:8px 0;">{_msg}</div>'),
        mo.Html(
            f'<div aria-live="polite" aria-atomic="true" role="status" '
            f'style="position:absolute;left:-10000px;top:auto;width:1px;height:1px;overflow:hidden;">'
            f'{_live_msg}</div>'
        ),
    ])
    return


@app.cell
def __provoquer_ui(mo):
    # R32 P0.6 : texte explicite (pas emoji seul) + tonalité préfixée pour lecteur d'écran
    provo_moodys = mo.ui.button(label="⚠ Alerte — Moody's dégrade", kind="danger")
    provo_accident = mo.ui.button(label="⚠ Alerte — accident grave Rivoli", kind="danger")
    provo_cper = mo.ui.button(label="✓ Opportunité — avenant CPER +50 M€", kind="success")
    provo_canicule = mo.ui.button(label="● Choc — canicule usage vélo", kind="neutral")
    return provo_accident, provo_canicule, provo_cper, provo_moodys


@app.cell
def __provoquer_display(mo, provo_moodys, provo_accident, provo_cper, provo_canicule):
    mo.Html("""
    <div style="margin-top: 14px; padding: 10px 14px; background: #fafaf9; border-radius: 4px;
         font-size: 12px; color: #6C757D;">
      <b>Provoque un événement</b> — teste ton scénario face à une crise ou une opportunité.
      Le prochain tour intègre l'événement forcé en plus du tirage aléatoire.
    </div>
    """)
    mo.hstack([provo_moodys, provo_accident, provo_cper, provo_canicule], justify="start")
    return


@app.cell
def __avance_button(mo, get_state, ANNEE_FIN):
    _etat = get_state()
    _fin = _etat["annee"] > ANNEE_FIN
    _label = "↺ Recommencer (nouveau tirage)" if _fin else f"Avance → {_etat['annee']+1}"
    avance_btn = mo.ui.button(label=_label, kind="success")
    return (avance_btn,)


@app.cell
def __avance_display(mo, avance_btn):
    mo.hstack([avance_btn], justify="center")
    return


@app.cell
def __tick(avance_btn, get_state, set_state, pistes, maintenance, velib,
           concertation, EVENTS, COUT_MOYEN_KM_MEUR, ANNEE_FIN, OBJECTIF_KM,
           provo_moodys, provo_accident, provo_cper, provo_canicule,
           arrondissement, ARRONDISSEMENTS):
    """Wrap la logique dans une fonction interne pour permettre early returns
    sans casser marimo WASM (Bug 14 catalogue Forgeron)."""
    import random as _random

    def _process_tick():
        _ = avance_btn.value
        _etat = get_state()
        _arr = ARRONDISSEMENTS[arrondissement]
        _cout_effectif = COUT_MOYEN_KM_MEUR * _arr["cout_mult"]
        _concert_requise = _arr["concert_requise"]

        # Bug 16 : les .value peuvent être None au chargement initial marimo WASM
        _avance_count = avance_btn.value or 0

        _forced_id = None
        _provo_counts = [
            ("moodys_warning", provo_moodys.value or 0),
            ("accident_grave", provo_accident.value or 0),
            ("cper_avenant", provo_cper.value or 0),
            ("canicule", provo_canicule.value or 0),
        ]
        _max_provo = max((_v for _, _v in _provo_counts), default=0)
        _last_provo = _etat.get("last_provo_count") or 0
        if _max_provo > _last_provo:
            for _id, _v in _provo_counts:
                if _v == _max_provo:
                    _forced_id = _id
                    break

        # Reset si dépassé ANNEE_FIN et click
        if _etat["annee"] > ANNEE_FIN and _avance_count > 0:
            set_state({
                "annee": 2026, "km_realises": 72, "dette_mdeur": 9.4,
                "notation": "AA-", "usage_index": 100, "lobby_cyclo": 1.0,
                "capital_politique": 100,
                "historique": [{"annee": 2025, "km": 72, "dette": 9.4,
                                "budget_vote": 20, "event": "État initial"}],
                "events_tires": [],
                "last_provo_count": _max_provo,
            })
            return

        if _avance_count == 0:
            return

        # Bug 16 : sliders aussi peuvent être None au tout premier run
        _p = pistes.value or 20
        _m = maintenance.value or 15
        _v_val = velib.value or 20
        _c = concertation.value or 2

        # Km posés = pistes / coût effectif
        _km_ajoutes = _p / _cout_effectif
        _km_nouveau = _etat["km_realises"] + _km_ajoutes

        _usage_delta = 2 if _m >= 10 else -3
        _usage_delta += 1 if _v_val >= 15 else -2
        _usage_delta += int(_km_ajoutes / 2)
        _nouvel_usage = max(60, min(180, _etat["usage_index"] + _usage_delta))

        _cap_delta = int(_c * 2) - 2
        if _c < _concert_requise and _p > 25:
            _cap_delta -= 8
        if _p > 35 and _c < 3:
            _cap_delta -= 5
        _nouveau_cap = max(0, min(150, _etat["capital_politique"] + _cap_delta))

        _total = _p + _m + _v_val + _c
        _dette_delta = (_total - 60) * 0.005
        _nouvelle_dette = max(0, _etat["dette_mdeur"] + _dette_delta)

        _lobby_delta = (_km_ajoutes - 15) * 0.02
        _nouveau_lobby = max(0.3, min(2.0, _etat["lobby_cyclo"] + _lobby_delta))

        _event_tire = None
        if _forced_id:
            for _ev in EVENTS:
                if _ev["id"] == _forced_id:
                    _event_tire = _ev
                    break
        else:
            _random.seed(hash((_etat["annee"], _avance_count)) & 0xFFFFFFFF)
            _event_roll = _random.random()
            _cumul = 0
            for _ev in EVENTS:
                _cumul += _ev["proba"]
                if _event_roll < _cumul:
                    _event_tire = _ev
                    break

        _event_label = "RAS"
        _etat_notation = _etat["notation"]
        if _event_tire:
            _event_label = _event_tire["label"] + (" (provoqué)" if _forced_id else "")
            _effet = _event_tire["effet"]
            if "usage_index" in _effet:
                _nouvel_usage += _effet["usage_index"]
            if "notation_risk" in _effet:
                _scale = ["AAA", "AA+", "AA", "AA-", "A+", "A", "A-", "BBB+"]
                if _etat["notation"] in _scale:
                    _idx = _scale.index(_etat["notation"])
                    _etat_notation = _scale[min(_idx + 1, len(_scale) - 1)]
            if "lobby_cyclo" in _effet:
                _nouveau_lobby = max(0.3, _nouveau_lobby + _effet["lobby_cyclo"])
            if "capital_politique" in _effet:
                _nouveau_cap = max(0, min(150, _nouveau_cap + _effet["capital_politique"]))
            if "budget_bonus" in _effet:
                _km_ajoutes += _effet["budget_bonus"] / _cout_effectif
                _km_nouveau = _etat["km_realises"] + _km_ajoutes
            if "dette_cout" in _effet:
                _nouvelle_dette += _effet["dette_cout"] * 0.1

        _ans_cap_bas = _etat.get("ans_capital_bas", 0) + (1 if _nouveau_cap < 40 else 0)
        if _nouveau_cap >= 40:
            _ans_cap_bas = 0
        _cumul_concert = _etat.get("cumul_concertation", 0) + _c
        _ans_concert_elevee = _etat.get("ans_concert_elevee", 0) + (1 if _c >= 5 else 0)
        if _c < 5:
            _ans_concert_elevee = 0

        _branche = _etat.get("branche_active")
        _branche_event = None
        if _branche is None:
            if _ans_cap_bas >= 2:
                _branche = "demission"
                _branche_event = "🔔 Démission du maire : capital politique < 40 pendant 2 ans consécutifs"
                _nouveau_cap = min(150, _nouveau_cap + 30)
            elif _ans_concert_elevee >= 3 and _cumul_concert > 25:
                _branche = "mouvement_citoyen"
                _branche_event = "🌱 Naissance d'un mouvement citoyen Plan Vélo (3 ans concert ≥ 5 M€)"
                _nouveau_lobby = min(2.0, _nouveau_lobby + 0.3)

        _events_list = _etat["events_tires"] + [(_etat["annee"], _event_label)]
        if _branche_event:
            _events_list.append((_etat["annee"], _branche_event))

        _nouvel_historique = _etat["historique"] + [{
            "annee": _etat["annee"], "km": round(_km_nouveau, 1),
            "dette": round(_nouvelle_dette, 2), "budget_vote": _total,
            "event": _event_label, "usage": _nouvel_usage, "capital": _nouveau_cap,
        }]

        set_state({
            "annee": _etat["annee"] + 1,
            "km_realises": _km_nouveau, "dette_mdeur": _nouvelle_dette,
            "notation": _etat_notation, "usage_index": _nouvel_usage,
            "lobby_cyclo": _nouveau_lobby, "capital_politique": _nouveau_cap,
            "historique": _nouvel_historique,
            "events_tires": _events_list,
            "last_provo_count": _max_provo,
            "ans_capital_bas": _ans_cap_bas,
            "ans_concert_elevee": _ans_concert_elevee,
            "branche_active": _branche,
            "cumul_concertation": _cumul_concert,
        })

    _process_tick()
    return


@app.cell
def __dashboard(mo, get_state, ANNEE_FIN):
    _etat = get_state()
    _annee = _etat["annee"]
    _km, _dette = _etat["km_realises"], _etat["dette_mdeur"]
    _usage, _lobby = _etat["usage_index"], _etat["lobby_cyclo"]
    _cap, _notation = _etat["capital_politique"], _etat["notation"]

    def _color(val, green, yellow, plus_mieux=True):
        if plus_mieux:
            return "#2D6A4F" if val >= green else "#A8832E" if val >= yellow else "#C1554D"
        return "#2D6A4F" if val <= green else "#A8832E" if val <= yellow else "#C1554D"

    _signaux = [
        ("KM POSÉS", f"{_km:.0f} / 180", _color(_km, 150, 100, True)),
        ("DETTE", f"{_dette:.1f} Md€", _color(_dette, 10, 12, False)),
        ("NOTATION", _notation,
         "#2D6A4F" if _notation in ["AAA", "AA+", "AA"]
         else "#A8832E" if _notation in ["AA-", "A+"] else "#C1554D"),
        ("USAGE", f"{_usage:.0f}", _color(_usage, 120, 90, True)),
        ("LOBBY CYCLO", f"{_lobby:.2f}", _color(_lobby, 1.2, 0.8, True)),
        ("CAPITAL POLIT.", f"{_cap:.0f}", _color(_cap, 100, 60, True)),
    ]

    # R32 P0.3 : icône + aria-label pour redondance à la couleur (pas couleur seule)
    def _status_label(c):
        if c == "#2D6A4F":
            return ("●", "en bon état")
        elif c == "#A8832E":
            return ("◐", "à surveiller")
        return ("▲", "en alerte")

    _cards_html = []
    for _lbl, _v, _c in _signaux:
        _icon, _state = _status_label(_c)
        _cards_html.append(
            f'<div role="status" aria-label="{_lbl} {_v}, {_state}" '
            f'style="padding: 12px 14px; background: #fafaf9; border-top: 3px solid {_c}; '
            f'border-radius: 4px; min-width: 110px; flex: 1;">'
            f'<div style="font-size: 9px; color: #6C757D; letter-spacing: 0.06em;">'
            f'<span aria-hidden="true" style="color: {_c}; margin-right: 4px;">{_icon}</span>'
            f'{_lbl}</div>'
            f'<div style="font-family: El Messiri, serif; font-size: 20px; color: {_c}; '
            f'font-weight: 700; margin-top: 4px;">{_v}</div>'
            f'<div class="visually-hidden" style="position:absolute;left:-10000px;">{_state}</div>'
            f'</div>'
        )
    _cards = "".join(_cards_html)

    _status = (f"Année {_annee - 1} terminée" if _annee > ANNEE_FIN
               else f"Année {_annee} — décide puis avance")

    mo.Html(f"""
    <div style="margin: 16px 0;">
      <div style="font-family: El Messiri, serif; font-size: 18px; color: #1D3557; margin-bottom: 10px;">
        <b>Tableau de bord — {_status}</b>
      </div>
      <div style="display: flex; gap: 8px; flex-wrap: wrap;">{_cards}</div>
    </div>
    """)
    return


@app.cell
def __chart_history(mo, get_state):
    import plotly.graph_objects as _go

    _etat = get_state()
    _h = _etat["historique"]
    _annees = [_r["annee"] for _r in _h]
    _kms = [_r["km"] for _r in _h]
    _dettes = [_r["dette"] for _r in _h]

    _fig = _go.Figure()
    _fig.add_trace(_go.Scatter(x=_annees, y=_kms, mode="lines+markers",
                              name="Km posés", line=dict(color="#b45309", width=3),
                              yaxis="y1"))
    _fig.add_trace(_go.Scatter(x=_annees, y=_dettes, mode="lines+markers",
                              name="Dette (Md€)", line=dict(color="#C1554D", width=2, dash="dot"),
                              yaxis="y2"))
    _fig.add_hline(y=180, line_dash="dash", line_color="#2D6A4F", yref="y1",
                   annotation_text="Objectif 180 km", annotation_position="top right",
                   annotation_font=dict(size=10, color="#2D6A4F"))
    _fig.update_layout(
        title=dict(text="<b>Ton histoire jusqu'ici</b>", x=0.02, xanchor="left",
                   font=dict(size=14, family="El Messiri")),
        xaxis=dict(title="Année", tickmode="linear", dtick=1),
        yaxis=dict(title="Km", side="left", range=[0, 220]),
        yaxis2=dict(title="Dette (Md€)", overlaying="y", side="right",
                    showgrid=False, range=[0, 15]),
        font=dict(family="Inter", size=11, color="#1D3557"),
        plot_bgcolor="#fafaf9", paper_bgcolor="#fafaf9",
        height=300, margin=dict(l=50, r=50, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=-0.22, xanchor="left", x=0),
    )

    # R32 P1.1 — description textuelle alternative du graphique pour lecteurs d'écran
    _km_debut, _km_fin = _kms[0], _kms[-1]
    _dette_debut, _dette_fin = _dettes[0], _dettes[-1]
    if _km_fin > _km_debut + 5:
        _trend_km = "ascendante"
    elif _km_fin < _km_debut - 5:
        _trend_km = "descendante"
    else:
        _trend_km = "plate"
    if _dette_fin > _dette_debut + 0.5:
        _trend_dette = "en hausse"
    elif _dette_fin < _dette_debut - 0.5:
        _trend_dette = "en baisse"
    else:
        _trend_dette = "stable"
    _desc_hist = (
        f"Courbe des kilomètres posés en orange, tendance {_trend_km} "
        f"de {_km_debut:.0f} à {_km_fin:.0f} km entre {_annees[0]} et {_annees[-1]}. "
        f"Courbe de la dette en rouge pointillé, {_trend_dette} "
        f"de {_dette_debut:.1f} à {_dette_fin:.1f} milliards d'euros. "
        f"Ligne verte horizontale marque l'objectif 180 km."
    )
    mo.Html(
        f'<figure role="figure" aria-labelledby="cap-history" '
        f'style="margin: 0;">'
        f'<figcaption id="cap-history" class="sr-only">{_desc_hist}</figcaption>'
        f'</figure>'
    )
    mo.ui.plotly(_fig)
    return


@app.cell
def __chart_spirale(mo, get_state):
    """Spirale du désengagement en temps réel — les 4 nœuds s'allument selon l'état."""
    import plotly.graph_objects as _go

    _etat = get_state()
    _km = _etat["km_realises"]
    _cap = _etat["capital_politique"]
    _lobby = _etat["lobby_cyclo"]
    _dette = _etat["dette_mdeur"]

    # Évaluation de chaque nœud (rouge = en alerte, vert = OK)
    _noeuds = [
        ("Budget\nvélo", _km >= 100),   # OK si au-dessus
        ("Capital\npolitique", _cap >= 70),
        ("Lobby\ncyclo", _lobby >= 0.8),
        ("Dette\ntaux", _dette <= 11),
    ]

    # Positionnement circulaire
    import math
    _positions = [(math.cos(i * math.pi / 2), math.sin(i * math.pi / 2)) for i in range(4)]

    _fig = _go.Figure()

    # Flèches circulaires entre les nœuds
    for _i in range(4):
        _x1, _y1 = _positions[_i]
        _x2, _y2 = _positions[(_i + 1) % 4]
        _actif_i = not _noeuds[_i][1]
        _couleur_arrow = "#C1554D" if _actif_i else "#DEE2E6"
        _fig.add_annotation(
            x=_x2 * 0.72, y=_y2 * 0.72,
            ax=_x1 * 0.72, ay=_y1 * 0.72,
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=2, arrowsize=1.2, arrowwidth=2.5,
            arrowcolor=_couleur_arrow,
        )

    # Nœuds
    _colors = ["#2D6A4F" if _ok else "#C1554D" for _, _ok in _noeuds]
    _labels = [_l for _l, _ in _noeuds]
    _fig.add_trace(_go.Scatter(
        x=[_p[0] for _p in _positions],
        y=[_p[1] for _p in _positions],
        mode="markers+text",
        marker=dict(size=95, color=_colors, line=dict(color="#1D3557", width=2)),
        text=_labels,
        textposition="middle center",
        textfont=dict(family="Inter", size=11, color="white", weight="bold"),
        hoverinfo="text", hovertext=_labels,
    ))

    _n_rouges = sum(1 for _, _ok in _noeuds if not _ok)
    _titre = "<b>Spirale du désengagement</b>"
    if _n_rouges >= 3:
        _titre += f" — <span style='color:#C1554D'>activée ({_n_rouges}/4 rouges)</span>"
    elif _n_rouges >= 2:
        _titre += f" — <span style='color:#A8832E'>à surveiller ({_n_rouges}/4)</span>"
    else:
        _titre += " — <span style='color:#2D6A4F'>sous contrôle</span>"

    _fig.update_layout(
        title=dict(text=_titre, x=0.02, xanchor="left",
                   font=dict(size=14, family="El Messiri")),
        xaxis=dict(visible=False, range=[-1.5, 1.5]),
        yaxis=dict(visible=False, range=[-1.5, 1.5], scaleanchor="x"),
        plot_bgcolor="#fafaf9", paper_bgcolor="#fafaf9",
        height=280, margin=dict(l=20, r=20, t=50, b=20),
        showlegend=False,
    )

    # R32 P1.1 — description textuelle alternative
    _labels_noeuds = ["Budget vélo", "Capital politique", "Lobby cyclo", "Dette/taux"]
    _etats_noeuds = [
        f"{_lbl} {'OK' if _ok else 'en alerte'}"
        for _lbl, (_, _ok) in zip(_labels_noeuds, _noeuds)
    ]
    _desc_spirale = (
        f"Diagramme circulaire à 4 nœuds représentant la spirale du désengagement. "
        f"État actuel : {', '.join(_etats_noeuds)}. "
        f"{_n_rouges} nœud(s) en alerte sur 4. "
        f"Les flèches rouges entre nœuds en alerte indiquent un renforcement mutuel."
    )
    mo.Html(
        f'<figure role="figure" aria-labelledby="cap-spirale" style="margin: 0;">'
        f'<figcaption id="cap-spirale" class="sr-only">{_desc_spirale}</figcaption>'
        f'</figure>'
    )
    mo.ui.plotly(_fig)
    return


@app.cell
def __chart_radar(mo, get_state):
    """Radar des 6 dimensions du pilotage — voir l'équilibre instantané."""
    import plotly.graph_objects as _go

    _etat = get_state()
    _km = _etat["km_realises"]
    _dette = _etat["dette_mdeur"]
    _usage = _etat["usage_index"]
    _lobby = _etat["lobby_cyclo"]
    _cap = _etat["capital_politique"]
    _notation = _etat["notation"]

    _notation_score = {"AAA": 100, "AA+": 90, "AA": 80, "AA-": 70,
                       "A+": 60, "A": 50, "A-": 40, "BBB+": 30}.get(_notation, 50)

    _axes = ["Km\n/objectif", "Soutenabilité\ndette", "Usage", "Lobby", "Capital\npolitique", "Notation"]
    _valeurs = [
        min(100, _km / 180 * 100),
        max(0, 100 - (_dette - 9.4) * 15),
        min(100, _usage / 180 * 100),
        min(100, _lobby / 2 * 100),
        min(100, _cap / 150 * 100),
        _notation_score,
    ]

    _fig = _go.Figure()
    _fig.add_trace(_go.Scatterpolar(
        r=_valeurs + [_valeurs[0]],
        theta=_axes + [_axes[0]],
        fill="toself",
        line=dict(color="#b45309", width=2),
        fillcolor="rgba(180, 83, 9, 0.2)",
        name="Ton scénario",
        hovertemplate="<b>%{theta}</b><br>%{r:.0f}/100<extra></extra>",
    ))
    _fig.add_trace(_go.Scatterpolar(
        r=[50] * 7,
        theta=_axes + [_axes[0]],
        mode="lines",
        line=dict(color="#DEE2E6", width=1, dash="dot"),
        name="Zone 'à surveiller'",
        hoverinfo="skip",
    ))

    _fig.update_layout(
        title=dict(text="<b>Radar des 6 dimensions</b> — équilibre instantané",
                   x=0.02, xanchor="left", font=dict(size=14, family="El Messiri")),
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], showticklabels=False,
                            gridcolor="rgba(29,53,87,.08)"),
            angularaxis=dict(tickfont=dict(family="Inter", size=10, color="#1D3557")),
            bgcolor="#fafaf9",
        ),
        paper_bgcolor="#fafaf9",
        height=320, margin=dict(l=60, r=60, t=50, b=30),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5,
                    font=dict(size=10)),
    )

    # R32 P1.1 — description textuelle alternative
    _axes_lisibles = ["Km/objectif", "Soutenabilité dette", "Usage", "Lobby cyclo",
                      "Capital politique", "Notation"]
    _details = ", ".join(
        f"{_lbl} {int(_val)}/100"
        for _lbl, _val in zip(_axes_lisibles, _valeurs)
    )
    _desc_radar = (
        f"Radar à 6 axes en forme de polygone orange. Valeurs actuelles : {_details}. "
        f"Ligne pointillée grise marque la zone à surveiller (50/100 sur chaque axe)."
    )
    mo.Html(
        f'<figure role="figure" aria-labelledby="cap-radar" style="margin: 0;">'
        f'<figcaption id="cap-radar" class="sr-only">{_desc_radar}</figcaption>'
        f'</figure>'
    )
    mo.ui.plotly(_fig)
    return


@app.cell
def __events_log(mo, get_state):
    _etat = get_state()
    _events = _etat["events_tires"]
    if _events:
        _lines = "".join(
            f'<tr><td style="padding:4px 10px;font-family:JetBrains Mono;">{_a}</td>'
            f'<td style="padding:4px 10px;">{_lbl}</td></tr>'
            for _a, _lbl in _events
        )
        mo.Html(f"""
        <div style="margin: 16px 0;">
          <div style="font-family: El Messiri, serif; font-size: 15px; color: #1D3557; margin-bottom: 8px;">
            <b>Chronique des événements</b>
          </div>
          <table style="width:100%; border-collapse: collapse; font-size: 12px;">
            <thead><tr style="background:#fafaf9;">
              <th style="text-align:left; padding:6px 10px;">Année</th>
              <th style="text-align:left; padding:6px 10px;">Événement</th>
            </tr></thead>
            <tbody>{_lines}</tbody>
          </table>
        </div>
        """)
    else:
        mo.md("*Aucun événement tiré pour l'instant.*")
    return


@app.cell
def __voix(mo, get_state, pistes, concertation, maintenance):
    """Cinq voix adaptatives — Hamide, maire, FUB, PMR, livreur."""
    _etat = get_state()
    _usage, _cap = _etat["usage_index"], _etat["capital_politique"]
    _lobby, _annee = _etat["lobby_cyclo"], _etat["annee"]
    _km = _etat["km_realises"]

    # 1. Hamide — témoin rue de Rivoli
    if _usage > 130 and _km < 140:
        _hamide = ("Les pistes sont pleines mais le trottoir se rétrécit. "
                   "Je vois passer plus de vélos-cargo, c'est du boulot pour eux.")
    elif _usage < 90:
        _hamide = "Les pistes se vident. Même la nuit, il y avait plus de passage en 2025."
    elif pistes.value < 15 and _annee > 2027:
        _hamide = "Plus personne ne parle du plan vélo rue Rivoli. Ils posent des potelets."
    elif concertation.value >= 5:
        _hamide = "Y'a eu une réunion dans le local associatif. Ils avaient posé des cartes par terre."
    else:
        _hamide = "Moi je regarde passer. Ma question c'est les bancs publics, mais personne ne compte ça."

    # 2. Maire hypothétique
    if _cap > 110:
        _gregoire = "Notre plan tient. Les Parisiens voient les résultats."
    elif _cap > 70:
        _gregoire = "On arbitre serré. La doctrine tient, la mise en œuvre prend du retard."
    elif _cap > 40:
        _gregoire = "Il faut parler moins, faire plus. Le Conseil de Paris se tend."
    else:
        _gregoire = "Je suis fragilisé. La Chambre régionale revient sur la dette, on recentre."

    # 3. FUB
    if _lobby < 0.6:
        _fub = "Nos adhérents se désengagent. Paris n'est plus l'exemple."
    elif _lobby < 1.0:
        _fub = "Nous réclamons une accélération. La promesse doit tenir."
    elif _lobby > 1.5:
        _fub = "Nous nous félicitons du rythme. Paris redevient moteur national."
    else:
        _fub = "Nous observons. Le mandat continue."

    # 4. APF — usagère PMR
    if concertation.value >= 5:
        _apf = "Enfin. On nous a consultés sur la largeur des pistes. Trois mois trop tard mais consultés."
    elif maintenance.value < 8:
        _apf = "Les pistes se dégradent. Un trou sur la piste, c'est une chute pour moi."
    elif pistes.value > 30 and concertation.value < 3:
        _apf = "Les pistes se multiplient, la continuité non. Traverser reste le problème."
    else:
        _apf = "Nous attendons. L'accessibilité n'est toujours pas un critère du Plan Vélo."

    # 5. Livreur vélo-cargo
    if _usage > 130 and _km < 140:
        _livreur = "Les pistes sont pleines. Les pros comme moi tournent en rond."
    elif pistes.value > 35:
        _livreur = "Nouvelle piste rue de Turenne. On a gagné 8 minutes par tournée."
    elif _lobby > 1.3:
        _livreur = "Le syndicat des livreurs vélo a été reçu en mairie. Première fois."
    elif maintenance.value < 10:
        _livreur = "Ma remorque a fini son troisième pneu crevé ce mois. Les pistes sont foutues."
    else:
        _livreur = "Ma tournée, c'est encore 40% de trottoir pour tenir les délais."

    _annee_affichage = _annee - 1 if _annee > 2026 else 2026

    _voices = [
        ("HAMIDE — RUE DE RIVOLI · TÉMOIN", "#8B5E83", _hamide, "voix-hamide",
         "Témoignage de Hamide, témoin rue de Rivoli"),
        ("LE MAIRE (HYPOTHÉTIQUE)", "#b45309", _gregoire, "voix-maire",
         "Voix du maire hypothétique"),
        ("FUB — FÉDÉRATION DES USAGERS DU VÉLO", "#2D6A4F", _fub, "voix-fub",
         "Position de la FUB, fédération des usagers du vélo"),
        ("APF — USAGÈRE EN FAUTEUIL", "#457B9D", _apf, "voix-apf",
         "Témoignage d'une usagère APF en fauteuil roulant"),
        ("CARGO — LIVREUR VÉLO INDÉPENDANT", "#A8832E", _livreur, "voix-cargo",
         "Voix d'un livreur vélo-cargo indépendant"),
    ]

    # R32 P1.5 — figure + blockquote + figcaption pour les 5 voix
    _blocs = "".join(
        f'<figure role="figure" aria-label="{_aria}" '
        f'style="padding: 11px 15px; margin: 0; background: #fafaf9; border-left: 4px solid {_c}; '
        f'border-radius: 3px;">'
        f'<figcaption style="font-size: 10px; color: {_c}; font-weight: 600; letter-spacing: 0.05em;">'
        f'{_label}</figcaption>'
        f'<blockquote style="margin: 3px 0 0 0; font-size: 13px; color: #1D3557; font-style: italic;">'
        f'« {_txt} »</blockquote></figure>'
        for _label, _c, _txt, _id, _aria in _voices
    )

    mo.Html(f"""
    <div style="margin: 20px 0;">
      <div style="font-family: El Messiri, serif; font-size: 16px; color: #1D3557; margin-bottom: 10px;">
        <b>Cinq voix, année {_annee_affichage}</b>
        <span style="font-size: 11px; color: #6C757D; font-weight: 400;">
          — témoignages adaptatifs
        </span>
      </div>
      <div style="display: grid; gap: 8px;">{_blocs}</div>
    </div>
    """)
    return


@app.cell
def __twist(mo, get_state):
    """Twist narratif aléatoire selon l'état (sans early return — R-marimo WASM)."""
    import random as _random

    _etat = get_state()
    _annee = _etat["annee"]
    _in_range = 2026 < _annee <= 2031

    _show = False
    if _in_range:
        _random.seed(hash((_annee, _etat["km_realises"])) & 0xFFFFFFFF)
        _roll = _random.random()
        _show = _roll <= 0.35

    _twists_positifs = [
        "<b>Un lecteur Tawiza</b> te demande une interview. Tu acceptes ?",
        "<b>Une start-up vélo-cargo</b> ouvre 3 emplois à Stalingrad.",
        "<b>La RATP</b> annonce un partenariat Vélib' sur les métros sud.",
        "<b>Une étude publique</b> confirme 12% de baisse des particules fines sur axe Rivoli.",
    ]
    _twists_tensions = [
        "<b>Un conseiller LR</b> publie une tribune : « Pistes vides, rues encombrées ».",
        "<b>Le Canard</b> révèle un retard de paiement à un sous-traitant voirie.",
        "<b>Une pétition</b> des commerçants de la rue Turenne atteint 4 500 signatures.",
        "<b>Le Préfet</b> demande une clarification sur la ligne « Mobilités actives ».",
    ]
    _twists_neutres = [
        "<b>Paris Match</b> publie un portrait du nouveau chef de chantier voirie.",
        "<b>Un urbaniste</b> propose une carte alternative en open data.",
        "<b>Le Louvre</b> ferme son cycle de conférences sur la ville cyclable.",
    ]

    if _show:
        if _etat["capital_politique"] > 80:
            _pool = _twists_positifs + _twists_neutres
        elif _etat["capital_politique"] < 50:
            _pool = _twists_tensions + _twists_neutres
        else:
            _pool = _twists_positifs + _twists_tensions + _twists_neutres
        _t = _random.choice(_pool)
        mo.Html(f"""
        <div style="margin: 12px 0; padding: 12px 16px; background: #fff8e6; border: 1px dashed #D4A843;
             border-radius: 4px; font-size: 13px; color: #1D3557;">
          <span style="font-size: 10px; color: #A8832E; font-weight: 700; letter-spacing: 0.05em;">
            TWIST NARRATIF ALÉATOIRE — ANNÉE {_annee - 1}
          </span><br/>
          {_t}
        </div>
        """)
    else:
        mo.md("")
    return


@app.cell
def __branche_narrative(mo, get_state):
    """Affiche la branche narrative active si une a été déclenchée."""
    _etat = get_state()
    _branche = _etat.get("branche_active")
    if _branche == "demission":
        mo.Html("""
        <div style="padding: 14px 18px; background: linear-gradient(90deg, #8B5E8322, #fafaf9);
             border: 2px solid #8B5E83; border-radius: 6px; margin: 16px 0;">
          <div style="font-family: El Messiri, serif; font-size: 15px; color: #8B5E83; font-weight: 700;">
            🔔 Branche narrative : démission + nouveau maire
          </div>
          <div style="font-size: 12px; color: #1D3557; margin-top: 4px; line-height: 1.5;">
            Le maire a démissionné suite à 2 ans de capital politique très bas. Un nouveau maire
            prend la suite avec +30 capital politique "en dot" — mais il hérite de tes choix
            budgétaires. La suite te dira si ce nouveau souffle suffit ou si la Ville reste
            dans la spirale.
          </div>
        </div>
        """)
    elif _branche == "mouvement_citoyen":
        mo.Html("""
        <div style="padding: 14px 18px; background: linear-gradient(90deg, #2D6A4F22, #fafaf9);
             border: 2px solid #2D6A4F; border-radius: 6px; margin: 16px 0;">
          <div style="font-family: El Messiri, serif; font-size: 15px; color: #2D6A4F; font-weight: 700;">
            🌱 Branche narrative : mouvement citoyen né
          </div>
          <div style="font-size: 12px; color: #1D3557; margin-top: 4px; line-height: 1.5;">
            Un mouvement citoyen Plan Vélo s'est structuré après 3 ans de concertation soutenue
            (≥ 5 M€/an). Le lobby cyclo grimpe durablement de +0,3. Les prochains arbitrages
            auront un nouvel acteur organisé dans la boucle.
          </div>
        </div>
        """)
    else:
        mo.md("")
    return


@app.cell
def __boucle_alert(mo, get_state):
    _etat = get_state()
    _km, _usage = _etat["km_realises"], _etat["usage_index"]
    _cap, _lobby = _etat["capital_politique"], _etat["lobby_cyclo"]
    _annee = _etat["annee"]

    _desengagement = (_km < 130 and _lobby < 0.8 and _cap < 70) and _annee > 2028
    _saturation = (_usage > 140 and _km < 150) and _annee > 2028

    if _desengagement:
        # R32 P1.4 — région nommée pour navigation par landmarks
        mo.Html("""
        <section role="region" aria-labelledby="alert-desengagement"
             style="padding: 14px 18px; background: linear-gradient(90deg, #C1554D22, #fafaf9);
             border: 2px solid #C1554D; border-radius: 6px; margin: 16px 0;">
          <div id="alert-desengagement"
               style="font-family: El Messiri, serif; font-size: 15px; color: #C1554D; font-weight: 700;">
            <span aria-hidden="true">⚠ </span>Boucle cumulative activée : spirale du désengagement
          </div>
          <div style="font-size: 12px; color: #1D3557; margin-top: 4px;">
            Km sous cible + lobby affaibli + capital politique bas.
            Chaque baisse renforce la suivante.
          </div>
        </section>
        """)
    elif _saturation:
        mo.Html("""
        <section role="region" aria-labelledby="alert-saturation"
             style="padding: 14px 18px; background: linear-gradient(90deg, #D4A84322, #fafaf9);
             border: 2px solid #D4A843; border-radius: 6px; margin: 16px 0;">
          <div id="alert-saturation"
               style="font-family: El Messiri, serif; font-size: 15px; color: #A8832E; font-weight: 700;">
            <span aria-hidden="true">⚠ </span>Boucle cumulative activée : saturation dangereuse
          </div>
          <div style="font-size: 12px; color: #1D3557; margin-top: 4px;">
            Forte demande + réseau insuffisant. Risque accidentogène croissant.
          </div>
        </section>
        """)
    else:
        mo.md("")
    return


@app.cell
def __final_scorecard(mo, get_state, ANNEE_FIN, OBJECTIF_KM):
    _etat = get_state()
    if _etat["annee"] > ANNEE_FIN:
        _km, _dette = _etat["km_realises"], _etat["dette_mdeur"]
        _cap, _usage = _etat["capital_politique"], _etat["usage_index"]

        _s_km = min(100, int(_km / OBJECTIF_KM * 100))
        _s_fin = max(0, int(100 - (_dette - 9.4) * 15))
        _s_pol = int(_cap * 100 / 150)
        _s_usage = int(_usage / 180 * 100)
        _s_total = int(_s_km * 0.3 + _s_fin * 0.2 + _s_pol * 0.25 + _s_usage * 0.25)

        if _s_total >= 80:
            _titre = "Paris 2031 — ville-modèle cyclable"
            _verdict = "Un scénario rare : cible atteinte sans casser les équilibres."
            _couleur = "#2D6A4F"
        elif _s_total >= 60:
            _titre = "Paris 2031 — promesse maintenue"
            _verdict = "Rythme insuffisant, doctrine cohérente. Un successeur peut finir."
            _couleur = "#A8832E"
        elif _s_total >= 40:
            _titre = "Paris 2031 — Plan Vélo dilué"
            _verdict = "La promesse de 2021 est devenue une aspiration. L'usage tient par inertie."
            _couleur = "#E67E22"
        else:
            _titre = "Paris 2031 — abandon silencieux"
            _verdict = "Les chiffres sont durs. La spirale du désengagement était visible dès 2028."
            _couleur = "#C1554D"

        mo.Html(f"""
        <section role="region" aria-labelledby="scorecard-titre"
             style="margin: 24px 0; padding: 24px; background: linear-gradient(135deg, {_couleur}15, #fafaf9);
             border: 2px solid {_couleur}; border-radius: 10px; position: relative; overflow: hidden;">
          <!-- Filigrane anti-détournement (R33) : visible sur capture, responsive mobile -->
          <div aria-hidden="true" class="tw-watermark" style="position: absolute; top: 50%; left: 50%;
               transform: translate(-50%, -50%) rotate(-20deg);
               font-family: El Messiri, serif; font-size: clamp(28px, 8vw, 52px);
               color: rgba(0,0,0,0.04); pointer-events: none; user-select: none;
               letter-spacing: 0.15em; white-space: nowrap; font-weight: 700;
               text-transform: uppercase; z-index: 0; max-width: 100%;">
            simulation tawiza
          </div>
          <div aria-hidden="true" style="position: absolute; top: 10px; right: 14px;
               font-family: JetBrains Mono, monospace; font-size: 9px;
               color: rgba(29,53,87,0.4); letter-spacing: 0.08em;
               text-transform: uppercase; font-weight: 600; z-index: 1;">
            tawiza.fr · simulation
          </div>
          <div style="position: relative; z-index: 2;">
          <h2 id="scorecard-titre" style="font-family: El Messiri, serif; font-size: 22px; color: {_couleur};
               font-weight: 700; margin: 0 0 8px 0;">{_titre}</h2>
          <div style="font-size: 14px; color: #1D3557; margin-bottom: 18px; line-height: 1.5;">
            {_verdict}
          </div>
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px;">
            <div style="padding: 10px; background: #fff; border-radius: 3px;">
              <div style="font-size: 9px; color: #6C757D;">KM / OBJECTIF</div>
              <div style="font-family: El Messiri, serif; font-size: 20px; color: #1D3557; font-weight: 700;">{_s_km}/100</div>
            </div>
            <div style="padding: 10px; background: #fff; border-radius: 3px;">
              <div style="font-size: 9px; color: #6C757D;">SANTÉ FINANCIÈRE</div>
              <div style="font-family: El Messiri, serif; font-size: 20px; color: #1D3557; font-weight: 700;">{_s_fin}/100</div>
            </div>
            <div style="padding: 10px; background: #fff; border-radius: 3px;">
              <div style="font-size: 9px; color: #6C757D;">CAPITAL POLIT.</div>
              <div style="font-family: El Messiri, serif; font-size: 20px; color: #1D3557; font-weight: 700;">{_s_pol}/100</div>
            </div>
            <div style="padding: 10px; background: #fff; border-radius: 3px;">
              <div style="font-size: 9px; color: #6C757D;">USAGE</div>
              <div style="font-family: El Messiri, serif; font-size: 20px; color: #1D3557; font-weight: 700;">{_s_usage}/100</div>
            </div>
            <div style="padding: 10px; background: {_couleur}20; border-radius: 3px;">
              <div style="font-size: 9px; color: {_couleur}; font-weight: 700;">SCORE</div>
              <div style="font-family: El Messiri, serif; font-size: 28px; color: {_couleur}; font-weight: 700;">{_s_total}</div>
            </div>
          </div>
          <div style="margin-top: 14px; padding: 10px 14px; background: #fff; border-radius: 4px; font-size: 11px; color: #6C757D;">
            <b>Ton scénario rejoint la collection des parties publiques</b>
            (signal 13 de la Trame, exposé comme <i>biaisé par construction</i> —
            R21, R28). Ce n'est pas un sondage, c'est une trace de lecteurs engagés.
          </div>
          <div style="margin-top: 8px; padding: 10px 14px; background: #fff8e6; border-radius: 4px;
               border-left: 3px solid #D4A843; font-size: 11px; color: #1D3557;">
            <b style="color: #A8832E;">⚠ Anti-détournement (R23).</b>
            Ce score N'EST PAS un indicateur de performance d'un élu réel.
            Il décrit l'état de <i>ton scénario simulé</i>, basé sur des coefficients
            pédagogiques. Utiliser un score moyen des parties publiques pour attaquer
            une maire ou une liste politique constitue un usage contraire à la
            doctrine Tawiza. Ce simulateur n'est pas un outil de campagne.
          </div>
          </div><!-- /z-index:2 wrapper -->
        </section>
        """)
    else:
        mo.md("")
    return


@app.cell
def __url_partage(mo, get_state, preset, arrondissement):
    """Génère une URL encodée pour partager ta partie, sans extraction (R16)."""
    _etat = get_state()
    _h = _etat["historique"]

    # Encode minimal : preset, arrondissement, sequence des budgets votés
    _budgets = "-".join(str(int(_r.get("budget_vote", 0))) for _r in _h[1:])
    _params = f"?preset={preset}&arr={arrondissement}&budgets={_budgets}"

    _n_tours = len(_h) - 1
    if _n_tours == 0:
        mo.md("*Joue au moins un tour pour obtenir une URL de partage.*")
    else:
        # R32 P1.6 — bouton natif "Copier" avec clipboard API + fallback
        _url_partage = f"https://tawiza.fr/notebooks/acte1-paris-velo/{_params}"
        _js = (
            "(function(btn){"
            "const url=btn.getAttribute('data-url');"
            "if(navigator.clipboard&&navigator.clipboard.writeText){"
            "navigator.clipboard.writeText(url).then(function(){"
            "btn.textContent='✓ Copié';btn.setAttribute('aria-label','URL copiée dans le presse-papiers');"
            "setTimeout(function(){btn.textContent='📋 Copier l\\'URL';"
            "btn.setAttribute('aria-label','Copier l\\'URL de partage dans le presse-papiers');},2000);"
            "});}else{"
            "const t=document.getElementById('url-partage-text');"
            "if(t){const r=document.createRange();r.selectNode(t);"
            "window.getSelection().removeAllRanges();window.getSelection().addRange(r);}"
            "}})(this)"
        )
        mo.Html(f"""
        <section role="region" aria-labelledby="partage-titre"
             style="margin: 20px 0; padding: 14px 18px; background: #fafaf9; border-radius: 4px;
             border: 1px dashed #b45309; font-size: 12px; color: #1D3557;">
          <h3 id="partage-titre"
              style="font-family: El Messiri, serif; font-size: 14px; color: #b45309;
              margin: 0 0 6px 0;">
            <span aria-hidden="true">📋 </span>Partager ta partie
          </h3>
          <div style="line-height: 1.5; margin-bottom: 8px;">
            Copie cette URL pour qu'un autre lecteur rejoue exactement ta partie ({_n_tours} tours).
            <br/><i>Tawiza ne stocke aucune donnée côté serveur (R16). Tout est dans l'URL.</i>
          </div>
          <div style="display: flex; gap: 8px; align-items: stretch; flex-wrap: wrap;">
            <code id="url-partage-text"
                  style="flex: 1; min-width: 200px; display: block; padding: 8px 10px;
                  background: #fff; border: 1px solid #e9ecef; border-radius: 3px;
                  font-size: 11px; word-break: break-all; color: #6C757D;">{_url_partage}</code>
            <button type="button"
                    aria-label="Copier l'URL de partage dans le presse-papiers"
                    data-url="{_url_partage}"
                    onclick="{_js}"
                    style="padding: 6px 14px; background: #b45309; color: #fff;
                    border: none; border-radius: 3px; font-family: Inter, sans-serif;
                    font-size: 12px; font-weight: 600; cursor: pointer;
                    white-space: nowrap;">
              <span aria-hidden="true">📋 </span>Copier l'URL
            </button>
          </div>
        </section>
        """)
    return


@app.cell
def __methodo(mo):
    mo.md(
        """
        ---

        ### Méthode et doctrine

        Ce simulateur s'inscrit dans la **Boucle Ambilocale Tawiza** : il consomme
        l'état réel de la Trame (12 fils, mis à jour régulièrement) pour calibrer
        ses probabilités d'événements. Ton scénario est une histoire alternative
        jouée dans le monde d'aujourd'hui.

        **Mythe Tawiza** : Tisserand-Cartographe. Chaque levier est un fil du tissu.
        Chaque événement est un coup de ciseau. Le tissu complet révèle un motif —
        ton scénario.

        **Doctrine** : 29 règles explicites, notamment *baliser sans prédire* (R11) ·
        *pas de scoring moralisant* (R15) · *pas d'extraction de données* (R16) ·
        *la simulation n'est pas un sondage* (R21) · *pas de streak ni de notifications push* (R22) ·
        *le backtest ne sera jamais optimisé pour impressionner* (R20).

        **Backtest Paris vélo 2021-2025** : 4 des 6 fils originels ont été
        *"vus juste"* avec une latence moyenne de 22,7 mois. Les 2 autres étaient
        *prématurés* (seuils trop stricts sur les dérives lentes DGF et CPER).

        ### Sources

        - Plan Vélo Paris 2021-2026 · Observatoire Paris en Selle · Budget Primitif Paris 2026 p.15
        - Chronique des événements : Moody's Paris, canicule 2022, accident Rivoli 2024, CPER IDF avenants
        - Coefficients de couplage : méta-analyses FUB + ADEME

        ### Le feuilleton

        - **Acte 1** — [Qui paie le vélo à Paris ?](/analyses/paris-velo-acte1.html)
        - **Acte 2** — La dette est-elle le vrai problème ?
        - **Acte 3** — Juin 2026 : le choix Grégoire

        *Tawiza · [lire la méthode complète](/methode/) · [tawiza.fr](/)*
        """
    )
    return


if __name__ == "__main__":
    app.run()
