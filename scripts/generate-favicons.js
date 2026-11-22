import { chromium } from '../apps/admin/node_modules/playwright-core/index.mjs';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');
const publicDir = path.resolve(rootDir, 'apps', 'admin', 'public');

// Authentic Apna GaonBazaar Brand Logo Vector SVG
// Signature Emerald Green (#0C8346), Crisp White (#FFFFFF), Soft Mint Tint (#E8F5E9)
const logoSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="512" height="512">
  <defs>
    <linearGradient id="gb-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0E9352" />
      <stop offset="100%" stop-color="#075E34" />
    </linearGradient>
  </defs>
  <!-- Rounded Square Container in GaonBazaar Signature Emerald Green -->
  <rect width="64" height="64" rx="14" fill="url(#gb-grad)" />
  
  <!-- Village Storefront Roof in Crisp White -->
  <path d="M32 9L10 25H54L32 9Z" fill="#FFFFFF" />
  <!-- Rooftop Flagpole & Flag -->
  <path d="M32 5V13M32 5L40 8.5L32 12" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
  
  <!-- Storefront Body in Soft Mint Tint (#E8F5E9) -->
  <rect x="15" y="25" width="34" height="22" rx="2" fill="#E8F5E9" />
  
  <!-- Left Pillar, Central Entrance, Right Pillar in GaonBazaar Green -->
  <rect x="19" y="28" width="5" height="16" rx="1" fill="#0C8346" />
  <rect x="29" y="31" width="6" height="13" rx="1" fill="#0C8346" />
  <rect x="40" y="28" width="5" height="16" rx="1" fill="#0C8346" />
  
  <!-- Delivery Cart Undercarriage Axle & Wheels in Crisp White -->
  <path d="M13 52H51" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" />
  <circle cx="21" cy="52" r="3.5" fill="#FFFFFF" />
  <circle cx="43" cy="52" r="3.5" fill="#FFFFFF" />
</svg>`;

async function generate() {
  console.log('[Favicon Generator] Launching Chrome...');
  const browser = await chromium.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: true
  });

  const page = await browser.newPage();

  // Save the master SVG file
  const svgPath = path.join(publicDir, 'favicon.svg');
  fs.writeFileSync(svgPath, logoSvg, 'utf-8');
  console.log(`[Favicon Generator] Saved master SVG to ${path.relative(rootDir, svgPath)}`);

  const sizes = [
    { name: 'favicon-512x512.png', size: 512 },
    { name: 'favicon-192x192.png', size: 192 },
    { name: 'apple-touch-icon.png', size: 180 },
    { name: 'favicon-96x96.png', size: 96 },
    { name: 'favicon.png', size: 96 },
    { name: 'favicon-48x48.png', size: 48 },
    { name: 'favicon-32x32.png', size: 32 },
    { name: 'favicon-16x16.png', size: 16 },
  ];

  for (const s of sizes) {
    const html = `<!DOCTYPE html>
<html>
<head>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { width: ${s.size}px; height: ${s.size}px; overflow: hidden; background: transparent; }
    svg { width: ${s.size}px; height: ${s.size}px; display: block; }
  </style>
</head>
<body>
  ${logoSvg}
</body>
</html>`;

    await page.setViewportSize({ width: s.size, height: s.size });
    await page.setContent(html);

    const outPath = path.join(publicDir, s.name);
    await page.screenshot({ path: outPath, omitBackground: true });
    console.log(`[Favicon Generator] Rendered ${s.name} (${s.size}x${s.size}) -> ${path.relative(rootDir, outPath)}`);
  }

  await browser.close();
  console.log('[Favicon Generator] PNG rasterization complete.');
}

generate().catch(err => {
  console.error('[Favicon Generator] Error:', err);
  process.exit(1);
});
