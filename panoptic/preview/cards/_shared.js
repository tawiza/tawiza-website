/* Shared eye SVG injection for panoptic cards.
   Each card calls injectEye(selector) to render the 3AYNE eye.
   Uses DOM APIs (no innerHTML) to comply with security policy. */

(function (window) {
  const SVG_NS = 'http://www.w3.org/2000/svg';

  const RECTS = {
    lashes_top: [[8,0,1,2],[14,0,1,2],[20,0,1,2],[26,0,1,2],[32,0,1,2]],
    lid_top: [[6,3,1,1],[7,2,2,1],[9,2,4,1],[13,2,4,1],[17,2,6,1],
              [23,2,4,1],[27,2,4,1],[31,2,2,1],[33,3,1,1]],
    sclera: [[8,4,24,8],[9,3,22,1],[9,12,22,1],[11,13,18,1]],
    iris:   [[15,4,10,1],[14,5,12,1],[13,6,14,1],[13,7,14,1],
             [13,8,14,1],[13,9,14,1],[14,10,12,1],[15,11,10,1]],
    iris_inner: [[16,5,8,1],[15,6,10,1],[15,7,10,1],[15,8,10,1],
                 [15,9,10,1],[16,10,8,1]],
    pupil: [[18,6,4,4]],
    highlight_a: [[18,6,1,1]],
    highlight_b: [[19,6,1,1]],
    lid_bottom: [[8,13,2,1],[10,14,20,1],[30,13,2,1]],
  };

  function addRects(parent, rects, attrs) {
    for (const [x, y, w, h] of rects) {
      const r = document.createElementNS(SVG_NS, 'rect');
      r.setAttribute('x', x);
      r.setAttribute('y', y);
      r.setAttribute('width', w);
      r.setAttribute('height', h);
      for (const k in attrs) r.setAttribute(k, attrs[k]);
      parent.appendChild(r);
    }
  }

  function renderEye(variant) {
    // variant: 'default' (cream iris ocre pupil ink), 'avatar' (iris ink pupil ocre)
    const opts = variant === 'avatar'
      ? { iris: '#1a1612', iris_inner: '#3a342c', pupil: '#b45309', sclera: '#faf5ef' }
      : { iris: '#b45309', iris_inner: '#C1554D', pupil: '#1a1612', sclera: '#f3ebdd' };

    const svg = document.createElementNS(SVG_NS, 'svg');
    svg.setAttribute('viewBox', '0 0 40 16');
    svg.setAttribute('shape-rendering', 'crispEdges');
    svg.setAttribute('class', 'eye-svg');
    svg.setAttribute('role', 'img');
    svg.setAttribute('aria-label', '3AYNE');

    // groupes ink (cils, paupieres)
    const gLash = document.createElementNS(SVG_NS, 'g');
    gLash.setAttribute('class', 'eye-lashes-top');
    gLash.setAttribute('fill', 'currentColor');
    addRects(gLash, RECTS.lashes_top);
    svg.appendChild(gLash);

    const gLid = document.createElementNS(SVG_NS, 'g');
    gLid.setAttribute('class', 'eye-lid-top');
    gLid.setAttribute('fill', 'currentColor');
    addRects(gLid, RECTS.lid_top);
    svg.appendChild(gLid);

    const gScl = document.createElementNS(SVG_NS, 'g');
    gScl.setAttribute('fill', `var(--eye-sclera, ${opts.sclera})`);
    addRects(gScl, RECTS.sclera);
    svg.appendChild(gScl);

    const gIris = document.createElementNS(SVG_NS, 'g');
    gIris.setAttribute('fill', `var(--eye-iris, ${opts.iris})`);
    addRects(gIris, RECTS.iris);
    svg.appendChild(gIris);

    const gIrisIn = document.createElementNS(SVG_NS, 'g');
    gIrisIn.setAttribute('fill', `var(--eye-iris-inner, ${opts.iris_inner})`);
    addRects(gIrisIn, RECTS.iris_inner);
    svg.appendChild(gIrisIn);

    const gPup = document.createElementNS(SVG_NS, 'g');
    gPup.setAttribute('class', 'eye-pupil');
    gPup.setAttribute('fill', `var(--eye-pupil, ${opts.pupil})`);
    addRects(gPup, RECTS.pupil);
    addRects(gPup, RECTS.highlight_a, { fill: opts.sclera });
    addRects(gPup, RECTS.highlight_b, { fill: opts.sclera, opacity: '0.55' });
    svg.appendChild(gPup);

    const gBot = document.createElementNS(SVG_NS, 'g');
    gBot.setAttribute('fill', 'currentColor');
    addRects(gBot, RECTS.lid_bottom);
    svg.appendChild(gBot);

    return svg;
  }

  window.injectEye = function (target, variant) {
    const el = typeof target === 'string' ? document.querySelector(target) : target;
    if (!el) return;
    const svg = renderEye(variant || 'default');
    el.appendChild(svg);
  };
})(window);
