/**
 * Liste des analyses + feuilletons Tawiza.
 * Source unique pour l'archive unifiée + méta de chaque article.
 * Ajouter une nouvelle analyse = une ligne ici + une page .astro correspondante.
 */

export interface Analysis {
  slug: string;
  num: string;
  title: string;
  em?: string; // mot en italique terre dans le titre
  lede: string;
  region: string;
  regionCode: string; // 'nat' | '59' | '62' | '93' | '84' ...
  date: string; // ISO
  dateDisplay: string;
  readMin: number;
  sources: number;
  type: 'analyse' | 'feuilleton';
  glyphVariant: 'grid' | 'ring' | 'stripe' | 'diag';
  glyphTint: 'mix' | 'ocre' | 'terre' | 'foret' | 'ink';
  filter: 'national' | 'région' | 'méthodologie';
  href: string;
}

export const analyses: Analysis[] = [
  {
    slug: 'ce-que-le-maire-controle',
    num: '05',
    title: 'ce que le maire contrôle',
    em: 'contrôle',
    lede: 'Steeve Briois (RN) réélu à 78 % à Hénin-Beaumont. 8 km plus loin, Liévin entre en duel PS-RN au second tour. Mêmes galères, choix opposés.',
    region: 'Pas-de-Calais',
    regionCode: '62',
    date: '2026-03-18',
    dateDisplay: '18 mars 2026',
    readMin: 9,
    sources: 14,
    type: 'analyse',
    glyphVariant: 'grid',
    glyphTint: 'mix',
    filter: 'région',
    href: '/analyses/ce-que-le-maire-controle/',
  },
  {
    slug: 'deux-villes-comptes',
    num: '04',
    title: 'plus pauvre, mieux gérée',
    em: 'mieux',
    lede: "Liévin est plus pauvre qu'Hénin-Beaumont. Pourtant elle investit 2,7 fois plus. On a ouvert les comptes de quatre communes. Euro par euro.",
    region: 'Pas-de-Calais',
    regionCode: '62',
    date: '2026-03-17',
    dateDisplay: '17 mars 2026',
    readMin: 12,
    sources: 18,
    type: 'analyse',
    glyphVariant: 'stripe',
    glyphTint: 'ocre',
    filter: 'région',
    href: '/analyses/deux-villes-comptes/',
  },
  {
    slug: 'deux-villes-un-miroir',
    num: '03',
    title: 'deux villes, un miroir',
    em: 'miroir',
    lede: "Clichy-sous-Bois vote à gauche, Hénin-Beaumont vote RN. Mêmes difficultés, choix opposés. Les programmes changent-ils quelque chose ? On a vérifié.",
    region: 'national',
    regionCode: 'nat',
    date: '2026-03-12',
    dateDisplay: '12 mars 2026',
    readMin: 11,
    sources: 16,
    type: 'analyse',
    glyphVariant: 'diag',
    glyphTint: 'terre',
    filter: 'national',
    href: '/analyses/deux-villes-un-miroir/',
  },
  {
    slug: 'dunkerque-vulnerabilite-energetique',
    num: '06',
    title: 'dunkerque, vitrine ou vulnérabilité ?',
    em: 'vulnérabilité',
    lede: "Dunkerque est la promesse industrielle de la France. Mais sous la vitrine des gigafactories, le territoire reste ancré dans des industries énergivores héritées. La crise d'Ormuz pose la question.",
    region: 'Nord',
    regionCode: '59',
    date: '2026-04-02',
    dateDisplay: '2 avril 2026',
    readMin: 10,
    sources: 21,
    type: 'analyse',
    glyphVariant: 'ring',
    glyphTint: 'terre',
    filter: 'région',
    href: '/analyses/dunkerque-vulnerabilite-energetique/',
  },
  {
    slug: 'risque-argile-silence-communal',
    num: '07',
    title: "risque argile, silence communal",
    em: 'silence',
    lede: "12,1 millions de maisons françaises sont exposées au retrait-gonflement des argiles. 8 031 communes n'ont jamais produit le document légal d'information. On a compté.",
    region: 'national',
    regionCode: 'nat',
    date: '2026-04-08',
    dateDisplay: '8 avril 2026',
    readMin: 8,
    sources: 12,
    type: 'analyse',
    glyphVariant: 'grid',
    glyphTint: 'foret',
    filter: 'national',
    href: '/analyses/risque-argile-silence-communal/',
  },
  {
    slug: 'paris-velo-2026',
    num: '01',
    title: 'qui paie le vélo à paris ?',
    em: 'paie',
    lede: "Un feuilleton en trois actes sur le plan vélo parisien. Budget, dette, et la bifurcation de juin 2026. Tout est sourcé, tout est public.",
    region: 'Paris',
    regionCode: '75',
    date: '2026-04-15',
    dateDisplay: '15 avril 2026',
    readMin: 28,
    sources: 42,
    type: 'feuilleton',
    glyphVariant: 'ring',
    glyphTint: 'terre',
    filter: 'région',
    href: '/articles/paris-velo-2026/',
  },
];

// Tri par date décroissante (plus récent d'abord)
export const analysesByDate = [...analyses].sort((a, b) => b.date.localeCompare(a.date));

// Compteur de régions (pour bloc "répartition")
export function regionCounts() {
  const counts = new Map<string, number>();
  for (const a of analyses) {
    counts.set(a.region, (counts.get(a.region) || 0) + 1);
  }
  return Array.from(counts.entries())
    .map(([region, count]) => ({ region, count }))
    .sort((a, b) => b.count - a.count);
}
