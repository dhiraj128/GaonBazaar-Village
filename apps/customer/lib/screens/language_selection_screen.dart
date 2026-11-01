import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import '../state/app_state.dart';
import 'phone_auth_screen.dart';

class LanguageSelectionScreen extends StatefulWidget {
  const LanguageSelectionScreen({super.key});

  @override
  State<LanguageSelectionScreen> createState() => _LanguageSelectionScreenState();
}

class _LanguageSelectionScreenState extends State<LanguageSelectionScreen> {
  String selected = 'hi';

  @override
  Widget build(BuildContext context) {
    final state = AppStateProvider.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 20),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: GBColors.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.translate_rounded, color: GBColors.primary, size: 32),
              ),
              const SizedBox(height: 20),
              Text(
                selected == 'hi' ? 'अपनी भाषा चुनें' : 'Choose Your Language',
                style: GBTypography.displayLarge(context),
              ),
              const SizedBox(height: 8),
              Text(
                selected == 'hi'
                    ? 'गाँव बाज़ार में आपका स्वागत है। अपनी पसंदीदा भाषा चुनें:'
                    : 'Welcome to GaonBazaar. Select your preferred app language:',
                style: GBTypography.bodyMedium(context),
              ),
              const SizedBox(height: 32),
              // Option 1: Hindi
              _buildLangCard(
                langCode: 'hi',
                title: 'हिंदी (Hindi)',
                subtitle: 'गाँव का अपना बाज़ार हिंदी में चलाएं',
                isSelected: selected == 'hi',
                isDark: isDark,
              ),
              const SizedBox(height: 16),
              // Option 2: English
              _buildLangCard(
                langCode: 'en',
                title: 'English',
                subtitle: 'Shop village essentials in English',
                isSelected: selected == 'en',
                isDark: isDark,
              ),
              const Spacer(),
              GBPrimaryButton(
                label: selected == 'hi' ? 'आगे बढ़ें (Continue)' : 'Continue',
                onPressed: () {
                  state.setLocale(selected);
                  Navigator.of(context).push(
                    MaterialPageRoute(builder: (_) => const PhoneAuthScreen()),
                  );
                },
              ),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildLangCard({
    required String langCode,
    required String title,
    required String subtitle,
    required bool isSelected,
    required bool isDark,
  }) {
    return InkWell(
      onTap: () {
        setState(() {
          selected = langCode;
        });
      },
      borderRadius: BorderRadius.circular(14),
      child: Container(
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          color: isSelected
              ? GBColors.primary.withOpacity(isDark ? 0.2 : 0.08)
              : (isDark ? GBColors.cardDark : GBColors.cardLight),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(
            color: isSelected ? GBColors.primary : (isDark ? GBColors.borderDark : GBColors.borderLight),
            width: isSelected ? 2 : 1,
          ),
        ),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w700,
                      color: isSelected ? GBColors.primary : null,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: TextStyle(
                      fontSize: 13,
                      color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
                    ),
                  ),
                ],
              ),
            ),
            Container(
              width: 24,
              height: 24,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: isSelected ? GBColors.primary : Colors.transparent,
                border: Border.all(
                  color: isSelected ? GBColors.primary : Colors.grey,
                  width: 2,
                ),
              ),
              child: isSelected
                  ? const Icon(Icons.check, size: 16, color: Colors.white)
                  : null,
            ),
          ],
        ),
      ),
    );
  }
}
