/* ============================================================
   TAWIZA GLYPH SYSTEM v0.2
   Signature visuelle générative - une empreinte par page
   ============================================================

   Règles structurantes (le système a des partis-pris) :

   1. DÉTERMINISTE - même seed = même glyph, toujours.
      Le seed vient du pathname (ou d'un data-seed explicite).

   2. CADRÉ - chaque glyph est un objet encadré (carte IGN / mire) :
      • marqueurs d'angle aux 4 coins
      • label mono en bas : seed + taille + densité
      • pas juste un carré de hachures - un objet mesuré

   3. RYTHME EN COUCHES - 3 couches successives :
      • L0 : trame de fond (points discrets, densité variable)
      • L1 : traits principaux (hachures directionnelles par zones)
      • L2 : accents rares (marques de type différent, couleur d'alerte)

   4. VOCABULAIRE FINI - 6 types de marques, pas plus :
      diagonal /, anti-diagonal \, horizontal -, vertical |, point ·, croix ×

   5. PALETTE MINÉRALE - ocre + terre + forêt + encre, rien d'autre.

   6. DÉTERMINISME DE LA DENSITÉ - la densité globale est dérivée
      du slug (courts slugs = plus denses, longs = plus aérés).
      Donne une identité cohérente par territoire/article.

   ============================================================ */

