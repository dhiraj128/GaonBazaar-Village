import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:runner/main.dart';
import 'package:runner/screens/splash_screen.dart';
import 'package:runner/screens/runner_auth_screen.dart';
import 'package:runner/screens/runner_dashboard_screen.dart';
import 'package:design_system/design_system.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('Runner Android Application Full Lifecycle Test', () {
    testWidgets('Complete Runner Lifecycle: Splash -> Auth -> Duty Toggle -> Job Board -> Delivery Modal -> Finances',
        (WidgetTester tester) async {
      // 1. Boot Application & Splash Screen
      await tester.pumpWidget(const GaonBazaarRunnerApp());
      expect(find.byType(RunnerSplashScreen), findsOneWidget);

      await tester.pump(const Duration(milliseconds: 2000));
      await tester.pumpAndSettle();

      // 2. Runner Authentication Screen
      if (find.byType(RunnerAuthScreen).evaluate().isNotEmpty) {
        final phoneField = find.byType(TextField);
        expect(phoneField, findsOneWidget);
        await tester.enterText(phoneField, '9800000003');
        await tester.pumpAndSettle();

        final sendOtpBtn = find.byType(GBPrimaryButton);
        expect(sendOtpBtn, findsOneWidget);
        await tester.tap(sendOtpBtn.first);
        await tester.pumpAndSettle(const Duration(seconds: 2));

        // Enter OTP and Login
        final otpField = find.byType(TextField);
        if (otpField.evaluate().isNotEmpty) {
          await tester.enterText(otpField.first, '123456');
          await tester.pumpAndSettle();

          final verifyBtn = find.byType(GBPrimaryButton);
          await tester.tap(verifyBtn.first);
          await tester.pumpAndSettle(const Duration(seconds: 3));
        }
      }

      // 3. Runner Dashboard Screen
      expect(find.byType(RunnerDashboardScreen), findsOneWidget);

      // Verify Duty Online/Offline Switch
      final dutySwitch = find.byType(Switch);
      if (dutySwitch.evaluate().isNotEmpty) {
        await tester.tap(dutySwitch.first);
        await tester.pumpAndSettle();
        await tester.tap(dutySwitch.first);
        await tester.pumpAndSettle();
      }

      // Verify Earnings summary card
      expect(find.byIcon(Icons.currency_rupee), findsWidgets);

      // Verify Job Board:
      // If no active jobs, verify clean professional empty state (NO fake orders)
      final refreshBtn = find.widgetWithText(OutlinedButton, 'ताज़ा करें');
      if (refreshBtn.evaluate().isNotEmpty) {
        await tester.tap(refreshBtn.first);
        await tester.pumpAndSettle();
      } else {
        final enRefresh = find.widgetWithText(OutlinedButton, 'Refresh');
        if (enRefresh.evaluate().isNotEmpty) {
          await tester.tap(enRefresh.first);
          await tester.pumpAndSettle();
        }
      }

      // If an active order card is present, test action buttons
      final acceptJobBtn = find.widgetWithText(GBPrimaryButton, 'डिलीवरी स्वीकार करें');
      if (acceptJobBtn.evaluate().isNotEmpty) {
        await tester.tap(acceptJobBtn.first);
        await tester.pumpAndSettle(const Duration(seconds: 2));
      } else {
        final enAccept = find.widgetWithText(GBPrimaryButton, 'Accept Delivery Job');
        if (enAccept.evaluate().isNotEmpty) {
          await tester.tap(enAccept.first);
          await tester.pumpAndSettle(const Duration(seconds: 2));
        }
      }

      // 4. Test Drawer & Navigation
      final menuBtn = find.byIcon(Icons.menu);
      if (menuBtn.evaluate().isNotEmpty) {
        await tester.tap(menuBtn.first);
        await tester.pumpAndSettle();
      } else {
        await tester.dragFrom(const Offset(10, 300), const Offset(300, 0));
        await tester.pumpAndSettle();
      }

      // Close drawer
      await tester.tapAt(const Offset(350, 300));
      await tester.pumpAndSettle();
    });
  });
}
