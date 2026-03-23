// Detection de zones territoriales sur les images
// Chaque zone correspond a un element reel de la commune
export class ZoneTracker {
  constructor(container, opts = {}) {
    this.el = container;
    this.zones = opts.zones || [];
    this.cats = {
      "Equipement public": "#E24B4A",
      "Habitat": "#D85A30",
      "Activite economique": "#BA7517",
      "Espace vert": "#1D9E75",
      "Hydrographie": "#378ADD",
      "Infrastructure": "#7F77DD",
    };
    this.svg = null;
    this.hud = null;
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

    this.hud = document.createElement('div');
    this.hud.classList.add('tracking-hud');
    this.el.appendChild(this.hud);
    this._updateHud(null);

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
    this.active = true;

    if (this._raf) cancelAnimationFrame(this._raf);
    this._raf = requestAnimationFrame(() => this.draw(mx, my));
  }

  draw(mx, my) {
    while (this.svg.firstChild) this.svg.removeChild(this.svg.firstChild);

    let hoveredZone = null;

    for (const z of this.zones) {
      const zx = z.x * this.vw;
      const zy = z.y * this.vh;
      const zw = z.w * this.vw;
      const zh = z.h * this.vh;
      const cx = zx + zw / 2;
      const cy = zy + zh / 2;

      const dx = mx - cx;
      const dy = my - cy;
      const dist = Math.sqrt(dx * dx + dy * dy);
      const maxDist = Math.max(this.vw, this.vh) * 0.25;
      const prox = Math.max(0, 1 - dist / maxDist);

      const inBox = mx >= zx && mx <= zx + zw && my >= zy && my <= zy + zh;
      if (inBox) hoveredZone = z;

      const color = this.cats[z.cat] || '#378ADD';
      const op = inBox ? 0.8 : Math.max(0, prox * 0.5);
      if (op < 0.02) continue;

      // Bounding box
      const box = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      box.setAttribute('x', zx);
      box.setAttribute('y', zy);
      box.setAttribute('width', zw);
      box.setAttribute('height', zh);
      box.setAttribute('fill', inBox ? color : 'none');
      box.setAttribute('fill-opacity', inBox ? '0.08' : '0');
      box.setAttribute('stroke', color);
      box.setAttribute('stroke-width', inBox ? '2' : '1');
      box.setAttribute('opacity', op);
      this.svg.appendChild(box);

      // Marqueurs de coin
      const cornerLen = Math.min(zw, zh) * (inBox ? 0.25 : 0.15) * Math.min(1, prox * 2 + 0.3);
      if (cornerLen > 2) {
        this._drawCorners(zx, zy, zw, zh, cornerLen, color, op);
      }

      // Label + confiance (visible si assez proche)
      if (prox > 0.12 || inBox) {
        const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        label.setAttribute('x', zx + 4);
        label.setAttribute('y', zy - 6);
        label.setAttribute('fill', color);
        label.setAttribute('font-family', 'monospace');
        label.setAttribute('font-size', '10');
        label.setAttribute('opacity', Math.min(1, op + 0.3));
        label.textContent = `${z.label} [${z.conf.toFixed(1)}%]`;
        this.svg.appendChild(label);
      }

      // Description (visible si dans la zone)
      if (inBox && z.desc) {
        const desc = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        desc.setAttribute('x', zx + 4);
        desc.setAttribute('y', zy + zh + 14);
        desc.setAttribute('fill', color);
        desc.setAttribute('font-family', 'monospace');
        desc.setAttribute('font-size', '9');
        desc.setAttribute('opacity', '0.8');
        desc.textContent = z.desc.length > 80 ? z.desc.substring(0, 77) + '...' : z.desc;
        this.svg.appendChild(desc);

        // Point central
        const dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        dot.setAttribute('cx', cx);
        dot.setAttribute('cy', cy);
        dot.setAttribute('r', '3');
        dot.setAttribute('fill', color);
        dot.setAttribute('opacity', '0.6');
        this.svg.appendChild(dot);

        // Liens vers zones de meme categorie
        this._drawCategoryLinks(z, cx, cy, color);
      }
    }

    this._updateHud(hoveredZone);
  }