(function () {
  'use strict';

  // ---------- API publique : TawizaGlyph ----------
  const TawizaGlyph = {
    render(container, opts) {
      opts = opts || {};
      const slug = opts.seed || container.dataset.seed || location.pathname || 'index';
      const size = opts.size || parseInt(container.dataset.size || '88', 10);
      const cells = opts.cells || parseInt(container.dataset.cells || '11', 10);
      const showFrame = opts.frame !== undefined ? opts.frame
                      : container.dataset.frame !== 'false';
      const showLabel = opts.label !== undefined ? opts.label
                      : container.dataset.label === 'true';

      renderGlyph(container, slug, size, cells, showFrame, showLabel);
    }
  };
  window.TawizaGlyph = TawizaGlyph;

  // ---------- Core ----------
  function hashSeed(str) {
    let h = 2166136261;
    for (let i = 0; i < str.length; i++) {
      h ^= str.charCodeAt(i);
      h = Math.imul(h, 16777619) >>> 0;
    }
    return h;
  }

  // PRNG déterministe (Mulberry32)
  function mulberry32(seed) {
    let a = seed >>> 0;
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function getPalette() {
    const css = getComputedStyle(document.documentElement);
    return {
      ocre:  (css.getPropertyValue('--ocre').trim()  || '#b45309'),
      terre: (css.getPropertyValue('--terre').trim() || '#C1554D'),
      foret: (css.getPropertyValue('--foret').trim() || '#2D6A4F'),
      ink:   (css.getPropertyValue('--ink').trim()   || '#1a1612'),
      bg:    (css.getPropertyValue('--bg').trim()    || '#faf5ef'),
      line:  (css.getPropertyValue('--line').trim()  || '#1a1612'),
      mute:  (css.getPropertyValue('--ink-mute').trim() || '#7a6e5e'),
    };
  }

  function clearNode(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
  }

  function renderGlyph(container, slug, size, cells, showFrame, showLabel) {
    const seed = hashSeed(slug);
    const rng = mulberry32(seed);
    const pal = getPalette();

    clearNode(container);
    container.classList.add('glyph-root');

    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const labelH = showLabel ? 18 : 0;

    const c = document.createElement('canvas');
    c.width  = size * dpr;
    c.height = (size + labelH) * dpr;
    // Do NOT fix inline pixel dimensions here; let CSS size the canvas
    // via its parent container. This allows responsive layouts to work
    // naturally (the render buffer stays at size*dpr so image remains crisp).
    c.style.display = 'block';
    c.style.width = '100%';
    c.style.height = '100%';
    c.style.maxWidth = '100%';
    c.style.maxHeight = '100%';
    container.appendChild(c);

    const ctx = c.getContext('2d');
    ctx.scale(dpr, dpr);
    ctx.lineCap = 'round';

    // --- Paramètres déterministes dérivés du seed/slug ---
    const slugLen = slug.length;
    const targetDensity = 0.62 - Math.min(0.28, (slugLen - 5) * 0.012);

    const palSeq = [pal.ocre, pal.terre, pal.foret, pal.ink];
    const dominant = palSeq[seed % 4];
    const secondary = palSeq[(seed * 7 + 1) % 4];
    const accent = palSeq[(seed * 13 + 3) % 4];

    const veinAngle = (seed % 4) * 45;

    if (showFrame) drawFrame(ctx, size, pal);

    const inset = showFrame ? 5 : 1;
    const area = size - inset * 2;
    const cell = area / cells;

    // === Couche L0 : trame de fond (points rares) ===
    ctx.save();
    ctx.translate(inset, inset);
    for (let y = 0; y < cells; y++) {
      for (let x = 0; x < cells; x++) {
        if (rng() < 0.15) {
          ctx.fillStyle = pal.mute;
          const cx = x * cell + cell * 0.5;
          const cy = y * cell + cell * 0.5;
          ctx.fillRect(cx - 0.5, cy - 0.5, 1, 1);
        }
      }
    }
    ctx.restore();

    // === Couche L1 : hachures principales ===
    ctx.save();
    ctx.translate(inset, inset);
    ctx.lineWidth = Math.max(1, cell * 0.11);
    for (let y = 0; y < cells; y++) {
      for (let x = 0; x < cells; x++) {
        const r = rng();
        if (r > targetDensity) continue;

        const cx = x * cell + cell * 0.5;
        const cy = y * cell + cell * 0.5;
        const len = cell * 0.65;

        let kind;
        if (rng() < 0.55) kind = veinAngle / 45;
        else kind = Math.floor(rng() * 4);

        const colorRoll = rng();
        ctx.strokeStyle = colorRoll < 0.58 ? dominant
                        : colorRoll < 0.88 ? secondary
                        : pal.ink;

        ctx.beginPath();
        if (kind === 0) {
          ctx.moveTo(cx - len/2, cy);
          ctx.lineTo(cx + len/2, cy);
        } else if (kind === 1) {
          ctx.moveTo(cx - len/2, cy - len/2);
          ctx.lineTo(cx + len/2, cy + len/2);
        } else if (kind === 2) {
          ctx.moveTo(cx, cy - len/2);
          ctx.lineTo(cx, cy + len/2);
        } else {
          ctx.moveTo(cx - len/2, cy + len/2);
          ctx.lineTo(cx + len/2, cy - len/2);
        }
        ctx.stroke();
      }
    }
    ctx.restore();

    // === Couche L2 : accents rares (croix, points carrés) ===
    ctx.save();
    ctx.translate(inset, inset);
    const accentCount = 2 + (seed % 4);
    for (let i = 0; i < accentCount; i++) {
      const gx = Math.floor(rng() * cells);
      const gy = Math.floor(rng() * cells);
      const cx = gx * cell + cell * 0.5;
      const cy = gy * cell + cell * 0.5;
      ctx.strokeStyle = accent;
      ctx.fillStyle = accent;
      ctx.lineWidth = Math.max(1, cell * 0.13);
      if (rng() < 0.5) {
        const s = cell * 0.38;
        ctx.beginPath();
        ctx.moveTo(cx - s, cy - s); ctx.lineTo(cx + s, cy + s);
        ctx.moveTo(cx - s, cy + s); ctx.lineTo(cx + s, cy - s);
        ctx.stroke();
      } else {
        const s = cell * 0.28;
        ctx.fillRect(cx - s/2, cy - s/2, s, s);
      }
    }
    ctx.restore();

    // --- Label sous le glyph ---
    if (showLabel) {
      const shortSeed = (seed >>> 0).toString(16).padStart(8, '0').slice(0, 6);
      const shortSlug = slug.length > 22 ? slug.slice(0, 20) + '..' : slug;
      ctx.fillStyle = pal.mute;
      ctx.font = '10px "JetBrains Mono", ui-monospace, monospace';
      ctx.textBaseline = 'middle';
      ctx.textAlign = 'left';
      ctx.fillText('// ' + shortSlug, 0, size + labelH * 0.35);
      ctx.textAlign = 'right';
      ctx.fillText(cells + 'x' + cells + ' / ' + shortSeed, size, size + labelH * 0.35);
    }
  }

  // ---------- Frame IGN / mire ----------
  function drawFrame(ctx, size, pal) {
    ctx.save();
    ctx.strokeStyle = pal.line;
    ctx.lineWidth = 0.5;
    ctx.strokeRect(0.5, 0.5, size - 1, size - 1);

    const m = 8, o = 2;
    ctx.lineWidth = 1;
    ctx.strokeStyle = pal.ocre;

    const corners = [
      [o, o,       o + m, o,       o, o + m],
      [size - o, o,  size - o - m, o,  size - o, o + m],
      [o, size - o,  o + m, size - o,  o, size - o - m],
      [size - o, size - o,  size - o - m, size - o,  size - o, size - o - m],
    ];
    corners.forEach(function (arr) {
      ctx.beginPath();
      ctx.moveTo(arr[2], arr[3]);
      ctx.lineTo(arr[0], arr[1]);
      ctx.lineTo(arr[4], arr[5]);
      ctx.stroke();
    });

    ctx.lineWidth = 0.5;
    ctx.strokeStyle = pal.mute;
    const mid = size / 2;
    ctx.beginPath();
    ctx.moveTo(mid, 0);       ctx.lineTo(mid, 3);
    ctx.moveTo(mid, size);    ctx.lineTo(mid, size - 3);
    ctx.moveTo(0, mid);       ctx.lineTo(3, mid);
    ctx.moveTo(size, mid);    ctx.lineTo(size - 3, mid);
    ctx.stroke();

    ctx.restore();
  }

  // ---------- Auto-mount ----------
  function mountAll() {
    const els = document.querySelectorAll('.glyph-slot, [data-glyph]');
    els.forEach(function (el) { TawizaGlyph.render(el); });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mountAll);
  } else {
    mountAll();
  }
})();
