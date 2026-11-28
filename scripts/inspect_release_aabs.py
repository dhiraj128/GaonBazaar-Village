import zipfile
import hashlib
import os
import subprocess
import re

aabs = [
    {
        "name": "Customer",
        "path": r"apps/customer/build/app/outputs/bundle/release/app-release.aab",
        "expected_pkg": "com.gaonbazaar.customer"
    },
    {
        "name": "Vendor",
        "path": r"apps/vendor/build/app/outputs/bundle/release/app-release.aab",
        "expected_pkg": "com.gaonbazaar.vendor"
    },
    {
        "name": "Runner",
        "path": r"apps/runner/build/app/outputs/bundle/release/app-release.aab",
        "expected_pkg": "com.gaonbazaar.runner"
    }
]

print("=" * 80)
print("INDEPENDENT ANDROID APP BUNDLE (.AAB) INSPECTION & METADATA REPORT")
print("=" * 80)

for item in aabs:
    p = item["path"]
    name = item["name"]
    print(f"\n--- Application: {name} ---")
    if not os.path.exists(p):
        print(f"ERROR: Bundle not found at {p}")
        continue

    # 1. File size & SHA-256
    file_bytes = open(p, "rb").read()
    size_bytes = len(file_bytes)
    sha256 = hashlib.sha256(file_bytes).hexdigest()
    print(f"Location: {p}")
    print(f"Size: {size_bytes} bytes ({size_bytes / (1024*1024):.2f} MB)")
    print(f"SHA-256: {sha256}")

    # 2. Signature verification with jarsigner
    try:
        verify_res = subprocess.run(["jarsigner", "-verify", "-certs", p], capture_output=True, text=True)
        is_verified = "jar verified" in verify_res.stdout
        print(f"Jarsigner Status: {'VERIFIED SIGNED' if is_verified else 'FAILED'}")
        for line in verify_res.stdout.splitlines():
            if "[certificate is valid" in line or "CN=Apna GaonBazaar" in line:
                print(f"Certificate: {line.strip()}")
    except Exception as e:
        print(f"Jarsigner error: {e}")

    # 3. Extract and parse binary protobuf AndroidManifest.xml from inside AAB
    with zipfile.ZipFile(p, "r") as z:
        manifest_raw = z.read("base/manifest/AndroidManifest.xml")
        
        # Look for targetSdkVersion
        target_sdk = "UNKNOWN"
        idx = manifest_raw.find(b"targetSdkVersion")
        if idx != -1:
            snippet = manifest_raw[idx:idx+40]
            # ASCII numbers in the protobuf snippet
            m = re.search(rb'[\x10-\x39](\d{2})', snippet)
            if m:
                target_sdk = m.group(1).decode("ascii")
            else:
                # Direct ASCII search
                for candidate in [b"36", b"35", b"34"]:
                    if candidate in snippet:
                        target_sdk = candidate.decode("ascii")
                        break
        
        # Look for minSdkVersion
        min_sdk = "UNKNOWN"
        idx_min = manifest_raw.find(b"minSdkVersion")
        if idx_min != -1:
            snippet_min = manifest_raw[idx_min:idx_min+40]
            for candidate in [b"24", b"21", b"26"]:
                if candidate in snippet_min:
                    min_sdk = candidate.decode("ascii")
                    break

        # Check permissions
        all_strings = set()
        for s in re.findall(rb'[a-zA-Z0-9_.:/-]{4,}', manifest_raw):
            all_strings.add(s.decode("latin1", errors="ignore"))

        permissions = sorted([s for s in all_strings if s.startswith("android.permission.")])
        has_call_phone = "android.permission.CALL_PHONE" in permissions
        has_cleartext = "usesCleartextTraffic" in all_strings

        print(f"Binary Manifest targetSdkVersion: {target_sdk}")
        print(f"Binary Manifest minSdkVersion: {min_sdk}")
        print(f"CALL_PHONE Present: {'CRITICAL ERROR - YES' if has_call_phone else 'CLEAN - NO'}")
        print(f"usesCleartextTraffic Present: {'WARNING - YES' if has_cleartext else 'CLEAN - NO'}")
        print(f"Declared Permissions ({len(permissions)}):")
        for perm in permissions:
            print(f"  - {perm}")

print("\n" + "=" * 80)
print("AAB INSPECTION COMPLETE")
print("=" * 80)
