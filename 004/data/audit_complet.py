#!/usr/bin/env python3
"""Audit complet BOAMP 2026 :
1. Récolter TOUS les marchés Annexe III (8 domaines)
2. Dédupliquer par idweb
3. Pattern RIA / AI Act / FRIA en regex STRICTE (pas search() API)
4. Identifier tous les acheteurs anticipateurs
5. Verbatims R15 pour chaque cas
"""
import json, urllib.request, urllib.parse, csv, re
from collections import Counter, defaultdict

BASE = 'https://boamp-datadila.opendatasoft.com/api/explore/v2.1/catalog/datasets/boamp/records'

# Toutes les requêtes Annexe III qui ont renvoyé > 0 hits
QUERIES = {
    # Domaine 1 · biométrie + identification
    'biometrie':       'search("biometrie") AND dateparution>="2026-01-01"',
    # Domaine 3 · éducation, formation, orientation
    'IA_education':    '(search("education") OR search("formation") OR search("scolaire") OR search("examen") OR search("orientation")) AND search("intelligence artificielle") AND dateparution>="2026-01-01"',
    # Domaine 4 · emploi, RH, recrutement (AVEC le scoring qui appartient à plusieurs)
    'IA_recrutement':  '(search("recrutement") OR search("tri de cv") OR search("selection candidat") OR search("orientation professionnelle")) AND search("intelligence artificielle") AND dateparution>="2026-01-01"',
    'scoring':         '(search("scoring") OR search("algorithme")) AND dateparution>="2026-01-01"',
    # Domaine 5 · services essentiels, santé, assurance
    'IA_sante':        '(search("sante") OR search("medical") OR search("hospitalier") OR search("clinique") OR search("triage")) AND search("intelligence artificielle") AND dateparution>="2026-01-01"',
    'IA_assurance':    'search("assurance") AND search("intelligence artificielle") AND dateparution>="2026-01-01"',
    # Domaine 6 · force de l'ordre, vidéo
    'video':           '(search("videoprotection") OR search("videosurveillance")) AND dateparution>="2026-01-01"',
    'IA_police':       '(search("police") OR search("gendarmerie")) AND search("intelligence artificielle") AND dateparution>="2026-01-01"',
    'IA_migration':    '(search("frontiere") OR search("asile") OR search("immigration") OR search("visa")) AND search("intelligence artificielle") AND dateparution>="2026-01-01"',
    # Domaine 8 · justice
    'IA_justice':      '(search("justice") OR search("juridiction") OR search("contentieux") OR search("jugement")) AND search("intelligence artificielle") AND dateparution>="2026-01-01"',
    # Filet général : tout marché contenant "intelligence artificielle"
    'IA_tout':         'search("intelligence artificielle") AND dateparution>="2026-01-01"',
}

def fetch_all(query, batch=100):
    out = []
    offset = 0
    while True:
        params = {'where': query, 'limit': batch, 'offset': offset}
        url = BASE + '?' + urllib.parse.urlencode(params)
        with urllib.request.urlopen(url, timeout=30) as r:
            data = json.load(r)
        recs = data['results']
        out.extend(recs)
        if len(recs) < batch or offset + batch >= data['total_count']:
            break
        offset += batch
    return out

# Étape 1 · récolter
print("=" * 70)
print("RÉCOLTE BOAMP 2026 · Annexe III complet")
print("=" * 70)

all_recs = {}  # idweb -> record
per_query_count = {}
for label, q in QUERIES.items():
    recs = fetch_all(q)
    per_query_count[label] = len(recs)
    for r in recs:
        idw = r.get('idweb')
        if idw:
            if idw not in all_recs:
                all_recs[idw] = r
                all_recs[idw]['_requetes'] = [label]
            else:
                all_recs[idw]['_requetes'].append(label)
    print(f"  {label:20s} : {len(recs):4d} marchés")

print(f"\n  Total unique dédupliqué : {len(all_recs)} marchés")

# Étape 2 · pattern AI Act en regex STRICTE
print(f"\n{'=' * 70}")
print(f"AUDIT MENTIONS AI ACT / RIA · PATTERN REGEX STRICT")
print(f"{'=' * 70}")

# Patterns avec word boundaries pour éviter les faux positifs
patterns_strict = {
    'RIA':          re.compile(r'\bRIA\b', re.IGNORECASE),
    'FRIA':         re.compile(r'\bFRIA\b', re.IGNORECASE),
    'AI_Act':       re.compile(r'\bAI\s*Act\b|\bIA\s*Act\b', re.IGNORECASE),
    'article_27':   re.compile(r'\barticle\s*27\b|\bart\.?\s*27\b', re.IGNORECASE),
    'reg_2024':     re.compile(r'\b2024[\s/-]+1689\b', re.IGNORECASE),
    'reg_IA':       re.compile(r'r[èe]glement\s+(?:europ[ée]en|UE|sur).{0,50}intelligence\s+artificielle', re.IGNORECASE),
    'haut_risque':  re.compile(r'haut[\s-]+risque|haute?[\s-]+risque', re.IGNORECASE),
    'analyse_DF':   re.compile(r'analyse.{0,30}impact.{0,30}droits\s+fondamentaux|FRIA', re.IGNORECASE),
    'CNIL':         re.compile(r'\bCNIL\b'),
    'RGPD_strict':  re.compile(r'\bRGPD\b'),
    'AIPD':         re.compile(r'\bAIPD\b'),
    'DPO':          re.compile(r'\bDPO\b'),
}

