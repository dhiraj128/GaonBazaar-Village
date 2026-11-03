import 'dart:async';
import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../state/vendor_state.dart';
import 'vendor_auth_screen.dart';
import 'vendor_dashboard_screen.dart';
import 'vendor_language_selection_screen.dart';
import 'vendor_pending_approval_screen.dart';
import 'vendor_onboarding_wizard.dart';

class VendorSplashScreen extends StatefulWidget {
  const VendorSplashScreen({super.key});

  @override
  State<VendorSplashScreen> createState() => _VendorSplashScreenState();
}

class _VendorSplashScreenState extends State<VendorSplashScreen> {
  @override
  void initState() {
    super.initState();
    Timer(const Duration(milliseconds: 1800), () {
      if (!mounted) return;
      final state = VendorStateProvider.of(context);
      SharedPreferences.getInstance().then((prefs) {
        final screen = prefs.getString('gb_v_pdf_screen');
        if (screen == 'language') {
          Navigator.of(context).pushReplacement(MaterialPageRoute(builder: (_) => const VendorLanguageSelectionScreen()));
          return;
        } else if (screen == 'auth') {
          Navigator.of(context).pushReplacement(MaterialPageRoute(builder: (_) => const VendorAuthScreen()));
          return;
        } else if (screen == 'onboarding') {
          Navigator.of(context).pushReplacement(MaterialPageRoute(builder: (_) => const VendorOnboardingWizard()));
          return;
        } else if (screen == 'pending') {
          Navigator.of(context).pushReplacement(MaterialPageRoute(builder: (_) => const VendorPendingApprovalScreen()));
          return;
        } else if (screen == 'dashboard') {
          Navigator.of(context).pushReplacement(MaterialPageRoute(builder: (_) => const VendorDashboardScreen()));
          return;
        }
      });
      if (state.currentUser != null) {
        if (state.myStore == null) {
          Navigator.of(context).pushReplacement(
            MaterialPageRoute(builder: (_) => const VendorOnboardingWizard()),
          );
        } else if (!state.isStoreApproved) {
          Navigator.of(context).pushReplacement(
            MaterialPageRoute(builder: (_) => const VendorPendingApprovalScreen()),
          );
        } else {
          Navigator.of(context).pushReplacement(
            MaterialPageRoute(builder: (_) => const VendorDashboardScreen()),
          );
        }
      } else if (state.hasSavedLocale) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const VendorAuthScreen()),
        );
      } else {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const VendorLanguageSelectionScreen()),
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: GBColors.primaryDark,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(22),
              decoration: BoxDecoration(
                color: Colors.white,
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.2),
                    blurRadius: 16,
                    offset: const Offset(0, 6),
                  ),
                ],
              ),
              child: const Icon(
                Icons.storefront_rounded,
                size: 60,
                color: GBColors.primaryDark,
              ),
            ),
            const SizedBox(height: 24),
            const Text(
              'गाँव बाज़ार विक्रेता',
              style: TextStyle(
                color: Colors.white,
                fontSize: 28,
                fontWeight: FontWeight.w900,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              'GaonBazaar Shopkeeper Partner',
              style: TextStyle(
                color: Colors.white.withOpacity(0.85),
                fontSize: 15,
                fontWeight: FontWeight.w600,
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
                '0% कमीशन • तुरंत डिलीवरी • मीनापुर पायलट',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
            const SizedBox(height: 48),
            const SizedBox(
              width: 24,
              height: 24,
              child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2.5),
            ),
          ],
        ),
      ),
    );
  }
}
