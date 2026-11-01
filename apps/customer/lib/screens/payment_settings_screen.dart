import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';

class PaymentSettingsScreen extends StatelessWidget {
  const PaymentSettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: Text(loc.tr('payments_title'), style: const TextStyle(fontWeight: FontWeight.w800)),
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
          children: [
            // COD Section Card
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: isDark ? GBColors.cardDark : Colors.white,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(
                  color: isDark ? GBColors.borderDark : GBColors.borderLight,
                ),
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
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Icon(Icons.money, color: GBColors.primary, size: 22),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              loc.tr('cod_status'),
                              style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              loc.tr('cod_desc'),
                              style: TextStyle(
                                fontSize: 12,
                                color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
                              ),
                            ),
                          ],
                        ),
                      ),
                      const Icon(Icons.check_circle, color: GBColors.primary, size: 22),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // Online Payment Section Card
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: isDark ? GBColors.cardDark : Colors.white,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(
                  color: isDark ? GBColors.borderDark : GBColors.borderLight,
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: Colors.blue.withAlpha(25),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Icon(Icons.qr_code_2, color: Colors.blue, size: 22),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          loc.tr('online_status'),
                          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text(
                    loc.tr('supported_payment_apps'),
                    style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
                  ),
                  const SizedBox(height: 12),
                  // Certified secure payment note
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: GBColors.primary.withAlpha(20),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: GBColors.primary.withAlpha(80)),
                    ),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Icon(Icons.verified_user_outlined, size: 18, color: GBColors.primary),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Text(
                            loc.tr('online_staging_note'),
                            style: TextStyle(
                              fontSize: 12,
                              height: 1.4,
                              color: isDark ? GBColors.textPrimaryDark : GBColors.textPrimaryLight,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // Payment FAQs Card
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: isDark ? GBColors.cardDark : Colors.white,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(
                  color: isDark ? GBColors.borderDark : GBColors.borderLight,
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    loc.tr('payment_faqs'),
                    style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15),
                  ),
                  const SizedBox(height: 12),
                  _buildFaqItem(
                    q: loc.isHindi ? 'क्या डिलीवरी पर नकद (COD) स्वीकार्य है?' : 'Is Cash on Delivery (COD) accepted?',
                    a: loc.isHindi
                        ? 'हाँ, मीनापुर ब्लॉक के सभी गाँवों में डिलीवरी पर नकद या यूपीआई द्वारा भुगतान पूरी तरह स्वीकार्य है।'
                        : 'Yes, Cash on Delivery or on-spot UPI is accepted across all villages in Minapur Block.',
                    isDark: isDark,
                  ),
                  const Divider(height: 20),
                  _buildFaqItem(
                    q: loc.isHindi ? 'क्या प्लेटफ़ॉर्म शुल्क वापस होता है?' : 'Is the platform fee refundable?',
                    a: loc.isHindi
                        ? '180 सेकंड के भीतर ऑर्डर रद्द करने पर ₹3 प्लेटफ़ॉर्म शुल्क सहित 100% पूरा रिफ़ंड वापस होता है।'
                        : 'If an order is cancelled within the 180s window, the 3.00 platform fee is 100% refunded.',
                    isDark: isDark,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFaqItem({required String q, required String a, required bool isDark}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(q, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13)),
        const SizedBox(height: 4),
        Text(
          a,
          style: TextStyle(
            fontSize: 12,
            height: 1.4,
            color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
          ),
        ),
      ],
    );
  }
}
