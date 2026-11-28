const fs = require('fs');
const crypto = require('crypto');
const { execSync } = require('child_process');

const aabs = [
  { name: 'Customer', path: 'apps/customer/build/app/outputs/bundle/release/app-release.aab' },
  { name: 'Vendor', path: 'apps/vendor/build/app/outputs/bundle/release/app-release.aab' },
  { name: 'Runner', path: 'apps/runner/build/app/outputs/bundle/release/app-release.aab' },
];

for (const a of aabs) {
  if (fs.existsSync(a.path)) {
    const stats = fs.statSync(a.path);
    const buf = fs.readFileSync(a.path);
    const sha256 = crypto.createHash('sha256').update(buf).digest('hex');
    console.log(`=== ${a.name} AAB ===`);
    console.log(`Path: ${a.path}`);
    console.log(`Size: ${(stats.size / (1024 * 1024)).toFixed(2)} MB (${stats.size} bytes)`);
    console.log(`SHA-256: ${sha256}`);
    try {
      const verify = execSync(`jarsigner -verify -certs "${a.path}"`).toString();
      const isSigned = verify.includes('jar verified');
      console.log(`Jarsigner Status: ${isSigned ? 'VERIFIED SIGNED' : 'CHECK FAILED'}`);
      const certLine = verify.split('\n').find(l => l.includes('[certificate'));
      if (certLine) console.log(`Cert: ${certLine.trim()}`);
    } catch (e) {
      console.log(`Jarsigner check error: ${e.message}`);
    }
  } else {
    console.log(`MISSING: ${a.path}`);
  }
}
