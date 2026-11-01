import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
import 'state/vendor_state.dart';
import 'screens/splash_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const GaonBazaarVendorApp());
}

class GaonBazaarVendorApp extends StatefulWidget {
  const GaonBazaarVendorApp({super.key});

  @override
  State<GaonBazaarVendorApp> createState() => _GaonBazaarVendorAppState();
}

class _GaonBazaarVendorAppState extends State<GaonBazaarVendorApp> {
  final VendorAppState _vendorState = VendorAppState();

  @override
  void initState() {
    super.initState();
    _vendorState.init();
  }

  @override
  Widget build(BuildContext context) {
    return VendorStateProvider(
      notifier: _vendorState,
      child: AnimatedBuilder(
        animation: _vendorState,
        builder: (context, _) {
          return MaterialApp(
            title: 'GaonBazaar Vendor Partner',
            debugShowCheckedModeBanner: false,
            theme: GBTheme.lightTheme,
            darkTheme: GBTheme.darkTheme,
            themeMode: _vendorState.themeMode,
            locale: Locale(_vendorState.currentLocale),
            supportedLocales: const [
              Locale('hi'),
              Locale('en'),
            ],
            localizationsDelegates: const [
              GBLocalizations.delegate,
              GlobalMaterialLocalizations.delegate,
              GlobalWidgetsLocalizations.delegate,
              GlobalCupertinoLocalizations.delegate,
            ],
            home: const VendorSplashScreen(),
          );
        },
      ),
    );
  }
}
