import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
import '../state/app_state.dart';
import 'language_selection_screen.dart';
import 'map_picker_screen.dart';

class AccountTab extends StatelessWidget {
  const AccountTab({super.key});

  @override
  Widget build(BuildContext context) {
    final state = AppStateProvider.of(context);
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: Text(loc.tr('tab_account'), style: const TextStyle(fontWeight: FontWeight.w800)),
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          children: [
            // User Header Profile Card
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: isDark ? GBColors.cardDark : Colors.white,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(
                  color: isDark ? GBColors.borderDark : GBColors.borderLight,
                ),
              ),
              child: Row(
                children: [
                  Container(
                    width: 56,
                    height: 56,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: GBColors.primary.withOpacity(0.12),
                    ),
                    child: const Center(
                      child: Icon(Icons.person, size: 32, color: GBColors.primary),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          state.currentUser?.name ?? 'रमेश सिंह (Ramesh Singh)',
                          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '+91 ${state.currentUser?.phone ?? "9876543210"}',
                          style: TextStyle(
                            fontSize: 13,
                            color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Container(
                          margin: const EdgeInsets.only(top: 4),
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: GBColors.primary.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: const Text(
                            'Minapur Pilot Member',
                            style: TextStyle(fontSize: 10, fontWeight: FontWeight.w700, color: GBColors.primary),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),

            // EXACTLY 7 PRIMARY ENTRIES
            Container(
              decoration: BoxDecoration(
                color: isDark ? GBColors.cardDark : Colors.white,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(
                  color: isDark ? GBColors.borderDark : GBColors.borderLight,
                ),
              ),
              child: Column(
                children: [
                  // 1. My Profile
                  _buildMenuItem(
                    context: context,
                    icon: Icons.person_outline_rounded,
                    title: loc.tr('menu_profile'),
                    subtitle: 'नाम व संपर्क जानकारी',
                    onTap: () {
                      _showEditProfileDialog(context, state);
                    },
                  ),
                  const Divider(height: 1, indent: 56),

                  // 2. My Addresses
                  _buildMenuItem(
                    context: context,
                    icon: Icons.location_on_outlined,
                    title: loc.tr('menu_addresses'),
                    subtitle: '${state.selectedAddress.village}, ${state.selectedAddress.block}',
                    onTap: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(builder: (_) => const MapPickerScreen()),
                      );
                    },
                  ),
                  const Divider(height: 1, indent: 56),

                  // 3. Payment Settings
                  _buildMenuItem(
                    context: context,
                    icon: Icons.account_balance_wallet_outlined,
                    title: loc.tr('menu_payments'),
                    subtitle: 'कैश ऑन डिलीवरी (COD) व यूपीआई',
                    onTap: () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('भुगतान विधियाँ: कैश ऑन डिलीवरी (COD) डिफ़ॉल्ट सक्षम है।')),
                      );
                    },
                  ),
                  const Divider(height: 1, indent: 56),

                  // 4. App Settings (Theme Light/Dark, Language)
                  _buildMenuItem(
                    context: context,
                    icon: Icons.settings_outlined,
                    title: loc.tr('menu_app_settings'),
                    subtitle: 'भाषा: ${state.isHindi ? "हिंदी" : "English"} • थीम: ${isDark ? "Dark" : "Light"}',
                    onTap: () {
                      _showAppSettingsDialog(context, state);
                    },
                  ),
                  const Divider(height: 1, indent: 56),

                  // 5. Help & Support
                  _buildMenuItem(
                    context: context,
                    icon: Icons.headset_mic_outlined,
                    title: loc.tr('menu_help'),
                    subtitle: 'टोल-फ्री नंबर व सहायता टिकट',
                    onTap: () {
                      _showHelpDialog(context);
                    },
                  ),
                  const Divider(height: 1, indent: 56),

                  // 6. Policies & Legal
                  _buildMenuItem(
                    context: context,
                    icon: Icons.policy_outlined,
                    title: loc.tr('menu_policies'),
                    subtitle: '८ किमी डिलीवरी व वापसी नीति',
                    onTap: () {
                      _showPoliciesDialog(context);
                    },
                  ),
                  const Divider(height: 1, indent: 56),

                  // 7. Logout
                  _buildMenuItem(
                    context: context,
                    icon: Icons.logout_rounded,
                    title: loc.tr('menu_logout'),
                    subtitle: 'खाते से बाहर निकलें',
                    textColor: GBColors.error,
                    iconColor: GBColors.error,
                    onTap: () {
                      state.logout();
                      Navigator.of(context).pushAndRemoveUntil(
                        MaterialPageRoute(builder: (_) => const LanguageSelectionScreen()),
                        (r) => false,
                      );
                    },
                  ),
                ],
              ),
            ),
            const SizedBox(height: 30),
          ],
        ),
      ),
    );
  }

  Widget _buildMenuItem({
    required BuildContext context,
    required IconData icon,
    required String title,
    String? subtitle,
    Color? textColor,
    Color? iconColor,
    required VoidCallback onTap,
  }) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return ListTile(
      leading: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: (iconColor ?? GBColors.primary).withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Icon(icon, color: iconColor ?? GBColors.primary, size: 20),
      ),
      title: Text(
        title,
        style: TextStyle(
          fontWeight: FontWeight.w700,
          fontSize: 14,
          color: textColor,
        ),
      ),
      subtitle: subtitle != null
          ? Text(
              subtitle,
              style: TextStyle(
                fontSize: 12,
                color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
              ),
            )
          : null,
      trailing: const Icon(Icons.chevron_right, size: 20, color: Colors.grey),
      onTap: onTap,
    );
  }

  void _showEditProfileDialog(BuildContext context, CustomerAppState state) {
    final nameCtrl = TextEditingController(text: state.currentUser?.name ?? 'Ramesh Singh');
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('प्रोफ़ाइल संपादित करें (Edit Profile)'),
        content: TextField(
          controller: nameCtrl,
          decoration: const InputDecoration(labelText: 'आपका पूरा नाम (Full Name)'),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('रद्द करें'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(ctx).pop();
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('प्रोफ़ाइल सफलतापूर्वक सहेजी गई।')),
              );
            },
            child: const Text('सहेजें (Save)'),
          ),
        ],
      ),
    );
  }

  void _showAppSettingsDialog(BuildContext context, CustomerAppState state) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'ऐप सेटिंग्स (App Settings)',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 16),
            ListTile(
              title: const Text('भाषा बदलें (Change Language)'),
              subtitle: Text(state.isHindi ? 'वर्तमान: हिंदी' : 'Current: English'),
              trailing: const Icon(Icons.translate),
              onTap: () {
                state.setLocale(state.isHindi ? 'en' : 'hi');
                Navigator.of(ctx).pop();
              },
            ),
            ListTile(
              title: const Text('डार्क मोड (Dark Mode)'),
              subtitle: Text(state.themeMode == ThemeMode.dark ? 'सक्षम है' : 'अक्षम है'),
              trailing: Switch(
                value: state.themeMode == ThemeMode.dark,
                activeColor: GBColors.primary,
                onChanged: (v) {
                  state.toggleTheme();
                  Navigator.of(ctx).pop();
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showHelpDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('सहायता और समर्थन (Help & Support)'),
        content: const Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('गाँव बाज़ार मीनापुर हेल्पलाइन:'),
            SizedBox(height: 8),
            Text('📞 1800-GAON-BAZAAR', style: TextStyle(fontWeight: FontWeight.w800)),
            Text('📱 व्हाट्सएप: +91 9800000001'),
            Text('✉️ support@gaonbazaar.in'),
            SizedBox(height: 12),
            Text('कार्यालय: मीनापुर ब्लॉक चौक, मुजफ्फरपुर, बिहार'),
          ],
        ),
        actions: [
          ElevatedButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('ठीक है'),
          ),
        ],
      ),
    );
  }

  void _showPoliciesDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('गाँव बाज़ार नीतियाँ (Policies)'),
        content: const SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('१. अधिकतम डिलीवरी सीमा ८ किमी है।', style: TextStyle(fontWeight: FontWeight.w700)),
              Text('२. प्लेटफ़ॉर्म शुल्क प्रति सफल ऑर्डर केवल ₹३ है।'),
              Text('३. ऑर्डर देने के १८० सेकंड (३ मिनट) के भीतर ग्राहक ऐप से तुरंत रद्द कर सकते हैं।'),
              Text('४. डिलीवरी साथी को ओटीपी कोड बताने पर ही सामान सुपुर्द किया जाता है।'),
            ],
          ),
        ),
        actions: [
          ElevatedButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('सहमत हैं'),
          ),
        ],
      ),
    );
  }
}
