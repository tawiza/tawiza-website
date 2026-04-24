import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://tawiza.fr',
  trailingSlash: 'always',
  build: {
    format: 'directory',
  },
  server: {
    host: '0.0.0.0',
    port: 4321,
  },
  vite: {
    server: {
      hmr: {
        clientPort: 4321,
      },
    },
  },
});
