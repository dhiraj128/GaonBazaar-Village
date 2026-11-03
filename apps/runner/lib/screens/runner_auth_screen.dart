import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:shared_models/shared_models.dart';
import '../state/runner_state.dart';
import 'runner_dashboard_screen.dart';
import 'runner_pending_approval_screen.dart';
import 'runner_onboarding_wizard.dart';

class RunnerAuthScreen extends StatefulWidget {
  const RunnerAuthScreen({super.key});

  @override
  State<RunnerAuthScreen> createState() => _RunnerAuthScreenState();
}

class _RunnerAuthScreenState extends State<RunnerAuthScreen> {
  final TextEditingController _phoneController = TextEditingController();
  final TextEditingController _otpController = TextEditingController();
  String? _sessionId;
  bool _otpSent = false;
  bool _isLoading = false;
  String? _errorMessage;

  final RegExp _phoneRegex = RegExp(r'^[6-9]\d{9}$');

  Future<void> _handleSendOtp(RunnerAppState state) async {
    final phone = _phoneController.text.trim();
    final isHi = state.isHindi;

    if (!_phoneRegex.hasMatch(phone)) {
      setState(() => _errorMessage = isHi
          ? 'कृपया सही 10-अंकीय भारतीय मोबाइल नंबर दर्ज करें (6-9 से शुरू)'
          : 'Please enter a valid 10-digit Indian mobile number (starts with 6-9)');
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final res = await state.apiClient.sendOtp(phone: phone, role: 'runner');

    if (!mounted) return;
    setState(() => _isLoading = false);

    if (res.isSuccess) {
      _sessionId = res.data?['session_id'] as String?;
      setState(() => _otpSent = true);
    } else {
      setState(() => _errorMessage = res.errorMessage ?? (isHi ? 'ओटीपी भेजने में विफल' : 'Failed to send OTP'));
    }
  }

  Future<void> _handleVerifyOtp(RunnerAppState state) async {
    final phone = _phoneController.text.trim();
    final otp = _otpController.text.trim();
    final isHi = state.isHindi;

    if (otp.length != 6) {
      setState(() => _errorMessage = isHi ? 'कृपया 6-अंकीय ओटीपी दर्ज करें' : 'Please enter 6-digit OTP');
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final res = await state.apiClient.verifyOtp(
      phone: phone,
      otp: otp,
      sessionId: _sessionId,
      role: 'runner',
    );

    if (!mounted) return;
    setState(() => _isLoading = false);

    if (res.isSuccess) {
      final data = res.data!;
      final user = GBUser.fromJson(data['user'] as Map<String, dynamic>);
      final token = data['access_token'] as String;

      state.setAuth(user, token);
      await state.fetchProfile();
      if (!mounted) return;

      if (state.runnerProfile == null) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const RunnerOnboardingWizard()),
        );
      } else if (!state.isApproved) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const RunnerPendingApprovalScreen()),
        );
      } else {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const RunnerDashboardScreen()),
        );
      }
    } else {
      setState(() => _errorMessage = res.errorMessage ?? (isHi ? 'ओटीपी सत्यापन विफल' : 'OTP verification failed'));
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = RunnerStateProvider.of(context);
    final isHi = state.isHindi;
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: Text(
          isHi ? 'डिलीवरी साथी लॉगिन' : 'Delivery Partner Login',
          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
        ),

      ),
      body: SafeArea(
        child: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  _otpSent
                      ? (isHi ? 'ओटीपी कोड दर्ज करें' : 'Enter OTP Code')
                      : (isHi ? 'डिलीवरी पार्टनर लॉगिन' : 'Delivery Partner Login'),
                  style: GBTypography.displayLarge(context),
                ),
                const SizedBox(height: 8),
                Text(
                  _otpSent
                      ? (isHi
                          ? '+91 ${_phoneController.text} पर भेजा गया 6-अंकीय कोड डालें'
                          : 'Enter the 6-digit code sent to +91 ${_phoneController.text}')
                      : (isHi
                          ? 'गाँव में डिलीवरी शुरू करने के लिए अपना पंजीकृत मोबाइल नंबर डालें'
                          : 'Enter your registered mobile number to start delivering in villages'),
                  style: GBTypography.bodyMedium(context),
                ),
                const SizedBox(height: 28),
                if (!_otpSent) ...[
                  Container(
                    decoration: BoxDecoration(
                      color: isDark ? GBColors.surfaceDark : Colors.white,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: isDark ? GBColors.borderDark : GBColors.borderLight, width: 1.5),
                    ),
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 4),
                    child: Row(
                      children: [
                        const Text('🇮🇳 +91', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
                        const SizedBox(width: 12),
                        Expanded(
                          child: TextField(
                            controller: _phoneController,
                            keyboardType: TextInputType.phone,
                            maxLength: 10,
                            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600, letterSpacing: 1.0),
                            decoration: InputDecoration(
                              hintText: isHi ? 'मोबाइल नंबर' : 'Mobile Number',
                              border: InputBorder.none,
                              counterText: '',
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 12),
                  InkWell(
                    onTap: () => setState(() {
                      _phoneController.text = '9800000003';
                      _errorMessage = null;
                    }),
                    borderRadius: BorderRadius.circular(8),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                      decoration: BoxDecoration(
                        color: GBColors.primary.withOpacity(0.08),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: GBColors.primary.withOpacity(0.3)),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(Icons.science_outlined, size: 16, color: GBColors.primary),
                          const SizedBox(width: 8),
                          Text(
                            isHi ? 'स्टेजिंग रनर फोन: 9800000003 (टैप करें)' : 'Staging Runner: 9800000003 (Tap to fill)',
                            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: GBColors.primary),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),
                  GBPrimaryButton(
                    label: isHi ? 'ओटीपी प्राप्त करें' : 'Send OTP',
                    isLoading: _isLoading,
                    onPressed: () => _handleSendOtp(state),
                  ),
                ] else ...[
                  Container(
                    decoration: BoxDecoration(
                      color: isDark ? GBColors.surfaceDark : Colors.white,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: isDark ? GBColors.borderDark : GBColors.borderLight, width: 1.5),
                    ),
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    child: TextField(
                      controller: _otpController,
                      keyboardType: TextInputType.number,
                      maxLength: 6,
                      textAlign: TextAlign.center,
                      style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w800, letterSpacing: 10),
                      decoration: const InputDecoration(
                        hintText: '------',
                        border: InputBorder.none,
                        counterText: '',
                      ),
                    ),
                  ),
                  if (_phoneController.text == '9800000003') ...[
                    const SizedBox(height: 12),
                    InkWell(
                      onTap: () => setState(() {
                        _otpController.text = '123456';
                        _errorMessage = null;
                      }),
                      borderRadius: BorderRadius.circular(8),
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                        decoration: BoxDecoration(
                          color: GBColors.primary.withOpacity(0.08),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: GBColors.primary.withOpacity(0.3)),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(Icons.science_outlined, size: 16, color: GBColors.primary),
                            const SizedBox(width: 8),
                            Text(
                              isHi ? 'स्टेजिंग ओटीपी: 123456 (टैप करें)' : 'Staging OTP: 123456 (Tap to fill)',
                              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: GBColors.primary),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                  const SizedBox(height: 24),
                  GBPrimaryButton(
                    label: isHi ? 'सत्यापित करें व लॉगिन करें' : 'Verify & Login',
                    isLoading: _isLoading,
                    onPressed: () => _handleVerifyOtp(state),
                  ),
                  const SizedBox(height: 12),
                  Center(
                    child: TextButton(
                      onPressed: () => setState(() => _otpSent = false),
                      child: Text(
                        isHi ? 'मोबाइल नंबर बदलें' : 'Change Phone Number',
                        style: const TextStyle(fontWeight: FontWeight.w600),
                      ),
                    ),
                  ),
                ],
                if (_errorMessage != null) ...[
                  const SizedBox(height: 12),
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: GBColors.error.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: GBColors.error),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.error_outline, size: 18, color: GBColors.error),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            _errorMessage!,
                            style: const TextStyle(color: GBColors.error, fontSize: 13, fontWeight: FontWeight.w600),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
                const SizedBox(height: 36),
                Center(
                  child: TextButton(
                    onPressed: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(builder: (_) => const RunnerOnboardingWizard()),
                      );
                    },
                    child: Text(
                      isHi ? 'नए डिलीवरी साथी? आवेदन फॉर्म भरें' : 'New Delivery Partner? Register Here',
                      style: const TextStyle(fontWeight: FontWeight.w700, color: GBColors.primary),
                    ),
                  ),
                ),
                const SizedBox(height: 12),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
