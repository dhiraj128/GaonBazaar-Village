import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
import '../state/app_state.dart';
import 'home_tab.dart';
import 'ai_assistant_tab.dart';
import 'cart_tab.dart';
import 'orders_tab.dart';
import 'account_tab.dart';

class MainNavScreen extends StatefulWidget {
  const MainNavScreen({super.key});

  @override
  State<MainNavScreen> createState() => _MainNavScreenState();
}

class _MainNavScreenState extends State<MainNavScreen> {
  int _currentIndex = 0;

  void _onTabChange(int index) {
    setState(() {
      _currentIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = AppStateProvider.of(context);
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    final tabs = [
      HomeTab(onTabChange: _onTabChange),
      AiAssistantTab(onTabChange: _onTabChange),
      CartTab(onTabChange: _onTabChange),
      OrdersTab(onTabChange: _onTabChange),
      AccountTab(onTabChange: _onTabChange),
    ];

    return WillPopScope(
      onWillPop: () async {
        if (_currentIndex != 0) {
          setState(() => _currentIndex = 0);
          return false;
        }
        return true;
      },
      child: Scaffold(
        body: IndexedStack(
          index: _currentIndex,
          children: tabs,
        ),
        bottomNavigationBar: BottomNavigationBar(
          currentIndex: _currentIndex,
          onTap: _onTabChange,
          type: BottomNavigationBarType.fixed,
          selectedItemColor: GBColors.primary,
          unselectedItemColor: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
          selectedFontSize: 12,
          unselectedFontSize: 11,
          items: [
            BottomNavigationBarItem(
              icon: const Icon(Icons.home_outlined),
              activeIcon: const Icon(Icons.home_filled),
              label: loc.tr('tab_home'),
            ),
            BottomNavigationBarItem(
              icon: const Icon(Icons.auto_awesome_outlined),
              activeIcon: const Icon(Icons.auto_awesome),
              label: loc.tr('tab_ai'),
            ),
            BottomNavigationBarItem(
              icon: Stack(
                clipBehavior: Clip.none,
                children: [
                  const Icon(Icons.shopping_cart_outlined),
                  if (state.cartCount > 0)
                    Positioned(
                      top: -4,
                      right: -8,
                      child: Container(
                        padding: const EdgeInsets.all(4),
                        decoration: const BoxDecoration(
                          color: GBColors.error,
                          shape: BoxShape.circle,
                        ),
                        child: Text(
                          '${state.cartCount}',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 10,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                      ),
                    ),
                ],
              ),
              activeIcon: Stack(
                clipBehavior: Clip.none,
                children: [
                  const Icon(Icons.shopping_cart),
                  if (state.cartCount > 0)
                    Positioned(
                      top: -4,
                      right: -8,
                      child: Container(
                        padding: const EdgeInsets.all(4),
                        decoration: const BoxDecoration(
                          color: GBColors.error,
                          shape: BoxShape.circle,
                        ),
                        child: Text(
                          '${state.cartCount}',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 10,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                      ),
                    ),
                ],
              ),
              label: loc.tr('tab_cart'),
            ),
            BottomNavigationBarItem(
              icon: const Icon(Icons.receipt_long_outlined),
              activeIcon: const Icon(Icons.receipt_long),
              label: loc.tr('tab_orders'),
            ),
            BottomNavigationBarItem(
              icon: const Icon(Icons.person_outline),
              activeIcon: const Icon(Icons.person),
              label: loc.tr('tab_account'),
            ),
          ],
        ),
      ),
    );
  }
}
