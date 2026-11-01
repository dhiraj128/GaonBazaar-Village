import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
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
    final loc = GBLocalizations.of(context);
    if (!RegExp(r'^[6-9]\d{9}$').hasMatch(phone)) {
      setState(() => _errorMessage = loc.isHindi
          ? 'कृपया 10 अंकों का वैध भारतीय मोबाइल नंबर दर्ज करें'
          : 'Please enter a valid 10-digit Indian mobile number');
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
      setState(() => _errorMessage = res.errorMessage ?? (loc.isHindi ? 'ओटीपी भेजने में विफल' : 'Failed to send OTP'));
    }
  }

  Future<void> _handleVerifyOtp() async {
    final phone = _phoneController.text.trim();
    final otp = _otpController.text.trim();
    final loc = GBLocalizations.of(context);

    if (otp.length != 6) {
      setState(() => _errorMessage = loc.isHindi ? 'कृपया 6-अंकीय ओटीपी दर्ज करें' : 'Please enter 6-digit OTP');
      return;
    }

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
      setState(() => _errorMessage = res.errorMessage ?? (loc.isHindi ? 'ओटीपी सत्यापन विफल' : 'OTP verification failed'));
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = VendorStateProvider.of(context);
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: Text(
          loc.tr('vendor_login'),
          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
        ),
        actions: [
          TextButton.icon(
            icon: const Icon(Icons.language, size: 18),
            label: Text(
              state.isHindi ? 'English' : 'हिंदी',
              style: const TextStyle(fontWeight: FontWeight.w700),
            ),
            onPressed: () {
              state.setLocale(state.isHindi ? 'en' : 'hi');
            },
          ),
        ],
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                _otpSent
                    ? (loc.isHindi ? 'ओटीपी दर्ज करें' : 'Enter Verification PIN')
                    : (loc.isHindi ? 'मोबाइल नंबर दर्ज करें' : 'Enter Mobile Number'),
                style: GBTypography.displayLarge(context),
              ),
              const SizedBox(height: 8),
              Text(
                _otpSent
                    ? (loc.isHindi
                        ? '+91 ${_phoneController.text} पर भेजा गया 6-अंकीय कोड डालें'
                        : 'Enter the 6-digit code sent to +91 ${_phoneController.text}')
                    : (loc.isHindi
                        ? 'गाँव बाज़ार में अपनी दुकान से ऑनलाइन बिक्री शुरू करने के लिए नंबर डालें'
                        : 'Enter your registered mobile number to manage your village store'),
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
                            hintText: loc.isHindi ? 'मोबाइल नंबर' : '10-Digit Mobile',
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
                  label: loc.isHindi ? 'ओटीपी प्राप्त करें' : 'Send OTP',
                  isLoading: _isLoading,
                  onPressed: _handleSendOtp,
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
                      hintText: '------',
                      border: InputBorder.none,
                      counterText: '',
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                GBPrimaryButton(
                  label: loc.isHindi ? 'सत्यापित करें व लॉगिन करें' : 'Verify & Login',
                  isLoading: _isLoading,
                  onPressed: _handleVerifyOtp,
                ),
                const SizedBox(height: 12),
                Center(
                  child: TextButton(
                    onPressed: () => setState(() => _otpSent = false),
                    child: Text(
                      loc.isHindi ? 'मोबाइल नंबर बदलें' : 'Change Mobile Number',
                      style: const TextStyle(color: GBColors.primary, fontWeight: FontWeight.w700),
                    ),
                  ),
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
                  child: Text(
                    loc.tr('vendor_register_store'),
                    style: const TextStyle(fontWeight: FontWeight.w700, color: GBColors.primary),
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
