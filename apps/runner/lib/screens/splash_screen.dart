import 'dart:async';
import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import '../state/runner_state.dart';
import 'runner_auth_screen.dart';
import 'runner_dashboard_screen.dart';

class RunnerSplashScreen extends StatefulWidget {
  const RunnerSplashScreen({super.key});

  @override
  State<RunnerSplashScreen> createState() => _RunnerSplashScreenState();
}

class _RunnerSplashScreenState extends State<RunnerSplashScreen> {
  @override
  void initState() {
    super.initState();
    Timer(const Duration(milliseconds: 1800), () {
      if (!mounted) return;
      final state = RunnerStateProvider.of(context);
      if (state.currentUser != null) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const RunnerDashboardScreen()),
        );
      } else {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const RunnerAuthScreen()),
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF1B5E20), // Dark Forest Emerald
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
                  BoxShadow(color: Colors.black.withOpacity(0.2), blurRadius: 16, offset: const Offset(0, 6)),
                ],
              ),
              child: const Icon(
                Icons.two_wheeler_rounded,
                size: 64,
                color: Color(0xFF1B5E20),
              ),
            ),
            const SizedBox(height: 24),
            const Text(
              'गाँव बाज़ार डिलीवरी साथी',
              style: TextStyle(
                color: Colors.white,
                fontSize: 26,
                fontWeight: FontWeight.w900,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              'GaonBazaar Delivery Partner',
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
                '८ किमी क्षेत्र • तुरंत भुगतान • मीनापुर पायलट',
                style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.w600),
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
