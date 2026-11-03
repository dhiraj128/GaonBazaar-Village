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

  // Step 0: Personal Details
  final _fullNameCtrl = TextEditingController();
  final _phoneCtrl = TextEditingController();
  final _altPhoneCtrl = TextEditingController();

  // Step 1: Vehicle Selection
  String _vehicleType = 'Motorcycle';
  final List<String> _vehicleTypes = [
    'Motorcycle',
    'Scooter',
    'Bicycle',
    'Electric Cycle',
  ];

  // Step 2: Delivery Zone
  String _preferredVillage = 'Chaturshi / Chatursi';
  String _shiftTiming = 'पूर्ण दिवस (Full Day 8 AM - 8 PM)';
  List<Map<String, dynamic>> _pilotVillages = [
    {'name': 'Chaturshi / Chatursi', 'latitude': 26.2230, 'longitude': 85.3520},
    {'name': 'Tubanaghara / Benaghara', 'latitude': 26.2080, 'longitude': 85.3370},
    {'name': 'Sivay Patti', 'latitude': 26.2310, 'longitude': 85.3610},
    {'name': 'Tulsi Ganj / Bangaon', 'latitude': 26.1980, 'longitude': 85.3420},
  ];

  // Step 3: Identity Verification (Test Mode)
  final _aadhaarCtrl = TextEditingController();
  bool _digiLockerConsented = false;

  // Step 4: Vehicle Documents
  final _bikeNoCtrl = TextEditingController();
  final _dlCtrl = TextEditingController();

  // Step 5: Bank & Payout
  final _upiCtrl = TextEditingController();
  final _bankNameCtrl = TextEditingController();
  final _accountNoCtrl = TextEditingController();
  final _ifscCtrl = TextEditingController();

  // Step 6: Equipment Readiness
  bool _hasDeliveryBag = true;
  bool _hasSmartphone = true;
  bool _hasHelmetOrVest = true;

  // Step 7: Agreement
  bool _agreedToTerms = false;
  bool _agreedToCodRemittance = false;

  bool get _isMotorized => _vehicleType == 'Motorcycle' || _vehicleType == 'Scooter';

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      final state = RunnerStateProvider.of(context);
      if (state.currentUser != null) {
        _fullNameCtrl.text = state.currentUser!.name ?? '';
        _phoneCtrl.text = state.currentUser!.phone;
      }
      try {
        final res = await state.apiClient.getPilotLocalities();
        if (res.isSuccess && res.data != null && res.data!.isNotEmpty) {
          setState(() {
            _pilotVillages = res.data!;
            if (!_pilotVillages.any((v) => v['name'] == _preferredVillage)) {
              _preferredVillage = _pilotVillages.first['name'].toString();
            }
          });
        }
      } catch (_) {}
    });
  }

  @override
  void dispose() {
    _fullNameCtrl.dispose();
    _phoneCtrl.dispose();
    _altPhoneCtrl.dispose();
    _aadhaarCtrl.dispose();
    _bikeNoCtrl.dispose();
    _dlCtrl.dispose();
    _upiCtrl.dispose();
    _bankNameCtrl.dispose();
    _accountNoCtrl.dispose();
    _ifscCtrl.dispose();
    super.dispose();
  }

  void _showError(String msg) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(msg), backgroundColor: GBColors.error),
    );
  }

  void _nextStep(RunnerAppState state) async {
    final isHi = state.isHindi;

    // Step-by-step validations
    if (_currentStep == 0) {
      if (_fullNameCtrl.text.trim().isEmpty) {
        _showError(isHi ? 'कृपया अपना पूरा नाम दर्ज करें' : 'Please enter your full name');
        return;
      }
    } else if (_currentStep == 3) {
      if (!_digiLockerConsented) {
        _showError(isHi ? 'कृपया पहचान सत्यापन सहमति स्वीकार करें' : 'Please accept verification consent');
        return;
      }
    } else if (_currentStep == 4) {
      // Motorized partners must provide DL and Vehicle Reg No. Bicycle partners are EXEMPT!
      if (_isMotorized) {
        if (_bikeNoCtrl.text.trim().isEmpty) {
          _showError(isHi ? 'मोटरसाइकिल/स्कूटर हेतु वाहन पंजीकरण संख्या अनिवार्य है' : 'Vehicle registration number is required for motorcycle/scooter');
          return;
        }
        if (_dlCtrl.text.trim().isEmpty) {
          _showError(isHi ? 'मोटरसाइकिल/स्कूटर हेतु ड्राइविंग लाइसेंस संख्या अनिवार्य है' : 'Driving licence number is required for motorcycle/scooter');
          return;
        }
      }
    } else if (_currentStep == 5) {
      if (_upiCtrl.text.trim().isEmpty && _accountNoCtrl.text.trim().isEmpty) {
        _showError(isHi ? 'कृपया पेआउट हेतु यूपीआई आईडी या बैंक खाता संख्या दर्ज करें' : 'Please enter UPI ID or Bank account for payouts');
        return;
      }
    } else if (_currentStep == 6) {
      if (!_hasSmartphone || !_hasDeliveryBag) {
        _showError(isHi ? 'डिलीवरी हेतु स्मार्टफोन और डिलीवरी बैग आवश्यक है' : 'Smartphone and delivery bag are required');
        return;
      }
    } else if (_currentStep == 7) {
      if (!_agreedToTerms || !_agreedToCodRemittance) {
        _showError(isHi ? 'कृपया सभी सेवा शर्तों और सीओडी नियमों को स्वीकार करें' : 'Please accept all terms and COD remittance rules');
        return;
      }
    }

    if (_currentStep < 7) {
      setState(() => _currentStep++);
    } else {
      // Step 8: Submit Application to Backend
      setState(() => _isSubmitting = true);

      final payload = {
        'full_name': _fullNameCtrl.text.trim(),
        'vehicle_type': _vehicleType,
        'vehicle_number': _isMotorized
            ? _bikeNoCtrl.text.trim().toUpperCase()
            : 'BICYCLE-${_fullNameCtrl.text.trim().toUpperCase().replaceAll(' ', '')}',
        'driving_licence_no': _isMotorized ? _dlCtrl.text.trim().toUpperCase() : 'EXEMPT-BICYCLE',
        'upi_id': _upiCtrl.text.trim().isEmpty ? 'runner@upi' : _upiCtrl.text.trim().toLowerCase(),
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
            isHi ? 'आवेदन समीक्षाधीन (Pending Review)' : 'Application Under Review',
            style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 17),
          ),
          content: Text(
            isHi
                ? 'आपका 8-चरणीय डिलीवरी साथी आवेदन सुपर एडमिन के पास समीक्षा के लिए जमा कर दिया गया है। अनुमोदन के बाद आप ड्यूटी ऑनलाइन कर सकेंगे।'
                : 'Your 8-step delivery partner application has been submitted to Super Admin. Once approved, you can start accepting orders.',
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
  }

  @override
  Widget build(BuildContext context) {
    final state = RunnerStateProvider.of(context);
    final isHi = state.isHindi;

    return Scaffold(
      appBar: AppBar(
        title: Text(
          isHi ? 'डिलीवरी साथी पंजीकरण (8 चरण)' : 'Runner Onboarding (8 Steps)',
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
                      label: _currentStep == 7
                          ? (isHi ? 'आवेदन जमा करें (Submit)' : 'Submit Application')
                          : (isHi ? 'आगे बढ़ें (Next)' : 'Next Step'),
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
            // Step 0: Personal & Contact Information
            Step(
              title: Text(isHi ? '1. व्यक्तिगत जानकारी' : '1. Personal Info'),
              isActive: _currentStep >= 0,
              content: Column(
                children: [
                  TextField(
                    controller: _fullNameCtrl,
                    decoration: InputDecoration(
                      labelText: isHi ? 'पूरा नाम (आधार कार्ड के अनुसार) *' : 'Full Name (as per ID) *',
                      prefixIcon: const Icon(Icons.person_outline),
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _phoneCtrl,
                    keyboardType: TextInputType.phone,
                    decoration: InputDecoration(
                      labelText: isHi ? 'मोबाइल नंबर *' : 'Mobile Number *',
                      prefixIcon: const Icon(Icons.phone_android),
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _altPhoneCtrl,
                    keyboardType: TextInputType.phone,
                    decoration: InputDecoration(
                      labelText: isHi ? 'आपातकालीन संपर्क नंबर (वैकल्पिक)' : 'Emergency Contact Phone (Optional)',
                      prefixIcon: const Icon(Icons.contact_phone_outlined),
                    ),
                  ),
                ],
              ),
            ),

            // Step 1: Vehicle & Transport Selection
            Step(
              title: Text(isHi ? '2. वाहन प्रकार' : '2. Vehicle Selection'),
              isActive: _currentStep >= 1,
              content: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  DropdownButtonFormField<String>(
                    value: _vehicleType,
                    decoration: InputDecoration(
                      labelText: isHi ? 'डिलीवरी वाहन चुनें *' : 'Select Delivery Vehicle *',
                      prefixIcon: const Icon(Icons.two_wheeler),
                    ),
                    items: _vehicleTypes
                        .map((v) => DropdownMenuItem(
                              value: v,
                              child: Text(
                                v == 'Bicycle'
                                    ? (isHi ? 'साइकिल (Bicycle) — DL/RC की आवश्यकता नहीं' : 'Bicycle — No DL/RC needed')
                                    : v == 'Electric Cycle'
                                        ? (isHi ? 'इलेक्ट्रिक साइकिल (E-Cycle)' : 'Electric Cycle')
                                        : v,
                              ),
                            ))
                        .toList(),
                    onChanged: (v) => setState(() => _vehicleType = v!),
                  ),
                  const SizedBox(height: 10),
                  Text(
                    _isMotorized
                        ? (isHi
                            ? 'नोट: मोटरसाइकिल/स्कूटर हेतु वैध ड्राइविंग लाइसेंस अनिवार्य है।'
                            : 'Note: Valid Driving Licence is required for motorcycle/scooter.')
                        : (isHi
                            ? '✓ साइकिल/ई-साइकिल डिलीवरी हेतु ड्राइविंग लाइसेंस आवश्यक नहीं है।'
                            : '✓ Bicycle partners are exempt from DL and vehicle RC requirements.'),
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: _isMotorized ? Colors.blue.shade800 : Colors.green.shade800,
                    ),
                  ),
                ],
              ),
            ),

            // Step 2: Delivery Operating Zone
            Step(
              title: Text(isHi ? '3. कार्य क्षेत्र व शिफ्ट' : '3. Zone & Shift'),
              isActive: _currentStep >= 2,
              content: Column(
                children: [
                  DropdownButtonFormField<String>(
                    value: _preferredVillage,
                    decoration: InputDecoration(
                      labelText: isHi ? 'प्राथमिक गाँव / टोला चुनें *' : 'Primary Operating Village *',
                      prefixIcon: const Icon(Icons.map_outlined),
                    ),
                    items: _pilotVillages
                        .map((v) => DropdownMenuItem(
                              value: v['name'] as String,
                              child: Text(v['name'] as String),
                            ))
                        .toList(),
                    onChanged: (v) => setState(() => _preferredVillage = v!),
                  ),
                  const SizedBox(height: 12),
                  DropdownButtonFormField<String>(
                    value: _shiftTiming,
                    decoration: InputDecoration(
                      labelText: isHi ? 'पसंदीदा शिफ्ट समय' : 'Preferred Shift Timing',
                      prefixIcon: const Icon(Icons.access_time),
                    ),
                    items: const [
                      DropdownMenuItem(value: 'पूर्ण दिवस (Full Day 8 AM - 8 PM)', child: Text('8 AM - 8 PM (Full Day)')),
                      DropdownMenuItem(value: 'प्रातः शिफ्ट (Morning 7 AM - 1 PM)', child: Text('7 AM - 1 PM (Morning)')),
                      DropdownMenuItem(value: 'सायं शिफ्ट (Evening 3 PM - 9 PM)', child: Text('3 PM - 9 PM (Evening)')),
                    ],
                    onChanged: (v) => setState(() => _shiftTiming = v!),
                  ),
                ],
              ),
            ),

            // Step 3: Identity Verification (TEST MODE)
            Step(
              title: Text(isHi ? '4. डिजिटल पहचान (KYC)' : '4. Identity Verification'),
              isActive: _currentStep >= 3,
              content: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Test mode banner
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(12),
                    margin: const EdgeInsets.only(bottom: 14),
                    decoration: BoxDecoration(
                      color: Colors.amber.shade50,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.amber.shade400, width: 1.5),
                    ),
                    child: Row(
                      children: [
                        Icon(Icons.warning_amber_rounded, color: Colors.amber.shade900, size: 24),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                isHi
                                    ? 'परीक्षण मोड — वास्तविक पहचान सत्यापन नहीं है'
                                    : 'TEST MODE — NOT REAL IDENTITY VERIFICATION',
                                style: TextStyle(
                                  fontWeight: FontWeight.w800,
                                  fontSize: 12,
                                  color: Colors.amber.shade900,
                                ),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                isHi
                                    ? 'स्टेजिंग वातावरण में केवल अंतिम 4 अंक दर्ज किए जा सकते हैं।'
                                    : 'Staging environment simulation. Please do not submit real Aadhaar/DL documents.',
                                style: TextStyle(fontSize: 11, color: Colors.amber.shade900),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                  TextField(
                    controller: _aadhaarCtrl,
                    keyboardType: TextInputType.number,
                    maxLength: 4,
                    decoration: InputDecoration(
                      labelText: isHi ? 'आधार के अंतिम 4 अंक' : 'Aadhaar Last 4 Digits',
                      hintText: 'XXXX',
                      prefixIcon: const Icon(Icons.credit_card),
                    ),
                  ),
                  CheckboxListTile(
                    contentPadding: EdgeInsets.zero,
                    value: _digiLockerConsented,
                    onChanged: (v) => setState(() => _digiLockerConsented = v ?? false),
                    title: Text(
                      isHi
                          ? 'मैं डिजिटल पहचान सत्यापन और डिलीवरी साथी नियमों की सहमति देता/देती हूँ।'
                          : 'I consent to digital partner KYC verification and delivery conduct policies.',
                      style: const TextStyle(fontSize: 12),
                    ),
                    controlAffinity: ListTileControlAffinity.leading,
                  ),
                ],
              ),
            ),

            // Step 4: Vehicle Documents (Conditional)
            Step(
              title: Text(isHi ? '5. वाहन दस्तावेज़' : '5. Vehicle Documents'),
              isActive: _currentStep >= 4,
              content: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (!_isMotorized) ...[
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.green.shade50,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.green.shade300),
                      ),
                      child: Row(
                        children: [
                          Icon(Icons.pedal_bike, color: Colors.green.shade800, size: 28),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Text(
                              isHi
                                  ? 'साइकिल डिलीवरी साथी: किसी ड्राइविंग लाइसेंस या वाहन पंजीकरण की आवश्यकता नहीं है। आप सीधे ऑनबोर्ड हो सकते हैं!'
                                  : 'Bicycle Partner: No driving licence or vehicle registration required. You are ready to deliver!',
                              style: TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.w700,
                                color: Colors.green.shade900,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      decoration: InputDecoration(
                        labelText: isHi ? 'साइकिल का रंग / ब्रांड (वैकल्पिक)' : 'Bicycle Color / Brand (Optional)',
                        hintText: isHi ? 'उदा. हरा एटलस' : 'e.g. Green Hero',
                        prefixIcon: const Icon(Icons.pedal_bike_outlined),
                      ),
                    ),
                  ] else ...[
                    TextField(
                      controller: _bikeNoCtrl,
                      textCapitalization: TextCapitalization.characters,
                      decoration: InputDecoration(
                        labelText: isHi ? 'वाहन पंजीकरण संख्या (RC) *' : 'Vehicle Registration No. (RC) *',
                        hintText: 'BR-06-AB-1234',
                        prefixIcon: const Icon(Icons.pin_outlined),
                      ),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _dlCtrl,
                      textCapitalization: TextCapitalization.characters,
                      decoration: InputDecoration(
                        labelText: isHi ? 'ड्राइविंग लाइसेंस संख्या (DL) *' : 'Driving Licence Number (DL) *',
                        hintText: 'DL-0620240099881',
                        prefixIcon: const Icon(Icons.badge_outlined),
                      ),
                    ),
                  ],
                ],
              ),
            ),

            // Step 5: Bank Account & Payout Setup
            Step(
              title: Text(isHi ? '6. बैंक व पेआउट' : '6. Payout & Bank'),
              isActive: _currentStep >= 5,
              content: Column(
                children: [
                  TextField(
                    controller: _upiCtrl,
                    decoration: InputDecoration(
                      labelText: isHi ? 'यूपीआई आईडी (दैनिक पेआउट हेतु) *' : 'UPI ID (For daily payouts) *',
                      hintText: 'runner@oksbi',
                      prefixIcon: const Icon(Icons.account_balance_wallet_outlined),
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _bankNameCtrl,
                    decoration: InputDecoration(
                      labelText: isHi ? 'बैंक का नाम (वैकल्पिक)' : 'Bank Name (Optional)',
                      hintText: 'State Bank of India',
                      prefixIcon: const Icon(Icons.account_balance_outlined),
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _accountNoCtrl,
                    keyboardType: TextInputType.number,
                    decoration: InputDecoration(
                      labelText: isHi ? 'खाता संख्या (वैकल्पिक)' : 'Account Number (Optional)',
                      prefixIcon: const Icon(Icons.numbers_outlined),
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _ifscCtrl,
                    textCapitalization: TextCapitalization.characters,
                    decoration: InputDecoration(
                      labelText: isHi ? 'आईएफएससी कोड (IFSC)' : 'IFSC Code',
                      hintText: 'SBIN0001234',
                      prefixIcon: const Icon(Icons.code),
                    ),
                  ),
                ],
              ),
            ),

            // Step 6: Equipment Readiness
            Step(
              title: Text(isHi ? '7. डिलीवरी तैयारी' : '7. Equipment'),
              isActive: _currentStep >= 6,
              content: Column(
                children: [
                  CheckboxListTile(
                    contentPadding: EdgeInsets.zero,
                    value: _hasSmartphone,
                    onChanged: (v) => setState(() => _hasSmartphone = v ?? false),
                    title: Text(
                      isHi
                          ? 'मेरे पास 4G इंटरनेट और जीपीएस युक्त स्मार्टफोन है।'
                          : 'I have a 4G-enabled smartphone with GPS.',
                      style: const TextStyle(fontSize: 13),
                    ),
                    controlAffinity: ListTileControlAffinity.leading,
                  ),
                  CheckboxListTile(
                    contentPadding: EdgeInsets.zero,
                    value: _hasDeliveryBag,
                    onChanged: (v) => setState(() => _hasDeliveryBag = v ?? false),
                    title: Text(
                      isHi
                          ? 'मेरे पास सामान सुरक्षित ले जाने हेतु मजबूत डिलीवरी बैग/कैरियर है।'
                          : 'I have a sturdy bag or vehicle carrier to transport items safely.',
                      style: const TextStyle(fontSize: 13),
                    ),
                    controlAffinity: ListTileControlAffinity.leading,
                  ),
                  CheckboxListTile(
                    contentPadding: EdgeInsets.zero,
                    value: _hasHelmetOrVest,
                    onChanged: (v) => setState(() => _hasHelmetOrVest = v ?? false),
                    title: Text(
                      isHi
                          ? 'मैं सड़क सुरक्षा नियमों (हेलमेट / रिफ्लेक्टर) का पालन करूँगा।'
                          : 'I will comply with road safety rules (helmet/reflectors).',
                      style: const TextStyle(fontSize: 13),
                    ),
                    controlAffinity: ListTileControlAffinity.leading,
                  ),
                ],
              ),
            ),

            // Step 7: Agreement Review & Safety Pledge
            Step(
              title: Text(isHi ? '8. सेवा अनुबंध व नियम' : '8. Agreement & Pledge'),
              isActive: _currentStep >= 7,
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
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          isHi ? 'डिलीवरी साथी प्रतिज्ञा:' : 'Delivery Partner Code of Conduct:',
                          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 13, color: GBColors.primary),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          isHi
                              ? '• ग्राहक को सामान सौंपते समय 4-अंकीय ओटीपी पिन सत्यापित करना अनिवार्य है।\n• नकद (COD) ऑर्डर की राशि उसी दिन हब/सिस्टम में जमा करनी होगी।\n• पारदर्शी 5-स्तरीय दूरी पेआउट (₹10 - ₹28) प्रति डिलीवरी प्राप्त होगा।'
                              : '• Always verify the 4-digit OTP from customer upon handover.\n• Collect and remit COD cash accurately on the same working day.\n• Transparent 5-tier distance payouts (₹10 - ₹28) per completed job.',
                          style: const TextStyle(fontSize: 12, height: 1.4),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 12),
                  CheckboxListTile(
                    contentPadding: EdgeInsets.zero,
                    value: _agreedToCodRemittance,
                    onChanged: (v) => setState(() => _agreedToCodRemittance = v ?? false),
                    title: Text(
                      isHi
                          ? 'मैं ग्राहक से प्राप्त सीओडी नकद राशि की पूर्ण सुरक्षा और समय पर जमा करने की जिम्मेदारी लेता/लेती हूँ।'
                          : 'I accept full responsibility for safe collection and accurate remittance of COD payments.',
                      style: const TextStyle(fontSize: 12),
                    ),
                    controlAffinity: ListTileControlAffinity.leading,
                  ),
                  CheckboxListTile(
                    contentPadding: EdgeInsets.zero,
                    value: _agreedToTerms,
                    onChanged: (v) => setState(() => _agreedToTerms = v ?? false),
                    title: Text(
                      isHi
                          ? 'मैंने गाँव बाज़ार डिलीवरी साथी सेवा अनुबंध व नीतियों को स्वीकार किया है।'
                          : 'I agree to the GaonBazaar Delivery Partner Terms of Service.',
                      style: const TextStyle(fontSize: 12),
                    ),
                    controlAffinity: ListTileControlAffinity.leading,
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
