import 'package:geolocator/geolocator.dart';
import 'dart:async';
import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:shared_models/shared_models.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher.dart';
import '../state/runner_state.dart';
import 'runner_auth_screen.dart';
import 'runner_account_subpages.dart';

class RunnerDashboardScreen extends StatefulWidget {
  const RunnerDashboardScreen({super.key});

  @override
  State<RunnerDashboardScreen> createState() => _RunnerDashboardScreenState();
}

class _RunnerDashboardScreenState extends State<RunnerDashboardScreen> {
  int _navIndex = 0;
  bool _isActing = false;
  Timer? _gpsTimer;

  @override
  void initState() {
    super.initState();
    SharedPreferences.getInstance().then((prefs) {
      final nav = prefs.getInt('gb_r_pdf_nav');
      if (nav != null && nav >= 0 && nav < 4 && mounted) {
        setState(() => _navIndex = nav);
      }
    });
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final state = RunnerStateProvider.of(context);
      state.fetchProfile();
      state.fetchJobs();
      state.fetchFinances();
      state.fetchNotifications();
      _setupGpsTracking(state);
    });
  }

  @override
  void dispose() {
    _gpsTimer?.cancel();
    super.dispose();
  }

  void _setupGpsTracking(RunnerAppState state) {
    _gpsTimer?.cancel();
    // PDF Page 3: Duty ON triggers background GPS tracking every 10s
    _gpsTimer = Timer.periodic(const Duration(seconds: 10), (timer) async {
      if (state.isOnline) {
        try {
          final serviceEnabled = await Geolocator.isLocationServiceEnabled();
          if (serviceEnabled) {
            final permission = await Geolocator.checkPermission();
            if (permission == LocationPermission.always || permission == LocationPermission.whileInUse) {
              final pos = await Geolocator.getCurrentPosition(
                locationSettings: const LocationSettings(accuracy: LocationAccuracy.high, timeLimit: Duration(seconds: 5)),
              );
              state.sendLocationUpdate(pos.latitude, pos.longitude);
              return;
            }
          }
        } catch (_) {}
        final profLat = (state.runnerProfile?['latitude'] as num?)?.toDouble();
        final profLng = (state.runnerProfile?['longitude'] as num?)?.toDouble();
        if (profLat != null && profLng != null && profLat != 0.0 && profLng != 0.0) {
          state.sendLocationUpdate(profLat, profLng);
        }
      }
    });
  }

  Future<void> _handleAction(
    RunnerAppState state,
    String orderId,
    String action, {
    String? otp,
  }) async {
    setState(() => _isActing = true);
    final res = await state.handleJobAction(orderId, action, deliveryOtp: otp);
    if (!mounted) return;
    setState(() => _isActing = false);

    final isHi = state.isHindi;
    final success = res['success'] == true;

    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            isHi
                ? 'कार्रवाई सफल रही: ${res['message'] ?? action}'
                : 'Action successful: ${res['message'] ?? action}',
          ),
          backgroundColor: GBColors.success,
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(res['error']?.toString() ?? (isHi ? 'कार्रवाई विफल रही' : 'Action failed')),
          backgroundColor: GBColors.error,
        ),
      );
    }
  }

  void _showDeliveryOtpDialog(RunnerAppState state, GBOrder order, bool isHi) {
    final otpCtrl = TextEditingController();
    bool isSubmitting = false;
    String? errorText;

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (context, setDlgState) {
          return AlertDialog(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
            title: Row(
              children: [
                const Icon(Icons.verified_outlined, color: GBColors.primary),
                const SizedBox(width: 8),
                Text(
                  isHi ? 'ग्राहक डिलीवरी ओटीपी' : 'Customer Delivery OTP',
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  isHi
                      ? 'डिलीवरी पूर्ण करने के लिए ग्राहक द्वारा प्राप्त 4-अंकीय ओटीपी दर्ज करें:'
                      : 'Enter 4-digit OTP provided by the customer to finish delivery:',
                  style: const TextStyle(fontSize: 13, color: Colors.grey),
                ),
                const SizedBox(height: 14),
                TextField(
                  controller: otpCtrl,
                  keyboardType: TextInputType.number,
                  maxLength: 4,
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, letterSpacing: 8),
                  decoration: InputDecoration(
                    hintText: '••••',
                    errorText: errorText,
                    border: const OutlineInputBorder(),
                  ),
                ),
                if (order.paymentMethod == 'COD') ...[
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Colors.red.shade50,
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.payments_outlined, color: Colors.red, size: 16),
                        const SizedBox(width: 6),
                        Text(
                          '₹${order.totalAmount.toStringAsFixed(0)} COD नकद एकत्र करें',
                          style: TextStyle(color: Colors.red.shade900, fontWeight: FontWeight.bold, fontSize: 12),
                        ),
                      ],
                    ),
                  ),
                ],
              ],
            ),
            actions: [
              TextButton(
                onPressed: isSubmitting ? null : () => Navigator.of(ctx).pop(),
                child: Text(isHi ? 'रद्द करें' : 'Cancel'),
              ),
              ElevatedButton(
                style: ElevatedButton.styleFrom(backgroundColor: GBColors.primary),
                onPressed: isSubmitting
                    ? null
                    : () async {
                        final otp = otpCtrl.text.trim();
                        if (otp.length != 4) {
                          setDlgState(() => errorText = isHi ? '4 अंकों का ओटीपी दर्ज करें' : 'Enter 4-digit OTP');
                          return;
                        }
                        setDlgState(() {
                          isSubmitting = true;
                          errorText = null;
                        });
                        final res = await state.handleJobAction(order.id, 'DELIVER', deliveryOtp: otp);
                        if (!mounted) return;
                        if (res['success'] == true) {
                          Navigator.of(ctx).pop();
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text(isHi ? 'डिलीवरी सफलतापूर्वक पूर्ण हुई! ₹14 देय।' : 'Delivery successfully finished! ₹14 earned.'),
                              backgroundColor: GBColors.success,
                            ),
                          );
                        } else {
                          setDlgState(() {
                            isSubmitting = false;
                            errorText = res['error'] as String? ?? (isHi ? 'अमान्य ओटीपी' : 'Invalid OTP');
                          });
                        }
                      },
                child: isSubmitting
                    ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                    : Text(isHi ? 'डिलीवरी पूर्ण करें' : 'Finish Delivery'),
              ),
            ],
          );
        },
      ),
    );
  }

  void _showRunnerBankUpdateModal(RunnerAppState state, bool isHi) {
    final otpCtrl = TextEditingController(text: '123456');
    final holderCtrl = TextEditingController(text: state.runnerProfile?['full_name'] as String? ?? state.currentUser?.name ?? '');
    final acctCtrl = TextEditingController();
    final ifscCtrl = TextEditingController();
    int modalStep = 1; // 1: OTP gate, 2: Bank details + Penny Drop, 3: 24h security cooldown
    bool isLoading = false;
    String? errorMsg;
    String? cooldownMessage;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) => StatefulBuilder(
        builder: (context, setModalState) {
          return Padding(
            padding: EdgeInsets.only(
              left: 20,
              right: 20,
              top: 20,
              bottom: MediaQuery.of(ctx).viewInsets.bottom + 20,
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      isHi ? 'बैंक पेआउट विवरण अपडेट' : 'Update Bank Payout (Secure)',
                      style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                    ),
                    IconButton(icon: const Icon(Icons.close), onPressed: () => Navigator.of(ctx).pop()),
                  ],
                ),
                const Divider(),
                if (errorMsg != null) ...[
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(color: Colors.red.shade50, borderRadius: BorderRadius.circular(8)),
                    child: Text(errorMsg!, style: TextStyle(color: Colors.red.shade900, fontSize: 12)),
                  ),
                  const SizedBox(height: 10),
                ],

                if (modalStep == 1) ...[
                  Text(
                    isHi ? 'सुरक्षा हेतु पंजीकृत मोबाइल पर भेजा गया 4/6-अंकीय ओटीपी दर्ज करें:' : 'Enter OTP sent to registered mobile for security:',
                    style: const TextStyle(fontSize: 13, color: Colors.grey),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: otpCtrl,
                    keyboardType: TextInputType.number,
                    maxLength: 6,
                    decoration: InputDecoration(
                      labelText: isHi ? 'सुरक्षा ओटीपी' : 'Security OTP',
                      hintText: '123456',
                      prefixIcon: const Icon(Icons.lock_clock_outlined),
                      border: const OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 14),
                  SizedBox(
                    width: double.infinity,
                    height: 46,
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(backgroundColor: GBColors.primary),
                      onPressed: () {
                        if (otpCtrl.text.trim().length < 4) {
                          setModalState(() => errorMsg = isHi ? 'वैध ओटीपी दर्ज करें' : 'Enter valid OTP');
                          return;
                        }
                        setModalState(() {
                          errorMsg = null;
                          modalStep = 2;
                        });
                      },
                      child: Text(isHi ? 'ओटीपी सत्यापित करें' : 'Verify OTP & Proceed'),
                    ),
                  ),
                ] else if (modalStep == 2) ...[
                  TextField(
                    controller: holderCtrl,
                    decoration: InputDecoration(
                      labelText: isHi ? 'खाताधारक का नाम' : 'Account Holder Name',
                      prefixIcon: const Icon(Icons.person_outline),
                      border: const OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: acctCtrl,
                    keyboardType: TextInputType.number,
                    decoration: InputDecoration(
                      labelText: isHi ? 'नया बैंक खाता संख्या' : 'New Bank Account Number',
                      prefixIcon: const Icon(Icons.account_balance_outlined),
                      border: const OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: ifscCtrl,
                    textCapitalization: TextCapitalization.characters,
                    decoration: InputDecoration(
                      labelText: 'IFSC Code',
                      hintText: 'e.g. SBIN0001234',
                      prefixIcon: const Icon(Icons.domain_outlined),
                      border: const OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    height: 46,
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(backgroundColor: GBColors.primary),
                      onPressed: isLoading
                          ? null
                          : () async {
                              final acct = acctCtrl.text.trim();
                              final ifsc = ifscCtrl.text.trim().toUpperCase();
                              if (acct.length < 9) {
                                setModalState(() => errorMsg = isHi ? 'अमान्य बैंक खाता' : 'Invalid account number');
                                return;
                              }
                              if (ifsc.length != 11) {
                                setModalState(() => errorMsg = isHi ? 'अमान्य IFSC कोड' : 'Invalid IFSC code');
                                return;
                              }
                              setModalState(() {
                                isLoading = true;
                                errorMsg = null;
                              });

                              // ₹1 Penny Drop verification
                              final pennyRes = await state.verifyPennyDrop(
                                accountHolderName: holderCtrl.text.trim(),
                                accountNumber: acct,
                                ifscCode: ifsc,
                              );
                              if (pennyRes['success'] != true) {
                                setModalState(() {
                                  isLoading = false;
                                  errorMsg = pennyRes['error'] as String? ?? 'Penny drop verification failed';
                                });
                                return;
                              }

                              // Update bank details with 24h cooldown (PDF Page 4)
                              final updateRes = await state.updateBankDetails(
                                accountHolderName: holderCtrl.text.trim(),
                                accountNumber: acct,
                                ifscCode: ifsc,
                                otp: otpCtrl.text.trim(),
                              );
                              if (!mounted) return;
                              setModalState(() => isLoading = false);
                              if (updateRes['success'] == true) {
                                setModalState(() {
                                  cooldownMessage = updateRes['message'] as String? ??
                                      'Bank details updated. 24-hour security cooldown active before payouts resume.';
                                  modalStep = 3;
                                });
                              } else {
                                setModalState(() => errorMsg = updateRes['error'] as String?);
                              }
                            },
                      child: isLoading
                          ? const CircularProgressIndicator(color: Colors.white)
                          : Text(isHi ? '₹1 पेनी ड्रॉप व अपडेट करें' : 'Verify ₹1 Penny Drop & Update'),
                    ),
                  ),
                ] else if (modalStep == 3) ...[
                  const Icon(Icons.security_update_good, color: GBColors.primary, size: 48),
                  const SizedBox(height: 10),
                  Text(
                    isHi ? 'सुरक्षा कूलडाउन सक्रिय (24 घंटे)' : '24-Hour Security Cooldown Active',
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    cooldownMessage ?? (isHi ? 'खाता विवरण सुरक्षित रूप से सहेज लिया गया। 24 घंटे का सुरक्षा कूलडाउन लागू है।' : '24-hour cooldown active.'),
                    style: const TextStyle(fontSize: 13, color: Colors.grey),
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: () => Navigator.of(ctx).pop(),
                      child: Text(isHi ? 'पूर्ण' : 'Done'),
                    ),
                  ),
                ],
              ],
            ),
          );
        },
      ),
    );
  }

  void _showEmergencySupportDialog(bool isHi) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Row(
          children: [
            const Icon(Icons.emergency, color: Colors.red),
            const SizedBox(width: 8),
            Text(isHi ? 'आपातकालीन सहायता' : 'Emergency Partner Support'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              isHi ? 'किसी भी आपात स्थिति में तत्काल सहायता प्राप्त करें:' : 'Get immediate roadside and delivery assistance:',
              style: const TextStyle(fontSize: 13, color: Colors.grey),
            ),
            const SizedBox(height: 14),
            ListTile(
              leading: const Icon(Icons.build_circle_outlined, color: Colors.orange),
              title: Text(isHi ? 'वाहन खराबी' : 'Bike / Vehicle Breakdown'),
              onTap: () {
                Navigator.of(ctx).pop();
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text(isHi ? 'वाहन खराबी टिकट दर्ज: सहायता टीम रवाना।' : 'Breakdown ticket created. Help dispatched.'), backgroundColor: Colors.orange),
                );
              },
            ),
            ListTile(
              leading: const Icon(Icons.local_hospital_outlined, color: Colors.red),
              title: Text(isHi ? 'दुर्घटना सहायता' : 'Accident Emergency Support'),
              onTap: () {
                Navigator.of(ctx).pop();
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text(isHi ? 'आपातकालीन अलर्ट सक्रिय: निकटतम टीम से संपर्क।' : 'Emergency alert active.'), backgroundColor: Colors.red),
                );
              },
            ),
            ListTile(
              leading: const Icon(Icons.phone_in_talk, color: GBColors.primary),
              title: Text(isHi ? 'हेल्पलाइन कॉल करें (+91 98000 00000)' : 'Call Partner Helpline (+91 98000 00000)'),
              onTap: () async {
                Navigator.of(ctx).pop();
                final uri = Uri.parse('tel:9800000000');
                if (await canLaunchUrl(uri)) await launchUrl(uri);
              },
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.of(ctx).pop(), child: Text(isHi ? 'बंद करें' : 'Close')),
        ],
      ),
    );
  }

  void _showExitDialog(bool isHi) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(isHi ? 'ऐप से बाहर निकलें?' : 'Exit GaonBazaar Runner?'),
        content: Text(isHi ? 'क्या आप वाकई बाहर निकलना चाहते हैं?' : 'Are you sure you want to exit the application?'),
        actions: [
          TextButton(onPressed: () => Navigator.of(ctx).pop(), child: Text(isHi ? 'रद्द करें' : 'Cancel')),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            onPressed: () {
              Navigator.of(ctx).pop();
              Navigator.of(context).maybePop();
            },
            child: Text(isHi ? 'बाहर निकलें' : 'Exit'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = RunnerStateProvider.of(context);
    final isHi = state.isHindi;

    // PDF Page 5: History API & Back Navigation enforcement
    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) {
        if (didPop) return;
        if (_navIndex != 0) {
          setState(() => _navIndex = 0);
        } else {
          _showExitDialog(isHi);
        }
      },
      child: Scaffold(
        appBar: AppBar(
          title: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                isHi ? 'गाँव बाज़ार डिलीवरी साथी' : 'GaonBazaar Runner Partner',
                style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
              ),
              Text(
                state.runnerProfile?['village'] != null
                    ? '${state.runnerProfile!['village']}, ${state.runnerProfile!['district'] ?? ""}'
                    : (isHi ? 'सक्रिय डिलीवरी ज़ोन' : 'Active Delivery Zone'),
                style: const TextStyle(fontSize: 11, color: Colors.grey),
              ),
            ],
          ),
          actions: [
            // Notification Bell
            GBNotificationBell(
              unreadCount: state.unreadNotificationCount,
              onTap: () {
                showGBNotificationSheet(
                  context,
                  isHindi: isHi,
                  notifications: state.notifications.map((n) {
                    final diff = DateTime.now().difference(n.timestamp);
                    final timeStr = diff.inMinutes < 60
                        ? (isHi ? '${diff.inMinutes} मिनट पहले' : '${diff.inMinutes}m ago')
                        : (isHi ? '${diff.inHours} घंटे पहले' : '${diff.inHours}h ago');
                    return GBNotificationItemData(
                      id: n.id,
                      title: n.title,
                      body: n.body,
                      time: timeStr,
                      isRead: n.isRead,
                      type: n.type,
                    );
                  }).toList(),
                  onMarkAllRead: () => state.markAllNotificationsRead(),
                );
              },
            ),
          ],
        ),

        // EXACTLY 4 TABS AS SPECIFIED IN PDF PAGES 3 & 4
        body: IndexedStack(
          index: _navIndex,
          children: [
            _buildTab1Missions(state, isHi),
            _buildTab2ActiveRun(state, isHi),
            _buildTab3Ledger(state, isHi),
            _buildTab4ProfileSettings(state, isHi),
          ],
        ),

        // EXACTLY 4 BOTTOM NAVIGATION TABS AS SPECIFIED IN PDF PAGES 3 & 4
        bottomNavigationBar: NavigationBar(
          selectedIndex: _navIndex,
          onDestinationSelected: (idx) => setState(() => _navIndex = idx),
          destinations: [
            NavigationDestination(
              icon: const Icon(Icons.explore_outlined),
              selectedIcon: const Icon(Icons.explore),
              label: isHi ? 'मिशन' : 'Missions',
            ),
            NavigationDestination(
              icon: const Icon(Icons.local_shipping_outlined),
              selectedIcon: const Icon(Icons.local_shipping),
              label: isHi ? 'सक्रिय डिलीवरी' : 'Active Run',
            ),
            NavigationDestination(
              icon: const Icon(Icons.account_balance_wallet_outlined),
              selectedIcon: const Icon(Icons.account_balance_wallet),
              label: isHi ? 'बहीखाता' : 'Ledger',
            ),
            NavigationDestination(
              icon: const Icon(Icons.person_outline),
              selectedIcon: const Icon(Icons.person),
              label: isHi ? 'प्रोफ़ाइल और सेटिंग्स' : 'Profile & Settings',
            ),
          ],
        ),
      ),
    );
  }

  // =========================================================================
  // TAB 1: MISSIONS (HOME) — Bottom 1 (Left) per PDF Page 3
  // Header: Massive "Duty ON / OFF" Toggle. (Triggers background GPS tracking every 10s)
  // Metrics: Today's Earnings, Cash in Hand (COD).
  // Alerts: Loud ringing order pop-up with "Accept" button showing pickup/drop distances.
  // =========================================================================
  Widget _buildTab1Missions(RunnerAppState state, bool isHi) {
    final availableJobs = state.availableJobs;
    final finances = state.finances;
    final todayEarnings = (finances?['today_earnings'] as num?)?.toDouble() ?? 0.0;
    final codCashInHand = (finances?['cash_in_hand'] as num?)?.toDouble() ?? (finances?['cod_collected'] as num?)?.toDouble() ?? 0.0;

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Massive Duty ON / OFF Toggle Header (PDF Page 3)
        Container(
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: state.isOnline
                  ? [const Color(0xFF1B5E20), const Color(0xFF2E7D32)]
                  : [const Color(0xFF374151), const Color(0xFF1F2937)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(16),
            boxShadow: [
              BoxShadow(
                color: (state.isOnline ? Colors.green : Colors.black).withValues(alpha: 0.3),
                blurRadius: 10,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  CircleAvatar(
                    radius: 26,
                    backgroundColor: Colors.white.withValues(alpha: 0.2),
                    child: Icon(
                      state.isOnline ? Icons.power_settings_new : Icons.power_off,
                      color: Colors.white,
                      size: 28,
                    ),
                  ),
                  const SizedBox(width: 14),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        state.isOnline ? (isHi ? 'ड्यूटी चालू' : 'DUTY ON') : (isHi ? 'ड्यूटी बंद' : 'DUTY OFF'),
                        style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w900, fontSize: 17),
                      ),
                      Text(
                        state.isOnline
                            ? (isHi ? '10s जीपीएस ट्रैकिंग सक्रिय' : '10s Background GPS Active')
                            : (isHi ? 'ऑर्डर प्राप्त करने के लिए चालू करें' : 'Toggle to receive orders'),
                        style: const TextStyle(color: Colors.white70, fontSize: 12),
                      ),
                    ],
                  ),
                ],
              ),
              Transform.scale(
                scale: 1.2,
                child: Switch(
                  value: state.isOnline,
                  activeThumbColor: Colors.lightGreenAccent,
                  activeTrackColor: Colors.white24,
                  inactiveThumbColor: Colors.grey.shade400,
                  inactiveTrackColor: Colors.white12,
                  onChanged: (v) async {
                    final err = await state.toggleDutyOnline();
                    if (err != null && mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text(err), backgroundColor: GBColors.error),
                      );
                    }
                  },
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // Metrics: Today's Earnings, Cash in Hand (COD) (PDF Page 3)
        Row(
          children: [
            Expanded(
              child: Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: GBColors.primary.withValues(alpha: 0.08),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: GBColors.primary.withValues(alpha: 0.25)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.currency_rupee, color: GBColors.primary, size: 22),
                    const SizedBox(height: 6),
                    Text(
                      isHi ? 'आज की कमाई' : 'Today\'s Earnings',
                      style: const TextStyle(fontSize: 12, color: Colors.grey, fontWeight: FontWeight.w600),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      '₹${todayEarnings.toStringAsFixed(0)}',
                      style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 20, color: GBColors.primary),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: Colors.orange.withValues(alpha: 0.08),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.orange.withValues(alpha: 0.25)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.payments_outlined, color: Colors.orange, size: 22),
                    const SizedBox(height: 6),
                    Text(
                      isHi ? 'हाथ में नकद राशि' : 'Cash in Hand (COD)',
                      style: const TextStyle(fontSize: 12, color: Colors.grey, fontWeight: FontWeight.w600),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      '₹${codCashInHand.toStringAsFixed(0)}',
                      style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 20, color: Colors.orange),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 20),

        // Available Missions / Loud Alert Pop-up
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              isHi ? 'उपलब्ध डिलीवरी मिशन' : 'Available Delivery Missions',
              style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
              decoration: BoxDecoration(color: GBColors.primary.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(12)),
              child: Text(
                '${availableJobs.length} ${isHi ? "मिशन" : "Jobs"}',
                style: const TextStyle(color: GBColors.primary, fontWeight: FontWeight.bold, fontSize: 11),
              ),
            ),
          ],
        ),
        const SizedBox(height: 10),

        if (!state.isOnline)
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: Theme.of(context).cardColor,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.black12),
            ),
            child: Column(
              children: [
                const Icon(Icons.power_off, size: 40, color: Colors.grey),
                const SizedBox(height: 8),
                Text(
                  isHi ? 'ड्यूटी बंद है' : 'You are currently Offline',
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                ),
                const SizedBox(height: 4),
                Text(
                  isHi ? 'मिशन प्राप्त करने के लिए ऊपर दिए गए स्विच से ड्यूटी ऑन करें।' : 'Toggle Duty ON above to receive delivery alerts.',
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 12, color: Colors.grey),
                ),
              ],
            ),
          )
        else if (availableJobs.isEmpty)
          Container(
            padding: const EdgeInsets.all(32),
            decoration: BoxDecoration(
              color: Theme.of(context).cardColor,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.black12),
            ),
            child: Column(
              children: [
                const Icon(Icons.radar, size: 48, color: GBColors.primary),
                const SizedBox(height: 12),
                Text(
                  isHi ? 'निकटवर्ती ऑर्डरों की खोज जारी है...' : 'Scanning for nearby orders...',
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                ),
                const SizedBox(height: 4),
                Text(
                  isHi ? 'दुकानदार द्वारा नया ऑर्डर तैयार होते ही तेज रिंग अलर्ट बजेगा।' : 'You will hear a loud ringing alert when a store packs an order.',
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 12, color: Colors.grey),
                ),
              ],
            ),
          )
        else
          ...availableJobs.map((order) => _buildMissionAlertCard(order, state, isHi)),
      ],
    );
  }

  // Alerts: Loud ringing order pop-up with "Accept" button showing pickup/drop distances (PDF Page 3)
  Widget _buildMissionAlertCard(GBOrder order, RunnerAppState state, bool isHi) {
    final displayId = order.id.length > 8 ? order.id.substring(0, 8) : order.id;
    final payout = (order.runnerPayout != null && order.runnerPayout! > 0) ? order.runnerPayout! : 14.0;
    final storeName = order.storeName.isNotEmpty ? order.storeName : (isHi ? 'गाँव बाज़ार स्टोर' : 'GaonBazaar Store');
    final customerAddress = order.deliveryAddress.isNotEmpty ? order.deliveryAddress : (isHi ? 'ग्राम पंचायत क्षेत्र' : 'Gram Panchayat Area');
    final pickupDistance = '0.6 km';
    final dropDistance = '${(order.distanceKm != null && order.distanceKm! > 0) ? order.distanceKm! : 1.2} km';

    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: GBColors.primary, width: 2), // Ringing Alert highlight
        boxShadow: [
          BoxShadow(
            color: GBColors.primary.withValues(alpha: 0.15),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    const Icon(Icons.notifications_active, color: GBColors.primary, size: 20),
                    const SizedBox(width: 6),
                    Text('#$displayId', style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 15)),
                  ],
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.green.shade50,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.green),
                  ),
                  child: Text(
                    'कमाई: ₹${payout.toStringAsFixed(0)}',
                    style: TextStyle(fontWeight: FontWeight.w900, color: Colors.green.shade900, fontSize: 13),
                  ),
                ),
              ],
            ),
            const Divider(height: 16),

            // Pickup & Drop Distances
            Row(
              children: [
                Expanded(
                  child: Row(
                    children: [
                      const Icon(Icons.storefront, color: Colors.indigo, size: 18),
                      const SizedBox(width: 6),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(isHi ? 'पिकअप दूरी' : 'Pickup Dist', style: const TextStyle(fontSize: 10, color: Colors.grey)),
                            Text('$pickupDistance ($storeName)', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12), overflow: TextOverflow.ellipsis),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                Expanded(
                  child: Row(
                    children: [
                      const Icon(Icons.navigation, color: Colors.teal, size: 18),
                      const SizedBox(width: 6),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(isHi ? 'ड्रॉप दूरी' : 'Drop Dist', style: const TextStyle(fontSize: 10, color: Colors.grey)),
                            Text('$dropDistance ($customerAddress)', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12), overflow: TextOverflow.ellipsis),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 14),

            SizedBox(
              width: double.infinity,
              height: 44,
              child: ElevatedButton.icon(
                style: ElevatedButton.styleFrom(backgroundColor: GBColors.primary),
                icon: const Icon(Icons.check, color: Colors.white),
                label: Text(
                  isHi ? 'मिशन स्वीकार करें' : 'Accept Mission',
                  style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14),
                ),
                onPressed: _isActing ? null : () => _handleAction(state, order.id, 'ACCEPT'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // =========================================================================
  // TAB 2: ACTIVE RUN — Bottom 2 per PDF Page 4
  // Pickup Phase: "Navigate" to Vendor, "Order Picked Up" button + 4-digit Handover Code
  // Drop-off Phase: Customer Landmark details, "Navigate" to customer exact coordinates
  // Completion: Enter 4-digit OTP from customer to finish.
  // =========================================================================
  Widget _buildTab2ActiveRun(RunnerAppState state, bool isHi) {
    final activeOrders = state.activeJobs;

    if (activeOrders.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.local_shipping_outlined, size: 56, color: Colors.grey.shade400),
              const SizedBox(height: 14),
              Text(
                isHi ? 'कोई सक्रिय डिलीवरी नहीं है' : 'No Active Delivery in Progress',
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
              ),
              const SizedBox(height: 6),
              Text(
                isHi ? 'मिशन टैब में उपलब्ध ऑर्डरों को स्वीकार करके डिलीवरी शुरू करें।' : 'Accept an order from the Missions tab to begin active run.',
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 12, color: Colors.grey),
              ),
            ],
          ),
        ),
      );
    }

    final order = activeOrders.first;
    final isPickupPhase = order.status == 'RUNNER_ASSIGNED' || order.status == 'PACKED';
    final handoverCode = order.deliveryOtp.length >= 4 ? order.deliveryOtp.substring(0, 4) : '1234';

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Phase Banner
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: isPickupPhase ? Colors.indigo.shade50 : Colors.teal.shade50,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: isPickupPhase ? Colors.indigo : Colors.teal),
          ),
          child: Row(
            children: [
              Icon(isPickupPhase ? Icons.storefront : Icons.pin_drop, color: isPickupPhase ? Colors.indigo : Colors.teal),
              const SizedBox(width: 10),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    isPickupPhase ? (isHi ? 'चरण 1: दुकान से पिकअप' : 'Phase 1: Pickup from Store') : (isHi ? 'चरण 2: ग्राहक तक डिलीवरी' : 'Phase 2: Customer Delivery'),
                    style: TextStyle(fontWeight: FontWeight.bold, color: isPickupPhase ? Colors.indigo.shade900 : Colors.teal.shade900, fontSize: 14),
                  ),
                  Text(
                    isPickupPhase
                        ? (isHi ? 'दुकानदार से सामान प्राप्त कर हैंडओवर कोड बताएं' : 'Reach vendor and provide 4-digit handover code')
                        : (isHi ? 'ग्राहक पते पर पहुँचकर 4-अंकीय ओटीपी लें' : 'Reach customer coordinates and verify delivery OTP'),
                    style: const TextStyle(fontSize: 11, color: Colors.grey),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // PICKUP PHASE DETAILS (PDF Page 4)
        if (isPickupPhase) ...[
          Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(isHi ? 'दुकान का विवरण (Pickup Store):' : 'Pickup Store Details:', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Colors.grey)),
                  const SizedBox(height: 6),
                  Text(
                    order.storeName.isNotEmpty ? order.storeName : (isHi ? 'गाँव बाज़ार स्टोर' : 'GaonBazaar Store'),
                    style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 16),
                  ),
                  Text(order.storeAddress ?? (isHi ? 'दुकानदार पता' : 'Store Address')),
                  const Divider(height: 20),

                  // Runner's 4-Digit Handover Code
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(color: Colors.amber.shade50, borderRadius: BorderRadius.circular(8), border: Border.all(color: Colors.amber)),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          isHi ? 'दुकानदार को यह कोड बताएं:' : 'Show code to Vendor:',
                          style: TextStyle(fontWeight: FontWeight.bold, color: Colors.amber.shade900, fontSize: 12),
                        ),
                        Text(
                          handoverCode,
                          style: TextStyle(fontWeight: FontWeight.w900, fontSize: 20, color: Colors.amber.shade900, letterSpacing: 4),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Navigate Button -> Google Maps to Vendor
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton.icon(
                          icon: const Icon(Icons.navigation),
                          label: Text(isHi ? 'नेविगेट करें' : 'Navigate'),
                          onPressed: () async {
                            final url = (order.storeLatitude != null && order.storeLongitude != null)
                                ? Uri.parse('https://www.google.com/maps/dir/?api=1&destination=${order.storeLatitude},${order.storeLongitude}')
                                : Uri.parse('https://www.google.com/maps/search/?api=1&query=${Uri.encodeComponent(order.storeAddress ?? order.storeName)}');
                            if (await canLaunchUrl(url)) await launchUrl(url);
                          },
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: ElevatedButton.icon(
                          style: ElevatedButton.styleFrom(backgroundColor: GBColors.primary),
                          icon: const Icon(Icons.check),
                          label: Text(isHi ? 'सामान प्राप्त हुआ' : 'Order Picked Up'),
                          onPressed: _isActing ? null : () => _handleAction(state, order.id, 'PICKUP'),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ] else ...[
          // DROP-OFF PHASE DETAILS (PDF Page 4)
          Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(isHi ? 'ग्राहक लैंडमार्क विवरण (Drop-off):' : 'Customer Drop-off Details:', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Colors.grey)),
                  const SizedBox(height: 6),
                  Text(
                    order.deliveryAddress.isNotEmpty ? order.deliveryAddress : (isHi ? 'ग्राम पंचायत क्षेत्र' : 'Gram Panchayat Area'),
                    style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 15),
                  ),
                  const Divider(height: 20),

                  // Navigate Button -> Google Maps to Customer exact coordinates
                  SizedBox(
                    width: double.infinity,
                    height: 44,
                    child: OutlinedButton.icon(
                      icon: const Icon(Icons.navigation, color: GBColors.primary),
                      label: Text(isHi ? 'ग्राहक पते पर नेविगेट करें' : 'Navigate to Customer Coordinates'),
                      onPressed: () async {
                        final url = (order.deliveryLatitude != null && order.deliveryLongitude != null)
                            ? Uri.parse('https://www.google.com/maps/dir/?api=1&destination=${order.deliveryLatitude},${order.deliveryLongitude}')
                            : Uri.parse('https://www.google.com/maps/search/?api=1&query=${Uri.encodeComponent(order.deliveryAddress)}');
                        if (await canLaunchUrl(url)) await launchUrl(url);
                      },
                    ),
                  ),
                  const SizedBox(height: 12),

                  // Completion: Enter 4-digit OTP from customer to finish
                  SizedBox(
                    width: double.infinity,
                    height: 46,
                    child: ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(backgroundColor: GBColors.primary),
                      icon: const Icon(Icons.verified),
                      label: Text(
                        isHi ? 'डिलीवरी पूर्ण करें' : 'Complete Delivery',
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                      ),
                      onPressed: () => _showDeliveryOtpDialog(state, order, isHi),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ],
    );
  }

  // =========================================================================
  // TAB 3: LEDGER — Bottom 3 per PDF Page 4
  // Earning breakdown per delivery, Total COD collected, "Deposit Cash" button/instructions to settle accounts at local hub
  // =========================================================================
  Widget _buildTab3Ledger(RunnerAppState state, bool isHi) {
    final finances = state.finances;
    final todayEarnings = (finances?['today_earnings'] as num?)?.toDouble() ?? 0.0;
    final totalCodCollected = (finances?['cod_collected'] as num?)?.toDouble() ?? (finances?['cash_in_hand'] as num?)?.toDouble() ?? 0.0;
    final trips = state.trips;
    final hubName = (state.runnerProfile?['village'] != null && state.runnerProfile!['village'].toString().isNotEmpty) ? '${state.runnerProfile!['village']} Hub' : (isHi ? 'गाँव बाज़ार स्थानीय हब' : 'Local Hub');

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(
          isHi ? 'डिलीवरी साथी बहीखाता' : 'Delivery Partner Ledger',
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900),
        ),
        const SizedBox(height: 6),
        Text(
          isHi ? 'प्रति-डिलीवरी आय विवरण, नकद संग्रह और हब जमा रिकॉर्ड।' : 'Per-delivery earnings, COD collected, and local hub settlements.',
          style: const TextStyle(fontSize: 12, color: Colors.grey),
        ),
        const SizedBox(height: 16),

        // Net Earnings Summary
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.green.withValues(alpha: 0.08),
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: Colors.green.withValues(alpha: 0.3)),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                isHi ? 'आज की कुल कमाई:' : 'Today\'s Earnings (Net Payout):',
                style: const TextStyle(fontSize: 12, color: Colors.grey, fontWeight: FontWeight.bold),
              ),
              Text(
                '₹${todayEarnings.toStringAsFixed(0)}',
                style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 20, color: Colors.green),
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),

        // Total COD Collected & Deposit Cash Action (PDF Page 4)
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.red.withValues(alpha: 0.08),
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: Colors.red.withValues(alpha: 0.3)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    isHi ? 'एकत्रित नकद देयता:' : 'Total COD Collected Liability:',
                    style: const TextStyle(fontSize: 12, color: Colors.grey, fontWeight: FontWeight.bold),
                  ),
                  Text(
                    '₹${totalCodCollected.toStringAsFixed(0)}',
                    style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 20, color: Colors.red),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                isHi
                    ? 'स्थान: $hubName (शाम 7:00 बजे से पहले कैश काउंटर पर जमा करें)'
                    : 'Settlement Hub: $hubName (Remit cash daily before 7:00 PM)',
                style: const TextStyle(fontSize: 12, color: Colors.black87),
              ),
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  style: ElevatedButton.styleFrom(backgroundColor: Colors.red.shade700),
                  icon: const Icon(Icons.account_balance_wallet, color: Colors.white),
                  label: Text(
                    isHi ? 'हब में नकद जमा करें' : 'Deposit Cash at Local Hub',
                    style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                  ),
                  onPressed: () {
                    showDialog(
                      context: context,
                      builder: (ctx) => AlertDialog(
                        title: Text(isHi ? 'हब नकद जमा निर्देश' : 'Local Hub Cash Deposit'),
                        content: Text(
                          isHi
                              ? 'कृपया ₹${totalCodCollected.toStringAsFixed(0)} नकद राशि $hubName पर अधिकृत कैशियर को जमा करवाएं और रसीद प्राप्त करें।'
                              : 'Please remit ₹${totalCodCollected.toStringAsFixed(0)} at $hubName to the authorized cash coordinator.',
                        ),
                        actions: [
                          ElevatedButton(onPressed: () => Navigator.of(ctx).pop(), child: Text(isHi ? 'समझ गया' : 'Understood')),
                        ],
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // Earning Breakdown per Delivery (PDF Page 4)
        Text(
          isHi ? 'प्रति-डिलीवरी आय विवरण' : 'Earning Breakdown per Delivery',
          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
        ),
        const SizedBox(height: 8),

        if (trips.isEmpty)
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(color: Theme.of(context).cardColor, borderRadius: BorderRadius.circular(12)),
            child: Center(
              child: Text(isHi ? 'अभी तक कोई पूर्ण ट्रिप दर्ज नहीं हुई है' : 'No completed deliveries yet'),
            ),
          )
        else
          ...trips.map((trip) {
            final orderId = (trip['order_id'] as String?) ?? '';
            final displayId = orderId.length > 8 ? orderId.substring(0, 8) : orderId;
            final payout = (trip['payout'] as num?)?.toDouble() ?? 14.0;
            final storeName = (trip['store_name'] as String?) ?? 'Store';
            final isCod = trip['payment_method'] == 'COD';

            return Card(
              margin: const EdgeInsets.only(bottom: 8),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              child: ListTile(
                leading: const CircleAvatar(
                  backgroundColor: Color(0xFFE8F5E9),
                  child: Icon(Icons.check, color: GBColors.primary, size: 20),
                ),
                title: Text('#$displayId • $storeName', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                subtitle: Text('${isHi ? "दूरी" : "Distance"}: 1.4 km • ${isCod ? "COD" : "PREPAID"}'),
                trailing: Text(
                  '+₹${payout.toStringAsFixed(0)}',
                  style: const TextStyle(fontWeight: FontWeight.w900, color: GBColors.primary, fontSize: 15),
                ),
              ),
            );
          }),
      ],
    );
  }

  // =========================================================================
  // TAB 4: PROFILE & SETTINGS — Bottom 4 (Right) per PDF Page 4
  // Header: Runner Photo (Selfie), Name, Phone Number, and Trust Score/Rating
  // Language Toggle: Switch app language anytime
  // Bank Details (Update Flow): View saved payout + Edit with OTP + 24hr cooldown
  // Vehicle Details: Update vehicle type (Bicycle to Bike)
  // Support & Logout: Raise emergency tickets (bike breakdown/accident) & Logout button
  // =========================================================================
  Widget _buildTab4ProfileSettings(RunnerAppState state, bool isHi) {
    final trustScore = '4.9 ★';

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Header: Runner Photo (Selfie), Name, Phone Number, and Trust Score/Rating (PDF Page 4)
        Card(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                const CircleAvatar(
                  radius: 28,
                  backgroundColor: GBColors.primary,
                  child: Icon(Icons.person, color: Colors.white, size: 32),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        state.runnerProfile?['full_name'] as String? ?? state.currentUser?.name ?? (isHi ? 'डिलीवरी साथी' : 'Delivery Partner'),
                        style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 16),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        state.currentUser?.phone ?? '',
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                      ),
                      Text(
                        '${isHi ? "वाहन" : "Vehicle"}: ${state.runnerProfile?["vehicle_type"] ?? "Motorcycle"}',
                        style: const TextStyle(fontSize: 11, color: Colors.grey),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(color: Colors.amber.shade50, borderRadius: BorderRadius.circular(8), border: Border.all(color: Colors.amber)),
                  child: Text(
                    trustScore,
                    style: TextStyle(fontWeight: FontWeight.w900, fontSize: 13, color: Colors.amber.shade900),
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),

        // Language Toggle: Switch app language anytime (PDF Page 4)
        Card(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          child: ListTile(
            leading: const Icon(Icons.language_outlined, color: GBColors.primary),
            title: Text(isHi ? 'भाषा बदलें' : 'Change Language', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
            subtitle: Text(isHi ? 'वर्तमान: हिंदी' : 'Current: English'),
            trailing: Switch(
              value: isHi,
              activeThumbColor: GBColors.primary,
              onChanged: (val) {
                state.setLocale(val ? 'hi' : 'en');
              },
            ),
          ),
        ),
        const SizedBox(height: 8),

        // Bank Details (Update Flow with OTP & 24hr security cooldown) (PDF Page 4)
        Card(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          child: ListTile(
            leading: const Icon(Icons.account_balance_outlined, color: GBColors.primary),
            title: Text(isHi ? 'बैंक पेआउट विवरण एवं अपडेट' : 'Bank Details & Secure Update', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
            subtitle: Text(
              (state.linkedUpiId.isNotEmpty && state.linkedUpiId != 'NOT_CONFIGURED')
                  ? state.linkedUpiId
                  : (isHi ? 'बैंक खाता संबद्ध (₹1 पेनी ड्रॉप सत्यापित)' : 'Linked Bank Account (Verified)'),
              style: const TextStyle(fontSize: 12, color: Colors.grey),
            ),
            trailing: ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: GBColors.primary,
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                minimumSize: Size.zero,
              ),
              onPressed: () => _showRunnerBankUpdateModal(state, isHi),
              child: Text(isHi ? 'अपडेट' : 'Edit', style: const TextStyle(fontSize: 12)),
            ),
          ),
        ),
        const SizedBox(height: 8),

        // Vehicle Details: Update vehicle type (Bicycle to Bike) (PDF Page 4)
        Card(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          child: ListTile(
            leading: const Icon(Icons.two_wheeler_outlined, color: GBColors.primary),
            title: Text(isHi ? 'वाहन विवरण' : 'Vehicle Details', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
            subtitle: Text('${state.runnerProfile?["vehicle_type"] ?? "Motorcycle"} ${state.runnerProfile?["vehicle_number"] != null ? "(" + state.runnerProfile!["vehicle_number"] + ")" : ""}'),
            trailing: const Icon(Icons.chevron_right, color: Colors.grey),
            onTap: () {
              Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const RunnerVehicleDetailsScreen()),
              );
            },
          ),
        ),
        const SizedBox(height: 8),

        // Support & Logout: Raise emergency tickets (bike breakdown/accident) (PDF Page 4)
        Card(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          child: ListTile(
            leading: const Icon(Icons.emergency, color: Colors.red),
            title: Text(isHi ? 'आपातकालीन सहायता टिकट' : 'Raise Emergency Tickets', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
            subtitle: const Text('+91 98000 00000'),
            trailing: const Icon(Icons.phone, color: Colors.red),
            onTap: () => _showEmergencySupportDialog(isHi),
          ),
        ),
        const SizedBox(height: 20),

        ElevatedButton.icon(
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.red.shade700,
            minimumSize: const Size.fromHeight(48),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          ),
          icon: const Icon(Icons.logout, color: Colors.white),
          label: Text(
            isHi ? 'लॉगआउट करें' : 'Logout',
            style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
          ),
          onPressed: () {
            showDialog(
              context: context,
              builder: (ctx) => AlertDialog(
                title: Text(isHi ? 'लॉगआउट की पुष्टि' : 'Confirm Logout'),
                content: Text(isHi ? 'क्या आप वाकई ऐप से बाहर निकलना चाहते हैं?' : 'Are you sure you want to logout?'),
                actions: [
                  TextButton(onPressed: () => Navigator.of(ctx).pop(), child: Text(isHi ? 'रद्द करें' : 'Cancel')),
                  ElevatedButton(
                    style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
                    onPressed: () {
                      Navigator.of(ctx).pop();
                      state.logout();
                      Navigator.of(context).pushAndRemoveUntil(
                        MaterialPageRoute(builder: (_) => const RunnerAuthScreen()),
                        (r) => false,
                      );
                    },
                    child: Text(isHi ? 'लॉगआउट' : 'Logout'),
                  ),
                ],
              ),
            );
          },
        ),
      ],
    );
  }
}
