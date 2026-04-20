# panoptic - site public

Un regard sur l'agrivoltaïsme français. On croise quatre registres publics (ADEME, projets-environnement, MRAe, CNPrV) - aucune source seule ne voit le pipeline complet.

Domaine cible : `panoptic.tawiza.fr`
Licence data : **CC-BY-SA 4.0**
Licence code : **AGPL-3.0**

## Structure

```
panoptic/
├── public/data/    export figé (JSON / GeoJSON / manifest) - remplacé à chaque build
├── src/            Next.js static export (à venir)
└── README.md
```

## Flow de build

1. Pipeline privé collecte les données (ADEME, projets-environnement, CRE, ArianeWeb, CNPrV, presse)
2. Pipeline privé pousse un export figé dans `public/data/`
3. Next.js consomme les fichiers statiques
4. Build Cloudflare Pages → CDN global

**Le site ne parle jamais à une API dynamique privée. Toutes les données sont pré-calculées.**

## Formats publiés

| Fichier | Format | Usage |
|---------|--------|-------|
| `public/data/projects.json` | JSON liste | Recherche client-side (MiniSearch) |
| `public/data/projects.geojson` | GeoJSON | Carte MapLibre |
| `public/data/projects-by-dept.json` | JSON agrégats | Stats département |
| `public/data/manifest.json` | JSON | Métadonnées build (date, counts, checksums) |

## Méthodologie

Voir la page Tawiza dédiée (à venir) et les 3 règles éditoriales :
- **Doublet** - chaque chiffre sur agrivoltaïsme mis en perspective avec fossile/nucléaire/éolien
- **Structures pas personnes** - pas de nominatif hors étiquette publique
- **L'algo doute** - chaque chiffre sourcé 3+ fois, sinon flagué

## Contribuer

Le pipeline de collecte est open source (AGPL-3.0). Pour signaler un projet manquant ou une erreur : tawiza.v0@gmail.com.
