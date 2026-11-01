import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:shared_models/shared_models.dart';
import '../state/runner_state.dart';
import 'runner_dashboard_screen.dart';
import 'runner_onboarding_wizard.dart';

class RunnerAuthScreen extends StatefulWidget {
  const RunnerAuthScreen({super.key});

  @override
  State<RunnerAuthScreen> createState() => _RunnerAuthScreenState();
}

class _RunnerAuthScreenState extends State<RunnerAuthScreen> {
  final TextEditingController _phoneController = TextEditingController(text: '9800000003');
  final TextEditingController _otpController = TextEditingController(text: '123456');
  bool _otpSent = false;
  bool _isLoading = false;
  String? _errorMessage;

  Future<void> _handleSendOtp() async {
    final phone = _phoneController.text.trim();
    if (phone.length != 10) {
      setState(() => _errorMessage = 'कृपया सही 10-अंकीय मोबाइल नंबर दर्ज करें');
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final state = RunnerStateProvider.of(context);
    final res = await state.apiClient.sendOtp(phone: phone, role: 'runner');

    setState(() => _isLoading = false);

    if (res.isSuccess) {
      setState(() => _otpSent = true);
    } else {
      setState(() => _errorMessage = res.errorMessage ?? 'ओटीपी भेजने में विफल');
    }
  }

  Future<void> _handleVerifyOtp() async {
    final phone = _phoneController.text.trim();
    final otp = _otpController.text.trim();

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final state = RunnerStateProvider.of(context);
    final res = await state.apiClient.verifyOtp(
      phone: phone,
      otp: otp,
      role: 'runner',
    );

    setState(() => _isLoading = false);

    if (res.isSuccess && mounted) {
      final data = res.data!;
      final user = GBUser.fromJson(data['user'] as Map<String, dynamic>);
      final token = data['access_token'] as String;

      state.setAuth(user, token);

      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => const RunnerDashboardScreen()),
      );
    } else if (mounted) {
      setState(() => _errorMessage = res.errorMessage ?? 'ओटीपी सत्यापन विफल');
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: const Text('डिलीवरी साथी लॉगिन (Runner Partner)', style: TextStyle(fontWeight: FontWeight.w800, fontSize: 16)),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                _otpSent ? 'ओटीपी कोड दर्ज करें' : 'डिलीवरी पार्टनर लॉगिन',
                style: GBTypography.displayLarge(context),
              ),
              const SizedBox(height: 8),
              Text(
                _otpSent
                    ? '+91 ${_phoneController.text} पर भेजा गया 6-अंकीय कोड डालें'
                    : 'गाँव में डिलीवरी शुरू करने के लिए अपना पंजीकृत मोबाइल नंबर डालें',
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
                          decoration: const InputDecoration(
                            hintText: 'मोबाइल नंबर',
                            border: InputBorder.none,
                            counterText: '',
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                GBPrimaryButton(
                  label: 'ओटीपी प्राप्त करें (Send OTP)',
                  isLoading: _isLoading,
                  onPressed: _handleSendOtp,
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
                const SizedBox(height: 24),
                GBPrimaryButton(
                  label: 'सत्यापित करें व शुरू करें (Login)',
                  isLoading: _isLoading,
                  onPressed: _handleVerifyOtp,
                ),
              ],
              if (_errorMessage != null) ...[
                const SizedBox(height: 12),
                Text(_errorMessage!, style: const TextStyle(color: GBColors.error, fontSize: 13)),
              ],
              const Spacer(),
              Center(
                child: TextButton(
                  onPressed: () {
                    Navigator.of(context).push(
                      MaterialPageRoute(builder: (_) => const RunnerOnboardingWizard()),
                    );
                  },
                  child: const Text(
                    'नए डिलीवरी साथी? आवेदन फॉर्म भरें (Register Partner)',
                    style: TextStyle(fontWeight: FontWeight.w700, color: GBColors.primary),
                  ),
                ),
              ),
              const SizedBox(height: 12),
            ],
          ),
        ),
      ),
    );
  }
}
