/* ============================================================
   TAWIZA ANNOTATE - auto-acronyms + term explanations
   ============================================================

   1. AUTO-WRAP ACRONYMS as <abbr title="Full Name">ACRO</abbr>
      Walks through every text node and replaces known Tawiza
      acronyms with <abbr> elements.

   2. MANUAL TERM EXPLANATIONS via data-explain attribute
      Wrap any word in <span data-explain="...">word</span>
      and the script adds a feutre-surligne class.

   Non-destructive: never touches <code>, <pre>, <script>, <style>,
   <a>, existing <abbr>, or [data-no-annotate].
   ============================================================ */

(function () {
  'use strict';

  const ACRONYMS = {
    'SIRENE':   'Syst\u00e8me Informatique pour le R\u00e9pertoire des Entreprises et des \u00c9tablissements',
    'BODACC':   'Bulletin Officiel des Annonces Civiles et Commerciales',
    'DVF':      'Demandes de Valeurs Fonci\u00e8res (donn\u00e9es des ventes immobili\u00e8res publiques)',
    'INSEE':    'Institut National de la Statistique et des \u00c9tudes \u00c9conomiques',
    'SSMSI':    'Service Statistique Minist\u00e9riel de la S\u00e9curit\u00e9 Int\u00e9rieure',
    'OFGL':     'Observatoire des Finances et de la Gestion publique Locales',
    'HATVP':    'Haute Autorit\u00e9 pour la Transparence de la Vie Publique',
    'DARES':    "Direction de l'Animation de la Recherche, des \u00c9tudes et des Statistiques",
    'BdF':      'Banque de France',
    'DGFiP':    'Direction G\u00e9n\u00e9rale des Finances Publiques',

    'PLU':      "Plan Local d'Urbanisme",
    'PLUi':     "Plan Local d'Urbanisme intercommunal",
    'SCOT':     'Sch\u00e9ma de Coh\u00e9rence Territoriale',
    'DICRIM':   "Document d'Information Communal sur les Risques Majeurs",
    'TIM':      "Transmission d'Information au Maire",
    'GASPAR':   'Gestion Assist\u00e9e des Proc\u00e9dures Administratives relatives aux Risques',
    'RGA':      'Retrait-Gonflement des Argiles',
    'CatNat':   'Catastrophes Naturelles (arr\u00eat\u00e9s pr\u00e9fectoraux)',
    'CCR':      'Caisse Centrale de R\u00e9assurance',
    'BRGM':     'Bureau de Recherches G\u00e9ologiques et Mini\u00e8res',
    'IGN':      'Institut G\u00e9ographique National',

    'BP':       "Budget Primitif (adopt\u00e9 en d\u00e9but d'ann\u00e9e)",
    'CA':       "Compte Administratif (cl\u00f4ture de l'exercice)",
    'CRC':      'Chambre R\u00e9gionale des Comptes',
    'IFF':      'Indicateur de Fragilit\u00e9 Financi\u00e8re',
    'DSIL':     "Dotation de Soutien \u00e0 l'Investissement Local",
    'DETR':     "Dotation d'\u00c9quipement des Territoires Ruraux",
    'DGF':      'Dotation Globale de Fonctionnement',

    'CDI':      "Contrat \u00e0 Dur\u00e9e Ind\u00e9termin\u00e9e",
    'CDD':      "Contrat \u00e0 Dur\u00e9e D\u00e9termin\u00e9e",
    'NAF':      'Nomenclature d\u0027Activit\u00e9s Fran\u00e7aise',
    'APE':      'Activit\u00e9 Principale Exerc\u00e9e',
    'URSSAF':   "Union de Recouvrement des cotisations de S\u00e9curit\u00e9 Sociale et d'Allocations Familiales",
    'Filosofi': 'FIchier LOcalis\u00e9 SOcial et FIscal (revenus par commune)',

    'NGA':      'National Gallery of Art (Washington)',
    'WPA':      'Works Progress Administration (New Deal, 1935-1943)',
    'IAD':      'Index of American Design (collection WPA)',

    'NOTRe':    'Nouvelle Organisation Territoriale de la R\u00e9publique (loi, 2015)',
    'RGPD':     'R\u00e8glement G\u00e9n\u00e9ral sur la Protection des Donn\u00e9es',
    'EPCI':     '\u00c9tablissement Public de Coop\u00e9ration Intercommunale',

    'ZIBAC':    "Zone Industrielle Bas-Carbone (d'action concert\u00e9e)"
  };

  const keys = Object.keys(ACRONYMS).sort(function (a, b) { return b.length - a.length; });
  const pattern = new RegExp(
    '\\b(' + keys.map(function (k) { return k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }).join('|') + ')\\b',
    'g'
  );

  function autoAnnotate() {
    const body = document.body;
    if (!body) return;

    const SKIP_TAGS = new Set(['CODE', 'PRE', 'SCRIPT', 'STYLE', 'TEXTAREA', 'ABBR', 'A']);
    const SKIP_SELECTOR = '.act-num, .hot-cell-code, [data-no-annotate]';

    const walker = document.createTreeWalker(
      body,
      NodeFilter.SHOW_TEXT,
      {
        acceptNode: function (node) {
          const parent = node.parentElement;
          if (!parent) return NodeFilter.FILTER_REJECT;
          if (SKIP_TAGS.has(parent.tagName)) return NodeFilter.FILTER_REJECT;
          if (parent.closest && parent.closest(SKIP_SELECTOR)) return NodeFilter.FILTER_REJECT;
          if (!node.nodeValue) return NodeFilter.FILTER_REJECT;
          if (!pattern.test(node.nodeValue)) return NodeFilter.FILTER_REJECT;
          pattern.lastIndex = 0;
          return NodeFilter.FILTER_ACCEPT;
        }
      }
    );

    const toProcess = [];
    let n;
    while ((n = walker.nextNode())) toProcess.push(n);

    toProcess.forEach(function (textNode) {
      const parent = textNode.parentNode;
      if (!parent) return;

      const text = textNode.nodeValue;
      const fragments = document.createDocumentFragment();
      let cursor = 0;

      const matches = Array.from(text.matchAll(pattern));
      matches.forEach(function (match) {
        const acronym = match[1];
        const start = match.index;
        const end = start + acronym.length;

        if (start > cursor) {
          fragments.appendChild(document.createTextNode(text.substring(cursor, start)));
        }

        const abbr = document.createElement('abbr');
        abbr.className = 'tz-abbr';
        abbr.setAttribute('title', ACRONYMS[acronym]);
        abbr.textContent = acronym;
        fragments.appendChild(abbr);

        cursor = end;
      });

      if (cursor < text.length) {
        fragments.appendChild(document.createTextNode(text.substring(cursor)));
      }

      if (matches.length > 0) parent.replaceChild(fragments, textNode);
    });
  }

  function enhanceExplanations() {
    const nodes = document.querySelectorAll('[data-explain]');
    nodes.forEach(function (el) {
      el.classList.add('tz-explain');
      el.setAttribute('role', 'button');
      el.setAttribute('tabindex', '0');
    });
  }

  function boot() {
    try {
      autoAnnotate();
      enhanceExplanations();
    } catch (err) {
      if (window.console) window.console.warn('Tawiza annotate error:', err);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
