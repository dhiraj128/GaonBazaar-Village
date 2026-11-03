import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';

class PoliciesScreen extends StatefulWidget {
  const PoliciesScreen({super.key});

  @override
  State<PoliciesScreen> createState() => _PoliciesScreenState();
}

class _PoliciesScreenState extends State<PoliciesScreen> {
  final TextEditingController _searchCtrl = TextEditingController();
  String _selectedCategory = 'All';

  @override
  void dispose() {
    _searchCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final isHi = loc.isHindi;

    final List<Map<String, dynamic>> allClauses = [
      {
        'num': 1,
        'category': 'Orders',
        'badge': isHi ? 'मूल सेवा शर्तें' : 'General Terms',
        'icon': Icons.description_outlined,
        'title': isHi ? '1. सेवा शर्तें (Terms of Service)' : '1. Terms of Service',
        'body': isHi
            ? 'गाँव बाज़ार एक ग्रामीण क्विक-कॉमर्स प्लेटफ़ॉर्म है जो स्थानीय गाँव के दुकानदारों, किसानों, डिलीवरी साथियों और उपभोक्ताओं को जोड़ता है। प्लेटफ़ॉर्म का उपयोग इन शर्तों के पूर्ण अनुपालन के अधीन है।'
            : 'GaonBazaar is a rural quick-commerce platform connecting village shopkeepers, farmers, delivery partners, and consumers. Platform use is subject to full acceptance of these commercial terms.',
        'bullets': isHi
            ? ['ग्रामीण व्यापार सशक्तिकरण हेतु 0% कमीशन पर संचालित', 'प्लेटफ़ॉर्म की सभी सेवाएं पारदर्शी नियमों पर आधारित हैं', 'किसी भी शर्त का उल्लंघन खाता निलंबन का आधार बन सकता है']
            : ['Operates on 0% commission to empower local village commerce', 'All transactions governed by transparent rural standards', 'Violations may lead to suspension or deactivation'],
      },
      {
        'num': 2,
        'category': 'Orders',
        'badge': isHi ? 'पात्रता' : 'Eligibility',
        'icon': Icons.how_to_reg_outlined,
        'title': isHi ? '2. पात्रता एवं खाता उपयोग (Eligibility and Account Use)' : '2. Eligibility and Account Use',
        'body': isHi
            ? 'केवल 18 वर्ष या उससे अधिक आयु के भारतीय नागरिक जिनके पास वैध भारतीय मोबाइल नंबर है, वे गाँव बाज़ार पर ऑर्डर करने या सेवाएं प्रदान करने के पात्र हैं।'
            : 'Users must be 18 years or older with an active Indian mobile number to register, place orders, or operate as a partner on GaonBazaar.',
        'bullets': isHi
            ? ['एक मोबाइल नंबर से केवल एक सक्रिय खाता मान्य', 'खाता जानकारी सत्य और अद्यतन रखना उपयोगकर्ता का दायित्व है']
            : ['Single active account per authenticated mobile number', 'Users are responsible for maintaining accurate profile records'],
      },
      {
        'num': 3,
        'category': 'Privacy',
        'badge': isHi ? 'ओटीपी सुरक्षा' : 'Security',
        'icon': Icons.lock_outline,
        'title': isHi ? '3. प्रमाणीकरण व खाता सुरक्षा (Authentication & Security)' : '3. Authentication & Account Security',
        'body': isHi
            ? 'लॉगिन केवल सिंगल-यूज़, एक्सपायरिंग एसएमएस ओटीपी (600s TTL) द्वारा होता है। अपना लॉगिन ओटीपी कभी भी किसी अन्य व्यक्ति के साथ साझा न करें।'
            : 'Access is guarded exclusively by single-use, expiring SMS OTPs (600s TTL). Never disclose your login OTP to anyone, including delivery partners or staff.',
        'bullets': isHi
            ? ['ओटीपी साझा करने से हुए अनधिकृत लेन-देन के लिए उपयोगकर्ता स्वयं उत्तरदायी होगा', 'संदेहास्पद गतिविधि पर तुरंत ग्राहक सहायता को सूचित करें']
            : ['Users bear responsibility for transactions under shared credentials', 'Report suspicious account activity immediately to helpline'],
      },
      {
        'num': 4,
        'category': 'Orders',
        'badge': isHi ? 'कैटलॉग' : 'Catalog',
        'icon': Icons.storefront_outlined,
        'title': isHi ? '4. उत्पाद सूची व उपलब्धता (Product Listing & Availability)' : '4. Product Listing and Availability',
        'body': isHi
            ? 'कैटलॉग में प्रदर्शित किराना, फल, सब्जियाँ और डेयरी उत्पाद स्थानीय पंजीकृत दुकानों द्वारा वास्तविक समय के स्टॉक के अनुसार सूचीबद्ध किए जाते हैं।'
            : 'All groceries, perishables, and essentials listed in the catalog reflect real-time stock published by local verified village stores.',
        'bullets': isHi
            ? ['स्टॉक समाप्त होने पर दुकानदार उत्पाद को तुरंत आउट-ऑफ-स्टॉक कर सकते हैं', 'उत्पाद की वास्तविक पैकेजिंग व चित्र में मामूली अंतर संभव है']
            : ['Stores dynamically toggle availability based on counter stock', 'Packaging and images may vary slightly from real products'],
      },
      {
        'num': 5,
        'category': 'Payments',
        'badge': isHi ? '₹3.00 स्थिर' : '₹3.00 Fixed',
        'icon': Icons.currency_rupee,
        'title': isHi ? '5. मूल्य निर्धारण व प्लेटफ़ॉर्म शुल्क (Pricing and Fees)' : '5. Pricing and Fees',
        'body': isHi
            ? 'प्रति आर्डर मात्र ₹3.00 का निश्चित प्लेटफ़ॉर्म शुल्क लिया जाता है। 5-स्तरीय दूरी आधारित पारदर्शी डिलीवरी शुल्क (₹15 - ₹40) लागू होता है। कोई छुपा हुआ सर्ज शुल्क नहीं है।'
            : 'A strict flat platform fee of ₹3.00 applies per completed order. Transparent 5-tier delivery fees (₹15 - ₹40) apply strictly by distance with zero surge fees.',
        'bullets': isHi
            ? ['0-1 किमी: ₹15 | 1-2 किमी: ₹20 | 2-4 किमी: ₹25 | 4-6 किमी: ₹30 | 6-8 किमी: ₹40', 'दुकानदार से 0% कमीशन लिया जाता है']
            : ['0-1km: ₹15 | 1-2km: ₹20 | 2-4km: ₹25 | 4-6km: ₹30 | 6-8km: ₹40', '100% zero-commission model for rural village vendors'],
      },
      {
        'num': 6,
        'category': 'Orders',
        'badge': isHi ? 'आर्डर स्वीकृति' : 'Acceptance',
        'icon': Icons.check_circle_outline,
        'title': isHi ? '6. ऑर्डर प्लेसमेंट व स्वीकृति (Order Placement & Acceptance)' : '6. Order Placement and Acceptance',
        'body': isHi
            ? 'ग्राहक द्वारा ऐप में चेकआउट करने पर आर्डर स्थानीय दुकानदार को भेजा जाता है। दुकानदार द्वारा स्वीकार किए जाने पर आर्डर की पुष्टि होती है।'
            : 'Orders placed on checkout are dispatched to the closest serviceable village store. Official confirmation occurs upon store acceptance.',
        'bullets': isHi
            ? ['दुकानदार 10 मिनट के भीतर ऑर्डर स्वीकार और पैक करते हैं', 'अस्वीकार होने पर प्रीपेड भुगतान तुरंत वापस कर दिया जाता है']
            : ['Stores accept and pack items within 10 minutes target', 'Instant refund issued if a store cannot fulfill an order'],
      },
      {
        'num': 7,
        'category': 'Payments',
        'badge': isHi ? 'कैश / यूपीआई' : 'COD / UPI',
        'icon': Icons.payment_outlined,
        'title': isHi ? '7. भुगतान शर्तें (Payment Terms)' : '7. Payment Terms',
        'body': isHi
            ? 'ग्राहक डिलीवरी पर नकद (COD) या ऑनलाइन यूपीआई / कार्ड द्वारा भुगतान कर सकते हैं। सीओडी भुगतान सामान की डिलीवरी के समय रनर को दिया जाना अनिवार्य है।'
            : 'Payments can be made via Cash on Delivery (COD) or verified digital UPI/Card gateways. COD cash must be handed to runner on physical delivery.',
        'bullets': isHi
            ? ['कोई काल्पनिक या अनधिकृत वॉलेट बैलेंस स्वीकार्य नहीं है', 'ऑनलाइन लेनदेन अधिकृत सुरक्षित पेमेंट गेटवे द्वारा प्रोसेस होते हैं']
            : ['No fabricated or mock wallet balances exist on platform', 'Online payments processed securely via certified gateways'],
      },
      {
        'num': 8,
        'category': 'Orders',
        'badge': isHi ? '15-25 मिनट' : '15-25 Mins',
        'icon': Icons.two_wheeler_outlined,
        'title': isHi ? '8. डिलीवरी शर्तें (Delivery Terms)' : '8. Delivery Terms',
        'body': isHi
            ? 'डिलीवरी केवल पंजीकृत ग्रामीण पते पर 15-25 मिनट के औसत समय में की जाती है। ग्राहक को सामान प्राप्त करते समय 4-अंकीय ओटीपी कोड रनर को बताना होगा।'
            : 'Deliveries target 15-25 minutes across village doorsteps. The customer must provide the 4-digit verification PIN to runner upon physical handover.',
        'bullets': isHi
            ? ['बिना 4-अंकीय डिलीवरी ओटीपी के डिलीवरी पूर्ण नहीं मानी जाएगी', 'मौसम या सड़क अवरोध पर डिलीवरी साथी ऐप में सूचित करेंगे']
            : ['Handover requires customer-verbalized 4-digit delivery PIN', 'Severe weather or rural road blocks communicated in real time'],
      },
      {
        'num': 9,
        'category': 'Orders',
        'badge': isHi ? '8.0 किमी सीमा' : '8.0 km Geofence',
        'icon': Icons.radar_outlined,
        'title': isHi ? '9. सेवा क्षेत्र व पता सटीकता (Service Area & Address Accuracy)' : '9. Service Area and Address Accuracy',
        'body': isHi
            ? 'गाँव बाज़ार मीनापुर हब से अधिकतम 8.0 किमी दायरे में सेवा प्रदान करता है। हैवर्सिन फॉर्मूला द्वारा दूरी की गणना होती है। 8.0 किमी से परे आर्डर स्वतः ब्लॉक होते हैं।'
            : 'Service is strictly limited to an 8.0 km radius from Minapur Pilot Hub via Haversine geofence calculations. Orders outside 8.0 km are automatically rejected.',
        'bullets': isHi
            ? ['पायलट क्षेत्र: चतुरसी, तुबनाघरा/बेनाघरा, सिवाय पट्टी, तुलसी गंज/बनगांव', 'गलत पता दर्ज करने पर डिलीवरी रद्द हो सकती है']
            : ['Pilot villages: Chaturshi, Benaghara, Sivay Patti, Bangaon', 'Accurate landmark and village selection required at checkout'],
      },
      {
        'num': 10,
        'category': 'Orders',
        'badge': isHi ? '180 सेकंड' : '180 Seconds',
        'icon': Icons.timer_outlined,
        'title': isHi ? '10. रद्दीकरण नीति (Cancellation Policy)' : '10. Cancellation Policy',
        'body': isHi
            ? 'ग्राहक ऑर्डर देने के 180 सेकंड के भीतर बिना किसी शुल्क के ऑर्डर रद्द कर सकते हैं। 180 सेकंड समाप्त होने या दुकानदार द्वारा पैकिंग शुरू करने के बाद रद्दीकरण लॉक हो जाता है।'
            : 'Customers enjoy a zero-penalty cancellation window for exactly 180 seconds after order placement. Once 180s expires or packing starts, cancellation locks.',
        'bullets': isHi
            ? ['180 सेकंड के भीतर 100% तुरंत रिफ़ंड', 'दुकानदार द्वारा सामान पैक करने के बाद भोजन की बर्बादी रोकने हेतु रद्दीकरण बंद']
            : ['100% instant refund on cancellations within 180s', 'Prevents perishable food wastage once shopkeeper packs items'],
      },
      {
        'num': 11,
        'category': 'Payments',
        'badge': isHi ? '100% रिफ़ंड' : 'Direct Refund',
        'icon': Icons.replay_outlined,
        'title': isHi ? '11. रिफ़ंड नीति (Refund Policy)' : '11. Refund Policy',
        'body': isHi
            ? 'स्वीकृत रिफ़ंड उसी भुगतान माध्यम (बैंक / यूपीआई) में 24-48 घंटों के भीतर प्रोसेस कर दिया जाता है। सीओडी ऑर्डर में रिफ़ंड बैंक खाते में अंतरित होता है।'
            : 'Approved refunds are credited directly to the source payment method or designated UPI within 24-48 hours. COD refunds transfer directly via UPI.',
        'bullets': isHi
            ? ['कोई गैर-वापसी योग्य कूपन या नकली टोकन नहीं दिया जाता', 'रिफ़ंड की स्थिति ऐप के सहायता केंद्र में ट्रैक की जा सकती है']
            : ['No synthetic tokens or locked store balances used', 'Refund status trackable live through in-app support desk'],
      },
      {
        'num': 12,
        'category': 'Orders',
        'badge': isHi ? 'डोरस्टेप जांच' : 'Inspection',
        'icon': Icons.change_circle_outlined,
        'title': isHi ? '12. वापसी एवं प्रतिस्थापन (Replacement and Return Policy)' : '12. Replacement and Return Policy',
        'body': isHi
            ? 'पैकेजिंग फटी होने या गलत सामान डिलीवर होने पर ग्राहक डिलीवरी साथी के समक्ष सामान अस्वीकार कर सकते हैं या 2 घंटे के भीतर ऐप पर फोटो अपलोड कर शिकायत कर सकते हैं।'
            : 'Items damaged in transit or incorrect items can be inspected and rejected at doorstep or reported with photo proof within 2 hours in the app.',
        'bullets': isHi
            ? ['दुकानदार द्वारा सही सामग्री का त्वरित प्रतिस्थापन भेजा जाएगा', 'गैर-खराब सामान मूल सीलबंद पैकेजिंग में ही वापस हो सकता है']
            : ['Expedited replacement dispatched directly from the store', 'Non-perishables must retain intact manufacturer seal'],
      },
      {
        'num': 13,
        'category': 'Orders',
        'badge': isHi ? 'ताज़ा उत्पाद' : 'Perishables',
        'icon': Icons.eco_outlined,
        'title': isHi ? '13. नाशवान सामग्री नीति (Perishable Goods Policy)' : '13. Perishable Goods Policy',
        'body': isHi
            ? 'दूध, दही, पनीर, ताज़ी सब्जियाँ और फल नाशवान हैं। ग्राहक डिलीवरी के समय गुणवत्ता की जांच करें। डिलीवरी पूर्ण होने के 2 घंटे बाद नाशवान सामान की वापसी संभव नहीं है।'
            : 'Dairy, curd, fresh vegetables and fruits are perishable commodities. Inspect freshness at doorstep. Quality disputes must be lodged within 2 hours.',
        'bullets': isHi
            ? ['स्थानीय किसानों व डेरियों से सीधे ताज़ा आपूर्ति', 'खराब पाए जाने पर 100% तुरंत रिप्लेसमेंट या रिफ़ंड']
            : ['Direct village farm and local Sudha dairy sourcing', 'Immediate resolution or replacement if freshness compromised'],
      },
      {
        'num': 14,
        'category': 'Partner',
        'badge': isHi ? 'सहायता केंद्र' : 'Complaints',
        'icon': Icons.support_agent_outlined,
        'title': isHi ? '14. ग्राहक शिकायत प्रक्रिया (Customer Complaint Procedure)' : '14. Customer Complaint Procedure',
        'body': isHi
            ? 'किसी भी समस्या के लिए ऐप के "सहायता केंद्र" में टिकट बनाएं या मीनापुर हब हेल्पलाइन +91 98000 00000 पर कॉल करें। सामान्य समाधान समय 30 मिनट है।'
            : 'Submit an in-app ticket under Support Hub or call Minapur Hub Helpline (+91 98000 00000). Average first-response resolution time is under 30 minutes.',
        'bullets': isHi
            ? ['ऑर्डर-विशिष्ट चैट सहायता उपलब्ध है', 'प्रत्येक शिकायत का एक अद्वितीय टिकट नंबर जनरेट होता है']
            : ['Order-specific chat with runner and customer support', 'Unique tracking ticket generated for every complaint'],
      },
      {
        'num': 15,
        'category': 'Privacy',
        'badge': isHi ? 'डेटा सुरक्षा' : 'Privacy',
        'icon': Icons.privacy_tip_outlined,
        'title': isHi ? '15. गोपनीयता नीति (Privacy Policy)' : '15. Privacy Policy',
        'body': isHi
            ? 'हम केवल सेवा प्रदान करने हेतु आवश्यक व्यक्तिगत डेटा (नाम, फोन नंबर, गाँव, जीपीएस पता) एकत्र करते हैं। आपका डेटा कभी किसी तीसरे पक्ष को नहीं बेचा जाता।'
            : 'We collect only essential data needed to fulfill village orders (name, phone, delivery locality, GPS coordinates). Data is never sold to third parties.',
        'bullets': isHi
            ? ['डेटा एन्क्रिप्शन मानकों का कड़ाई से पालन', 'उपयोगकर्ता जब चाहें खाता व डेटा हटाने का अनुरोध कर सकते हैं']
            : ['Strict database encryption and least-privilege access', 'Users may request complete account deletion at any time'],
      },
      {
        'num': 16,
        'category': 'Privacy',
        'badge': isHi ? 'जीपीएस सहमति' : 'GPS Consent',
        'icon': Icons.location_searching_outlined,
        'title': isHi ? '16. लोकेशन व लाइव ट्रैकिंग सहमति (Location & Tracking Consent)' : '16. Location and Live Tracking Consent',
        'body': isHi
            ? 'सटीक 8.0 किमी जियोफेंस सत्यापन और डिलीवरी साथी की लाइव दूरी प्रदर्शित करने के लिए ऐप लोकेशन अनुमतियों का उपयोग करता है। ट्रैकिंग केवल सक्रिय आर्डर के दौरान होती है।'
            : 'GPS coordinates verify 8.0 km serviceability and display runner live progress. Tracking operates strictly during active delivery assignments.',
        'bullets': isHi
            ? ['ऑर्डर पूरा होने पर लाइव लोकेशन शेयरिंग स्वतः समाप्त हो जाती है', 'पृष्ठभूमि में अनाधिकृत लोकेशन ट्रैकिंग प्रतिबंधित है']
            : ['Tracking automatically halts once delivery is completed', 'Zero unauthorized background surveillance'],
      },
      {
        'num': 17,
        'category': 'Privacy',
        'badge': isHi ? 'केवाईसी सुरक्षा' : 'KYC Privacy',
        'icon': Icons.badge_outlined,
        'title': isHi ? '17. पहचान सत्यापन व दस्तावेज़ गोपनीयता (Identity Verification Privacy)' : '17. Identity Verification & Document Privacy',
        'body': isHi
            ? 'स्टेजिंग परीक्षण मोड में वास्तविक आधार/पैन अपलोड नहीं कराया जाता। उत्पादन वातावरण में अधिकृत डिजीलॉकर एपीआई द्वारा सुरक्षित सत्यापन किया जाएगा।'
            : 'In staging preview mode, real Aadhaar/PAN documents are never stored. In production, official DigiLocker sandboxes manage verification securely.',
        'bullets': isHi
            ? ['स्टेजिंग पर केवल परीक्षण डेटा प्रयुक्त होता है', 'गोपनीय पहचान विवरण एन्क्रिप्टेड डेटाबेस में सुरक्षित रहते हैं']
            : ['Explicit "TEST MODE" badge displayed in staging wizards', 'Confidential partner documents protected under Indian IT rules'],
      },
      {
        'num': 18,
        'category': 'Partner',
        'badge': isHi ? '0% कमीशन' : '0% Commission',
        'icon': Icons.store_mall_directory_outlined,
        'title': isHi ? '18. विक्रेता / दुकानदार नियम (Vendor Terms)' : '18. Vendor Terms',
        'body': isHi
            ? 'गाँव बाज़ार स्थानीय दुकानदारों से 0% कमीशन लेता है। दुकानदार केवल असली, शुद्ध और उचित एमआरपी वाले उत्पाद बेचने और 10 मिनट में पैक करने के लिए बाध्य हैं।'
            : 'GaonBazaar levies 0% commission on registered village shopkeepers. Vendors agree to stock authentic, fresh goods and pack accepted orders within 10 minutes.',
        'bullets': isHi
            ? ['दुकान का दैनिक सेटलमेंट T+1 आधार पर यूपीआई/बैंक में भेजा जाता है', 'मिलावटी या एक्सपायर्ड सामान बेचने पर दुकान स्थायी रूप से ब्लैकलिस्ट होगी']
            : ['Daily T+1 settlements processed directly to vendor UPI/Bank', 'Strict zero-tolerance policy against adulterated or expired items'],
      },
      {
        'num': 19,
        'category': 'Partner',
        'badge': isHi ? 'डिलीवरी साथी' : 'Partner Code',
        'icon': Icons.directions_bike_outlined,
        'title': isHi ? '19. डिलीवरी पार्टनर नियम (Delivery Partner Terms)' : '19. Delivery Partner Terms',
        'body': isHi
            ? 'डिलीवरी साथी स्वतंत्र ग्रामीण सेवा प्रदाता हैं। वे सुरक्षित ड्राइविंग, विनम्र व्यवहार और समय पर सामान पहुंचाने के लिए प्रतिबद्ध हैं। साइकिल साथियों को डीएल की छूट है।'
            : 'Delivery partners operate as independent rural delivery partners. Bicycle runners are explicitly exempt from motor DL/RC rules.',
        'bullets': isHi
            ? ['मोटरसाइकिल साथियों के पास वैध ड्राइविंग लाइसेंस होना अनिवार्य है', 'सड़क सुरक्षा नियमों व हेलमेट/रिफ्लेक्टर का अनुपालन अनिवार्य']
            : ['Motorized partners must maintain valid driving licence', 'Helmet and road safety compliance strictly enforced'],
      },
      {
        'num': 20,
        'category': 'Partner',
        'badge': isHi ? '5-स्तरीय पेआउट' : '5-Tier Payout',
        'icon': Icons.monetization_on_outlined,
        'title': isHi ? '20. पार्टनर पेआउट संरचना (Delivery Partner Earnings)' : '20. Delivery Partner Earnings',
        'body': isHi
            ? 'दूरी के अनुसार पैसे-पैसे का पारदर्शी पेआउट: 0-1 किमी: ₹10 | 1-2 किमी: ₹14 | 2-4 किमी: ₹18 | 4-6 किमी: ₹22 | 6-8 किमी: ₹28। मल्टी-ऑर्डर बैच पर अतिरिक्त प्रोत्साहन।'
            : 'Paisa-accurate 5-tier distance payouts: 0-1km: ₹10 | 1-2km: ₹14 | 2-4km: ₹18 | 4-6km: ₹22 | 6-8km: ₹28. Multi-order batches earn incremental bonuses.',
        'bullets': isHi
            ? ['प्रत्येक पूर्ण ट्रिप का पेआउट दैनिक रूप से यूपीआई पर भेजा जाता है', 'बिना किसी अनुचित कटौती के पारदर्शी वित्तीय लेज़र']
            : ['Daily automated settlements to linked partner UPI IDs', 'Clear ledger breakdown visible in Runner earnings dashboard'],
      },
      {
        'num': 21,
        'category': 'Payments',
        'badge': isHi ? 'दैनिक जमा' : 'COD Remittance',
        'icon': Icons.attach_money_outlined,
        'title': isHi ? '21. सीओडी नकद संग्रह व जमा (COD Collection & Remittance)' : '21. COD Collection and Remittance',
        'body': isHi
            ? 'डिलीवरी पार्टनर ग्राहकों से नकद राशि एकत्र करने के लिए अधिकृत हैं। एकत्र की गई पूरी राशि उसी कार्य दिवस पर मीनापुर हब में जमा या यूपीआई द्वारा सिस्टम में सेटल करनी होगी।'
            : 'Runners collecting Cash on Delivery are strictly custodians of platform funds and must remit all cash to Minapur Hub or settle daily via UPI.',
        'bullets': isHi
            ? ['सीओडी राशि का गबन या रोक गैरकानूनी है और कानूनी कार्रवाई होगी', 'रनर ऐप में नकद दायित्व की वास्तविक समय ट्रैकिंग उपलब्ध है']
            : ['Diversion of cash is strictly prohibited and subject to legal action', 'Live cash-in-hand liability tracked in the Runner app'],
      },
      {
        'num': 22,
        'category': 'Payments',
        'badge': isHi ? 'T+1 सेटलमेंट' : 'Settlements',
        'icon': Icons.account_balance_outlined,
        'title': isHi ? '22. विक्रेता व रनर सेटलमेंट (Vendor & Runner Settlements)' : '22. Vendor and Runner Settlements',
        'body': isHi
            ? 'सभी वैध ऑर्डर के भुगतान का निपटारा T+1 कार्य दिवस में बैंक या यूपीआई के माध्यम से किया जाता है। कोई भी पेंडिंग सेटलमेंट 48 घंटे से अधिक नहीं रुकेगा।'
            : 'All completed order proceeds and delivery payouts settle within T+1 banking days directly to verified UPI/Bank accounts without hidden holdbacks.',
        'bullets': isHi
            ? ['दुकानदार डैशबोर्ड में संपूर्ण सेटलमेंट इतिहास उपलब्ध', 'विवादित ऑर्डर की जांच तक केवल विवादित राशि होल्ड होती है']
            : ['Complete settlement statements downloadable in vendor portal', 'Only disputed portion held during active grievance reviews'],
      },
      {
        'num': 23,
        'category': 'Partner',
        'badge': isHi ? 'पारदर्शी समायोजन' : 'Adjustments',
        'icon': Icons.balance_outlined,
        'title': isHi ? '23. वित्तीय विवाद व समायोजन (Disputes & Financial Adjustments)' : '23. Disputes and Financial Adjustments',
        'body': isHi
            ? 'यदि किसी ऑर्डर पर ग्राहक ने आंशिक रिफ़ंड मांगा हो, तो सुपर एडमिन द्वारा दुकानदार और रनर के साथ निष्पक्ष सत्यापन के बाद ही समायोजन किया जाता है।'
            : 'If partial returns or missing items arise, Super Admin reconciles with store and runner before financial adjustments are booked to the ledger.',
        'bullets': isHi
            ? ['दुकानदार को अपनी बात रखने का पूरा अवसर दिया जाता है', 'गलत कटौती के विरुद्ध अपील का अधिकार सुरक्षित']
            : ['Vendors provided fair hearing prior to any ledger debit', 'Full right to appeal dispute decisions through admin desk'],
      },
      {
        'num': 24,
        'category': 'Privacy',
        'badge': isHi ? 'सदाचार नियम' : 'Conduct',
        'icon': Icons.gavel_outlined,
        'title': isHi ? '24. उपयोगकर्ता आचरण व दुरुपयोग रोकथाम (User Conduct & Abuse)' : '24. User Conduct and Abuse Prevention',
        'body': isHi
            ? 'प्लेटफ़ॉर्म पर किसी भी प्रकार की धोखाधड़ी, नकली ऑर्डर, अभद्र भाषा, डिलीवरी साथियों से दुर्व्यवहार या सिस्टम में हेरफेर पूरी तरह प्रतिबंधित है।'
            : 'Abusive language, harassment of delivery partners, fraudulent orders, price manipulation, or malicious cancellations are strictly banned.',
        'bullets': isHi
            ? ['दुर्व्यवहार करने वाले उपयोगकर्ताओं का फोन नंबर स्थायी रूप से ब्लॉक होगा', 'गंभीर मामलों में स्थानीय पुलिस में रिपोर्ट दर्ज कराई जाएगी']
            : ['Perpetrators will face immediate and permanent phone banning', 'Serious offenses reported to local Minapur law enforcement'],
      },
      {
        'num': 25,
        'category': 'Privacy',
        'badge': isHi ? 'निलंबन नियम' : 'Suspension',
        'icon': Icons.block_outlined,
        'title': isHi ? '25. खाता निलंबन व समाप्ति (Account Suspension & Deactivation)' : '25. Account Suspension and Deactivation',
        'body': isHi
            ? 'नीति उल्लंघन, लगातार ऑर्डर अस्वीकार करने, नकद जमा न करने या खराब रेटिंग की स्थिति में गाँव बाज़ार को किसी भी खाते को निलंबित करने का अधिकार है।'
            : 'GaonBazaar reserves the right to suspend or deactivate accounts exhibiting policy violations, chronic order rejections, or unremitted cash.',
        'bullets': isHi
            ? ['निलंबन से पहले नोटिस और स्पष्टीकरण का अवसर दिया जाएगा', 'बकाया वैध पेआउट का भुगतान नियमानुसार पूर्ण किया जाएगा']
            : ['Advance notice provided where feasible before termination', 'Legitimate earned balances settled prior to final closure'],
      },
      {
        'num': 26,
        'category': 'Privacy',
        'badge': isHi ? 'डेटा अधिकार' : 'Data Retention',
        'icon': Icons.delete_sweep_outlined,
        'title': isHi ? '26. डेटा प्रतिधारण व विलोपन (Data Retention and Deletion)' : '26. Data Retention and Deletion',
        'body': isHi
            ? 'उपयोगकर्ता प्रोफाइल डेटा केवल खाता सक्रिय रहने तक सुरक्षित रखा जाता है। खाता हटाने के अनुरोध पर व्यक्तिगत पहचान विवरण 30 दिनों में मिटा दिया जाता है।'
            : 'User profile records remain stored while account is active. Upon account deletion requests, PII is securely purged within 30 days under Indian law.',
        'bullets': isHi
            ? ['कानूनी वित्तीय ऑडिट रिकॉर्ड नियमानुसार 7 वर्ष तक सुरक्षित रहते हैं', 'खाता हटाने का विकल्प प्रोफ़ाइल सेटिंग्स में उपलब्ध है']
            : ['Financial ledger records retained as required by tax statutes', 'Data purge request can be submitted via profile settings'],
      },
      {
        'num': 27,
        'category': 'Orders',
        'badge': isHi ? 'कानूनी दायित्व' : 'Liability',
        'icon': Icons.shield_outlined,
        'title': isHi ? '27. देयता की सीमा (Limitation of Liability)' : '27. Limitation of Liability, subject to applicable law',
        'body': isHi
            ? 'गाँव बाज़ार एक प्रौद्योगिकी प्लेटफ़ॉर्म है। स्थानीय दुकानदारों द्वारा निर्मित या पैक किए गए उत्पादों की आंतरिक निर्माण गुणवत्ता हेतु संबंधित निर्माता/दुकानदार उत्तरदायी हैं।'
            : 'GaonBazaar operates as a technology facilitator. Third-party product manufacturing and original packaging defects rest with the merchant/brand.',
        'bullets': isHi
            ? ['प्लेटफ़ॉर्म की कुल देयता संबंधित आर्डर के कुल मूल्य तक सीमित है', 'प्राकृतिक आपदा या नेटवर्क विफलता पर अप्रत्याशित देरी संभव']
            : ['Platform monetary liability is capped at the respective order value', 'Acts of nature, heavy monsoon floods, or cellular blackouts excused'],
      },
      {
        'num': 28,
        'category': 'Partner',
        'badge': isHi ? 'शिकायत निवारण' : 'Redressal',
        'icon': Icons.supervisor_account_outlined,
        'title': isHi ? '28. शिकायत निवारण अधिकारी (Grievance Redressal Officer)' : '28. Grievance Redressal',
        'body': isHi
            ? 'भारतीय उपभोक्ता संरक्षण (ई-कॉमर्स) नियम, 2020 के तहत नियुक्त शिकायत निवारण अधिकारी: श्री राजेश कुमार, ईमेल: grievance@gaonbazaar.in, संपर्क: +91 98000 00000।'
            : 'Designated Grievance Redressal Officer under Consumer Protection (E-Commerce) Rules, 2020: Mr. Rajesh Kumar, Email: grievance@gaonbazaar.in, Ph: +91 98000 00000.',
        'bullets': isHi
            ? ['शिकायत प्राप्ति की पावती 48 घंटों में दी जाएगी', 'समस्या का अंतिम समाधान अधिकतम 30 दिनों के भीतर अनिवार्य है']
            : ['Acknowledgement of grievance issued within 48 business hours', 'Complete disposal of grievance within 30 days maximum'],
      },
      {
        'num': 29,
        'category': 'Partner',
        'badge': isHi ? 'संपर्क केंद्र' : 'Contacts',
        'icon': Icons.contact_mail_outlined,
        'title': isHi ? '29. कानूनी एवं सहायता संपर्क (Legal & Support Contacts)' : '29. Legal and Support Contacts',
        'body': isHi
            ? 'मीनापुर परिचालन हब: ग्राम पंचायत भवन के पास, चतुरसी, मीनापुर ब्लॉक, मुजफ्फरपुर, बिहार - 843128। कस्टमर केयर: support@gaonbazaar.in, फ़ोन: +91 98000 00000।'
            : 'Operational Hub: Near Gram Panchayat Bhavan, Chaturshi, Minapur Block, Muzaffarpur, Bihar - 843128. Customer Support: support@gaonbazaar.in, Tel: +91 98000 00000.',
        'bullets': isHi
            ? ['कार्य दिवस: सोमवार से रविवार, प्रातः 7:00 बजे से रात्रि 9:00 बजे तक', 'विधिक सूचनाएं कानूनी विभाग: legal@gaonbazaar.in पर प्रेषित करें']
            : ['Operating Hours: Mon - Sun, 07:00 AM - 09:00 PM IST', 'Official legal notices: legal@gaonbazaar.in'],
      },
      {
        'num': 30,
        'category': 'Orders',
        'badge': isHi ? 'संस्करण 2.4' : 'v2.4 Nov 2026',
        'icon': Icons.update_outlined,
        'title': isHi ? '30. नीति अद्यतन व प्रभावी तिथि (Policy Updates & Effective Dates)' : '30. Policy Updates and Effective Dates',
        'body': isHi
            ? 'यह नीति संस्करण 2.4 नवंबर 2026 से प्रभावी है। प्लेटफ़ॉर्म समय-समय पर नियमों को अद्यतन कर सकता है। महत्वपूर्ण परिवर्तनों की सूचना ऐप में 7 दिन पूर्व दी जाएगी।'
            : 'This policy Version 2.4 is effective as of November 2026. GaonBazaar may revise terms periodically. Material updates communicated 7 days in advance via in-app banner.',
        'bullets': isHi
            ? ['नवीनतम नीतियां हमेशा इस स्क्रीन पर उपलब्ध रहेंगी', 'सेवाओं का निरंतर उपयोग अद्यतन शर्तों की स्वीकृति माना जाएगा']
            : ['Latest policies remain accessible anytime under Account → Policies', 'Continued use of the platform constitutes acceptance of updated terms'],
      },
    ];

    final query = _searchCtrl.text.trim().toLowerCase();
    final filteredClauses = allClauses.where((c) {
      if (_selectedCategory != 'All' && c['category'] != _selectedCategory) {
        return false;
      }
      if (query.isEmpty) return true;
      final title = (c['title'] as String).toLowerCase();
      final body = (c['body'] as String).toLowerCase();
      final badge = (c['badge'] as String).toLowerCase();
      return title.contains(query) || body.contains(query) || badge.contains(query);
    }).toList();

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          tooltip: isHi ? 'पीछे जाएं' : 'Back',
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: Text(
          loc.tr('policies_title'),
          style: const TextStyle(fontWeight: FontWeight.w800),
        ),
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Top Search & Category Filter Header
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              color: isDark ? const Color(0xFF1E293B) : Colors.grey.shade100,
              child: Column(
                children: [
                  TextField(
                    controller: _searchCtrl,
                    onChanged: (_) => setState(() {}),
                    decoration: InputDecoration(
                      hintText: isHi ? '30 धाराओं में खोजें (उदा. रिफ़ंड, 8 किमी, पेआउट)' : 'Search 30 clauses (e.g. refund, fee, runner)',
                      prefixIcon: const Icon(Icons.search, size: 20),
                      suffixIcon: _searchCtrl.text.isNotEmpty
                          ? IconButton(
                              icon: const Icon(Icons.clear, size: 18),
                              onPressed: () => setState(() => _searchCtrl.clear()),
                            )
                          : null,
                      filled: true,
                      fillColor: Theme.of(context).cardColor,
                      contentPadding: const EdgeInsets.symmetric(vertical: 0, horizontal: 16),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(10),
                        borderSide: BorderSide.none,
                      ),
                    ),
                  ),
                  const SizedBox(height: 10),
                  SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Row(
                      children: [
                        _buildFilterPill('All', isHi ? 'सभी 30 धाराएं' : 'All 30 Clauses'),
                        const SizedBox(width: 8),
                        _buildFilterPill('Orders', isHi ? 'ऑर्डर व डिलीवरी' : 'Orders & Delivery'),
                        const SizedBox(width: 8),
                        _buildFilterPill('Payments', isHi ? 'भुगतान व रिफ़ंड' : 'Payments & Refunds'),
                        const SizedBox(width: 8),
                        _buildFilterPill('Partner', isHi ? 'विक्रेता व साथी' : 'Vendors & Partners'),
                        const SizedBox(width: 8),
                        _buildFilterPill('Privacy', isHi ? 'गोपनीयता व सुरक्षा' : 'Privacy & Security'),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            // Clauses List
            Expanded(
              child: filteredClauses.isEmpty
                  ? Center(
                      child: Text(
                        isHi ? 'कोई धारा नहीं मिली।' : 'No matching policy clauses found.',
                        style: const TextStyle(color: Colors.grey),
                      ),
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.all(16),
                      itemCount: filteredClauses.length + 1,
                      itemBuilder: (context, idx) {
                        if (idx == 0) {
                          return Container(
                            margin: const EdgeInsets.only(bottom: 14),
                            padding: const EdgeInsets.all(14),
                            decoration: BoxDecoration(
                              color: GBColors.primary.withValues(alpha: 0.08),
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(color: GBColors.primary.withValues(alpha: 0.2)),
                            ),
                            child: Row(
                              children: [
                                const Icon(Icons.verified_outlined, color: GBColors.primary, size: 30),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        isHi ? 'आधिकारिक 30 ग्रामीण वाणिज्य नीतियां' : 'Official 30 Commercial Clauses',
                                        style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14, color: GBColors.primary),
                                      ),
                                      const SizedBox(height: 2),
                                      Text(
                                        isHi
                                            ? 'मीनापुर पायलट क्लस्टर (मुजफ्फरपुर, बिहार) — प्रभावी संस्करण 2.4'
                                            : 'Minapur Pilot Cluster (Muzaffarpur, Bihar) — Version 2.4 Active',
                                        style: TextStyle(fontSize: 11, color: isDark ? Colors.white70 : Colors.black87),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                          );
                        }

                        final clause = filteredClauses[idx - 1];
                        return _buildPolicyCard(
                          context: context,
                          icon: clause['icon'] as IconData,
                          badge: clause['badge'] as String,
                          title: clause['title'] as String,
                          body: clause['body'] as String,
                          bulletPoints: (clause['bullets'] as List).cast<String>(),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFilterPill(String categoryKey, String label) {
    final isSelected = _selectedCategory == categoryKey;
    return InkWell(
      onTap: () => setState(() => _selectedCategory = categoryKey),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: isSelected ? GBColors.primary : Colors.white,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isSelected ? GBColors.primary : Colors.grey.shade300,
          ),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.w700,
            color: isSelected ? Colors.white : Colors.black87,
          ),
        ),
      ),
    );
  }

  Widget _buildPolicyCard({
    required BuildContext context,
    required IconData icon,
    required String badge,
    required String title,
    required String body,
    required List<String> bulletPoints,
  }) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isDark ? GBColors.cardDark : Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: isDark ? GBColors.borderDark : GBColors.borderLight,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.04),
            blurRadius: 4,
            offset: const Offset(0, 1),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: GBColors.primary.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(icon, color: GBColors.primary, size: 20),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  title,
                  style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: GBColors.primary.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  badge,
                  style: const TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w700,
                    color: GBColors.primary,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            body,
            style: TextStyle(
              fontSize: 12.5,
              height: 1.45,
              color: isDark ? Colors.white70 : Colors.black87,
            ),
          ),
          if (bulletPoints.isNotEmpty) ...[
            const SizedBox(height: 8),
            ...bulletPoints.map(
              (bp) => Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Padding(
                      padding: EdgeInsets.only(top: 4, right: 8),
                      child: Icon(Icons.check_circle, size: 13, color: GBColors.primary),
                    ),
                    Expanded(
                      child: Text(
                        bp,
                        style: TextStyle(
                          fontSize: 11.5,
                          color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