union_pat = re.compile(
    r'\bRIA\b|\bFRIA\b|\bAI\s*Act\b|\bIA\s*Act\b|\barticle\s*27\b|\bart\.?\s*27\b|2024[\s/-]+1689|r[èe]glement\s+(?:europ[ée]en|UE|sur).{0,50}intelligence\s+artificielle',
    re.IGNORECASE
)

per_pattern_hits = {label: [] for label in patterns_strict}
union_hits = []
for idw, r in all_recs.items():
    objet = r.get('objet') or ''
    for label, pat in patterns_strict.items():
        if pat.search(objet):
            per_pattern_hits[label].append(r)
    if union_pat.search(objet):
        union_hits.append(r)

print(f"\n  {'Pattern':20s} : {'Hits':>5s}")
print(f"  {'-' * 20:20s}   {'----':>5s}")
for label, hits in per_pattern_hits.items():
    print(f"  {label:20s} : {len(hits):>5d}")

print(f"\n  UNION (RIA|FRIA|AI Act|art.27|2024/1689|règlement IA) : {len(union_hits)}")

# Étape 3 · détail des acheteurs mentionnant AI Act
print(f"\n{'=' * 70}")
print(f"ACHETEURS MENTIONNANT AI ACT (regex stricte UNION)")
print(f"{'=' * 70}")

acheteurs_AI = defaultdict(list)
for r in union_hits:
    nom = r.get('nomacheteur', '?')
    acheteurs_AI[nom].append(r)

print(f"\n  Nombre d'acheteurs uniques mentionnant AI Act : {len(acheteurs_AI)}")
print(f"\n  {'Acheteur':50s} | {'#avis':>5s} | dates")
print(f"  {'-' * 50:50s} | {'-' * 5:>5s} | {'-' * 30}")
for nom, avis_list in sorted(acheteurs_AI.items(), key=lambda x: -len(x[1])):
    dates = sorted(set(a.get('dateparution', '?')[:10] for a in avis_list))
    print(f"  {nom[:50]:50s} | {len(avis_list):>5d} | {', '.join(dates[:5])}")

# Étape 4 · verbatims pour chaque acheteur
print(f"\n{'=' * 70}")
print(f"VERBATIMS R15 · chaque acheteur unique")
print(f"{'=' * 70}")
for nom, avis_list in acheteurs_AI.items():
    objets_uniques = list(set(a.get('objet') or '' for a in avis_list))
    print(f"\n--- {nom} ({len(avis_list)} avis, {len(objets_uniques)} objet(s) uniques) ---")
    for objet in objets_uniques:
        print(f"  « {objet[:300]} »")
        if len(objet) > 300:
            print(f"    [...] ({len(objet)} char total)")

# Étape 5 · top acheteurs Annexe III (tous)
print(f"\n{'=' * 70}")
print(f"TOP 15 ACHETEURS ANNEXE III 2026 (toute mention IA)")
print(f"{'=' * 70}")
top_global = Counter(r.get('nomacheteur', '?') for r in all_recs.values()).most_common(15)
print(f"\n  {'Acheteur':60s} | {'Marchés':>7s}")
for nom, n in top_global:
    print(f"  {nom[:60]:60s} | {n:>7d}")

# Étape 6 · distribution par requête (pour comprendre où sont les marchés)
print(f"\n{'=' * 70}")
print(f"DISTRIBUTION PAR REQUÊTE · déduplication montrant le chevauchement")
print(f"{'=' * 70}")
solo = Counter()
for r in all_recs.values():
    requetes = tuple(sorted(r['_requetes']))
    solo[requetes] += 1
for combo, n in sorted(solo.items(), key=lambda x: -x[1])[:15]:
    print(f"  {n:>4d} × {combo}")

# Étape 7 · export CSV global
with open('/tmp/tawiza-004-post/boamp-annexe3-COMPLET-2026.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f, quoting=csv.QUOTE_ALL)
    w.writerow(['idweb', 'dateparution', 'nomacheteur', 'objet', 'etat', 'url_avis', 'requetes', 'mention_AIAct'])
    for r in all_recs.values():
        objet = (r.get('objet') or '').replace('\n', ' ').replace('\r', ' ')
        w.writerow([
            r.get('idweb', ''),
            r.get('dateparution', ''),
            r.get('nomacheteur', ''),
            objet,
            r.get('etat', ''),
            r.get('url_avis', ''),
            '|'.join(r['_requetes']),
            'OUI' if union_pat.search(r.get('objet') or '') else 'NON',
        ])

print(f"\nCSV global : /tmp/tawiza-004-post/boamp-annexe3-COMPLET-2026.csv ({len(all_recs)} lignes)")

# Étape 8 · verdict consolidé
print(f"\n{'=' * 70}")
print(f"VERDICT")
print(f"{'=' * 70}")
print(f"  Marchés Annexe III 2026 (1er jan → aujourd'hui)")
print(f"    Périmètre élargi (8 domaines + filet IA général) : {len(all_recs)} marchés uniques")
print(f"    Périmètre initial (IA + scoring + vidéo)         : 273 marchés (manquait {len(all_recs) - 273})")
print(f"  Mentions AI Act (regex stricte UNION)              : {len(union_hits)} avis")
print(f"  Acheteurs uniques mentionnant AI Act               : {len(acheteurs_AI)}")