  _drawCorners(x, y, w, h, len, color, op) {
    const corners = [
      [x, y, x + len, y, x, y + len],
      [x + w, y, x + w - len, y, x + w, y + len],
      [x, y + h, x + len, y + h, x, y + h - len],
      [x + w, y + h, x + w - len, y + h, x + w, y + h - len],
    ];
    for (const [cx, cy, hx, hy, vx, vy] of corners) {
      const l1 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      l1.setAttribute('x1', cx); l1.setAttribute('y1', cy);
      l1.setAttribute('x2', hx); l1.setAttribute('y2', hy);
      l1.setAttribute('stroke', color); l1.setAttribute('stroke-width', '2');
      l1.setAttribute('opacity', op);
      this.svg.appendChild(l1);

      const l2 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      l2.setAttribute('x1', cx); l2.setAttribute('y1', cy);
      l2.setAttribute('x2', vx); l2.setAttribute('y2', vy);
      l2.setAttribute('stroke', color); l2.setAttribute('stroke-width', '2');
      l2.setAttribute('opacity', op);
      this.svg.appendChild(l2);
    }
  }

  _drawCategoryLinks(zone, cx, cy, color) {
    for (const other of this.zones) {
      if (other === zone || other.cat !== zone.cat) continue;
      const ox = other.x * this.vw + other.w * this.vw / 2;
      const oy = other.y * this.vh + other.h * this.vh / 2;

      const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      line.setAttribute('x1', cx); line.setAttribute('y1', cy);
      line.setAttribute('x2', ox); line.setAttribute('y2', oy);
      line.setAttribute('stroke', color);
      line.setAttribute('stroke-width', '1');
      line.setAttribute('stroke-dasharray', '4 4');
      line.setAttribute('opacity', '0.3');
      this.svg.appendChild(line);

      const dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      dot.setAttribute('cx', ox); dot.setAttribute('cy', oy);
      dot.setAttribute('r', '4');
      dot.setAttribute('fill', 'none');
      dot.setAttribute('stroke', color);
      dot.setAttribute('stroke-width', '1');
      dot.setAttribute('opacity', '0.4');
      this.svg.appendChild(dot);
    }
  }

  _updateHud(zone) {
    // Le HUD n'affiche que du texte statique, pas d'input utilisateur
    while (this.hud.firstChild) this.hud.removeChild(this.hud.firstChild);

    const line1 = document.createElement('span');
    line1.style.color = '#378ADD';
    line1.textContent = `TAWIZA // ANALYSE TERRITORIALE`;
    this.hud.appendChild(line1);

    const line2 = document.createElement('span');
    line2.style.color = '#85B7EB';
    line2.textContent = `${this.zones.length} zones detectees`;
    this.hud.appendChild(line2);

    if (zone) {
      const color = this.cats[zone.cat] || '#378ADD';

      const line3 = document.createElement('span');
      line3.style.color = color;
      line3.textContent = zone.label;
      this.hud.appendChild(line3);

      const line4 = document.createElement('span');
      line4.style.color = color;
      line4.style.opacity = '0.8';
      line4.textContent = `${zone.cat} - ${zone.conf.toFixed(1)}%`;
      this.hud.appendChild(line4);

      if (zone.desc) {
        const line5 = document.createElement('span');
        line5.style.color = '#ccc';
        line5.style.fontSize = '9px';
        line5.textContent = zone.desc;
        this.hud.appendChild(line5);
      }
    }
  }

  async loadZones(url) {
    const res = await fetch(url);
    this.zones = await res.json();
  }

  onLeave() {
    this.active = false;
    if (this.svg) while (this.svg.firstChild) this.svg.removeChild(this.svg.firstChild);
    this._updateHud(null);
  }

  destroy() {
    this.el.removeEventListener('mousemove', this._onMove);
    this.el.removeEventListener('mouseleave', this._onLeave);
    if (this._ro) this._ro.disconnect();
    if (this._raf) cancelAnimationFrame(this._raf);
    if (this.svg && this.svg.parentNode) this.svg.parentNode.removeChild(this.svg);
    if (this.hud && this.hud.parentNode) this.hud.parentNode.removeChild(this.hud);
  }
}
