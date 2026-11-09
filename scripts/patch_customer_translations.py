with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    'login_title: "Enter Mobile Number",',
    'login_title: "Mobile Login",'
)
text = text.replace(
    'login_sub: "We will send a 4-digit verification code to your phone number for secure login.",',
    'login_sub: "Enter your mobile number to receive a secure 6-digit SMS verification code on your phone.",'
)
text = text.replace(
    'login_title: "मोबाइल नंबर दर्ज करें",',
    'login_title: "मोबाइल लॉगिन",'
)
text = text.replace(
    'login_sub: "सुरक्षित लॉगिन के लिए हम आपके मोबाइल पर 4 अंकों का कोड भेजेंगे।",',
    'login_sub: "सुरक्षित 6-अंकीय SMS सत्यापन कोड प्राप्त करने के लिए अपना मोबाइल नंबर दर्ज करें।",'
)

with open('public_web/customer/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated translations in customer index.html successfully')
