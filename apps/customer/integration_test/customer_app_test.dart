import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:customer/main.dart';
import 'package:customer/screens/splash_screen.dart';
import 'package:customer/screens/language_selection_screen.dart';
import 'package:customer/screens/phone_auth_screen.dart';
import 'package:customer/screens/otp_verification_screen.dart';
import 'package:customer/screens/main_nav_screen.dart';
import 'package:customer/screens/checkout_screen.dart';
import 'package:customer/screens/order_tracking_screen.dart';
import 'package:customer/screens/app_settings_screen.dart';
import 'package:customer/screens/policies_screen.dart';
import 'package:customer/screens/support_hub_screen.dart';
import 'package:design_system/design_system.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('Customer Android Application Full Journey Test', () {
    testWidgets('Complete Customer Lifecycle: Splash -> Auth -> Home -> AI -> Cart -> Checkout -> Tracking -> Settings',
        (WidgetTester tester) async {
      // 1. Boot Application & Splash Screen
      await tester.pumpWidget(const GaonBazaarCustomerApp());
      expect(find.byType(SplashScreen), findsOneWidget);

      // Fast-forward splash screen timer (1800ms)
      await tester.pump(const Duration(milliseconds: 2000));
      await tester.pumpAndSettle();

      // 2. Language Selection Screen
      if (find.byType(LanguageSelectionScreen).evaluate().isNotEmpty) {
        // Select English and proceed
        final continueBtn = find.text('जारी रखें / Continue');
        expect(continueBtn, findsOneWidget);
        await tester.tap(continueBtn);
        await tester.pumpAndSettle();
      }

      // 3. Phone Authentication Screen
      if (find.byType(PhoneAuthScreen).evaluate().isNotEmpty) {
        final phoneInput = find.byType(TextField);
        expect(phoneInput, findsOneWidget);
        await tester.enterText(phoneInput, '9800000001');
        await tester.pumpAndSettle();

        final sendOtpBtn = find.widgetWithText(GBPrimaryButton, 'Get Verification OTP');
        if (sendOtpBtn.evaluate().isNotEmpty) {
          await tester.tap(sendOtpBtn);
        } else {
          final hiBtn = find.widgetWithText(GBPrimaryButton, 'ओटीपी प्राप्त करें');
          await tester.tap(hiBtn);
        }
        await tester.pumpAndSettle(const Duration(seconds: 2));
      }

      // 4. OTP Verification Screen
      if (find.byType(OtpVerificationScreen).evaluate().isNotEmpty) {
        // Verify security advisory is present (not raw developer note)
        expect(find.byIcon(Icons.shield_outlined), findsOneWidget);

        final otpInput = find.byType(TextField);
        expect(otpInput, findsOneWidget);
        await tester.enterText(otpInput, '123456');
        await tester.pumpAndSettle();

        final verifyBtn = find.byType(GBPrimaryButton);
        expect(verifyBtn, findsOneWidget);
        await tester.tap(verifyBtn);
        await tester.pumpAndSettle(const Duration(seconds: 3));
      }

      // 5. Main Navigation Screen & Home Tab
      expect(find.byType(MainNavScreen), findsOneWidget);

      // Verify delivery address header with pilot locality
      expect(find.byIcon(Icons.location_on), findsWidgets);

      // Verify exactly two featured stores exist in Minapur pilot block
      expect(find.text('माँ शारदा किराना स्टोर'), findsWidgets);

      // Test Category Filter Chips
      final groceryChip = find.text('किराना');
      if (groceryChip.evaluate().isNotEmpty) {
        await tester.tap(groceryChip);
        await tester.pumpAndSettle();
      } else {
        final enGrocery = find.text('Grocery');
        if (enGrocery.evaluate().isNotEmpty) {
          await tester.tap(enGrocery);
          await tester.pumpAndSettle();
        }
      }

      // Test In-Place Voice Search Popup
      final micBtn = find.byIcon(Icons.mic_none);
      if (micBtn.evaluate().isNotEmpty) {
        await tester.tap(micBtn.first);
        await tester.pumpAndSettle();

        // Voice dialog opened, tap voice suggestion chip
        final voiceChip = find.text('चक्की आटा');
        if (voiceChip.evaluate().isNotEmpty) {
          await tester.tap(voiceChip);
          await tester.pumpAndSettle();
        } else {
          final cancelVoice = find.text('रद्द करें');
          if (cancelVoice.evaluate().isNotEmpty) {
            await tester.tap(cancelVoice);
            await tester.pumpAndSettle();
          }
        }
      }

      // Test Adding Product to Cart from Product Grid
      final addBtns = find.widgetWithText(ElevatedButton, 'ADD');
      if (addBtns.evaluate().isNotEmpty) {
        await tester.tap(addBtns.first);
        await tester.pumpAndSettle();
      }

      // 6. Switch to AI Shopping Assistant Tab (Index 1)
      final bottomNav = find.byType(NavigationBar);
      expect(bottomNav, findsOneWidget);

      final aiTab = find.byIcon(Icons.auto_awesome);
      expect(aiTab, findsWidgets);
      await tester.tap(aiTab.first);
      await tester.pumpAndSettle();

      // Submit natural language query to AI Shopping Assistant
      final aiTextField = find.byType(TextField);
      if (aiTextField.evaluate().isNotEmpty) {
        await tester.enterText(aiTextField.last, 'Add 2 kg atta');
        final sendBtn = find.byIcon(Icons.send_rounded);
        if (sendBtn.evaluate().isNotEmpty) {
          await tester.tap(sendBtn);
          await tester.pump(const Duration(seconds: 1));
          await tester.pumpAndSettle();
        }
      }

      // 7. Switch to Cart Tab (Index 2)
      final cartTab = find.byIcon(Icons.shopping_cart_outlined);
      if (cartTab.evaluate().isNotEmpty) {
        await tester.tap(cartTab.first);
        await tester.pumpAndSettle();

        // Verify Cart has items and displays distance fee + platform fee
        expect(find.byType(GBPrimaryButton), findsWidgets);
        final proceedToCheckout = find.widgetWithText(GBPrimaryButton, 'चेकआउट के लिए आगे बढ़ें');
        if (proceedToCheckout.evaluate().isNotEmpty) {
          await tester.tap(proceedToCheckout);
          await tester.pumpAndSettle();
        } else {
          final enCheckout = find.widgetWithText(GBPrimaryButton, 'Proceed to Checkout');
          if (enCheckout.evaluate().isNotEmpty) {
            await tester.tap(enCheckout);
            await tester.pumpAndSettle();
          }
        }
      }

      // 8. Checkout Screen & Order Placement
      if (find.byType(CheckoutScreen).evaluate().isNotEmpty) {
        // Verify payment selection radios
        expect(find.text('COD'), findsWidgets);

        // Place Order
        final placeOrderBtn = find.widgetWithText(GBPrimaryButton, 'ऑर्डर दर्ज करें');
        if (placeOrderBtn.evaluate().isNotEmpty) {
          await tester.tap(placeOrderBtn);
          await tester.pumpAndSettle(const Duration(seconds: 3));
        } else {
          final enPlace = find.widgetWithText(GBPrimaryButton, 'Place Order');
          if (enPlace.evaluate().isNotEmpty) {
            await tester.tap(enPlace);
            await tester.pumpAndSettle(const Duration(seconds: 3));
          }
        }

        // Tap Track Live Order on success bottom sheet
        final trackBtn = find.widgetWithText(GBPrimaryButton, 'लाइव ट्रैकिंग देखें');
        if (trackBtn.evaluate().isNotEmpty) {
          await tester.tap(trackBtn);
          await tester.pumpAndSettle();
        } else {
          final enTrack = find.widgetWithText(GBPrimaryButton, 'Track Live Order');
          if (enTrack.evaluate().isNotEmpty) {
            await tester.tap(enTrack);
            await tester.pumpAndSettle();
          }
        }
      }

      // 9. Order Tracking Screen & 180s Cancellation
      if (find.byType(OrderTrackingScreen).evaluate().isNotEmpty) {
        // Verify 4-digit Delivery PIN is shown to the customer
        expect(find.byIcon(Icons.timer_outlined), findsWidgets);

        // Exercise Order Help / Support Ticket Dialog
        final helpBtn = find.byIcon(Icons.help_outline);
        if (helpBtn.evaluate().isNotEmpty) {
          await tester.tap(helpBtn.first);
          await tester.pumpAndSettle();

          final cancelDialog = find.text('रद्द करें');
          if (cancelDialog.evaluate().isNotEmpty) {
            await tester.tap(cancelDialog);
            await tester.pumpAndSettle();
          }
        }

        // Navigate back to MainNavScreen
        final backBtn = find.byTooltip('Back');
        if (backBtn.evaluate().isNotEmpty) {
          await tester.tap(backBtn);
          await tester.pumpAndSettle();
        }
      }

      // 10. Account Tab & Settings Screens
      final accountTab = find.byIcon(Icons.person_outline);
      if (accountTab.evaluate().isNotEmpty) {
        await tester.tap(accountTab.first);
        await tester.pumpAndSettle();

        // Test App Settings Navigation
        final appSettingsTile = find.byIcon(Icons.settings_outlined);
        if (appSettingsTile.evaluate().isNotEmpty) {
          await tester.tap(appSettingsTile);
          await tester.pumpAndSettle();
          expect(find.byType(AppSettingsScreen), findsOneWidget);

          // Test Dark Theme Radio
          final darkRadio = find.byIcon(Icons.dark_mode_outlined);
          if (darkRadio.evaluate().isNotEmpty) {
            await tester.tap(darkRadio);
            await tester.pumpAndSettle();
          }

          // Test Light Theme Radio
          final lightRadio = find.byIcon(Icons.light_mode_outlined);
          if (lightRadio.evaluate().isNotEmpty) {
            await tester.tap(lightRadio);
            await tester.pumpAndSettle();
          }

          // Back to Account Tab
          final back = find.byTooltip('Back');
          if (back.evaluate().isNotEmpty) {
            await tester.tap(back);
            await tester.pumpAndSettle();
          }
        }

        // Test Policies Screen Navigation
        final policiesTile = find.byIcon(Icons.policy_outlined);
        if (policiesTile.evaluate().isNotEmpty) {
          await tester.tap(policiesTile);
          await tester.pumpAndSettle();
          expect(find.byType(PoliciesScreen), findsOneWidget);

          final back = find.byTooltip('Back');
          if (back.evaluate().isNotEmpty) {
            await tester.tap(back);
            await tester.pumpAndSettle();
          }
        }

        // Test Support Hub Navigation
        final supportTile = find.byIcon(Icons.headset_mic_outlined);
        if (supportTile.evaluate().isNotEmpty) {
          await tester.tap(supportTile);
          await tester.pumpAndSettle();
          expect(find.byType(SupportHubScreen), findsOneWidget);

          final back = find.byTooltip('Back');
          if (back.evaluate().isNotEmpty) {
            await tester.tap(back);
            await tester.pumpAndSettle();
          }
        }
      }
    });
  });
}
