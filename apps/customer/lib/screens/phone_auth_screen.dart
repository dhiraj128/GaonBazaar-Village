import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
import '../state/app_state.dart';
import 'otp_verification_screen.dart';
import 'main_nav_screen.dart';

class PhoneAuthScreen extends StatefulWidget {
  const PhoneAuthScreen({super.key});

  @override
  State<PhoneAuthScreen> createState() => _PhoneAuthScreenState();
}

class _PhoneAuthScreenState extends State<PhoneAuthScreen> {
  final TextEditingController _phoneController = TextEditingController(text: '9876543210');
  bool _isLoading = false;
  String? _errorMessage;

  Future<void> _handleGetOtp() async {
    final phone = _phoneController.text.trim();
    if (phone.length != 10 || !RegExp(r'^[6-9]\d{9}$').hasMatch(phone)) {
      setState(() {
        _errorMessage = 'कृपया सही 10 अंकों का मोबाइल नंबर दर्ज करें (Valid 10-digit number required)';
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final state = AppStateProvider.of(context);
    final response = await state.apiClient.sendOtp(phone: phone, role: 'customer');

    setState(() {
      _isLoading = false;
    });

    if (response.isSuccess && mounted) {
      final sessionId = response.data?['session_id'] as String?;
      Navigator.of(context).push(
        MaterialPageRoute(
          builder: (_) => OtpVerificationScreen(
            phone: phone,
            sessionId: sessionId,
          ),
        ),
      );
    } else if (mounted) {
      setState(() {
        _errorMessage = response.errorMessage ?? 'ओटीपी भेजने में विफल (Failed to send OTP)';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.of(context).pop(),
        ),
        actions: [
          TextButton(
            onPressed: () {
              // Allow browsing without sign in
              Navigator.of(context).pushReplacement(
                MaterialPageRoute(builder: (_) => const MainNavScreen()),
              );
            },
            child: Text(
              loc.isHindi ? 'छोड़ें (Skip)' : 'Skip',
              style: const TextStyle(fontWeight: FontWeight.w700),
            ),
          ),
        ],
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                loc.tr('enter_phone'),
                style: GBTypography.displayLarge(context),
              ),
              const SizedBox(height: 8),
              Text(
                loc.tr('phone_subtitle'),
                style: GBTypography.bodyMedium(context),
              ),
              const SizedBox(height: 32),
              // Phone input container
              Container(
                decoration: BoxDecoration(
                  color: isDark ? GBColors.surfaceDark : Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: _errorMessage != null
                        ? GBColors.error
                        : (isDark ? GBColors.borderDark : GBColors.borderLight),
                    width: 1.5,
                  ),
                ),
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 4),
                child: Row(
                  children: [
                    const Text(
                      '🇮🇳 +91',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Container(
                      width: 1,
                      height: 24,
                      color: isDark ? GBColors.borderDark : GBColors.borderLight,
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: TextField(
                        controller: _phoneController,
                        keyboardType: TextInputType.phone,
                        maxLength: 10,
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w600,
                          letterSpacing: 1.0,
                        ),
                        decoration: InputDecoration(
                          hintText: loc.tr('phone_hint'),
                          border: InputBorder.none,
                          enabledBorder: InputBorder.none,
                          focusedBorder: InputBorder.none,
                          counterText: '',
                          contentPadding: EdgeInsets.zero,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              if (_errorMessage != null) ...[
                const SizedBox(height: 10),
                Text(
                  _errorMessage!,
                  style: const TextStyle(color: GBColors.error, fontSize: 12),
                ),
              ],
              const SizedBox(height: 24),
              GBPrimaryButton(
                label: loc.tr('get_otp'),
                isLoading: _isLoading,
                onPressed: _handleGetOtp,
              ),
              const Spacer(),
              Center(
                child: Text(
                  loc.isHindi
                      ? 'आगे बढ़ने पर आप गाँव बाज़ार की सेवा शर्तों से सहमत होते हैं।'
                      : 'By continuing, you agree to GaonBazaar Terms of Service.',
                  textAlign: TextAlign.center,
                  style: GBTypography.bodySmall(context),
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
