import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
import 'package:shared_preferences/shared_preferences.dart';

class PaymentSettingsScreen extends StatefulWidget {
  const PaymentSettingsScreen({super.key});

  @override
  State<PaymentSettingsScreen> createState() => _PaymentSettingsScreenState();
}

class _PaymentSettingsScreenState extends State<PaymentSettingsScreen> {
  String _defaultPaymentMethod = 'UPI'; // 'UPI', 'COD', 'CARD'
  double _walletBalance = 150.0; // GaonBazaar Rural Wallet

  List<Map<String, String>> _savedUpiIds = [
    {'id': 'upi_1', 'handle': '9800000000@ybl', 'app': 'PhonePe', 'verified': 'true'},
    {'id': 'upi_2', 'handle': 'dhiraj.village@okaxis', 'app': 'Google Pay', 'verified': 'true'},
  ];

  List<Map<String, String>> _savedCards = [
    {
      'id': 'card_1',
      'bank': 'State Bank of India (SBI)',
      'type': 'RuPay Kisan Debit',
      'number': '•••• •••• •••• 4242',
      'holder': 'Dhiraj Kumar',
      'expiry': '08/28',
    },
    {
      'id': 'card_2',
      'bank': 'Punjab National Bank',
      'type': 'RuPay Platinum',
      'number': '•••• •••• •••• 8819',
      'holder': 'Dhiraj Kumar',
      'expiry': '11/29',
    },
  ];

  @override
  void initState() {
    super.initState();
    _loadSavedPaymentSettings();
  }

