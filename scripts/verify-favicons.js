import fs from 'fs';
import assert from 'assert';

// 1. Verify files exist in apps/admin/public and have positive size
const files = [
  'favicon.ico',
  'favicon.svg',
  'favicon.png',
  'favicon-16x16.png',
  'favicon-32x32.png',
  'favicon-48x48.png',
  'favicon-96x96.png',
  'favicon-192x192.png',
  'favicon-512x512.png',
  'apple-touch-icon.png',
  'icons/Icon-192.png',
  'icons/Icon-512.png',
  'icons/Icon-maskable-192.png',
  'icons/Icon-maskable-512.png'
];

for (const f of files) {
  const p = 'apps/admin/public/' + f;
  assert(fs.existsSync(p), 'Missing: ' + p);
  const stat = fs.statSync(p);
  assert(stat.size > 0, 'Zero size: ' + p);
  console.log('OK file:', f, stat.size, 'bytes');
}

// 2. Check HTML files contain favicon links
const htmlFiles = [
  'apps/admin/index.html',
  'apps/admin/public/customer/index.html',
  'apps/admin/public/vendor/index.html',
  'apps/admin/public/runner/index.html',
  'apps/admin/public/terms.html',
  'apps/admin/public/privacy-policy.html',
  'apps/admin/public/delete-account.html'
];

for (const hf of htmlFiles) {
  const content = fs.readFileSync(hf, 'utf8');
  assert(content.includes('rel="icon"'), 'No rel="icon" in ' + hf);
  assert(content.includes('favicon.ico') || content.includes('/favicon.ico'), 'No favicon.ico in ' + hf);
  assert(!content.includes('data:image/svg+xml'), 'Generic inline data:image in ' + hf);
  console.log('OK html:', hf);
}

// 3. Verify robots.txt
const robots = fs.readFileSync('apps/admin/public/robots.txt', 'utf8');
assert(robots.includes('Googlebot-Image'), 'robots.txt missing Googlebot-Image');
assert(robots.includes('Allow: /favicon.ico'), 'robots.txt missing /favicon.ico');
console.log('OK robots.txt');

console.log('\n[ALL FAVICON CHECKS PASSED]');
