import 'dart:async';
import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
import 'package:shared_models/shared_models.dart';
import '../state/app_state.dart';
import 'main_nav_screen.dart';

class OtpVerificationScreen extends StatefulWidget {
  final String phone;
  final String? sessionId;

  const OtpVerificationScreen({
    super.key,
    required this.phone,
    this.sessionId,
  });

  @override
  State<OtpVerificationScreen> createState() => _OtpVerificationScreenState();
}

class _OtpVerificationScreenState extends State<OtpVerificationScreen> {
  final TextEditingController _otpController = TextEditingController(text: '123456');
  bool _isLoading = false;
  String? _errorMessage;
  int _secondsRemaining = 60;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _startCountdown();
  }

  void _startCountdown() {
    _timer?.cancel();
    setState(() => _secondsRemaining = 60);
    _timer = Timer.periodic(const Duration(seconds: 1), (t) {
      if (_secondsRemaining > 0) {
        setState(() => _secondsRemaining--);
      } else {
        t.cancel();
      }
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    _otpController.dispose();
    super.dispose();
  }

  Future<void> _handleVerify() async {
    final loc = GBLocalizations.of(context);
    final otp = _otpController.text.trim();
    if (otp.length < 4) {
      setState(() => _errorMessage = loc.tr('otp_invalid'));
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final state = AppStateProvider.of(context);
    final response = await state.apiClient.verifyOtp(
      phone: widget.phone,
      otp: otp,
      sessionId: widget.sessionId,
      role: 'customer',
    );

    setState(() => _isLoading = false);

    if (response.isSuccess && mounted) {
      final data = response.data!;
      final userJson = data['user'] as Map<String, dynamic>;
      final user = GBUser.fromJson(userJson);
      final token = data['access_token'] as String;

      state.setAuth(user, token);

      Navigator.of(context).pushAndRemoveUntil(
        MaterialPageRoute(builder: (_) => const MainNavScreen()),
        (route) => false,
      );
    } else if (mounted) {
      setState(() {
        _errorMessage = response.errorMessage ?? loc.tr('otp_invalid');
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
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                loc.tr('verify_otp'),
                style: GBTypography.displayLarge(context),
              ),
              const SizedBox(height: 8),
              Text(
                '${loc.tr('otp_sent_to')} +91 ${widget.phone}',
                style: GBTypography.bodyMedium(context),
              ),
              const SizedBox(height: 28),
              // OTP Input field
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
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                child: TextField(
                  controller: _otpController,
                  keyboardType: TextInputType.number,
                  maxLength: 6,
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.w800,
                    letterSpacing: 10,
                  ),
                  decoration: const InputDecoration(
                    hintText: '------',
                    border: InputBorder.none,
                    enabledBorder: InputBorder.none,
                    focusedBorder: InputBorder.none,
                    counterText: '',
                  ),
                ),
              ),
              if (_errorMessage != null) ...[
                const SizedBox(height: 10),
                Text(
                  _errorMessage!,
                  style: const TextStyle(color: GBColors.error, fontSize: 13, fontWeight: FontWeight.w500),
                ),
              ],
              const SizedBox(height: 20),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    _secondsRemaining > 0
                        ? '${loc.tr('resend_in')} ${_secondsRemaining} ${loc.tr('seconds')}'
                        : (loc.isHindi ? 'ओटीपी नहीं मिला?' : 'Didn\'t receive OTP?'),
                    style: GBTypography.bodySmall(context),
                  ),
                  TextButton(
                    onPressed: _secondsRemaining == 0
                        ? () {
                            _startCountdown();
                            AppStateProvider.of(context).apiClient.sendOtp(
                                  phone: widget.phone,
                                  role: 'customer',
                                );
                          }
                        : null,
                    child: Text(
                      loc.tr('resend_otp'),
                      style: TextStyle(
                        fontWeight: FontWeight.w700,
                        color: _secondsRemaining == 0 ? GBColors.primary : Colors.grey,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: GBColors.primary.withOpacity(0.08),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: GBColors.primary.withOpacity(0.2)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.shield_outlined, size: 18, color: GBColors.primary),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        loc.tr('otp_dev_note'),
                        style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: GBColors.primary),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),
              GBPrimaryButton(
                label: loc.tr('verify_and_proceed'),
                isLoading: _isLoading,
                onPressed: _handleVerify,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
