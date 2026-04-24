// panoptic graph · carte interactive de l'écosystème
// Cytoscape.js + fcose. Pas de build step.

(function () {
  'use strict';

  const COL = {
    ocre: '#b45309',
    terre: '#C1554D',
    foret: '#2D6A4F',
    creme: '#faf5ef',
    ivoire: '#f3ebdd',
    encre: '#1a1612',
    ardoise: '#5B7BA5',
    greyM: '#6b5f52',
    greyL: '#b8ad9e',
  };

  const COUNTRY_LABELS = {
    FRA: 'France', IRL: 'Irlande', ESP: 'Espagne', DEU: 'Allemagne',
    CHE: 'Suisse', LUX: 'Luxembourg', NLD: 'Pays-Bas', ITA: 'Italie',
    GBR: 'Royaume-Uni', USA: 'États-Unis', CAN: 'Canada',
  };

  const $ = (id) => document.getElementById(id);
  const sidebar = $('sidebar');
  const sidebarContent = $('sidebar-content');

  let graph = null;
  let cy = null;

  function motherSize(n) {
    const logN = Math.log10(Math.max(1, n)) * 16 + 22;
    return Math.max(22, Math.min(80, logN));
  }

  fetch('graph.json?v=' + Date.now())
    .then((r) => r.json())
    .then((data) => {
      graph = data;
      $('stat-mothers').textContent = data.stats.n_mothers;
      $('stat-alarm').textContent = data.stats.n_mothers_alarm;
      $('stat-foreign').textContent = data.stats.n_mothers_foreign;
      $('stat-group').textContent = data.stats.n_subsidiaries_group_total.toLocaleString('fr');
      initGraph();
    })
    .catch((err) => {
      console.error('fetch graph.json failed', err);
      const errEl = document.createElement('p');
      errEl.style.color = COL.terre;
      errEl.textContent = 'Erreur de chargement du graphe. Réessaye plus tard.';
      $('stats').appendChild(errEl);
    });

  function initGraph() {
    const elements = [];
    for (const n of graph.nodes) {
      elements.push({
        data: Object.assign({}, n, { label: buildLabel(n) }),
        classes: nodeClasses(n),
      });
    }
    for (const e of graph.edges) {
      elements.push({
        data: {
          id: 'e:' + e.source + ':' + e.target,
          source: e.source,
          target: e.target,
          kind: e.kind,
          level: e.level,
        },
        classes: 'edge-' + e.kind,
      });
    }

    cy = cytoscape({
      container: $('cy'),
      elements: elements,
      style: cytoscapeStyle(),
      layout: { name: 'preset' },
      wheelSensitivity: 0.2,
      minZoom: 0.1,
      maxZoom: 3,
    });

    cy.on('tap', 'node', (evt) => showNodeDetails(evt.target.data()));
    cy.on('dblclick', 'node[type = "mother"]', () => {
      $('show-holdings').checked = true;
      applyFilters();
    });
    $('close-sidebar').addEventListener('click', () => sidebar.classList.add('sidebar-hidden'));

    ['filter-alarm', 'filter-foreign', 'show-holdings', 'show-spv'].forEach((id) =>
      $(id).addEventListener('change', applyFilters)
    );
    $('search-box').addEventListener('input', handleSearch);
    $('reset-btn').addEventListener('click', () => {
      ['filter-alarm', 'filter-foreign', 'show-holdings', 'show-spv'].forEach((id) => {
        $(id).checked = false;
      });
      $('search-box').value = '';
      sidebar.classList.add('sidebar-hidden');
      applyFilters();
    });

    applyFilters();
  }

  function buildLabel(n) {
    if (n.type === 'mother') return n.canonical;
    if (n.type === 'country') return n.label;
    return '';
  }

  function nodeClasses(n) {
    const c = ['type-' + n.type];
    if (n.type === 'mother') {
      if ((n.max_signal_score || 0) >= 75) c.push('alarm');
      if ((n.ultimate_country || 'FRA') !== 'FRA') c.push('foreign');
    }
    return c.join(' ');
  }

  function cytoscapeStyle() {
    return [
      { selector: 'edge', style: {
          width: 1.2,
          'line-color': COL.greyL,
          'target-arrow-color': COL.greyL,
          'target-arrow-shape': 'triangle',
          'curve-style': 'bezier',
          opacity: 0.6,
      }},
      { selector: '.edge-controlled_by', style: {
          'line-color': COL.terre, 'target-arrow-color': COL.terre, width: 2, opacity: 0.9,
      }},
      { selector: '.edge-holding_of', style: {
          'line-color': COL.greyM, 'target-arrow-color': COL.greyM, 'line-style': 'dashed',
      }},
      { selector: '.edge-presided_by', style: {
          'line-color': COL.greyL, 'target-arrow-color': COL.greyL, opacity: 0.4,
      }},
      { selector: 'node.type-mother', style: {
          'background-color': COL.ocre,
          'border-width': 2,
          'border-color': COL.ocre,
          label: 'data(label)',
          color: COL.encre,
          'font-size': 12,
          'font-weight': 600,
          'text-valign': 'bottom',
          'text-margin-y': 5,
          'text-background-color': COL.creme,
          'text-background-opacity': 0.85,
          'text-background-padding': 3,
          width: (ele) => motherSize(ele.data('n_subsidiaries_group')),
          height: (ele) => motherSize(ele.data('n_subsidiaries_group')),
      }},
      { selector: 'node.type-mother.alarm', style: {
          'background-color': COL.terre, 'border-color': COL.terre,
      }},
      { selector: 'node.type-mother.foreign', style: {
          'border-width': 4, 'border-color': COL.ardoise,
      }},
      { selector: 'node.type-country', style: {
          'background-color': COL.ardoise,
          shape: 'round-rectangle',
          width: 80, height: 32,
          label: 'data(label)',
          color: COL.creme,
          'font-size': 12,
          'font-weight': 700,
          'text-valign': 'center',
          'text-halign': 'center',
          'text-transform': 'uppercase',
      }},
      { selector: 'node.type-holding', style: {
          'background-color': COL.ivoire,
          'border-width': 1.5,
          'border-color': COL.greyM,
          'border-style': 'dashed',
          shape: 'ellipse',
          width: 14, height: 14,
          label: '',
      }},
      { selector: 'node.type-spv', style: {
          'background-color': '#e4d9c5',
          width: 8, height: 8,
          'border-width': 0,
          label: '',
      }},
      { selector: 'node:selected', style: {
          'border-width': 5,
          'border-color': COL.foret,
          'overlay-opacity': 0.15,
          'overlay-color': COL.foret,
      }},
      { selector: 'node.faded', style: { opacity: 0.15 } },
      { selector: 'edge.faded', style: { opacity: 0.08 } },
    ];
  }

  function applyFilters() {
    if (!cy) return;
    const wantAlarm = $('filter-alarm').checked;
    const wantForeign = $('filter-foreign').checked;
    const wantHoldings = $('show-holdings').checked;
    const wantSpv = $('show-spv').checked;

    const visibleNodeIds = new Set();

    cy.nodes().forEach((n) => {
      const t = n.data('type');
      let visible = true;
      if (t === 'mother') {
        if (wantAlarm && (n.data('max_signal_score') || 0) < 75) visible = false;
        if (wantForeign && (n.data('ultimate_country') || 'FRA') === 'FRA') visible = false;
      } else if (t === 'country') {
        visible = false;
      } else if (t === 'holding') {
        visible = wantHoldings;
      } else if (t === 'spv') {
        visible = wantSpv;
      }
      n.style('display', visible ? 'element' : 'none');
      if (visible) visibleNodeIds.add(n.id());
    });

    cy.nodes('.type-country').forEach((c) => {
      const incoming = c.connectedEdges().filter((e) =>
        e.source().data('type') === 'mother' && e.source().style('display') !== 'none'
      );
      const visible = incoming.length > 0;
      c.style('display', visible ? 'element' : 'none');
      if (visible) visibleNodeIds.add(c.id());
    });

    cy.edges().forEach((e) => {
      const ok = visibleNodeIds.has(e.source().id()) && visibleNodeIds.has(e.target().id());
      e.style('display', ok ? 'element' : 'none');
    });

    const visible = cy.elements().filter((el) => el.style('display') !== 'none');
    visible.layout({
      name: 'fcose',
      animate: true,
      animationDuration: 500,
      padding: 40,
      nodeSeparation: 75,
      idealEdgeLength: 120,
      numIter: 1500,
      tile: true,
      tilingPaddingVertical: 12,
      tilingPaddingHorizontal: 12,
    }).run();
  }

  function handleSearch(evt) {
    const q = (evt.target.value || '').trim().toLowerCase();
    if (!q) {
      cy.elements().removeClass('faded');
      return;
    }
    const matched = cy.nodes().filter((n) => {
      const label = String(n.data('canonical') || n.data('label') || n.data('denomination') || '').toLowerCase();
      return label.includes(q);
    });
    cy.elements().addClass('faded');
    matched.removeClass('faded');
    matched.neighborhood().removeClass('faded');
    matched.connectedEdges().removeClass('faded');
    if (matched.length > 0) {
      cy.animate({ fit: { eles: matched, padding: 80 }, duration: 400 });
    }
  }

  // --- safe DOM rendering helpers (no innerHTML for user content) ---
  function el(tag, opts) {
    const e = document.createElement(tag);
    if (!opts) return e;
    if (opts.cls) e.className = opts.cls;
    if (opts.text !== undefined && opts.text !== null) e.textContent = String(opts.text);
    if (opts.style) Object.assign(e.style, opts.style);
    return e;
  }
  function row(label, value, italic) {
    const div = el('div', { cls: 'block' });
    div.appendChild(el('div', { cls: 'block-label', text: label }));
    if (italic) {
      const span = el('span', { text: value });
      span.style.fontStyle = 'italic';
      div.appendChild(span);
    } else {
      div.appendChild(document.createTextNode(value));
    }
    return div;
  }
  function clear(node) { while (node.firstChild) node.removeChild(node.firstChild); }

  function showNodeDetails(d) {
    sidebar.classList.remove('sidebar-hidden');
    clear(sidebarContent);

    if (d.type === 'mother') {
      sidebarContent.appendChild(el('h3', { text: d.canonical }));
      let meta = 'SIREN ' + d.siren;
      if (d.denomination && d.denomination !== d.canonical) {
        meta += ' · ' + d.denomination;
      }
      sidebarContent.appendChild(el('p', { cls: 'meta', text: meta }));

      const empreinte = d.n_subsidiaries_group.toLocaleString('fr') + ' filiales (groupe)';
      const extra = d.n_subsidiaries_solo !== d.n_subsidiaries_group
        ? ' · ' + d.n_subsidiaries_solo + ' présidées directement'
        : '';
      sidebarContent.appendChild(row('empreinte RNE', empreinte + extra));

      if (d.president_current) {
        const block = el('div', { cls: 'block' });
        block.appendChild(el('div', { cls: 'block-label', text: 'président actuel' }));
        block.appendChild(document.createTextNode(d.president_current));
        if (d.president_is_legal) {
          const em = el('em', { text: ' (personne morale)' });
          block.appendChild(em);
        }
        sidebarContent.appendChild(block);
      }

      if (d.ultimate_country && d.ultimate_country !== 'FRA') {
        sidebarContent.appendChild(row('contrôle ultime',
          'via une entité en ' + (COUNTRY_LABELS[d.ultimate_country] || d.ultimate_country)
        ));
      }

      if (Array.isArray(d.signals) && d.signals.length > 0) {
        const block = el('div', { cls: 'block' });
        block.appendChild(el('div', { cls: 'block-label', text: 'signaux actionnariaux' }));
        d.signals.forEach((s) => {
          const span = el('span', { cls: s.is_alarm ? 'signal alarm' : 'signal' });
          span.appendChild(document.createTextNode(s.title || s.kind));
          const score = el('span', { cls: 'score', text: 'score ' + s.score });
          span.appendChild(score);
          block.appendChild(span);
        });
        sidebarContent.appendChild(block);
      }

      const cliHint = el('div', { cls: 'block' });
      cliHint.style.marginTop = '22px';
      cliHint.style.fontSize = '0.85rem';
      cliHint.style.color = COL.greyM;
      cliHint.appendChild(document.createTextNode('→ interroger en CLI : '));
      cliHint.appendChild(el('code', { text: 'panoptic operators' }));
      sidebarContent.appendChild(cliHint);
    } else if (d.type === 'country') {
      sidebarContent.appendChild(el('h3', { text: d.label }));
      sidebarContent.appendChild(el('p', { cls: 'meta', text: 'pays de contrôle · code ' + d.code }));
      const neighbors = cy.getElementById(d.id).incomers('node.type-mother');
      if (neighbors.length > 0) {
        const block = el('div', { cls: 'block' });
        block.appendChild(el('div', {
          cls: 'block-label',
          text: 'opérateurs contrôlés depuis ' + d.label,
        }));
        neighbors.forEach((m) => {
          block.appendChild(el('div', { text: '· ' + m.data('canonical') }));
        });
        sidebarContent.appendChild(block);
      }
    } else if (d.type === 'holding') {
      sidebarContent.appendChild(el('h3', { text: d.denomination || d.siren }));
      sidebarContent.appendChild(el('p', {
        cls: 'meta',
        text: 'SIREN ' + d.siren + ' · holding intermédiaire',
      }));
      sidebarContent.appendChild(row('rattachée au groupe', d.parent));
    } else if (d.type === 'spv') {
      sidebarContent.appendChild(el('h3', { text: d.denomination || d.siren }));
      sidebarContent.appendChild(el('p', {
        cls: 'meta',
        text: 'SIREN ' + d.siren + ' · société de projet',
      }));
      const block = el('div', { cls: 'block' });
      block.appendChild(el('div', { cls: 'block-label', text: 'présidée par' }));
      block.appendChild(document.createTextNode(d.parent));
      if (d.role_in_parent) {
        block.appendChild(el('em', { text: ' (' + d.role_in_parent + ')' }));
      }
      sidebarContent.appendChild(block);
    }
  }
})();
