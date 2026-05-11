"""
Notebook reproductible - Article 003 "Cyberfuites, la dette d'information"

Ce fichier est pensé pour être lu pas-à-pas par une personne qui ne code pas
forcément en Python. Chaque section commence par une explication en français
clair, puis le code, puis le résultat attendu.

Pour le lancer chez vous :
  - Installez Python 3.11+
  - Installez pandas : pip install pandas
  - Téléchargez ce fichier et les CSV depuis github.com/tawiza/tawiza-website
  - Lancez : python cyberfuites-2026.py

Vous n'avez pas envie de lancer le code ? La page HTML compagnon montre
toutes les étapes et les résultats : tawiza.fr/notebooks/cyberfuites/
"""

from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# OÙ SONT LES DONNÉES
# ---------------------------------------------------------------------------
# Les CSV viennent du dossier assets/data/cyberfuites/ du même repo public.
# On les charge avec pandas (la bibliothèque la plus courante pour les
# tableaux de données en Python).

DATA = Path(__file__).resolve().parent.parent / "assets" / "data" / "cyberfuites"

# Si le dossier n'existe pas (par exemple en local), on retombe sur le repo
# d'analyse Tawiza où les fichiers sont disponibles.
if not DATA.exists():
    DATA = Path("/root/tawiza/articles/003-cyberfuites/data/raw")


# ---------------------------------------------------------------------------
# ÉTAPE 1 - LES CHIFFRES BRUTS DE LA CNIL
# ---------------------------------------------------------------------------
# On charge le tableau récapitulatif des bilans annuels de la CNIL.
# Source : cnil.fr/fr/bilan-sanctions-2025 et le bilan 2024 équivalent.

print("\n=== ÉTAPE 1 : Sanctions CNIL annuelles ===\n")

sanctions = pd.read_csv(DATA / "sanctions_cnil_annuel.csv")
print(sanctions[["annee", "total_sanctions", "total_amendes_eur",
                 "sanctions_publiques", "amendes_publiques_eur"]])

# Ce qu'on lit dans ce tableau :
#   - "total_sanctions" : nombre de sanctions prononcées dans l'année
#   - "total_amendes_eur" : montant cumulé des amendes (privé + public)
#   - "sanctions_publiques" : nombre d'organismes publics sanctionnés
#   - "amendes_publiques_eur" : montant cumulé pour le public uniquement
#
# Ces chiffres viennent des bilans annuels publiés par la CNIL elle-même.


# ---------------------------------------------------------------------------
# ÉTAPE 2 - POURQUOI ON N'A PAS COMPARÉ PUBLIC vs PRIVÉ
# ---------------------------------------------------------------------------
# L'article explique qu'on a renoncé à présenter un "ratio public/privé".
# La raison est simple : en 2025, deux sanctions cookies (Google et Shein)
# représentent à elles seules 475 millions d'euros, soit 97,5 % du total
# annuel de 486,8 millions. Comparer le total public au total privé revient
# donc à mettre dans la balance des sanctions "cookies" et des sanctions
# "fuites de données", ce qui ne tient pas méthodologiquement.

print("\n=== ÉTAPE 2 : Pourquoi on ne compare pas public vs privé ===\n")

google_shein_meur = 325 + 150          # Google 325 M€ + Shein 150 M€
total_2025_meur = 486.8                 # bilan CNIL 2025
part_cookies_pct = google_shein_meur / total_2025_meur * 100

print(f"Sanctions cookies Google + Shein 2025 : {google_shein_meur} M€")
print(f"Total amendes CNIL 2025             : {total_2025_meur} M€")
print(f"Part cookies dans le total          : {part_cookies_pct:.1f} %")
print()
print("Lecture : 97,5 % du montant total annuel vient de DEUX sanctions sur 83.")
print("Un ratio public/privé total serait donc fortement biaisé par les")
print("amendes cookies, étrangères au sujet des fuites de données publiques.")


# ---------------------------------------------------------------------------
# ÉTAPE 3 - LA "DETTE D'INFORMATION" : LES CHIFFRES DOMINANTS
# ---------------------------------------------------------------------------
# Deux sources convergent :
#   (a) La CNIL déclare officiellement 40,3 millions de comptes compromis
#       en France en 2025 (source : bilan CNIL 2025).
#   (b) Le sondage Ipsos d'août 2025 indique que 37 % des Français se sentent
#       informés de l'usage de leurs données par les acteurs publics. Donc
#       63 % ne se sentent pas informés.

print("\n=== ÉTAPE 3 : Le calcul de la 'dette d'information' ===\n")

population_france = 67_000_000          # INSEE estimation au 1er janv 2025
ipsos_part_non_informes = 0.63          # 100 % - 37 %
non_informes_estimes = int(population_france * ipsos_part_non_informes)
comptes_compromis_2025 = 40_300_000     # CNIL bilan 2025

print(f"Population française                    : {population_france:>14,}".replace(",", " "))
print(f"Part Ipsos non informés (août 2025)    : {ipsos_part_non_informes:>14.0%}")
print(f"Estimation non informés                 : {non_informes_estimes:>14,}".replace(",", " "))
print(f"Comptes compromis 2025 (CNIL officiel) : {comptes_compromis_2025:>14,}".replace(",", " "))
print()
print("Lecture : les deux ordres de grandeur convergent autour de 40 millions")
print("de personnes. C'est le 'chiffre central' de l'article.")
print()
print("ATTENTION : nous ne prétendons PAS que les 42,2 millions de non-informés")
print("sont les mêmes personnes que les 40,3 millions de comptes compromis. Ce")
print("sont deux mesures différentes du même phénomène d'opacité.")


