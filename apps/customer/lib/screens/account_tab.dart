import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
import '../state/app_state.dart';
import 'profile_screen.dart';
import 'map_picker_screen.dart';
import 'payment_settings_screen.dart';
import 'app_settings_screen.dart';
import 'support_hub_screen.dart';
import 'policies_screen.dart';
import 'language_selection_screen.dart';

class AccountTab extends StatelessWidget {
  final Function(int)? onTabChange;

  const AccountTab({super.key, this.onTabChange});

  @override
  Widget build(BuildContext context) {
    final state = AppStateProvider.of(context);
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    final currentName = state.currentUser?.name;
    final userName = (currentName != null && currentName.trim().isNotEmpty)
        ? currentName.trim()
        : (loc.isHindi ? 'गाँव बाज़ार ग्राहक' : 'GaonBazaar Customer');

    final userPhone = (state.currentUser?.phone != null && state.currentUser!.phone.isNotEmpty)
        ? state.currentUser!.phone
        : '9800000000';

    final userEmail = state.currentUser?.email;

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          tooltip: loc.isHindi ? 'होम पर वापस जाएं' : 'Back to Home',
          onPressed: () {
            if (onTabChange != null) {
              onTabChange!(0);
            } else if (Navigator.of(context).canPop()) {
              Navigator.of(context).pop();
            }
          },
        ),
        title: Text(
          loc.tr('tab_account'),
          style: const TextStyle(fontWeight: FontWeight.w800),
        ),
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
                          userName,
                          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
                        ),
                        const SizedBox(height: 3),
                        Text(
                          '+91 $userPhone',
                          style: TextStyle(
                            fontSize: 13,
                            color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
                          ),
                        ),
                        if (userEmail != null && userEmail.isNotEmpty) ...[
                          const SizedBox(height: 2),
                          Text(
                            userEmail,
                            style: TextStyle(
                              fontSize: 12,
                              color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
                            ),
                          ),
                        ],
                        const SizedBox(height: 4),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: GBColors.primary.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            loc.isHindi ? 'गाँव बाज़ार सदस्य' : 'GaonBazaar Member',
                            style: const TextStyle(
                              fontSize: 10,
                              fontWeight: FontWeight.w700,
                              color: GBColors.primary,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.edit_outlined, size: 20, color: GBColors.primary),
                    onPressed: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(builder: (_) => const ProfileScreen()),
                      );
                    },
                  ),
                ],
              ),
            ),

            const SizedBox(height: 18),

            // EXACTLY 7 PRIMARY ENTRIES LINKED TO DEDICATED FULL SCREENS
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
                    subtitle: loc.isHindi ? 'नाम, मोबाइल व ईमेल जानकारी' : 'Name, mobile and contact details',
                    onTap: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(builder: (_) => const ProfileScreen()),
                      );
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
                    subtitle: loc.isHindi
                        ? 'कैश ऑन डिलीवरी (COD) व यूपीआई'
                        : 'Cash on Delivery (COD) & Online UPI',
                    onTap: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(builder: (_) => const PaymentSettingsScreen()),
                      );
                    },
                  ),
                  const Divider(height: 1, indent: 56),

                  // 4. App Settings (Theme, Language, Notifications)
                  _buildMenuItem(
                    context: context,
                    icon: Icons.settings_outlined,
                    title: loc.tr('menu_app_settings'),
                    subtitle: loc.isHindi
                        ? 'भाषा: हिंदी • थीम: ${isDark ? "रात (Dark)" : "दिन (Light)"}'
                        : 'Language: English • Theme: ${isDark ? "Dark" : "Light"}',
                    onTap: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(builder: (_) => const AppSettingsScreen()),
                      );
                    },
                  ),
                  const Divider(height: 1, indent: 56),

                  // 5. Help & Support Hub
                  _buildMenuItem(
                    context: context,
                    icon: Icons.headset_mic_outlined,
                    title: loc.tr('menu_help'),
                    subtitle: loc.isHindi
                        ? 'एआई सहायता, शिकायतें व हेल्पलाइन'
                        : 'AI assistant, support tickets & helpline',
                    onTap: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(builder: (_) => const SupportHubScreen()),
                      );
                    },
                  ),
                  const Divider(height: 1, indent: 56),

                  // 6. Policies & Legal
                  _buildMenuItem(
                    context: context,
                    icon: Icons.policy_outlined,
                    title: loc.tr('menu_policies'),
                    subtitle: loc.isHindi
                        ? '8.0 किमी दायरा, ₹3.00 शुल्क व 180s रद्दीकरण'
                        : '8.0 km radius, 3.00 fee & 180s cancellation',
                    onTap: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(builder: (_) => const PoliciesScreen()),
                      );
                    },
                  ),
                  const Divider(height: 1, indent: 56),

                  // 7. Logout
                  _buildMenuItem(
                    context: context,
                    icon: Icons.logout_rounded,
                    title: loc.tr('menu_logout'),
                    subtitle: loc.isHindi ? 'खाते से बाहर निकलें' : 'Sign out from this device',
                    textColor: GBColors.error,
                    iconColor: GBColors.error,
                    onTap: () => _confirmLogout(context, state, loc),
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

  void _confirmLogout(BuildContext context, CustomerAppState state, GBLocalizations loc) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(loc.tr('menu_logout')),
        content: Text(loc.tr('logout_confirm')),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: Text(loc.tr('cancel')),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: GBColors.error,
              foregroundColor: Colors.white,
            ),
            onPressed: () {
              Navigator.of(ctx).pop();
              state.logout();
              Navigator.of(context).pushAndRemoveUntil(
                MaterialPageRoute(builder: (_) => const LanguageSelectionScreen()),
                (r) => false,
              );
            },
            child: Text(loc.tr('confirm')),
          ),
        ],
      ),
    );
  }

  Widget _buildMenuItem({
    required BuildContext context,
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
    Color? textColor,
    Color? iconColor,
  }) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return ListTile(
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      leading: Container(
        width: 40,
        height: 40,
        decoration: BoxDecoration(
          color: (iconColor ?? GBColors.primary).withOpacity(0.1),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Icon(icon, color: iconColor ?? GBColors.primary, size: 22),
      ),
      title: Text(
        title,
        style: TextStyle(
          fontWeight: FontWeight.w700,
          fontSize: 15,
          color: textColor,
        ),
      ),
      subtitle: Text(
        subtitle,
        style: TextStyle(
          fontSize: 12,
          color: textColor?.withOpacity(0.7) ??
              (isDark ? GBColors.textMutedDark : GBColors.textMutedLight),
        ),
      ),
      trailing: Icon(
        Icons.chevron_right,
        size: 20,
        color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
      ),
      onTap: onTap,
    );
  }
}
