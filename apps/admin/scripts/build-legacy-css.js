import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const adminRoot = path.resolve(__dirname, '..');

console.log('[Build CSS] Compiling legacy Tailwind CSS...');
execSync('npx @tailwindcss/cli -i src/legacy-tailwind.css -o public/css/tailwind-legacy.min.css --minify', {
  cwd: adminRoot,
  stdio: 'inherit'
});

const sourceCss = path.join(adminRoot, 'public/css/tailwind-legacy.min.css');
const destinations = [
  path.join(adminRoot, 'public/customer.css'),
  path.join(adminRoot, 'public/vendor.css'),
  path.join(adminRoot, 'public/runner.css'),
  path.join(adminRoot, 'public/customer/customer.css'),
  path.join(adminRoot, 'public/vendor/vendor.css'),
  path.join(adminRoot, 'public/runner/runner.css')
];

for (const dest of destinations) {
  fs.copyFileSync(sourceCss, dest);
  console.log(`[Build CSS] Copied static CSS to ${path.relative(adminRoot, dest)}`);
}

console.log('[Build CSS] All legacy stylesheets successfully generated.');