# ---------------------------------------------------------------------------
# ÉTAPE 4 - LA TIMELINE DES FUITES PUBLIQUES 2024-2026
# ---------------------------------------------------------------------------
# On charge le recensement des fuites publiques nationales et on calcule
# leur somme brute (avec doublons : la même personne peut figurer dans
# plusieurs bases différentes).

print("\n=== ÉTAPE 4 : Cumul des fuites publiques 2024-2026 ===\n")

fuites = pd.read_csv(DATA / "breaches_nationales.csv")
fuites_chiffrees = fuites.dropna(subset=["personnes_concernees"])
fuites_chiffrees = fuites_chiffrees[fuites_chiffrees["personnes_concernees"] > 0]

print(fuites_chiffrees[["date", "entite", "personnes_concernees"]].to_string(index=False))
total = int(fuites_chiffrees["personnes_concernees"].sum())
print()
print(f"Cumul brut (avec doublons probables) : {total:,} personnes".replace(",", " "))
print()
print("Lecture : 73 millions de personnes apparaissent au moins une fois dans")
print("une fuite publique nationale entre 2024 et 2026. Comme une personne")
print("peut figurer dans plusieurs bases (par exemple France Travail + CAF +")
print("ANTS), le chiffre RÉEL de personnes touchées est inférieur à 73 M, mais")
print("nettement supérieur aux 40 M annoncés par la seule année 2025.")


# ---------------------------------------------------------------------------
# ÉTAPE 5 - LE CALCULATEUR D'EXPOSITION PERSONNELLE
# ---------------------------------------------------------------------------
# Le calculateur de l'article (HTML+JS) utilise une méthode "hybride" :
#   - Si vous remplissez un critère donné (par exemple "j'ai demandé un
#     titre d'identité depuis 2020"), la probabilité de figurer dans la
#     fuite correspondante (ANTS 2026) est calculée comme le rapport
#     personnes_exposées / population_éligible.
#   - Sinon, une probabilité résiduelle très faible est gardée pour tenir
#     compte d'une erreur d'attribution.
#
# Exemple de calcul pour un profil "actif 40 ans, ex-inscrit France Travail,
# allocataire CAF, a demandé un passeport depuis 2020" :

print("\n=== ÉTAPE 5 : Exemple de calcul d'exposition ===\n")

# Définitions des fuites avec leur "base éligible"
bases_eligibles = {
    "France Travail mars 2024":       (43_000_000, 35_000_000),
    "CAF décembre 2025":              ( 8_000_000, 13_000_000),
    "ANTS avril 2026":                (18_500_000, 30_000_000),
    "FICOBA janvier 2026":            ( 1_200_000, 50_000_000),  # tous les détenteurs de compte
}

# Pour notre profil exemple, on coche les trois premiers critères
print(f"{'Base':<35}{'Pop. fuitée':>14}{'Pop. éligible':>16}{'Proba':>10}")
print("-" * 75)
proba_au_moins_une = 1.0
for nom, (pop_fuite, pop_eligible) in bases_eligibles.items():
    p = min(1.0, pop_fuite / pop_eligible)
    proba_au_moins_une *= (1 - p)
    print(f"{nom:<35}{pop_fuite:>14,}{pop_eligible:>16,}{p:>10.0%}".replace(",", " "))
proba_au_moins_une = 1 - proba_au_moins_une
print()
print(f"Probabilité d'être dans AU MOINS UNE de ces fuites : {proba_au_moins_une:.0%}")
print()
print("Pour notre profil exemple (actif 40 ans avec CAF + FT + passeport),")
print("la probabilité d'apparaître dans au moins une fuite publique majeure")
print("dépasse 95 %.")


# ---------------------------------------------------------------------------
# ÉTAPE 6 - CE QUE CE CALCUL NE DIT PAS
# ---------------------------------------------------------------------------
# - Il ne prend en compte que les fuites NATIONALES de 2024-2026.
#   Il ignore les fuites des collectivités locales (mairies, hôpitaux,
#   lycées), même si elles peuvent concerner les mêmes personnes.
# - Il ne tient pas compte des fuites des prestataires privés (Cegedim
#   Santé, Majorel, etc.) qui hébergent en pratique des données publiques.
# - L'hypothèse d'indépendance entre fuites est une simplification : en
#   réalité, qui figure dans la base France Travail a plus de chances que
#   la moyenne de figurer aussi dans la base CAF.
# - Le calcul est volontairement conservateur. Le chiffre réel est
#   probablement plus élevé.

print("\n=== Pour aller plus loin ===\n")
print("Article complet  : tawiza.fr/analyses/cyberfuites-2026.html")
print("Code source      : github.com/tawiza/tawiza-website")
print("Données brutes   : assets/data/cyberfuites/sanctions_cnil_annuel.csv,")
print("                   assets/data/cyberfuites/breaches_nationales.csv,")
print("                   assets/data/cyberfuites/breaches_locales.csv")
print()
print("Toutes les sources sont citées dans la section Sources de l'article.")
