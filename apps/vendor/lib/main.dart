import 'package:flutter/foundation.dart';
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
            builder: (context, child) {
              if (kIsWeb) {
                return Container(
                  color: const Color(0xFF0F172A),
                  alignment: Alignment.center,
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(28),
                    child: Container(
                      constraints: const BoxConstraints(maxWidth: 430, maxHeight: 900),
                      decoration: BoxDecoration(
                        color: Theme.of(context).scaffoldBackgroundColor,
                        border: Border.all(color: Colors.white24, width: 2),
                        boxShadow: const [
                          BoxShadow(
                            color: Colors.black54,
                            blurRadius: 30,
                            spreadRadius: 8,
                          ),
                        ],
                      ),
                      child: child,
                    ),
                  ),
                );
              }
              return child ?? const SizedBox();
            },
            home: const VendorSplashScreen(),
          );
        },
      ),
    );
  }
}
