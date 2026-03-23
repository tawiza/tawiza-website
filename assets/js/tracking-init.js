// Initialisation du tracking sur les images du site
// Desactive sur mobile (pas de hover) et si prefers-reduced-motion
import { EdgeTracker } from './edge-tracker.js';
import { ZoneTracker } from './zone-tracker.js';

if (window.matchMedia('(hover: hover)').matches &&
    !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {

  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-tracking]').forEach(async (el) => {
      const type = el.dataset.tracking; // "edge", "zones", "both"
      const zonesFile = el.dataset.zones;

      if (type === 'edge' || type === 'both') {
        new EdgeTracker(el);
      }

      if (type === 'zones' || type === 'both') {
        const tracker = new ZoneTracker(el);
        if (zonesFile) {
          await tracker.loadZones(`/assets/data/zones/${zonesFile}.json`);
        }
      }
    });
  });
}
