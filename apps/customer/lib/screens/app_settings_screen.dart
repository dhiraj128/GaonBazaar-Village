import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
import '../state/app_state.dart';

class AppSettingsScreen extends StatefulWidget {
  const AppSettingsScreen({super.key});

  @override
  State<AppSettingsScreen> createState() => _AppSettingsScreenState();
}

class _AppSettingsScreenState extends State<AppSettingsScreen> {
  bool _orderNotifications = true;

  @override
  Widget build(BuildContext context) {
    final state = AppStateProvider.of(context);
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          tooltip: loc.isHindi ? 'पीछे जाएं' : 'Back',
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: Text(loc.tr('app_settings_title'), style: const TextStyle(fontWeight: FontWeight.w800)),
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
          children: [
            // 1. Appearance Section (Explicit Light / Dark, No System)
            Text(
              loc.tr('appearance_section'),
              style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 10),
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
                  RadioListTile<ThemeMode>(
                    value: ThemeMode.light,
                    groupValue: state.themeMode,
                    activeColor: GBColors.primary,
                    title: Row(
                      children: [
                        const Icon(Icons.light_mode_outlined, size: 20, color: Colors.orange),
                        const SizedBox(width: 12),
                        Text(loc.tr('appearance_light'), style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14)),
                      ],
                    ),
                    onChanged: (val) {
                      if (val != null) state.setTheme(val);
                    },
                  ),
                  const Divider(height: 1, indent: 48),
                  RadioListTile<ThemeMode>(
                    value: ThemeMode.dark,
                    groupValue: state.themeMode,
                    activeColor: GBColors.primary,
                    title: Row(
                      children: [
                        const Icon(Icons.dark_mode_outlined, size: 20, color: Colors.indigo),
                        const SizedBox(width: 12),
                        Text(loc.tr('appearance_dark'), style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14)),
                      ],
                    ),
                    onChanged: (val) {
                      if (val != null) state.setTheme(val);
                    },
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // 2. Language Section
            Text(
              loc.tr('language_section'),
              style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 10),
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
                  RadioListTile<String>(
                    value: 'hi',
                    groupValue: state.currentLocale,
                    activeColor: GBColors.primary,
                    title: Text(loc.tr('lang_hindi'), style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14)),
                    onChanged: (val) {
                      if (val != null) state.setLocale(val);
                    },
                  ),
                  const Divider(height: 1, indent: 20),
                  RadioListTile<String>(
                    value: 'en',
                    groupValue: state.currentLocale,
                    activeColor: GBColors.primary,
                    title: Text(loc.tr('lang_english'), style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14)),
                    onChanged: (val) {
                      if (val != null) state.setLocale(val);
                    },
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // 3. Notifications Section
            Text(
              loc.tr('notifications_section'),
              style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 10),
            Container(
              decoration: BoxDecoration(
                color: isDark ? GBColors.cardDark : Colors.white,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(
                  color: isDark ? GBColors.borderDark : GBColors.borderLight,
                ),
              ),
              child: SwitchListTile(
                value: _orderNotifications,
                activeColor: GBColors.primary,
                title: Text(loc.tr('order_notifications'), style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14)),
                subtitle: Text(
                  loc.isHindi ? 'ऑर्डर की स्थिति में बदलाव की तुरंत सूचना' : 'Real-time order stage updates',
                  style: TextStyle(fontSize: 12, color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight),
                ),
                onChanged: (val) {
                  setState(() => _orderNotifications = val);
                },
              ),
            ),

            const SizedBox(height: 24),

            // 4. Permissions Section
            Text(
              loc.tr('system_permissions'),
              style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 10),
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
                  _buildPermissionRow(
                    icon: Icons.mic_none,
                    title: loc.isHindi ? 'माइक्रोफ़ोन अनुमति' : 'Microphone Permission',
                    subtitle: loc.isHindi ? 'वॉयस शॉपिंग और खोज के लिए' : 'For voice search and shopping assistant',
                  ),
                  const Divider(height: 20),
                  _buildPermissionRow(
                    icon: Icons.location_on_outlined,
                    title: loc.isHindi ? 'लोकेशन (जीपीएस) अनुमति' : 'Location (GPS) Permission',
                    subtitle: loc.isHindi ? '8.0 किमी डिलीवरी दायरा जांच के लिए' : 'For 8.0 km delivery geofence validation',
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // 5. Staging Build Diagnostics Badge
            Center(
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 7),
                decoration: BoxDecoration(
                  color: isDark ? GBColors.cardDark : Colors.grey.shade100,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: Colors.grey.shade300),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.verified, size: 14, color: GBColors.primary),
                    const SizedBox(width: 6),
                    Text(
                      'GaonBazaar Village • Staging Build a9197f5',
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w700,
                        color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }

  Widget _buildPermissionRow({required IconData icon, required String title, required String subtitle}) {
    return Row(
      children: [
        Icon(icon, color: GBColors.primary, size: 22),
        const SizedBox(width: 14),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13)),
              Text(subtitle, style: const TextStyle(fontSize: 11, color: Colors.grey)),
            ],
          ),
        ),
        const Icon(Icons.check_circle, color: GBColors.primary, size: 18),
      ],
    );
  }
}
