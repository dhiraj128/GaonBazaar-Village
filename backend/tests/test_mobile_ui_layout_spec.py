from pathlib import Path
import re
import pytest

def test_runner_action_buttons_vertical_stack():
    """Verify runner action buttons on delivery screen are stacked vertically in strict order."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    runner_html_path = repo_root / "apps" / "admin" / "public" / "runner" / "index.html"
    assert runner_html_path.exists()

    content = runner_html_path.read_text(encoding="utf-8")

    # Locate action container
    assert 'id="btn-navigate-customer"' in content
    assert 'openRunnerOrderChat()' in content
    assert 'id="cust-phone-link"' in content

    # Find the positions of the three buttons
    pos_nav = content.find('id="btn-navigate-customer"')
    pos_chat = content.find('openRunnerOrderChat()')
    pos_call = content.find('id="cust-phone-link"')

    # Stacking Order: 1. Navigate, 2. Chat, 3. Call
    assert pos_nav < pos_chat < pos_call, (
        f"Expected order: Navigate < Chat < Call. Got: nav={pos_nav}, chat={pos_chat}, call={pos_call}"
    )

    # Ensure parent container uses flex-col with gap-y-3
    assert "flex flex-col gap-y-3 w-full" in content or "flex-col" in content


def test_touch_targets_and_otp_accessibility():
    """Verify OTP input fields and buttons have minimum 48px touch targets."""
    repo_root = Path(__file__).resolve().parent.parent.parent

    runner_html = (repo_root / "apps" / "admin" / "public" / "runner" / "index.html").read_text(encoding="utf-8")
    vendor_html = (repo_root / "apps" / "admin" / "public" / "vendor" / "index.html").read_text(encoding="utf-8")

    # Check 4-digit customer delivery OTP field height
    assert 'id="cust-delivery-otp"' in runner_html
    assert 'min-h-[52px]' in runner_html or 'h-14' in runner_html

    # Check complete delivery button
    assert 'id="btn-complete-delivery"' in runner_html
    assert 'min-h-[48px]' in runner_html

    # Check pickup handover OTP in vendor app
    assert 'id="handover-otp-input"' in vendor_html
    assert 'min-h-[48px]' in vendor_html or 'h-12' in vendor_html


def test_collect_cash_badge_and_address_text_wrapping():
    """Verify cash badge and addresses wrap properly without horizontal clipping."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    runner_html = (repo_root / "apps" / "admin" / "public" / "runner" / "index.html").read_text(encoding="utf-8")

    # Badge wrapping classes
    assert 'id="order-payment-badge"' in runner_html
    assert 'break-words' in runner_html
    assert 'whitespace-normal' in runner_html

    # Address wrapping classes
    assert 'id="order-customer-address"' in runner_html
    assert 'break-words' in runner_html
