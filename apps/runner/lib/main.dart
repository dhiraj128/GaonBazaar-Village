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
            home: const RunnerSplashScreen(),
          );
        },
      ),
    );
  }
}
