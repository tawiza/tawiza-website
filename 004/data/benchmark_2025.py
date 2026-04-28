#!/usr/bin/env python3
"""Benchmark RGPD 2025 : sur les marchés Annexe III publiés en 2025
(catégories IA, scoring, vidéoprotection), combien mentionnent RGPD,
GDPR, "données personnelles", "règlement (UE) 2016/679" dans l'objet ?

Réponse → calibre si 0/270 AI Act 2026 est anormal ou trivial.
"""
import json, urllib.request, urllib.parse, csv, re
from collections import Counter

BASE = 'https://boamp-datadila.opendatasoft.com/api/explore/v2.1/catalog/datasets/boamp/records'

QUERIES_2025 = {
    'IA':       'search("intelligence artificielle") AND dateparution>="2025-01-01" AND dateparution<="2025-12-31"',
    'scoring':  '(search("scoring") OR search("algorithme")) AND dateparution>="2025-01-01" AND dateparution<="2025-12-31"',
    'video':    '(search("videoprotection") OR search("videosurveillance")) AND dateparution>="2025-01-01" AND dateparution<="2025-12-31"',
}

def fetch_all(query, batch=100):
    out = []
    offset = 0
    while True:
        params = {'where': query, 'limit': batch, 'offset': offset, 'order_by': 'dateparution desc'}
        url = BASE + '?' + urllib.parse.urlencode(params)
        with urllib.request.urlopen(url, timeout=30) as r:
            data = json.load(r)
        recs = data['results']
        out.extend(recs)
        if len(recs) < batch or offset + batch >= data['total_count']:
            break
        offset += batch
    return out, data['total_count']

print("=" * 70)
print("BENCHMARK 2025 · Marchés Annexe III & mentions RGPD")
print("=" * 70)

all_records = []
totals = {}
for label, q in QUERIES_2025.items():
    recs, total = fetch_all(q)
    totals[label] = (len(recs), total)
    for r in recs:
        r['_requete'] = label
    all_records.extend(recs)
    print(f"  {label:8s} : {len(recs):4d} récupérés / {total:4d} déclarés")

print(f"\n  TOTAL 2025 : {len(all_records)} marchés Annexe III")
print(f"  Pour comparaison 2026 (4 mois) : 270 marchés Annexe III")

# Patterns à grepper
patterns = {
    'RGPD':              re.compile(r'\bRGPD\b|\bGDPR\b', re.IGNORECASE),
    'donnees_personnel': re.compile(r'donn[ée]es?\s+(?:[àa]\s+caract[èe]re\s+)?personnel(?:les?)?', re.IGNORECASE),
    'reg_2016_679':      re.compile(r'2016/679|r[èe]glement.{0,30}europ[ée]en.{0,30}prot[ée]ction', re.IGNORECASE),
    'CNIL':              re.compile(r'\bCNIL\b', re.IGNORECASE),
    'AIPD_DPIA':         re.compile(r'\bAIPD\b|\bDPIA\b|analyse.{0,20}impact.{0,20}prot[ée]ction', re.IGNORECASE),
    'DPO':               re.compile(r'\bDPO\b|d[ée]l[ée]gu[ée].{0,5}prot[ée]ction', re.IGNORECASE),
}

print(f"\n=== Mentions dans l'objet (sur n={len(all_records)} marchés 2025) ===")
hits = {label: [] for label in patterns}
for r in all_records:
    objet = (r.get('objet') or '')
    for label, pat in patterns.items():
        if pat.search(objet):
            hits[label].append(r)

for label, hh in hits.items():
    pct = (100 * len(hh) / len(all_records)) if all_records else 0
    print(f"  {label:25s} : {len(hh):4d} / {len(all_records)} = {pct:5.1f}%")

# Aussi : compter union (au moins une mention privacy)
union_pat = re.compile(r'\bRGPD\b|\bGDPR\b|donn[ée]es?\s+(?:[àa]\s+caract[èe]re\s+)?personnel(?:les?)?|2016/679|r[èe]glement.{0,30}europ[ée]en.{0,30}prot[ée]ction|\bCNIL\b|\bAIPD\b|\bDPIA\b|\bDPO\b', re.IGNORECASE)
union_hits = [r for r in all_records if union_pat.search(r.get('objet') or '')]
pct_union = (100 * len(union_hits) / len(all_records)) if all_records else 0
print(f"\n  AU MOINS UNE mention privacy : {len(union_hits):4d} / {len(all_records)} = {pct_union:5.1f}%")

# Échantillon de 5 verbatims pour validation manuelle
print(f"\n=== 5 verbatims (R15) ===")
for i, r in enumerate(union_hits[:5]):
    objet = (r.get('objet') or '')[:200]
    print(f"  [{i+1}] {r.get('dateparution','?')[:10]} · {r.get('nomacheteur','?')[:50]}")
    print(f"      {objet}")

# Export CSV des verbatims (pour vérif Vigie + R20 reproductibilité)
with open('/tmp/tawiza-004-post/benchmark-2025-rgpd-hits.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f, quoting=csv.QUOTE_ALL)
    w.writerow(['idweb', 'dateparution', 'nomacheteur', 'objet', 'etat', 'url_avis', 'requete_source', 'mentions'])
    for r in union_hits:
        objet = r.get('objet') or ''
        which = []
        for label, pat in patterns.items():
            if pat.search(objet):
                which.append(label)
        w.writerow([
            r.get('idweb', ''),
            r.get('dateparution', ''),
            r.get('nomacheteur', ''),
            objet.replace('\n', ' ').replace('\r', ' '),
            r.get('etat', ''),
            r.get('url_avis', ''),
            r.get('_requete', ''),
            '|'.join(which),
        ])

print(f"\nCSV verbatims : /tmp/tawiza-004-post/benchmark-2025-rgpd-hits.csv ({len(union_hits)} lignes)")
print(f"\n{'=' * 70}")
print(f"VERDICT")
print(f"{'=' * 70}")
print(f"  Marchés Annexe III 2025 : {len(all_records)}")
print(f"  Mentions privacy (union)  : {len(union_hits)} ({pct_union:.1f}%)")
print(f"  Marchés Annexe III 2026 (4 mois) : 270")
print(f"  Mentions AI Act 2026      : 0 (0.0%)")
print()
if pct_union > 1:
    print(f"  → 0/270 AI Act EST anormal (RGPD baseline {pct_union:.1f}% > 0%)")
elif pct_union > 0:
    print(f"  → 0/270 AI Act EST légèrement anormal (RGPD baseline {pct_union:.1f}%)")
else:
    print(f"  → 0/270 AI Act EST TRIVIAL (RGPD baseline 0% aussi · les marchés ne nomment pas les règlements)")
