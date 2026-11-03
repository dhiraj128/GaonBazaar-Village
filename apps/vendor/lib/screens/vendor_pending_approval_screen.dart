import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import '../state/vendor_state.dart';
import 'vendor_dashboard_screen.dart';
import 'vendor_auth_screen.dart';
import 'vendor_onboarding_wizard.dart';

class VendorPendingApprovalScreen extends StatefulWidget {
  const VendorPendingApprovalScreen({super.key});

  @override
  State<VendorPendingApprovalScreen> createState() => _VendorPendingApprovalScreenState();
}

class _VendorPendingApprovalScreenState extends State<VendorPendingApprovalScreen> {
  bool _isChecking = false;

  Future<void> _checkStatus(VendorAppState state) async {
    setState(() => _isChecking = true);
    await state.fetchStoreProfile();
    if (!mounted) return;
    setState(() => _isChecking = false);

    if (state.isStoreApproved) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            state.isHindi ? 'बधाई! आपकी दुकान स्वीकृत हो चुकी है।' : 'Congratulations! Your store is approved.',
          ),
          backgroundColor: GBColors.success,
        ),
      );
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => const VendorDashboardScreen()),
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
    final state = VendorStateProvider.of(context);
    final isHi = state.isHindi;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final store = state.myStore;
    final isRejected = store != null && !store.isApproved && store.landmark == 'REJECTED';

    return Scaffold(
      appBar: AppBar(
        title: Text(
          isHi ? 'दुकान स्थिति (Store Status)' : 'Store Verification Status',
          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout_rounded),
            tooltip: isHi ? 'लॉग आउट' : 'Sign Out',
            onPressed: () {
              state.logout();
              Navigator.of(context).pushReplacement(
                MaterialPageRoute(builder: (_) => const VendorAuthScreen()),
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
                  color: (isRejected ? Colors.red : Colors.amber).withOpacity(0.12),
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
                    ? (isHi ? 'आवेदन अस्वीकृत (Application Rejected)' : 'Application Rejected')
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
                        ? 'सुपर एडमिन द्वारा आपके आवेदन में सुधार की आवश्यकता पाई गई है। कृपया जानकारी ठीक कर पुनः जमा करें।'
                        : 'Super Admin found corrections needed in your application. Please review and resubmit.')
                    : (isHi
                        ? 'आपकी दुकान का 8-चरणीय विवरण सफलतापूर्वक जमा हो चुका है। सुपर एडमिन द्वारा सत्यापन और भौतिक जांच के बाद आपकी दुकान सक्रिय कर दी जाएगी।'
                        : 'Your 8-step store registration has been submitted. Once verified by Super Admin, your shop will go live with 0% commission.'),
                style: GBTypography.bodyMedium(context),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 28),
              if (store != null)
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
                        isHi ? 'पंजीकृत विवरण:' : 'Registered Store Details:',
                        style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
                      ),
                      const Divider(height: 20),
                      _infoRow(isHi ? 'दुकान का नाम' : 'Shop Name', store.shopName),
                      _infoRow(isHi ? 'संचालक' : 'Owner', store.ownerName),
                      _infoRow(isHi ? 'श्रेणी' : 'Category', store.category),
                      _infoRow(isHi ? 'गाँव / क्षेत्र' : 'Village / Area', store.village),
                      _infoRow(
                        isHi ? 'अनुमोदन स्थिति' : 'Approval Status',
                        isRejected
                            ? (isHi ? 'अस्वीकृत (Rejected)' : 'Rejected')
                            : (isHi ? 'समीक्षाधीन (Pending Review)' : 'Pending Review'),
                        color: isRejected ? Colors.red : Colors.amber.shade800,
                      ),
                    ],
                  ),
                ),
              const SizedBox(height: 32),
              if (isRejected)
                GBPrimaryButton(
                  label: isHi ? 'विवरण सुधारें (Edit & Resubmit)' : 'Edit & Resubmit',
                  onPressed: () {
                    Navigator.of(context).push(
                      MaterialPageRoute(builder: (_) => const VendorOnboardingWizard()),
                    );
                  },
                )
              else
                GBPrimaryButton(
                  label: _isChecking
                      ? (isHi ? 'जांच जारी है...' : 'Checking...')
                      : (isHi ? 'स्थिति पुनः जांचें (Check Status)' : 'Check Status'),
                  onPressed: _isChecking ? null : () => _checkStatus(state),
                ),
              const SizedBox(height: 16),
              OutlinedButton.icon(
                icon: const Icon(Icons.logout, size: 18),
                label: Text(isHi ? 'लॉग आउट करें (Sign Out)' : 'Sign Out'),
                style: OutlinedButton.styleFrom(
                  minimumSize: const Size.fromHeight(48),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                onPressed: () {
                  state.logout();
                  Navigator.of(context).pushReplacement(
                    MaterialPageRoute(builder: (_) => const VendorAuthScreen()),
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
