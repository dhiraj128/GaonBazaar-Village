import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import '../state/runner_state.dart';
import 'runner_dashboard_screen.dart';
import 'runner_auth_screen.dart';
import 'runner_onboarding_wizard.dart';

class RunnerPendingApprovalScreen extends StatefulWidget {
  const RunnerPendingApprovalScreen({super.key});

  @override
  State<RunnerPendingApprovalScreen> createState() => _RunnerPendingApprovalScreenState();
}

class _RunnerPendingApprovalScreenState extends State<RunnerPendingApprovalScreen> {
  bool _isChecking = false;

  Future<void> _checkStatus(RunnerAppState state) async {
    setState(() => _isChecking = true);
    await state.fetchProfile();
    if (!mounted) return;
    setState(() => _isChecking = false);

    if (state.isApproved) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            state.isHindi ? 'बधाई! आपकी प्रोफ़ाइल स्वीकृत हो चुकी है।' : 'Congratulations! Your profile is approved.',
          ),
          backgroundColor: GBColors.success,
        ),
      );
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => const RunnerDashboardScreen()),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            state.isHindi
                ? 'समीक्षा अभी जारी है। कृपया कुछ समय बाद पुनः प्रयास करें।'
                : 'Application is still under review. Please check back shortly.',
          ),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = RunnerStateProvider.of(context);
    final isHi = state.isHindi;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final profile = state.runnerProfile;
    final isRejected = profile != null && !state.isApproved && profile['rejection_reason'] != null;

    return Scaffold(
      appBar: AppBar(
        title: Text(
          isHi ? 'पार्टनर सत्यापन स्थिति' : 'Partner Verification Status',
          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout_rounded),
            tooltip: isHi ? 'लॉग आउट' : 'Sign Out',
            onPressed: () {
              state.logout();
              Navigator.of(context).pushReplacement(
                MaterialPageRoute(builder: (_) => const RunnerAuthScreen()),
              );
            },
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const SizedBox(height: 20),
              Container(
                width: 90,
                height: 90,
                decoration: BoxDecoration(
                  color: (isRejected ? Colors.red : Colors.amber).withValues(alpha: 0.12),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  isRejected ? Icons.cancel_outlined : Icons.hourglass_top_rounded,
                  color: isRejected ? Colors.red : Colors.amber.shade800,
                  size: 48,
                ),
              ),
              const SizedBox(height: 20),
              Text(
                isRejected
                    ? (isHi ? 'आवेदन अस्वीकृत' : 'Application Rejected')
                    : (isHi ? 'आवेदन समीक्षाधीन है' : 'Application Under Review'),
                style: GBTypography.displayLarge(context).copyWith(
                  color: isRejected ? Colors.red : Colors.amber.shade900,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 12),
              Text(
                isRejected
                    ? (isHi
                        ? 'सुपर एडमिन द्वारा आपके आवेदन में सुधार की आवश्यकता पाई गई है: ${profile['rejection_reason']}'
                        : 'Super Admin found corrections needed: ${profile['rejection_reason']}')
                    : (isHi
                        ? 'आपका डिलीवरी साथी पंजीकरण विवरण सफलतापूर्वक जमा हो चुका है। सुपर एडमिन द्वारा दस्तावेज़ सत्यापन के बाद आपकी आईडी सक्रिय कर दी जाएगी।'
                        : 'Your delivery partner registration has been submitted. Once verified by Super Admin, you will be authorized to accept delivery missions.'),
                style: GBTypography.bodyMedium(context),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 28),
              if (profile != null)
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(18),
                  decoration: BoxDecoration(
                    color: isDark ? const Color(0xFF1E293B) : Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: isDark ? Colors.white12 : Colors.black12),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        isHi ? 'पंजीकृत साथी विवरण:' : 'Registered Partner Details:',
                        style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
                      ),
                      const Divider(height: 20),
                      _infoRow(isHi ? 'नाम' : 'Full Name', profile['full_name']?.toString() ?? '-'),
                      _infoRow(isHi ? 'वाहन प्रकार' : 'Vehicle Type', profile['vehicle_type']?.toString() ?? '-'),
                      _infoRow(isHi ? 'वाहन नंबर' : 'Vehicle Number', profile['vehicle_number']?.toString() ?? '-'),
                      _infoRow(
                        isHi ? 'अनुमोदन स्थिति' : 'Approval Status',
                        isRejected
                            ? (isHi ? 'अस्वीकृत' : 'Rejected')
                            : (isHi ? 'समीक्षाधीन' : 'Pending Review'),
                        color: isRejected ? Colors.red : Colors.amber.shade800,
                      ),
                    ],
                  ),
                ),
              const SizedBox(height: 32),
              if (isRejected)
                GBPrimaryButton(
                  label: isHi ? 'विवरण सुधारें' : 'Edit & Resubmit',
                  onPressed: () {
                    Navigator.of(context).push(
                      MaterialPageRoute(builder: (_) => const RunnerOnboardingWizard()),
                    );
                  },
                )
              else
                GBPrimaryButton(
                  label: _isChecking
                      ? (isHi ? 'जांच जारी है...' : 'Checking...')
                      : (isHi ? 'स्थिति पुनः जांचें' : 'Check Status'),
                  onPressed: _isChecking ? null : () => _checkStatus(state),
                ),
              const SizedBox(height: 16),
              OutlinedButton.icon(
                icon: const Icon(Icons.logout, size: 18),
                label: Text(isHi ? 'लॉग आउट करें' : 'Sign Out'),
                style: OutlinedButton.styleFrom(
                  minimumSize: const Size.fromHeight(48),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                onPressed: () {
                  state.logout();
                  Navigator.of(context).pushReplacement(
                    MaterialPageRoute(builder: (_) => const RunnerAuthScreen()),
                  );
                },
              ),
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }

  Widget _infoRow(String label, String value, {Color? color}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontSize: 13, color: Colors.grey)),
          Text(
            value,
            style: TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w600,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}
