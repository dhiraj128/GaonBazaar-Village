import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:shared_models/shared_models.dart';
import '../state/runner_state.dart';
import 'runner_dashboard_screen.dart';
import 'runner_pending_approval_screen.dart';
import 'runner_onboarding_wizard.dart';
import 'runner_language_selection_screen.dart';

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

    if (otp.length < 4) {
      setState(() => _errorMessage = isHi ? 'कृपया 4-अंकीय ओटीपी दर्ज करें' : 'Please enter 4-digit OTP');
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

      final upi = state.runnerProfile?['upi_id']?.toString().trim();
      final hasCompletedOnboarding = state.runnerProfile != null &&
          upi != null &&
          upi.isNotEmpty &&
          upi != 'NOT_CONFIGURED';

      if (!hasCompletedOnboarding) {
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
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            if (_otpSent) {
              setState(() {
                _otpSent = false;
                _otpController.clear();
                _errorMessage = null;
              });
            } else {
              Navigator.of(context).pushReplacement(
                MaterialPageRoute(builder: (_) => const RunnerLanguageSelectionScreen()),
              );
            }
          },
        ),
        title: Text(
          isHi ? 'मोबाइल नंबर सत्यापन' : 'Mobile Number Verification',
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
                      ? (isHi ? 'ओटीपी दर्ज करें' : 'Enter 4-Digit OTP')
                      : (isHi ? 'मोबाइल नंबर दर्ज करें' : 'Enter Mobile Number'),
                  style: GBTypography.displayLarge(context),
                ),
                const SizedBox(height: 8),
                Text(
                  _otpSent
                      ? (isHi
                          ? '+91 ${_phoneController.text} पर भेजा गया 4-अंकीय ओटीपी दर्ज करें'
                          : 'Enter the 4-digit OTP sent to +91 ${_phoneController.text}')
                      : (isHi
                          ? 'गाँव बाज़ार से जुड़कर डिलीवरी करके दैनिक कमाई करने के लिए लॉगिन करें'
                          : 'Enter your registered mobile number to deliver orders and earn daily'),
                  style: GBTypography.bodyMedium(context),
                ),
                const SizedBox(height: 28),
                if (!_otpSent) ...[
                  Container(
                    decoration: BoxDecoration(
                      color: isDark ? GBColors.surfaceDark : Colors.white,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: isDark ? GBColors.borderDark : GBColors.borderLight,
                        width: 1.5,
                      ),
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
                              hintText: isHi ? '10-अंकीय मोबाइल नंबर' : '10-Digit Mobile',
                              border: InputBorder.none,
                              enabledBorder: InputBorder.none,
                              focusedBorder: InputBorder.none,
                              counterText: '',
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 14),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      ActionChip(
                        avatar: const Icon(Icons.person_add_alt_1_outlined, size: 16, color: GBColors.primary),
                        label: Text(
                          isHi ? 'नया आवेदक: 9800000031' : 'New Applicant: 9800000031',
                          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: GBColors.primary),
                        ),
                        backgroundColor: GBColors.primary.withValues(alpha: 0.08),
                        onPressed: () => setState(() {
                          _phoneController.text = '9800000031';
                          _errorMessage = null;
                        }),
                      ),
                      ActionChip(
                        avatar: const Icon(Icons.two_wheeler_outlined, size: 16, color: GBColors.primary),
                        label: Text(
                          isHi ? 'स्वीकृत साथी: 9800000003' : 'Approved Partner: 9800000003',
                          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: GBColors.primary),
                        ),
                        backgroundColor: GBColors.primary.withValues(alpha: 0.08),
                        onPressed: () => setState(() {
                          _phoneController.text = '9800000003';
                          _errorMessage = null;
                        }),
                      ),
                    ],
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
                      border: Border.all(
                        color: isDark ? GBColors.borderDark : GBColors.borderLight,
                        width: 1.5,
                      ),
                    ),
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    child: TextField(
                      controller: _otpController,
                      keyboardType: TextInputType.number,
                      maxLength: 6,
                      textAlign: TextAlign.center,
                      style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w800, letterSpacing: 10),
                      decoration: const InputDecoration(
                        hintText: '••••',
                        border: InputBorder.none,
                        counterText: '',
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  ActionChip(
                    avatar: const Icon(Icons.key_outlined, size: 16, color: GBColors.primary),
                    label: Text(
                      isHi ? 'परीक्षण ओटीपी: 1234 (टैप करें)' : 'Test OTP: 1234 (Tap to fill)',
                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: GBColors.primary),
                    ),
                    backgroundColor: GBColors.primary.withValues(alpha: 0.08),
                    onPressed: () => setState(() {
                      _otpController.text = '1234';
                      _errorMessage = null;
                    }),
                  ),
                  const SizedBox(height: 24),
                  GBPrimaryButton(
                    label: isHi ? 'ओटीपी सत्यापित करें' : 'Verify OTP',
                    isLoading: _isLoading,
                    onPressed: () => _handleVerifyOtp(state),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      TextButton(
                        onPressed: _isLoading ? null : () => _handleSendOtp(state),
                        child: Text(
                          isHi ? 'पुनः ओटीपी भेजें' : 'Resend OTP',
                          style: const TextStyle(fontWeight: FontWeight.w700),
                        ),
                      ),
                      const Text('•', style: TextStyle(color: Colors.grey)),
                      TextButton(
                        onPressed: () => setState(() {
                          _otpSent = false;
                          _otpController.clear();
                          _errorMessage = null;
                        }),
                        child: Text(
                          isHi ? 'मोबाइल नंबर बदलें' : 'Change Number',
                          style: const TextStyle(color: GBColors.primary, fontWeight: FontWeight.w700),
                        ),
                      ),
                    ],
                  ),
                ],
                if (_errorMessage != null) ...[
                  const SizedBox(height: 12),
                  Text(_errorMessage!, style: const TextStyle(color: GBColors.error, fontSize: 13)),
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
                      isHi ? 'नया डिलीवरी साथी पंजीकरण' : 'Register New Delivery Partner',
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
