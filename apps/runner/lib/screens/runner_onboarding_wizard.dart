import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import '../state/runner_state.dart';
import 'runner_dashboard_screen.dart';

class RunnerOnboardingWizard extends StatefulWidget {
  const RunnerOnboardingWizard({super.key});

  @override
  State<RunnerOnboardingWizard> createState() => _RunnerOnboardingWizardState();
}

class _RunnerOnboardingWizardState extends State<RunnerOnboardingWizard> {
  int _currentStep = 0;
  bool _isSubmitting = false;

  final _fullNameCtrl = TextEditingController();
  final _phoneCtrl = TextEditingController();
  final _bikeNoCtrl = TextEditingController();
  final _dlCtrl = TextEditingController();
  final _upiCtrl = TextEditingController();
  String _vehicleType = 'Motorcycle';
  bool _digiLockerConsented = false;

  @override
  void dispose() {
    _fullNameCtrl.dispose();
    _phoneCtrl.dispose();
    _bikeNoCtrl.dispose();
    _dlCtrl.dispose();
    _upiCtrl.dispose();
    super.dispose();
  }

  Future<void> _submitApplication(RunnerAppState state) async {
    final isHi = state.isHindi;

    if (_fullNameCtrl.text.trim().isEmpty) {
      _showError(isHi ? 'कृपया अपना पूरा नाम दर्ज करें' : 'Please enter your full name');
      return;
    }
    if (_bikeNoCtrl.text.trim().isEmpty) {
      _showError(isHi ? 'कृपया वाहन पंजीकरण संख्या दर्ज करें' : 'Please enter vehicle registration number');
      return;
    }
    if (_dlCtrl.text.trim().isEmpty) {
      _showError(isHi ? 'कृपया ड्राइविंग लाइसेंस संख्या दर्ज करें' : 'Please enter driving licence number');
      return;
    }
    if (!_digiLockerConsented) {
      _showError(isHi ? 'कृपया डिजीलॉकर सत्यापन सहमति स्वीकार करें' : 'Please accept DigiLocker verification consent');
      return;
    }
    if (_upiCtrl.text.trim().isEmpty) {
      _showError(isHi ? 'कृपया यूपीआई आईडी दर्ज करें' : 'Please enter UPI ID for payouts');
      return;
    }

    setState(() => _isSubmitting = true);

    final payload = {
      'full_name': _fullNameCtrl.text.trim(),
      'vehicle_type': _vehicleType,
      'vehicle_number': _bikeNoCtrl.text.trim().toUpperCase(),
      'driving_licence_no': _dlCtrl.text.trim().toUpperCase(),
      'upi_id': _upiCtrl.text.trim().toLowerCase(),
    };

    await state.onboardRunner(payload);

    if (!mounted) return;
    setState(() => _isSubmitting = false);

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => AlertDialog(
        icon: const Icon(Icons.check_circle_outline, color: GBColors.primary, size: 48),
        title: Text(
          isHi ? 'आवेदन सफलतापूर्वक जमा हुआ' : 'Application Submitted',
          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 17),
        ),
        content: Text(
          isHi
              ? 'आपका डिलीवरी साथी आवेदन सुपर एडमिन के पास समीक्षा के लिए जमा कर दिया गया है। अनुमोदन के बाद आप ड्यूटी ऑनलाइन कर सकेंगे।'
              : 'Your delivery partner application has been submitted to Super Admin for verification. You can go on duty once approved.',
          style: const TextStyle(fontSize: 13),
        ),
        actions: [
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: GBColors.primary),
            onPressed: () {
              Navigator.of(ctx).pop();
              Navigator.of(context).pushReplacement(
                MaterialPageRoute(builder: (_) => const RunnerDashboardScreen()),
              );
            },
            child: Text(isHi ? 'डैशबोर्ड पर जाएँ' : 'Go to Dashboard'),
          ),
        ],
      ),
    );
  }

  void _showError(String msg) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(msg), backgroundColor: GBColors.error),
    );
  }

  void _nextStep(RunnerAppState state) {
    if (_currentStep < 3) {
      setState(() => _currentStep++);
    } else {
      _submitApplication(state);
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = RunnerStateProvider.of(context);
    final isHi = state.isHindi;

    return Scaffold(
      appBar: AppBar(
        title: Text(
          isHi ? 'डिलीवरी साथी पंजीकरण' : 'Delivery Partner Registration',
          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
        ),
      ),
      body: SafeArea(
        child: Stepper(
          currentStep: _currentStep,
          onStepContinue: () => _nextStep(state),
          onStepCancel: () {
            if (_currentStep > 0) setState(() => _currentStep--);
          },
          controlsBuilder: (context, details) {
            return Padding(
              padding: const EdgeInsets.only(top: 20),
              child: Row(
                children: [
                  Expanded(
                    child: GBPrimaryButton(
                      label: _currentStep == 3
                          ? (isHi ? 'आवेदन जमा करें' : 'Submit Application')
                          : (isHi ? 'आगे बढ़ें' : 'Next Step'),
                      isLoading: _isSubmitting,
                      onPressed: details.onStepContinue,
                    ),
                  ),
                  if (_currentStep > 0) ...[
                    const SizedBox(width: 12),
                    OutlinedButton(
                      onPressed: details.onStepCancel,
                      child: Text(isHi ? 'पीछे' : 'Back'),
                    ),
                  ],
                ],
              ),
            );
          },
          steps: [
            // Step 1: Personal Details
            Step(
              title: Text(isHi ? 'व्यक्तिगत जानकारी' : 'Personal Details'),
              isActive: _currentStep >= 0,
              content: Column(
                children: [
                  TextFormField(
                    controller: _fullNameCtrl,
                    decoration: InputDecoration(
                      labelText: isHi ? 'पूरा नाम' : 'Full Name',
                      hintText: isHi ? 'उदा. संतोष कुमार' : 'e.g. Santosh Kumar',
                      border: const OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 14),
                  TextFormField(
                    controller: _phoneCtrl,
                    keyboardType: TextInputType.phone,
                    decoration: InputDecoration(
                      labelText: isHi ? 'मोबाइल नंबर' : 'Phone Number',
                      hintText: isHi ? 'उदा. 9876543210' : 'e.g. 9876543210',
                      prefixText: '+91 ',
                      border: const OutlineInputBorder(),
                    ),
                  ),
                ],
              ),
            ),

            // Step 2: Vehicle & Driving Licence
            Step(
              title: Text(isHi ? 'वाहन व ड्राइविंग लाइसेंस' : 'Vehicle & Licence'),
              isActive: _currentStep >= 1,
              content: Column(
                children: [
                  DropdownButtonFormField<String>(
                    value: _vehicleType,
                    decoration: InputDecoration(
                      labelText: isHi ? 'वाहन का प्रकार' : 'Vehicle Type',
                      border: const OutlineInputBorder(),
                    ),
                    items: [
                      DropdownMenuItem(
                        value: 'Motorcycle',
                        child: Text(isHi ? 'मोटरसाइकिल / बाइक' : 'Motorcycle / Bike'),
                      ),
                      DropdownMenuItem(
                        value: 'Bicycle',
                        child: Text(isHi ? 'साइकिल' : 'Bicycle'),
                      ),
                    ],
                    onChanged: (v) => setState(() => _vehicleType = v!),
                  ),
                  const SizedBox(height: 14),
                  TextFormField(
                    controller: _bikeNoCtrl,
                    decoration: InputDecoration(
                      labelText: isHi ? 'बाइक पंजीकरण संख्या' : 'Vehicle Registration Number',
                      hintText: isHi ? 'उदा. BR-06-AB-1234' : 'e.g. BR-06-AB-1234',
                      border: const OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 14),
                  TextFormField(
                    controller: _dlCtrl,
                    decoration: InputDecoration(
                      labelText: isHi ? 'ड्राइविंग लाइसेंस नंबर' : 'Driving Licence Number',
                      hintText: isHi ? 'उदा. DL-062024009876' : 'e.g. DL-062024009876',
                      border: const OutlineInputBorder(),
                    ),
                  ),
                ],
              ),
            ),

            // Step 3: Identity & DigiLocker
            Step(
              title: Text(isHi ? 'पहचान व डिजीलॉकर सत्यापन' : 'Identity Verification'),
              isActive: _currentStep >= 2,
              content: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: GBColors.primary.withValues(alpha: 0.08),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: GBColors.primary.withValues(alpha: 0.2)),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.verified_user_outlined, color: GBColors.primary, size: 28),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            isHi
                                ? 'सरकारी डिजीलॉकर द्वारा सुरक्षित एवं तुरंत दस्तावेज़ सत्यापन'
                                : 'Secure instant document verification via Government DigiLocker',
                            style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 12),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 12),
                  CheckboxListTile(
                    value: _digiLockerConsented,
                    activeColor: GBColors.primary,
                    contentPadding: EdgeInsets.zero,
                    title: Text(
                      isHi
                          ? 'मैं अपने ड्राइविंग लाइसेंस एवं आधार सत्यापन हेतु सहमति प्रदान करता हूँ।'
                          : 'I authorize verification of my driving licence and Aadhaar via DigiLocker.',
                      style: const TextStyle(fontSize: 13),
                    ),
                    onChanged: (v) => setState(() => _digiLockerConsented = v ?? false),
                  ),
                ],
              ),
            ),

            // Step 4: Payout Details
            Step(
              title: Text(isHi ? 'कमाई भुगतान खाता' : 'Earnings Payout Account'),
              isActive: _currentStep >= 3,
              content: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  TextFormField(
                    controller: _upiCtrl,
                    decoration: InputDecoration(
                      labelText: isHi ? 'यूपीआई आईडी' : 'UPI ID',
                      hintText: isHi ? 'उदा. आपकानाम@upi' : 'e.g. yourname@upi',
                      border: const OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 10),
                  Text(
                    isHi
                        ? 'प्रति डिलीवरी मिलने वाला शुल्क सीधे आपके बैंक / यूपीआई खाते में बिना किसी देरी के भेजा जाता है।'
                        : 'Your delivery fees are transferred directly to your bank account / UPI ID without delays.',
                    style: const TextStyle(fontSize: 12, color: Colors.grey),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
