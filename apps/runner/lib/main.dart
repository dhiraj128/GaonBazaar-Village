import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
import 'state/runner_state.dart';
import 'screens/splash_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const GaonBazaarRunnerApp());
}

class GaonBazaarRunnerApp extends StatefulWidget {
  const GaonBazaarRunnerApp({super.key});

  @override
  State<GaonBazaarRunnerApp> createState() => _GaonBazaarRunnerAppState();
}

class _GaonBazaarRunnerAppState extends State<GaonBazaarRunnerApp> {
  final RunnerAppState _runnerState = RunnerAppState();

  @override
  void initState() {
    super.initState();
    _runnerState.init();
  }

  @override
  Widget build(BuildContext context) {
    return RunnerStateProvider(
      notifier: _runnerState,
      child: AnimatedBuilder(
        animation: _runnerState,
        builder: (context, _) {
          return MaterialApp(
            title: 'GaonBazaar Delivery Partner',
            debugShowCheckedModeBanner: false,
            theme: GBTheme.lightTheme,
            darkTheme: GBTheme.darkTheme,
            themeMode: _runnerState.themeMode,
            locale: Locale(_runnerState.currentLocale),
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
            home: const RunnerSplashScreen(),
          );
        },
      ),
    );
  }
}
