import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:vendor/main.dart';
import 'package:vendor/screens/splash_screen.dart';
import 'package:vendor/screens/vendor_auth_screen.dart';
import 'package:vendor/screens/vendor_dashboard_screen.dart';
import 'package:vendor/screens/product_library_screen.dart';
import 'package:vendor/screens/vendor_inventory_screen.dart';
import 'package:vendor/screens/vendor_settlements_screen.dart';
import 'package:design_system/design_system.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('Vendor Android Application Full Lifecycle Test', () {
    testWidgets('Complete Vendor Workflow: Splash -> Auth -> Dashboard -> Catalog -> Inventory -> Settlements',
        (WidgetTester tester) async {
      // 1. Boot Application & Splash Screen
      await tester.pumpWidget(const GaonBazaarVendorApp());
      expect(find.byType(VendorSplashScreen), findsOneWidget);

      await tester.pump(const Duration(milliseconds: 2000));
      await tester.pumpAndSettle();

      // 2. Vendor Authentication Screen
      if (find.byType(VendorAuthScreen).evaluate().isNotEmpty) {
        final phoneField = find.byType(TextField);
        expect(phoneField, findsOneWidget);
        await tester.enterText(phoneField, '9800000002');
        await tester.pumpAndSettle();

        final sendOtpBtn = find.widgetWithText(GBPrimaryButton, 'ओटीपी प्राप्त करें');
        if (sendOtpBtn.evaluate().isNotEmpty) {
          await tester.tap(sendOtpBtn);
        } else {
          final enBtn = find.widgetWithText(GBPrimaryButton, 'Send OTP');
          if (enBtn.evaluate().isNotEmpty) {
            await tester.tap(enBtn);
          }
        }
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

      // 3. Vendor Dashboard Screen
      expect(find.byType(VendorDashboardScreen), findsOneWidget);

      // Verify Store Online Switch
      final onlineSwitch = find.byType(Switch);
      expect(onlineSwitch, findsWidgets);
      await tester.tap(onlineSwitch.first);
      await tester.pumpAndSettle();
      await tester.tap(onlineSwitch.first);
      await tester.pumpAndSettle();

      // Test Order Status Tabs (New, Packing, Ready, Delivered)
      final tabs = find.byType(Tab);
      expect(tabs, findsNWidgets(4));

      // Tap Packing tab
      await tester.tap(tabs.at(1));
      await tester.pumpAndSettle();

      // Tap Ready tab
      await tester.tap(tabs.at(2));
      await tester.pumpAndSettle();

      // Tap Delivered tab
      await tester.tap(tabs.at(3));
      await tester.pumpAndSettle();

      // Return to New tab
      await tester.tap(tabs.at(0));
      await tester.pumpAndSettle();

      // 4. Open Navigation Drawer
      final scaffold = find.byType(Scaffold);
      expect(scaffold, findsWidgets);
      final menuBtn = find.byIcon(Icons.menu);
      if (menuBtn.evaluate().isNotEmpty) {
        await tester.tap(menuBtn.first);
        await tester.pumpAndSettle();
      } else {
        // Open drawer via drag
        await tester.dragFrom(const Offset(10, 300), const Offset(300, 0));
        await tester.pumpAndSettle();
      }

      // 5. Navigate to Central Product Library
      final catalogTile = find.byIcon(Icons.library_add_outlined);
      if (catalogTile.evaluate().isNotEmpty) {
        await tester.tap(catalogTile);
        await tester.pumpAndSettle();
        expect(find.byType(ProductLibraryScreen), findsOneWidget);

        // Search in catalog
        final searchField = find.byType(TextField);
        if (searchField.evaluate().isNotEmpty) {
          await tester.enterText(searchField.first, 'आटा');
          await tester.pumpAndSettle();
        }

        // Tap Add to My Store button on an item
        final addStoreBtns = find.byType(ElevatedButton);
        if (addStoreBtns.evaluate().isNotEmpty) {
          await tester.tap(addStoreBtns.first);
          await tester.pumpAndSettle();

          // Cancel or Submit price dialog
          final cancelBtn = find.text('रद्द करें');
          if (cancelBtn.evaluate().isNotEmpty) {
            await tester.tap(cancelBtn);
            await tester.pumpAndSettle();
          }
        }

        // Navigate back to Dashboard
        final back = find.byTooltip('Back');
        if (back.evaluate().isNotEmpty) {
          await tester.tap(back);
          await tester.pumpAndSettle();
        }
      }

      // 6. Navigate to Inventory Management
      await tester.dragFrom(const Offset(10, 300), const Offset(300, 0));
      await tester.pumpAndSettle();

      final inventoryTile = find.byIcon(Icons.inventory_2_outlined);
      if (inventoryTile.evaluate().isNotEmpty) {
        await tester.tap(inventoryTile);
        await tester.pumpAndSettle();
        expect(find.byType(VendorInventoryScreen), findsOneWidget);

        // Navigate back
        final back = find.byTooltip('Back');
        if (back.evaluate().isNotEmpty) {
          await tester.tap(back);
          await tester.pumpAndSettle();
        }
      }

      // 7. Navigate to Settlements Screen
      await tester.dragFrom(const Offset(10, 300), const Offset(300, 0));
      await tester.pumpAndSettle();

      final settlementsTile = find.byIcon(Icons.account_balance_wallet_outlined);
      if (settlementsTile.evaluate().isNotEmpty) {
        await tester.tap(settlementsTile);
        await tester.pumpAndSettle();
        expect(find.byType(VendorSettlementsScreen), findsOneWidget);

        final back = find.byTooltip('Back');
        if (back.evaluate().isNotEmpty) {
          await tester.tap(back);
          await tester.pumpAndSettle();
        }
      }
    });
  });
}
