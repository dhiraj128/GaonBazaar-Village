import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/customer/auth-service.js', 'r', encoding='utf-8') as f:
    auth_service = f.read()
print("=== auth-service.js ===")
print(auth_service[:1500])

for app in ['customer', 'runner', 'vendor']:
    with open(f'public_web/{app}/index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    print(f"\n=== {app.upper()} Mobile Login & OTP ===")
    m_send = re.search(r'function (?:sendOtp|sendMobileOtp|sendMobileOTP|handleSendOtp)[^{]*\{.*?\n    \}', html, re.DOTALL)
    if m_send:
        print("Send OTP func:\n", m_send.group(0)[:800])
    m_verify = re.search(r'function (?:verifyOtp|verifyMobileOtp|verifyMobileOTP|handleVerifyOtp)[^{]*\{.*?\n    \}', html, re.DOTALL)
    if m_verify:
        print("Verify OTP func:\n", m_verify.group(0)[:800])
