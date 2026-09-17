import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { execSync } from 'node:child_process';

function getBuildVersion() {
  try {
    return execSync('git describe --always --dirty', {
      stdio: ['ignore', 'pipe', 'ignore']
    })
      .toString()
      .trim();
  } catch {
    return 'unknown';
  }
}

const buildVersion = getBuildVersion();

export default defineConfig({
  plugins: [svelte()],
  define: {
    __APP_BUILD_VERSION__: JSON.stringify(buildVersion)
  },
  publicDir: false,
  build: {
    outDir: 'public',
    emptyOutDir: false
  }
});
