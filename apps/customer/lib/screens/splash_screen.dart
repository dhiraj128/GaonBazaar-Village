import 'dart:async';
import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import '../state/app_state.dart';
import 'language_selection_screen.dart';
import 'phone_auth_screen.dart';
import 'main_nav_screen.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    Timer(const Duration(milliseconds: 1800), () {
      if (!mounted) return;
      final state = AppStateProvider.of(context);
      if (state.currentUser != null) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const MainNavScreen()),
        );
      } else if (state.hasSavedLocale) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const PhoneAuthScreen()),
        );
      } else {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const LanguageSelectionScreen()),
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: GBColors.primary,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: Colors.white,
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.15),
                    blurRadius: 20,
                    offset: const Offset(0, 8),
                  ),
                ],
              ),
              child: const Icon(
                Icons.local_shipping_rounded,
                size: 64,
                color: GBColors.primary,
              ),
            ),
            const SizedBox(height: 24),
            const Text(
              'गाँव बाज़ार',
              style: TextStyle(
                color: Colors.white,
                fontSize: 32,
                fontWeight: FontWeight.w900,
                letterSpacing: 0.5,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              'GaonBazaar',
              style: TextStyle(
                color: Colors.white.withOpacity(0.85),
                fontSize: 16,
                fontWeight: FontWeight.w600,
                letterSpacing: 1.2,
              ),
            ),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.2),
                borderRadius: BorderRadius.circular(20),
              ),
              child: const Text(
                'गाँव का अपना डिलीवरी बाज़ार (Minapur Pilot)',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 12,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
            const SizedBox(height: 48),
            const SizedBox(
              width: 24,
              height: 24,
              child: CircularProgressIndicator(
                color: Colors.white,
                strokeWidth: 2.5,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
