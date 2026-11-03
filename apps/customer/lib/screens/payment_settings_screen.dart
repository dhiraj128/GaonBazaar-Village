import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../state/app_state.dart';

class PaymentSettingsScreen extends StatefulWidget {
  const PaymentSettingsScreen({super.key});

  @override
  State<PaymentSettingsScreen> createState() => _PaymentSettingsScreenState();
}

class _PaymentSettingsScreenState extends State<PaymentSettingsScreen> {
  String _preferredMethod = 'COD'; // 'COD' or 'ONLINE'
  bool _isLoading = true;
  bool _onlineGatewayEnabled = false;
  String _gatewayMessage = '';

  @override
  void initState() {
    super.initState();
    _loadSettingsAndStatus();
  }

  Future<void> _loadSettingsAndStatus() async {
    setState(() => _isLoading = true);
    try {
      final prefs = await SharedPreferences.getInstance();
      final savedPref = prefs.getString('gb_preferred_payment_method');
      if (savedPref != null) {
        _preferredMethod = savedPref;
      }

      final state = AppStateProvider.of(context);
      final statusRes = await state.apiClient.getPaymentStatus();
      if (statusRes.isSuccess && statusRes.data != null) {
        _onlineGatewayEnabled = statusRes.data!['online_enabled'] == true;
        _gatewayMessage = statusRes.data!['message'] as String? ?? '';
      } else {
        _onlineGatewayEnabled = false;
        _gatewayMessage = 'Online payments currently unavailable. Cash on Delivery (COD) is 100% operational.';
      }
    } catch (_) {
      _onlineGatewayEnabled = false;
      _gatewayMessage = 'Cash on Delivery (COD) is 100% operational.';
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _setPreferredMethod(String method) async {
    setState(() => _preferredMethod = method);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('gb_preferred_payment_method', method);
    if (!mounted) return;
    final loc = GBLocalizations.of(context);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          loc.isHindi
              ? 'प्राथमिक भुगतान विधि सेट हो गई: ${method == "COD" ? "कैश ऑन डिलीवरी (COD)" : "ऑनलाइन भुगतान"}'
              : 'Default payment method set to: ${method == "COD" ? "Cash on Delivery (COD)" : "Online Payment"}',
        ),
        backgroundColor: GBColors.success,
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
        child: _isLoading
            ? const Center(child: CircularProgressIndicator())
            : RefreshIndicator(
                onRefresh: _loadSettingsAndStatus,
                child: ListView(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                  children: [
                    // Cash on Delivery Primary Rural Mode
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: isDark ? GBColors.cardDark : Colors.white,
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(
                          color: _preferredMethod == 'COD' ? GBColors.primary : (isDark ? GBColors.borderDark : GBColors.borderLight),
                          width: _preferredMethod == 'COD' ? 2 : 1,
                        ),
                        boxShadow: const [BoxShadow(color: Colors.black12, blurRadius: 4, offset: Offset(0, 1))],
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.all(8),
                                decoration: BoxDecoration(
                                  color: GBColors.primary.withAlpha(25),
                                  shape: BoxShape.circle,
                                ),
                                child: const Icon(Icons.payments, color: GBColors.primary, size: 24),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      isHi ? 'कैश ऑन डिलीवरी (COD)' : 'Cash on Delivery (COD)',
                                      style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15),
                                    ),
                                    Text(
                                      isHi ? 'सक्रिय • 100% सुरक्षित एवं ग्रामीण पसंदीदा' : 'Active • 100% Reliable & Village Standard',
                                      style: const TextStyle(fontSize: 11, color: GBColors.success, fontWeight: FontWeight.bold),
                                    ),
                                  ],
                                ),
                              ),
                              Radio<String>(
                                value: 'COD',
                                groupValue: _preferredMethod,
                                activeColor: GBColors.primary,
                                onChanged: (v) => _setPreferredMethod('COD'),
                              ),
                            ],
                          ),
                          const SizedBox(height: 10),
                          Text(
                            isHi
                                ? 'सामान मिलने पर डिलीवरी पार्टनर को नकद भुगतान करें। डिलीवरी साथी के पास खुल्ले पैसे और यूपीआई क्यूआर उपलब्ध रहता है।'
                                : 'Pay cash directly upon doorstep delivery. Delivery partners carry exact change and dynamic UPI QR code on delivery.',
                            style: TextStyle(fontSize: 12, color: isDark ? Colors.grey.shade300 : Colors.grey.shade700),
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 14),

                    // Online Payment Gateway (Razorpay) Real Status Card
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: isDark ? GBColors.cardDark : Colors.white,
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(
                          color: _preferredMethod == 'ONLINE' ? GBColors.primary : (isDark ? GBColors.borderDark : GBColors.borderLight),
                          width: _preferredMethod == 'ONLINE' ? 2 : 1,
                        ),
                        boxShadow: const [BoxShadow(color: Colors.black12, blurRadius: 4, offset: Offset(0, 1))],
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.all(8),
                                decoration: BoxDecoration(
                                  color: (_onlineGatewayEnabled ? GBColors.primary : Colors.grey).withAlpha(25),
                                  shape: BoxShape.circle,
                                ),
                                child: Icon(
                                  Icons.account_balance,
                                  color: _onlineGatewayEnabled ? GBColors.primary : Colors.grey,
                                  size: 24,
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      isHi ? 'ऑनलाइन भुगतान (UPI / Cards / Net Banking)' : 'Online Payments (UPI / Cards / Net Banking)',
                                      style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
                                    ),
                                    Text(
                                      _onlineGatewayEnabled
                                          ? (isHi ? 'गेटवे सक्रिय (Razorpay)' : 'Gateway Active (Razorpay)')
                                          : (isHi ? 'गेटवे अप्रमाणित (सत्यापन जारी)' : 'Gateway Currently Unconfigured'),
                                      style: TextStyle(
                                        fontSize: 11,
                                        fontWeight: FontWeight.bold,
                                        color: _onlineGatewayEnabled ? GBColors.success : GBColors.warning,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              Radio<String>(
                                value: 'ONLINE',
                                groupValue: _preferredMethod,
                                activeColor: GBColors.primary,
                                onChanged: (v) {
                                  if (!_onlineGatewayEnabled) {
                                    ScaffoldMessenger.of(context).showSnackBar(
                                      SnackBar(
                                        content: Text(
                                          isHi
                                              ? 'ऑनलाइन गेटवे वर्तमान में सक्रिय नहीं है। कैश ऑन डिलीवरी (COD) का उपयोग करें।'
                                              : 'Online gateway is unconfigured. Please use Cash on Delivery (COD).',
                                        ),
                                        backgroundColor: GBColors.warning,
                                      ),
                                    );
                                  } else {
                                    _setPreferredMethod('ONLINE');
                                  }
                                },
                              ),
                            ],
                          ),
                          const SizedBox(height: 10),
                          Container(
                            padding: const EdgeInsets.all(10),
                            decoration: BoxDecoration(
                              color: (_onlineGatewayEnabled ? GBColors.success : GBColors.warning).withAlpha(15),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Row(
                              children: [
                                Icon(
                                  _onlineGatewayEnabled ? Icons.check_circle_outline : Icons.info_outline,
                                  size: 16,
                                  color: _onlineGatewayEnabled ? GBColors.success : GBColors.warning,
                                ),
                                const SizedBox(width: 8),
                                Expanded(
                                  child: Text(
                                    _gatewayMessage.isNotEmpty ? _gatewayMessage : 'Cash on Delivery (COD) is available.',
                                    style: TextStyle(
                                      fontSize: 11,
                                      color: _onlineGatewayEnabled ? GBColors.success : Colors.amber.shade900,
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 20),

                    // Security & Transparency Statement
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: isDark ? GBColors.backgroundDark : Colors.grey.shade50,
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(color: Colors.grey.shade300),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              const Icon(Icons.shield_outlined, color: GBColors.primary, size: 20),
                              const SizedBox(width: 8),
                              Text(
                                isHi ? 'गाँव बाज़ार सुरक्षा प्रतिज्ञा' : 'GaonBazaar Payment Safeguards',
                                style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 13),
                              ),
                            ],
                          ),
                          const SizedBox(height: 10),
                          _buildPolicyItem(
                            Icons.check,
                            isHi ? 'कोई छुपा हुआ शुल्क नहीं — केवल ₹3 पारदर्शी प्लेटफ़ॉर्म शुल्क।' : 'Zero hidden charges — only flat transparent ₹3 platform fee.',
                            isDark,
                          ),
                          _buildPolicyItem(
                            Icons.lock_outline,
                            isHi ? 'हम कभी भी आपका कार्ड नंबर, सीवीवी या पिन सहेजते नहीं हैं।' : 'We never collect or store raw card numbers, CVVs, or bank PINs.',
                            isDark,
                          ),
                          _buildPolicyItem(
                            Icons.replay,
                            isHi ? '180 सेकंड में ऑर्डर रद्द करने पर 100% तुरंत रिफ़ंड गारंटी।' : '100% full refund guarantee on cancellation within 180 seconds.',
                            isDark,
                          ),
                          _buildPolicyItem(
                            Icons.handshake_outlined,
                            isHi ? 'सामान हाथ में मिलने के बाद ही भुगतान (कैश या क्यूआर)।' : 'Pay only after physical inspection of items at your doorstep.',
                            isDark,
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
      ),
    );
  }

  Widget _buildPolicyItem(IconData icon, String text, bool isDark) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 16, color: GBColors.primary),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              text,
              style: TextStyle(
                fontSize: 12,
                color: isDark ? Colors.grey.shade300 : Colors.grey.shade800,
                height: 1.3,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
