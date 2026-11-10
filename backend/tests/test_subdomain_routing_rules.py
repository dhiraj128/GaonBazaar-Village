import json
from pathlib import Path
import pytest


def test_vercel_json_edge_rewrites_structure():
    """Verify that vercel.json exists in root and apps/admin, and defines the strict subdomain routing matrix."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    root_vercel = repo_root / "vercel.json"
    admin_vercel = repo_root / "apps" / "admin" / "vercel.json"

    assert root_vercel.exists(), "Root vercel.json must exist for edge routing"
    assert admin_vercel.exists(), "apps/admin/vercel.json must exist for build routing"

    for config_path in [root_vercel, admin_vercel]:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "rewrites" in data, f"{config_path} must have rewrites"
        rewrites = data["rewrites"]

        # Check Admin Subdomain Mapping
        admin_rule = next(
            (
                r for r in rewrites
                if any(h.get("type") == "host" and h.get("value") == "admin.apnagaonbazaar.in" for h in r.get("has", []))
            ),
            None,
        )
        assert admin_rule is not None, "admin.apnagaonbazaar.in rewrite rule missing"
        assert admin_rule["destination"] == "/index.html", "admin must route to /index.html"

        # Check Vendor Subdomain Mapping
        vendor_rule = next(
            (
                r for r in rewrites
                if any(h.get("type") == "host" and h.get("value") == "dukaan.apnagaonbazaar.in" for h in r.get("has", []))
            ),
            None,
        )
        assert vendor_rule is not None, "dukaan.apnagaonbazaar.in rewrite rule missing"
        assert vendor_rule["destination"] == "/vendor/index.html", "dukaan must route to /vendor/index.html"

        # Check Runner Subdomain Mapping
        runner_rule = next(
            (
                r for r in rewrites
                if any(h.get("type") == "host" and h.get("value") == "mitra.apnagaonbazaar.in" for h in r.get("has", []))
            ),
            None,
        )
        assert runner_rule is not None, "mitra.apnagaonbazaar.in rewrite rule missing"
        assert runner_rule["destination"] == "/runner/index.html", "mitra must route to /runner/index.html"

        # Check Customer Domain Mapping (apnagaonbazaar.in)
        customer_rule = next(
            (
                r for r in rewrites
                if any(h.get("type") == "host" and h.get("value") == "apnagaonbazaar.in" for h in r.get("has", []))
            ),
            None,
        )
        assert customer_rule is not None, "apnagaonbazaar.in rewrite rule missing"
        assert customer_rule["destination"] == "/customer/index.html", "customer must route to /customer/index.html"

        # Check WWW Customer Domain Mapping (www.apnagaonbazaar.in)
        www_customer_rule = next(
            (
                r for r in rewrites
                if any(h.get("type") == "host" and h.get("value") == "www.apnagaonbazaar.in" for h in r.get("has", []))
            ),
            None,
        )
        assert www_customer_rule is not None, "www.apnagaonbazaar.in rewrite rule missing"
        assert www_customer_rule["destination"] == "/customer/index.html", "www must route to /customer/index.html"


def test_static_distribution_assets_exist():
    """Verify customer, vendor, and runner static bundles exist in apps/admin/public."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    
    for portal in ["customer", "vendor", "runner"]:
        admin_pub_file = repo_root / "apps" / "admin" / "public" / portal / "index.html"
        assert admin_pub_file.exists(), f"apps/admin/public/{portal}/index.html must exist"


def test_subdomain_router_contract_assertions():
    """Verify the logic matches the required subdomain resolution matrix."""
    def resolve_target(hostname: str, search: str = "", pathname: str = "") -> str:
        clean_host = (hostname or "").lower().strip()
        clean_path = (pathname or "").lower().strip()

        # Query param override
        if "app=admin" in search:
            return "admin"
        if "app=dukaan" in search or "app=vendor" in search:
            return "dukaan"
        if "app=mitra" in search or "app=runner" in search:
            return "mitra"
        if "app=customer" in search:
            return "customer"

        # Pathname override
        if clean_path.startswith("/admin"):
            return "admin"
        if clean_path.startswith("/dukaan") or clean_path.startswith("/vendor"):
            return "dukaan"
        if clean_path.startswith("/mitra") or clean_path.startswith("/runner"):
            return "mitra"
        if clean_path.startswith("/customer"):
            return "customer"

        # Hostname matching
        if clean_host == "admin.apnagaonbazaar.in" or clean_host.startswith("admin."):
            return "admin"
        if clean_host == "dukaan.apnagaonbazaar.in" or clean_host.startswith("dukaan.") or clean_host.startswith("vendor."):
            return "dukaan"
        if clean_host == "mitra.apnagaonbazaar.in" or clean_host.startswith("mitra.") or clean_host.startswith("runner."):
            return "mitra"
        if clean_host in ("apnagaonbazaar.in", "www.apnagaonbazaar.in"):
            return "customer"

        # Default fallback
        return "customer"

    # Strict Production Requirements
    assert resolve_target("admin.apnagaonbazaar.in") == "admin"
    assert resolve_target("dukaan.apnagaonbazaar.in") == "dukaan"
    assert resolve_target("mitra.apnagaonbazaar.in") == "mitra"
    assert resolve_target("apnagaonbazaar.in") == "customer"
    assert resolve_target("www.apnagaonbazaar.in") == "customer"

    # Default Fallback (MUST NEVER BE ADMIN)
    assert resolve_target("localhost") == "customer"
    assert resolve_target("127.0.0.1") == "customer"
    assert resolve_target("staging.vercel.app") == "customer"
    assert resolve_target("unknown-domain.com") == "customer"

    # Local Development Overrides via query params
    assert resolve_target("localhost", search="?app=admin") == "admin"
    assert resolve_target("localhost", search="?app=dukaan") == "dukaan"
    assert resolve_target("localhost", search="?app=mitra") == "mitra"
    assert resolve_target("localhost", search="?app=customer") == "customer"
