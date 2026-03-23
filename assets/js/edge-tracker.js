// Edge detection - cercle d'analyse qui suit le curseur
// Le SVG genere est entierement controle par le code (pas d'input utilisateur)
// donc innerHTML est safe ici - aucune donnee externe non sanitisee.
export class EdgeTracker {
  constructor(container, opts = {}) {
    this.el = container;
    this.color = opts.color || '#378ADD';
    this.trailColor = opts.trailColor || '#85B7EB';
    this.r = opts.radius || 40;
    this.rayCount = opts.rayCount || 20;
    this.trailDur = opts.trailDuration || 1800;
    this.trail = [];
    this.svg = null;
    this.vw = 0;
    this.vh = 0;
    this.active = false;
    this._onMove = this.onMove.bind(this);
    this._onLeave = this.onLeave.bind(this);
    this._raf = null;
    this.init();
  }

  init() {
    const rect = this.el.getBoundingClientRect();
    this.vw = rect.width;
    this.vh = rect.height;

    this.svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    this.svg.classList.add('tracking-svg');
    this.svg.setAttribute('viewBox', `0 0 ${this.vw} ${this.vh}`);
    this.svg.setAttribute('preserveAspectRatio', 'none');
    this.el.appendChild(this.svg);

    this.el.addEventListener('mousemove', this._onMove);
    this.el.addEventListener('mouseleave', this._onLeave);

    if (window.ResizeObserver) {
      this._ro = new ResizeObserver(() => {
        const r = this.el.getBoundingClientRect();
        this.vw = r.width;
        this.vh = r.height;
        this.svg.setAttribute('viewBox', `0 0 ${this.vw} ${this.vh}`);
      });
      this._ro.observe(this.el);
    }
  }

  onMove(e) {
    const rect = this.el.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const now = Date.now();

    this.trail.push({ x: mx, y: my, t: now });
    this.trail = this.trail.filter(p => now - p.t < this.trailDur);
    this.active = true;

    if (this._raf) cancelAnimationFrame(this._raf);
    this._raf = requestAnimationFrame(() => this.draw(mx, my, now));
  }

  draw(mx, my, now) {
    // Tout le SVG est genere a partir de valeurs numeriques internes,
    // aucune donnee utilisateur n'est injectee.
    const c = this.color;
    const tc = this.trailColor;
    const r = this.r;
    const rot = now * 0.0012;

    // On vide et reconstruit le SVG via DOM pur
    while (this.svg.firstChild) this.svg.removeChild(this.svg.firstChild);

    // Trail
    if (this.trail.length > 1) {
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      let d = `M ${this.trail[0].x} ${this.trail[0].y}`;
      for (let i = 1; i < this.trail.length; i++) {
        d += ` L ${this.trail[i].x} ${this.trail[i].y}`;
      }
      path.setAttribute('d', d);
      path.setAttribute('fill', 'none');
      path.setAttribute('stroke', tc);
      path.setAttribute('stroke-width', '1.5');
      path.setAttribute('opacity', '0.3');
      this.svg.appendChild(path);

      for (let i = 0; i < this.trail.length; i += 3) {
        const p = this.trail[i];
        const age = (now - p.t) / this.trailDur;
        const op = Math.max(0, 0.4 - age * 0.4);
        const dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        dot.setAttribute('cx', p.x);
        dot.setAttribute('cy', p.y);
        dot.setAttribute('r', '2');
        dot.setAttribute('fill', tc);
        dot.setAttribute('opacity', op);
        this.svg.appendChild(dot);
      }
    }

    // Cercle detection (pointilles)
    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('cx', mx);
    circle.setAttribute('cy', my);
    circle.setAttribute('r', r);
    circle.setAttribute('fill', 'none');
    circle.setAttribute('stroke', c);
    circle.setAttribute('stroke-width', '1');
    circle.setAttribute('stroke-dasharray', '4 3');
    circle.setAttribute('opacity', '0.7');
    this.svg.appendChild(circle);

    // Rayons rotatifs
    for (let i = 0; i < this.rayCount; i++) {
      const angle = (i * (360 / this.rayCount) + rot * 57.3) * Math.PI / 180;
      const len = r + 6 + Math.sin(now * 0.003 + i * 0.5) * 8;
      const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      line.setAttribute('x1', mx + Math.cos(angle) * r);
      line.setAttribute('y1', my + Math.sin(angle) * r);
      line.setAttribute('x2', mx + Math.cos(angle) * len);
      line.setAttribute('y2', my + Math.sin(angle) * len);
      line.setAttribute('stroke', c);
      line.setAttribute('stroke-width', '0.8');
      line.setAttribute('opacity', '0.5');
      this.svg.appendChild(line);
    }

    // Crosshair
    const ch1 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    ch1.setAttribute('x1', mx - 6); ch1.setAttribute('y1', my);
    ch1.setAttribute('x2', mx + 6); ch1.setAttribute('y2', my);
    ch1.setAttribute('stroke', c); ch1.setAttribute('stroke-width', '0.8'); ch1.setAttribute('opacity', '0.6');
    this.svg.appendChild(ch1);

    const ch2 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    ch2.setAttribute('x1', mx); ch2.setAttribute('y1', my - 6);
    ch2.setAttribute('x2', mx); ch2.setAttribute('y2', my + 6);
    ch2.setAttribute('stroke', c); ch2.setAttribute('stroke-width', '0.8'); ch2.setAttribute('opacity', '0.6');
    this.svg.appendChild(ch2);

    // Coordonnees
    const px = ((mx / this.vw) * 100).toFixed(1);
    const py = ((my / this.vh) * 100).toFixed(1);
    const txt = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    txt.setAttribute('x', mx + r + 8);
    txt.setAttribute('y', my - 4);
    txt.setAttribute('fill', c);
    txt.setAttribute('font-family', 'monospace');
    txt.setAttribute('font-size', '9');
    txt.setAttribute('opacity', '0.7');
    txt.textContent = `${px}% ${py}%`;
    this.svg.appendChild(txt);
  }

  onLeave() {
    this.trail = [];
    this.active = false;
    if (this.svg) while (this.svg.firstChild) this.svg.removeChild(this.svg.firstChild);
  }

  destroy() {
    this.el.removeEventListener('mousemove', this._onMove);
    this.el.removeEventListener('mouseleave', this._onLeave);
    if (this._ro) this._ro.disconnect();
    if (this._raf) cancelAnimationFrame(this._raf);
    if (this.svg && this.svg.parentNode) this.svg.parentNode.removeChild(this.svg);
  }
}
