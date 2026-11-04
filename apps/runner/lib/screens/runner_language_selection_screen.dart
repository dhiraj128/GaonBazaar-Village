import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import '../state/runner_state.dart';
import 'runner_auth_screen.dart';

class RunnerLanguageSelectionScreen extends StatefulWidget {
  const RunnerLanguageSelectionScreen({super.key});

  @override
  State<RunnerLanguageSelectionScreen> createState() => _RunnerLanguageSelectionScreenState();
}

class _RunnerLanguageSelectionScreenState extends State<RunnerLanguageSelectionScreen> {
  String selected = 'hi';

  @override
  Widget build(BuildContext context) {
    final state = RunnerStateProvider.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 24),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: GBColors.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.two_wheeler_rounded, color: GBColors.primary, size: 36),
              ),
              const SizedBox(height: 20),
              Text(
                selected == 'hi' ? 'डिलीवरी साथी भाषा चुनें' : 'Select Delivery Language',
                style: GBTypography.displayLarge(context),
              ),
              const SizedBox(height: 8),
              Text(
                selected == 'hi'
                    ? 'गाँव बाज़ार डिलीवरी साथी पोर्टल में आपका स्वागत है। अपनी कार्य भाषा चुनें:'
                    : 'Welcome to GaonBazaar Delivery Partner Portal. Choose your working language:',
                style: GBTypography.bodyMedium(context),
              ),
              const SizedBox(height: 32),
              // Option 1: Hindi
              _buildLangCard(
                langCode: 'hi',
                title: 'हिंदी',
                subtitle: 'डिलीवरी ऑर्डर और दैनिक कमाई हिंदी में देखें',
                isSelected: selected == 'hi',
                isDark: isDark,
              ),
              const SizedBox(height: 16),
              // Option 2: English
              _buildLangCard(
                langCode: 'en',
                title: 'English',
                subtitle: 'View delivery jobs and daily payouts in English',
                isSelected: selected == 'en',
                isDark: isDark,
              ),
              const Spacer(),
              GBPrimaryButton(
                label: selected == 'hi' ? 'आगे बढ़ें' : 'Continue',
                onPressed: () {
                  state.setLocale(selected);
                  Navigator.of(context).pushReplacement(
                    MaterialPageRoute(builder: (_) => const RunnerAuthScreen()),
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
      onTap: () => setState(() => selected = langCode),
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: isDark ? const Color(0xFF1E293B) : Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: isSelected ? GBColors.primary : (isDark ? Colors.white12 : Colors.black12),
            width: isSelected ? 2.5 : 1,
          ),
          boxShadow: isSelected
              ? [
                  BoxShadow(
                    color: GBColors.primary.withOpacity(0.12),
                    blurRadius: 10,
                    offset: const Offset(0, 4),
                  )
                ]
              : null,
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
                      color: isSelected ? GBColors.primary : (isDark ? Colors.white : Colors.black87),
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: TextStyle(
                      fontSize: 13,
                      color: isDark ? Colors.white60 : Colors.black54,
                    ),
                  ),
                ],
              ),
            ),
            Icon(
              isSelected ? Icons.check_circle_rounded : Icons.radio_button_off_rounded,
              color: isSelected ? GBColors.primary : Colors.grey,
              size: 24,
            ),
          ],
        ),
      ),
    );
  }
}
