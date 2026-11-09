import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    customer = f.read()

# check translations object
m_en = re.search(r'en:\s*\{', customer)
m_hi = re.search(r'hi:\s*\{', customer)

print("en translation found:", bool(m_en))
print("hi translation found:", bool(m_hi))

keys_to_add_en = '''
        checkout_payment_title: "Select Payment Method",
        checkout_payment_sub: "Safe & Verified Rural Checkout",
        checkout_bill_items: "Item Total:",
        checkout_bill_delivery: "Delivery Fee:",
        checkout_bill_platform: "Platform Fee:",
        checkout_bill_cod: "COD Convenience Fee:",
        checkout_bill_total: "To Pay:",
        checkout_pay_upi: "Pay via UPI",
        checkout_pay_upi_desc: "Fast & secure instant UPI payment",
        checkout_pay_cod: "Cash on Delivery (COD)",
        checkout_pay_cod_desc: "Pay cash directly to runner upon delivery",'''

keys_to_add_hi = '''
        checkout_payment_title: "भुगतान का तरीका चुनें",
        checkout_payment_sub: "सुरक्षित एवं सत्यापित ग्रामीण चेकआउट",
        checkout_bill_items: "सामान का कुल मूल्य:",
        checkout_bill_delivery: "वितरण शुल्क:",
        checkout_bill_platform: "प्लेटफ़ॉर्म शुल्क:",
        checkout_bill_cod: "सीओडी सुविधा शुल्क:",
        checkout_bill_total: "कुल देय राशि:",
        checkout_pay_upi: "UPI द्वारा भुगतान करें",
        checkout_pay_upi_desc: "तेज़ एवं सुरक्षित तत्काल यूपीआई भुगतान",
        checkout_pay_cod: "कैश ऑन डिलीवरी (COD)",
        checkout_pay_cod_desc: "डिलीवरी के समय सीधे राइडर को नकद भुगतान करें",'''

if m_en:
    customer = customer[:m_en.end()] + keys_to_add_en + customer[m_en.end():]
if m_hi:
    # re-find after first replacement
    m_hi2 = re.search(r'hi:\s*\{', customer)
    if m_hi2:
        customer = customer[:m_hi2.end()] + keys_to_add_hi + customer[m_hi2.end():]

with open('public_web/customer/index.html', 'w', encoding='utf-8') as f:
    f.write(customer)

print("Added customer i18n keys successfully.")