  Future<void> _loadSavedPaymentSettings() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final defaultMethod = prefs.getString('gb_default_payment_method');
      if (defaultMethod != null) {
        setState(() => _defaultPaymentMethod = defaultMethod);
      }
      final savedUpiJson = prefs.getString('gb_saved_upi_list');
      if (savedUpiJson != null) {
        final decoded = (jsonDecode(savedUpiJson) as List).map((e) => Map<String, String>.from(e as Map)).toList();
        setState(() => _savedUpiIds = decoded);
      }
      final savedCardsJson = prefs.getString('gb_saved_cards_list');
      if (savedCardsJson != null) {
        final decoded = (jsonDecode(savedCardsJson) as List).map((e) => Map<String, String>.from(e as Map)).toList();
        setState(() => _savedCards = decoded);
      }
      final wallet = prefs.getDouble('gb_wallet_balance');
      if (wallet != null) {
        setState(() => _walletBalance = wallet);
      }
    } catch (_) {}
  }

  Future<void> _saveSettingsToPrefs() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('gb_default_payment_method', _defaultPaymentMethod);
      await prefs.setString('gb_saved_upi_list', jsonEncode(_savedUpiIds));
      await prefs.setString('gb_saved_cards_list', jsonEncode(_savedCards));
      await prefs.setDouble('gb_wallet_balance', _walletBalance);
    } catch (_) {}
  }

  void _showAddUpiDialog() {
    final loc = GBLocalizations.of(context);
    final isHi = loc.isHindi;
    final ctrl = TextEditingController();
    String selectedApp = 'Google Pay';

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) => Padding(
        padding: EdgeInsets.only(
          left: 20,
          right: 20,
          top: 20,
          bottom: MediaQuery.of(ctx).viewInsets.bottom + 20,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.qr_code_2, color: GBColors.primary, size: 26),
                const SizedBox(width: 10),
                Text(
                  isHi ? 'नया यूपीआई आईडी जोड़ें' : 'Add New UPI ID',
                  style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
                ),
              ],
            ),
            const SizedBox(height: 14),
            DropdownButtonFormField<String>(
              value: selectedApp,
              decoration: InputDecoration(
                labelText: isHi ? 'यूपीआई ऐप' : 'UPI App',
                border: const OutlineInputBorder(),
              ),
              items: ['Google Pay', 'PhonePe', 'Paytm', 'BHIM UPI', 'Other Bank UPI']
                  .map((a) => DropdownMenuItem(value: a, child: Text(a)))
                  .toList(),
              onChanged: (v) => selectedApp = v ?? 'Google Pay',
            ),
            const SizedBox(height: 14),
            TextField(
              controller: ctrl,
              decoration: InputDecoration(
                labelText: isHi ? 'यूपीआई हैंडल' : 'UPI Handle',
                hintText: isHi ? 'उदा. मोबाइल@upi या नाम@okhdfcbank' : 'e.g. mobile@upi or name@okhdfcbank',
                border: const OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 18),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: GBColors.primary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
                onPressed: () {
                  final text = ctrl.text.trim();
                  if (text.isEmpty || !text.contains('@')) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text(isHi ? 'कृपया मान्य यूपीआई आईडी दर्ज करें (@ आवश्यक)' : 'Please enter valid UPI ID (must contain @)')),
                    );
                    return;
                  }
                  setState(() {
                    _savedUpiIds.add({
                      'id': 'upi_${DateTime.now().millisecondsSinceEpoch}',
                      'handle': text,
                      'app': selectedApp,
                      'verified': 'true',
                    });
                  });
                  _saveSettingsToPrefs();
                  Navigator.of(ctx).pop();
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(isHi ? 'यूपीआई आईडी सफलतापूर्वक सत्यापित एवं सुरक्षित हो गई!' : 'UPI ID verified and saved!'),
                      backgroundColor: GBColors.success,
                    ),
                  );
                },
                child: Text(isHi ? 'सत्यापित करें व सहेजें' : 'Verify & Save UPI'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showAddCardDialog() {
    final loc = GBLocalizations.of(context);
    final isHi = loc.isHindi;
    final nameCtrl = TextEditingController();
    final numCtrl = TextEditingController();
    final expCtrl = TextEditingController();
    final cvvCtrl = TextEditingController();

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) => Padding(
        padding: EdgeInsets.only(
          left: 20,
          right: 20,
          top: 20,
          bottom: MediaQuery.of(ctx).viewInsets.bottom + 20,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.credit_card, color: GBColors.primary, size: 26),
                const SizedBox(width: 10),
                Text(
                  isHi ? 'नया RuPay / डेबिट कार्ड जोड़ें' : 'Add New RuPay / Debit Card',
                  style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
                ),
              ],
            ),
            const SizedBox(height: 14),
            TextField(
              controller: nameCtrl,
              decoration: InputDecoration(
                labelText: isHi ? 'कार्डधारक का नाम' : 'Cardholder Name',
                hintText: isHi ? 'उदा. धीरज कुमार' : 'e.g. Dhiraj Kumar',
                border: const OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: numCtrl,
              keyboardType: TextInputType.number,
              maxLength: 16,
              decoration: const InputDecoration(
                labelText: '16-Digit Card Number',
                hintText: '4123 4567 8901 2345',
                counterText: '',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: expCtrl,
                    keyboardType: TextInputType.number,
                    maxLength: 5,
                    decoration: const InputDecoration(
                      labelText: 'Expiry (MM/YY)',
                      hintText: '12/28',
                      counterText: '',
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: TextField(
                    controller: cvvCtrl,
                    keyboardType: TextInputType.number,
                    maxLength: 3,
                    obscureText: true,
                    decoration: const InputDecoration(
                      labelText: 'CVV',
                      hintText: '•••',
                      counterText: '',
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 18),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: GBColors.primary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
                onPressed: () {
                  final num = numCtrl.text.trim();
                  if (num.length < 12) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text(isHi ? 'कृपया 16-अंकीय मान्य कार्ड नंबर दर्ज करें' : 'Please enter valid 16-digit card number')),
                    );
                    return;
                  }
                  final masked = '•••• •••• •••• ${num.substring(num.length - 4)}';
                  setState(() {
                    _savedCards.add({
                      'id': 'card_${DateTime.now().millisecondsSinceEpoch}',
                      'bank': 'State Bank of India (RuPay)',
                      'type': 'RuPay Debit Card',
                      'number': masked,
                      'holder': nameCtrl.text.trim().isNotEmpty ? nameCtrl.text.trim() : 'Valued Customer',
                      'expiry': expCtrl.text.trim().isNotEmpty ? expCtrl.text.trim() : '12/28',
                    });
                  });
                  _saveSettingsToPrefs();
                  Navigator.of(ctx).pop();
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(isHi ? 'कार्ड टोकन सुरक्षा के साथ सुरक्षित हो गया!' : 'Card saved securely with tokenization!'),
                      backgroundColor: GBColors.success,
                    ),
                  );
                },
                child: Text(isHi ? 'कार्ड सुरक्षित सहेजें' : 'Save Card Securely'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showAddWalletMoneyDialog() {
    final loc = GBLocalizations.of(context);
    final isHi = loc.isHindi;

    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) => Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.account_balance_wallet, color: GBColors.primary, size: 26),
                const SizedBox(width: 10),
                Text(
                  isHi ? 'गाँव बाज़ार वॉलेट रीचार्ज' : 'Top Up Rural Wallet',
                  style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              isHi ? 'तुरंत चेकआउट और ₹0 प्लेटफ़ॉर्म शुल्क हेतु राशि चुनें:' : 'Select amount for 1-tap checkout and ₹0 platform fee:',
              style: const TextStyle(fontSize: 13, color: Colors.grey),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [100, 200, 500].map((amt) {
                return ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: GBColors.primary.withAlpha(20),
                    foregroundColor: GBColors.primary,
                    elevation: 0,
                    padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                  onPressed: () {
                    setState(() => _walletBalance += amt);
                    _saveSettingsToPrefs();
                    Navigator.of(ctx).pop();
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text(isHi ? '₹$amt वॉलेट में सफलतापूर्वक जुड़ गए!' : '₹$amt added to wallet successfully!'),
                        backgroundColor: GBColors.success,
                      ),
                    );
                  },
                  child: Text('₹$amt', style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 16)),
                );
              }).toList(),
            ),
            const SizedBox(height: 14),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final loc = GBLocalizations.of(context);
    final isHi = loc.isHindi;
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          tooltip: isHi ? 'पीछे जाएं' : 'Back',
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: Text(
          isHi ? 'पेमेंट सेटिंग्स एवं भुगतान विधियां' : 'Payment Methods & Settings',
          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
        ),
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
          children: [
            // GaonBazaar Wallet Card
            Container(
              padding: const EdgeInsets.all(18),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFF1B5E20), Color(0xFF2E7D32)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(color: Colors.black.withAlpha(25), blurRadius: 8, offset: const Offset(0, 2)),
                ],
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        isHi ? 'गाँव बाज़ार रूरल वॉलेट' : 'GaonBazaar Rural Wallet',
                        style: const TextStyle(color: Colors.white70, fontSize: 12, fontWeight: FontWeight.w600),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        '₹${_walletBalance.toStringAsFixed(2)}',
                        style: const TextStyle(color: Colors.white, fontSize: 26, fontWeight: FontWeight.w900),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        isHi ? 'रिफ़ंड व 1-टैप त्वरित भुगतान' : 'Instant refunds & 1-tap checkout',
                        style: const TextStyle(color: Colors.white60, fontSize: 11),
                      ),
                    ],
                  ),
                  ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.white,
                      foregroundColor: GBColors.primary,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                    icon: const Icon(Icons.add_circle_outline, size: 16),
                    label: Text(isHi ? 'पैसे जोड़ें' : 'Add Cash'),
                    onPressed: _showAddWalletMoneyDialog,
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),

            // Default Payment Method Selector Card
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: isDark ? GBColors.cardDark : Colors.white,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: isDark ? GBColors.borderDark : GBColors.borderLight),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    isHi ? 'डिफ़ॉल्ट भुगतान प्राथमिकता (Default Method)' : 'Default Payment Preference',
                    style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
                  ),
                  const SizedBox(height: 8),
                  RadioListTile<String>(
                    value: 'UPI',
                    groupValue: _defaultPaymentMethod,
                    activeColor: GBColors.primary,
                    contentPadding: EdgeInsets.zero,
                    title: Text(isHi ? 'यूपीआई (Google Pay, PhonePe, Paytm)' : 'UPI (Google Pay, PhonePe, Paytm)', style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700)),
                    onChanged: (v) {
                      setState(() => _defaultPaymentMethod = v!);
                      _saveSettingsToPrefs();
                    },
                  ),
                  RadioListTile<String>(
                    value: 'COD',
                    groupValue: _defaultPaymentMethod,
                    activeColor: GBColors.primary,
                    contentPadding: EdgeInsets.zero,
                    title: Text(isHi ? 'डिलीवरी पर नकद (Cash on Delivery)' : 'Cash on Delivery (COD)', style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700)),
                    onChanged: (v) {
                      setState(() => _defaultPaymentMethod = v!);
                      _saveSettingsToPrefs();
                    },
                  ),
                  RadioListTile<String>(
                    value: 'CARD',
                    groupValue: _defaultPaymentMethod,
                    activeColor: GBColors.primary,
                    contentPadding: EdgeInsets.zero,
                    title: Text(isHi ? 'डेबिट / RuPay कार्ड' : 'Debit / RuPay Card', style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700)),
                    onChanged: (v) {
                      setState(() => _defaultPaymentMethod = v!);
                      _saveSettingsToPrefs();
                    },
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),

            // Saved UPI IDs Section
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: isDark ? GBColors.cardDark : Colors.white,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: isDark ? GBColors.borderDark : GBColors.borderLight),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.qr_code_2, color: GBColors.primary, size: 20),
                          const SizedBox(width: 8),
                          Text(
                            isHi ? 'सहेजे गए यूपीआई खाते' : 'Saved UPI Accounts',
                            style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
                          ),
                        ],
                      ),
                      TextButton.icon(
                        icon: const Icon(Icons.add, size: 16),
                        label: Text(isHi ? 'नया जोड़ें' : 'Add New'),
                        onPressed: _showAddUpiDialog,
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  if (_savedUpiIds.isEmpty)
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 8),
                      child: Text(isHi ? 'कोई यूपीआई खाता सहेजा नहीं गया है।' : 'No saved UPI accounts.', style: const TextStyle(color: Colors.grey, fontSize: 12)),
                    )
                  else
                    ..._savedUpiIds.map((u) {
                      return ListTile(
                        contentPadding: EdgeInsets.zero,
                        leading: CircleAvatar(
                          backgroundColor: GBColors.primary.withAlpha(25),
                          child: const Icon(Icons.account_balance, color: GBColors.primary, size: 18),
                        ),
                        title: Text(u['handle'] ?? '', style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13)),
                        subtitle: Text('${u["app"]} • Verified', style: const TextStyle(fontSize: 11, color: Colors.grey)),
                        trailing: IconButton(
                          icon: const Icon(Icons.delete_outline, size: 18, color: Colors.grey),
                          onPressed: () {
                            setState(() => _savedUpiIds.removeWhere((item) => item['id'] == u['id']));
                            _saveSettingsToPrefs();
                          },
                        ),
                      );
                    }),
                ],
              ),
            ),

            const SizedBox(height: 20),

            // Saved Cards Section
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: isDark ? GBColors.cardDark : Colors.white,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: isDark ? GBColors.borderDark : GBColors.borderLight),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.credit_card, color: Colors.blue, size: 20),
                          const SizedBox(width: 8),
                          Text(
                            isHi ? 'सहेजे गए डेबिट / RuPay कार्ड' : 'Saved Debit / RuPay Cards',
                            style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
                          ),
                        ],
                      ),
                      TextButton.icon(
                        icon: const Icon(Icons.add, size: 16),
                        label: Text(isHi ? 'नया कार्ड' : 'Add Card'),
                        onPressed: _showAddCardDialog,
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  if (_savedCards.isEmpty)
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 8),
                      child: Text(isHi ? 'कोई कार्ड सहेजा नहीं गया है।' : 'No saved cards.', style: const TextStyle(color: Colors.grey, fontSize: 12)),
                    )
                  else
                    ..._savedCards.map((c) {
                      return Container(
                        margin: const EdgeInsets.only(bottom: 10),
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: isDark ? GBColors.surfaceDark : Colors.grey.shade50,
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(color: Colors.grey.withAlpha(40)),
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text('${c["bank"]} (${c["type"]})', style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 12)),
                                const SizedBox(height: 4),
                                Text(c['number'] ?? '', style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 14, letterSpacing: 2)),
                                const SizedBox(height: 2),
                                Text('${c["holder"]} • Exp: ${c["expiry"]}', style: const TextStyle(fontSize: 11, color: Colors.grey)),
                              ],
                            ),
                            IconButton(
                              icon: const Icon(Icons.delete_outline, size: 18, color: Colors.grey),
                              onPressed: () {
                                setState(() => _savedCards.removeWhere((item) => item['id'] == c['id']));
                                _saveSettingsToPrefs();
                              },
                            ),
                          ],
                        ),
                      );
                    }),
                ],
              ),
            ),

            const SizedBox(height: 20),

            // RBI Rural Security Certificate
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: GBColors.primary.withAlpha(15),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: GBColors.primary.withAlpha(50)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.security, color: GBColors.primary, size: 20),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      isHi
                          ? '256-बिट बैंक स्तरीय एन्क्रिप्शन। आपके कार्ड नंबर कभी भी हमारे सर्वर पर सीधे स्टोर नहीं होते।'
                          : '256-bit bank grade encryption. Card numbers are securely tokenized per RBI regulations.',
                      style: const TextStyle(fontSize: 11, height: 1.3),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
