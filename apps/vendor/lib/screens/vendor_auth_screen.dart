import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:shared_models/shared_models.dart';
import '../state/vendor_state.dart';
import 'vendor_dashboard_screen.dart';
import 'vendor_onboarding_wizard.dart';

class VendorAuthScreen extends StatefulWidget {
  const VendorAuthScreen({super.key});

  @override
  State<VendorAuthScreen> createState() => _VendorAuthScreenState();
}

class _VendorAuthScreenState extends State<VendorAuthScreen> {
  final TextEditingController _phoneController = TextEditingController(text: '9800000001');
  final TextEditingController _otpController = TextEditingController(text: '123456');
  bool _otpSent = false;
  bool _isLoading = false;
  String? _errorMessage;

  Future<void> _handleSendOtp() async {
    final phone = _phoneController.text.trim();
    if (phone.length != 10) {
      setState(() => _errorMessage = 'कृपया 10 अंकों का मोबाइल नंबर दर्ज करें');
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final state = VendorStateProvider.of(context);
    final res = await state.apiClient.sendOtp(phone: phone, role: 'vendor');

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

    final state = VendorStateProvider.of(context);
    final res = await state.apiClient.verifyOtp(
      phone: phone,
      otp: otp,
      role: 'vendor',
    );

    setState(() => _isLoading = false);

    if (res.isSuccess && mounted) {
      final data = res.data!;
      final user = GBUser.fromJson(data['user'] as Map<String, dynamic>);
      final token = data['access_token'] as String;

      state.setAuth(user, token);

      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => const VendorDashboardScreen()),
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
        title: const Text('दुकानदार लॉगिन (Vendor Partner)', style: TextStyle(fontWeight: FontWeight.w800, fontSize: 16)),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                _otpSent ? 'ओटीपी दर्ज करें' : 'मोबाइल नंबर दर्ज करें',
                style: GBTypography.displayLarge(context),
              ),
              const SizedBox(height: 8),
              Text(
                _otpSent
                    ? '+91 ${_phoneController.text} पर भेजा गया 6-अंकीय कोड डालें'
                    : 'गाँव बाज़ार में अपनी दुकान से ऑनलाइन बिक्री शुरू करने के लिए नंबर डालें',
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
                            enabledBorder: InputBorder.none,
                            focusedBorder: InputBorder.none,
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
                  label: 'लॉगिन करें (Verify & Login)',
                  isLoading: _isLoading,
                  onPressed: _handleVerifyOtp,
                ),
              ],
              if (_errorMessage != null) ...[
                const SizedBox(height: 12),
                Text(_errorMessage!, style: const TextStyle(color: GBColors.error, fontSize: 13)),
              ],
              const Spacer(),
              // New store registration wizard link
              Center(
                child: TextButton(
                  onPressed: () {
                    Navigator.of(context).push(
                      MaterialPageRoute(builder: (_) => const VendorOnboardingWizard()),
                    );
                  },
                  child: const Text(
                    'नई दुकान जोड़ें? ऑनबोर्डिंग फॉर्म भरें (Register Store)',
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
