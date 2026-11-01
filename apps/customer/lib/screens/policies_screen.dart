import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';

class PoliciesScreen extends StatelessWidget {
  const PoliciesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: Text(
          loc.tr('policies_title'),
          style: const TextStyle(fontWeight: FontWeight.w800),
        ),
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
          children: [
            // Overview Banner
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: GBColors.primary.withOpacity(0.08),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: GBColors.primary.withOpacity(0.25)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.shield_outlined, color: GBColors.primary, size: 36),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          loc.isHindi ? 'पारदर्शी ग्रामीण नीतियां' : 'Transparent Rural Policies',
                          style: const TextStyle(
                            fontWeight: FontWeight.w800,
                            fontSize: 16,
                            color: GBColors.primary,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          loc.isHindi
                              ? 'गाँव बाज़ार निष्पक्ष और स्पष्ट नियमों के साथ ग्रामीण समुदायों को सशक्त बनाता है।'
                              : 'GaonBazaar operates with transparent, community-first standards designed for village commerce.',
                          style: TextStyle(
                            fontSize: 12,
                            color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 18),

            // Policy 1: 8.0 km Delivery Radius
            _buildPolicyCard(
              context: context,
              icon: Icons.radar,
              badge: loc.isHindi ? '8.0 किमी दायरा' : '8.0 km Radius',
              title: loc.tr('policy_delivery_title'),
              body: loc.tr('policy_delivery_body'),
              bulletPoints: loc.isHindi
                  ? [
                      'मीनापुर ब्लॉक की स्थानीय किराना और सब्ज़ी दुकानों से सीधी डिलीवरी',
                      '8.0 किमी से अधिक दूरी के पते स्वतः ब्लॉक कर दिए जाते हैं',
                      'ताज़ा दूध, सब्ज़ी और आवश्यक सामग्री 45 मिनट के भीतर पहुंचेगी',
                    ]
                  : [
                      'Direct delivery from local Minapur village stores and farmers',
                      'Orders beyond 8.0 km are automatically halted by the geofence engine',
                      'Ensures fresh vegetables, dairy, and grocery delivery within 45 minutes',
                    ],
            ),

            const SizedBox(height: 14),

            // Policy 2: Fixed ₹3.00 Platform Fee
            _buildPolicyCard(
              context: context,
              icon: Icons.currency_rupee,
              badge: loc.isHindi ? '₹3.00 निश्चित' : '₹3.00 Fixed',
              title: loc.tr('policy_fee_title'),
              body: loc.tr('policy_fee_body'),
              bulletPoints: loc.isHindi
                  ? [
                      'प्रत्येक आर्डर पर मात्र ₹3.00 का स्थिर पारदर्शी शुल्क',
                      'स्थानीय डिलीवरी मित्रों के स्वास्थ्य एवं दुर्घटना बीमा में योगदान',
                      'कोई छिपा हुआ शुल्क या अतिरिक्त सर्ज चार्ज नहीं',
                    ]
                  : [
                      'Flat, non-negotiable rural platform fee of 3.00 per completed order',
                      'Directly funds local village delivery partner insurance and emergency support',
                      'No surge charges, hidden convenience fees, or nighttime penalties',
                    ],
            ),

            const SizedBox(height: 14),

            // Policy 3: 180-Second Cancellation
            _buildPolicyCard(
              context: context,
              icon: Icons.timer_outlined,
              badge: loc.isHindi ? '180 सेकंड रद्दीकरण' : '180s Free Cancellation',
              title: loc.tr('policy_cancel_title'),
              body: loc.tr('policy_cancel_body'),
              bulletPoints: loc.isHindi
                  ? [
                      'ऑर्डर देने के तुरंत बाद 180 सेकंड तक बिना किसी शुल्क के रद्दीकरण संभव',
                      '100% रिफ़ंड सीधे आपके खाते या कैश विकल्प में तत्काल लागू',
                      'दुकानदार द्वारा सामान पैक करने के बाद रद्दीकरण बंद हो जाता है',
                    ]
                  : [
                      'Zero-penalty cancellation window for exactly 180 seconds post-placement',
                      '100% immediate refund to source payment or order clearance',
                      'Locks once the village store begins physical packaging to prevent waste',
                    ],
            ),

            const SizedBox(height: 14),

            // Policy 4: Returns & Refunds
            _buildPolicyCard(
              context: context,
              icon: Icons.verified_user_outlined,
              badge: loc.isHindi ? '2 घंटे सुरक्षा' : '2-Hour Resolution',
              title: loc.tr('policy_returns_title'),
              body: loc.tr('policy_returns_body'),
              bulletPoints: loc.isHindi
                  ? [
                      'सामान मिलने के 2 घंटे के भीतर ऐप के सहायता केंद्र से शिकायत दर्ज करें',
                      'खराब फल, सब्ज़ी या छूटे हुए सामान का 100% त्वरित समाधान',
                      'स्थानीय सहायता टीम 30 मिनट के भीतर जांच कर कार्रवाई करेगी',
                    ]
                  : [
                      'Report damaged, spoiled, or missing goods within 2 hours of delivery',
                      'Instant replacement or direct refund for perishable agricultural items',
                      'Local Minapur support desk verifies and resolves tickets within 30 minutes',
                    ],
            ),

            const SizedBox(height: 20),

            // Grievance Redressal Officer Information
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: isDark ? GBColors.cardDark : Colors.white,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: isDark ? GBColors.borderDark : GBColors.borderLight,
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    loc.isHindi ? 'शिकायत निवारण अधिकारी' : 'Grievance Redressal Officer',
                    style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    loc.isHindi
                        ? 'अमित कुमार (नोडल अधिकारी)\nगाँव बाज़ार ऑपरेशन्स हब, मीनापुर ब्लॉक\nमुज़फ़्फ़रपुर, बिहार - 843128\nईमेल: support@gaonbazaar.in\nहेल्पलाइन: +91 9800000000'
                        : 'Amit Kumar (Nodal Officer)\nGaonBazaar Operations Hub, Minapur Block\nMuzaffarpur, Bihar - 843128\nEmail: support@gaonbazaar.in\nHelpline: +91 9800000000',
                    style: TextStyle(
                      fontSize: 12,
                      height: 1.5,
                      color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
          ],
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
                  color: GBColors.primary.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(icon, color: GBColors.primary, size: 20),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  title,
                  style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15),
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: GBColors.primary.withOpacity(0.1),
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
          const SizedBox(height: 12),
          Text(
            body,
            style: TextStyle(
              fontSize: 13,
              height: 1.45,
              color: isDark ? Colors.white70 : Colors.black87,
            ),
          ),
          const SizedBox(height: 10),
          ...bulletPoints.map(
            (bp) => Padding(
              padding: const EdgeInsets.only(bottom: 6),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Padding(
                    padding: EdgeInsets.only(top: 4, right: 8),
                    child: Icon(Icons.check_circle, size: 14, color: GBColors.primary),
                  ),
                  Expanded(
                    child: Text(
                      bp,
                      style: TextStyle(
                        fontSize: 12,
                        color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
