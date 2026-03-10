# tawiza.fr

Site officiel de [Tawiza](https://tawiza.fr) — intelligence territoriale open source.

## Le projet

Tawiza collecte les donnees publiques francaises (INSEE, SIRENE, BODACC, DVF, Banque de France), les croise et les transforme en analyses lisibles. Open source, gratuit, bien commun numerique.

## Structure

```
index.html              Page d'accueil
manifeste.html          Manifeste — pourquoi ce projet
communs.html            Essai — theorie des communs (Ostrom, Axelrod, Nash)
architecture.html       Architecture technique (aujourd'hui vs en construction)
a-propos.html           A propos du projet
contribuer.html         Comment contribuer
analyses/               Articles d'analyse
  index.html            Listing des analyses
  deux-villes-un-miroir.html   Clichy-sous-Bois vs Henin-Beaumont
style.css               CSS principal
manifeste.css           CSS manifeste et essai
feed.xml                Flux RSS
sitemap.xml             Sitemap SEO
```

## Stack

HTML/CSS/JS statique. Pas de framework, pas de build. Heberge sur GitHub Pages.

- **Typographie** : Newsreader (titres), Inter (corps), JetBrains Mono (code)
- **Analytics** : Plausible self-hosted (pas de cookies, GDPR compliant)
- **Deploiement** : GitHub Pages (push to main)

## Contribuer

Voir [contribuer.html](https://tawiza.fr/contribuer.html) ou ouvrir une [issue](https://github.com/tawiza/tawiza-website/issues).

## Licence

MIT
