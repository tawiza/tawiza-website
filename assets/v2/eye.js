/* 3AYNE - l'œil qui joue
   - Pupille qui suit le curseur dans une fenêtre contrainte
   - Clignement aléatoire (6-14s)
   - Au clic : wink (clin d'œil vif)
   - Change de couleur iris selon scroll (chaud → froid)

   Respecte prefers-reduced-motion
*/
(function () {
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const eye = document.querySelector('.eye-root');
  if (!eye) return;

  const svg    = eye.querySelector('.eye-svg');
  const pupil  = eye.querySelector('.eye-pupil');
  const blink  = eye.querySelector('.blink-top');
  if (!svg || !pupil) return;

  // --- Pupille suit curseur ---
  const MAX_X = 3; // pixels d'amplitude horizontale
  const MAX_Y = 2; // amplitude verticale (moins, œil plus large que haut)

  function trackPointer(x, y) {
    const rect = svg.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top  + rect.height / 2;
    // Normalise entre -1 et 1 sur une distance de 400px
    const nx = Math.max(-1, Math.min(1, (x - cx) / 400));
    const ny = Math.max(-1, Math.min(1, (y - cy) / 300));
    eye.style.setProperty('--pupil-x', (nx * MAX_X) + 'px');
    eye.style.setProperty('--pupil-y', (ny * MAX_Y) + 'px');
  }

  if (!reduced) {
    window.addEventListener('pointermove', e => trackPointer(e.clientX, e.clientY), { passive: true });
    window.addEventListener('touchmove',   e => {
      if (e.touches[0]) trackPointer(e.touches[0].clientX, e.touches[0].clientY);
    }, { passive: true });
  }

  // --- Clignement aléatoire ---
  // On anime l'attribut height du rect `.blink-top` de 0 à 10 et retour
  function doBlink(doubled = false) {
    if (!blink || reduced) return;
    const start = performance.now();
    const dur = 180;
    function frame(t) {
      const p = (t - start) / dur;
      if (p < 0.5) {
        blink.setAttribute('height', (10 * (p * 2)).toFixed(2));
      } else if (p < 1) {
        blink.setAttribute('height', (10 * (1 - (p - 0.5) * 2)).toFixed(2));
      } else {
        blink.setAttribute('height', '0');
        if (doubled) setTimeout(() => doBlink(false), 140);
        return;
      }
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  function scheduleBlink() {
    const delay = 6000 + Math.random() * 8000;
    setTimeout(() => { doBlink(false); scheduleBlink(); }, delay);
  }
  if (!reduced) scheduleBlink();

  // --- Wink au clic ---
  eye.addEventListener('click', () => doBlink(true));
  eye.style.cursor = 'pointer';

  // --- Scroll : iris change de teinte ---
  // Haut de page = ocre chaud, bas = vert foret
  function updateMood() {
    const max = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
    const t = Math.min(1, window.scrollY / max);
    // interp ocre #b45309 → terre #C1554D → foret #2D6A4F
    const colors = [
      [180, 83, 9],    // ocre
      [193, 85, 77],   // terre
      [45, 106, 79],   // foret
    ];
    const seg = t < 0.5 ? 0 : 1;
    const local = t < 0.5 ? t * 2 : (t - 0.5) * 2;
    const a = colors[seg];
    const b = colors[seg + 1];
    const rgb = a.map((v, i) => Math.round(v + (b[i] - v) * local));
    eye.style.setProperty('--eye-iris', `rgb(${rgb.join(',')})`);
    // Iris-inner = version sombrée de l'iris
    const inner = rgb.map(v => Math.round(v * 0.78));
    eye.style.setProperty('--eye-iris-inner', `rgb(${inner.join(',')})`);
  }
  if (!reduced) {
    window.addEventListener('scroll', updateMood, { passive: true });
    updateMood();
  }
})();
