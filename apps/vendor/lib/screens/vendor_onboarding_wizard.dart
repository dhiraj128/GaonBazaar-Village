import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import '../state/vendor_state.dart';
import 'vendor_dashboard_screen.dart';

class VendorOnboardingWizard extends StatefulWidget {
  const VendorOnboardingWizard({super.key});

  @override
  State<VendorOnboardingWizard> createState() => _VendorOnboardingWizardState();
}

class _VendorOnboardingWizardState extends State<VendorOnboardingWizard> {
  int _currentStep = 0;
  bool _isSubmitting = false;

  // Step 0: Owner & Contact
  final _ownerNameCtrl = TextEditingController();
  final _phoneCtrl = TextEditingController();
  final _altPhoneCtrl = TextEditingController();

  // Step 1: Shop & Category
  final _shopNameCtrl = TextEditingController();
  final _tradeNameCtrl = TextEditingController();
  String _category = 'Grocery';

  // Step 2: Village & Location
  final _villageCtrl = TextEditingController(text: 'Chaturshi / Chatursi');
  final _landmarkCtrl = TextEditingController();
  final _blockCtrl = TextEditingController(text: 'Minapur');
  final _districtCtrl = TextEditingController(text: 'Muzaffarpur');

  // Step 3: Business Type
  String _businessType = 'Sole Proprietorship / एकल स्वामित्व';
  final _gstinCtrl = TextEditingController();
  final _fssaiCtrl = TextEditingController();

  // Step 4: Digital Verification / KYC (Test Mode)
  final _aadhaarCtrl = TextEditingController();
  final _panCtrl = TextEditingController();
  bool _digiLockerConsented = false;

  // Step 5: Bank & Payout
  final _bankNameCtrl = TextEditingController();
  final _accountNoCtrl = TextEditingController();
  final _ifscCtrl = TextEditingController();
  final _upiCtrl = TextEditingController();

  // Step 6: Operating Hours
  String _openingTime = '07:00 AM';
  String _closingTime = '09:00 PM';
  String _prepTime = '5-10 मिनट (Minutes)';
  final _handoverNotesCtrl = TextEditingController();

  // Step 7: Agreement
  bool _agreedToTerms = false;
  bool _agreedToAuthenticGoods = false;

  final List<String> _categories = [
    'Grocery',
    'Dairy',
    'Vegetables',
    'Electrical',
    'Pooja',
    'General',
  ];

  List<Map<String, dynamic>> _pilotVillages = [
    {'name': 'Chaturshi / Chatursi', 'latitude': 26.2230, 'longitude': 85.3520},
    {'name': 'Tubanaghara / Benaghara', 'latitude': 26.2080, 'longitude': 85.3370},
    {'name': 'Sivay Patti', 'latitude': 26.2310, 'longitude': 85.3610},
    {'name': 'Tulsi Ganj / Bangaon', 'latitude': 26.1980, 'longitude': 85.3420},
  ];

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      final state = VendorStateProvider.of(context);
      if (state.currentUser != null) {
        _ownerNameCtrl.text = state.currentUser!.name ?? '';
        _phoneCtrl.text = state.currentUser!.phone;
      }
      try {
        final res = await state.apiClient.getPilotLocalities();
        if (res.isSuccess && res.data != null && res.data!.isNotEmpty) {
          setState(() {
            _pilotVillages = res.data!;
            if (!_pilotVillages.any((v) => v['name'] == _villageCtrl.text)) {
              _villageCtrl.text = _pilotVillages.first['name'].toString();
            }
          });
        }
      } catch (_) {}
    });
  }

  @override
  void dispose() {
    _ownerNameCtrl.dispose();
    _phoneCtrl.dispose();
    _altPhoneCtrl.dispose();
    _shopNameCtrl.dispose();
    _tradeNameCtrl.dispose();
    _villageCtrl.dispose();
    _landmarkCtrl.dispose();
    _blockCtrl.dispose();
    _districtCtrl.dispose();
    _gstinCtrl.dispose();
    _fssaiCtrl.dispose();
    _aadhaarCtrl.dispose();
    _panCtrl.dispose();
    _bankNameCtrl.dispose();
    _accountNoCtrl.dispose();
    _ifscCtrl.dispose();
    _upiCtrl.dispose();
    _handoverNotesCtrl.dispose();
    super.dispose();
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: GBColors.error),
    );
  }

  void _nextStep() async {
    final state = VendorStateProvider.of(context);
    final isHi = state.isHindi;

    // Step-by-step validations
    if (_currentStep == 0) {
      if (_ownerNameCtrl.text.trim().isEmpty) {
        _showError(isHi ? 'कृपया दुकान मालिक का नाम दर्ज करें' : 'Please enter owner name');
        return;
      }
    } else if (_currentStep == 1) {
      if (_shopNameCtrl.text.trim().isEmpty) {
        _showError(isHi ? 'कृपया दुकान का नाम दर्ज करें' : 'Please enter shop name');
        return;
      }
    } else if (_currentStep == 2) {
      if (_villageCtrl.text.trim().isEmpty) {
        _showError(isHi ? 'कृपया गाँव चुनें' : 'Please select village');
        return;
      }
    } else if (_currentStep == 4) {
      if (!_digiLockerConsented) {
        _showError(isHi ? 'कृपया डिजीलॉकर सत्यापन सहमति स्वीकार करें' : 'Please accept verification consent');
        return;
      }
    } else if (_currentStep == 5) {
      if (_upiCtrl.text.trim().isEmpty && _accountNoCtrl.text.trim().isEmpty) {
        _showError(isHi ? 'कृपया भुगतान हेतु यूपीआई आईडी या बैंक खाता संख्या दर्ज करें' : 'Please enter UPI ID or Bank Account for payouts');
        return;
      }
    } else if (_currentStep == 7) {
      if (!_agreedToTerms || !_agreedToAuthenticGoods) {
        _showError(isHi ? 'कृपया सभी नियमों और घोषणाओं को स्वीकार करें' : 'Please accept all terms and declarations');
        return;
      }
    }

    if (_currentStep < 7) {
      setState(() => _currentStep++);
    } else {
      // Step 8: Submit to Backend
      setState(() => _isSubmitting = true);

      final selectedVillageObj = _pilotVillages.firstWhere(
        (v) => v['name'].toString().contains(_villageCtrl.text),
        orElse: () => _pilotVillages.first,
      );

      final payload = {
        'shop_name': _shopNameCtrl.text.trim(),
        'owner_name': _ownerNameCtrl.text.trim(),
        'category': _category,
        'latitude': (selectedVillageObj['latitude'] ?? selectedVillageObj['lat'] ?? 26.2230) as double,
        'longitude': (selectedVillageObj['longitude'] ?? selectedVillageObj['lng'] ?? 85.3520) as double,
        'village': _villageCtrl.text.trim(),
        'landmark': _landmarkCtrl.text.trim().isEmpty ? 'Near Panchayat Bhavan' : _landmarkCtrl.text.trim(),
        'block': _blockCtrl.text.trim(),
        'district': _districtCtrl.text.trim(),
        'upi_id': _upiCtrl.text.trim().isEmpty ? 'vendor@upi' : _upiCtrl.text.trim(),
        'banner_url': 'https://images.unsplash.com/photo-1542838132-92c53300491e?w=500',
      };

      await state.apiClient.onboardStore(payload);
      await state.fetchStoreProfile();

      if (!mounted) return;
      setState(() => _isSubmitting = false);

      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (ctx) => AlertDialog(
          icon: const Icon(Icons.verified_outlined, color: GBColors.primary, size: 48),
          title: Text(
            isHi ? 'आवेदन समीक्षाधीन (Pending Review)' : 'Application Under Review',
            style: const TextStyle(fontWeight: FontWeight.w800),
          ),
          content: Text(
            isHi
                ? 'आपकी दुकान का 8-चरणीय विवरण सफलतापूर्वक जमा हो गया है। सुपर एडमिन द्वारा सत्यापन के बाद आपकी दुकान 0% कमीशन पर ऑनलाइन हो जाएगी।'
                : 'Your 8-step store onboarding details have been submitted. Once verified by Super Admin, your shop will go live with 0% commission.',
          ),
          actions: [
            ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: GBColors.primary),
              onPressed: () {
                Navigator.of(ctx).pop();
                Navigator.of(context).pushReplacement(
                  MaterialPageRoute(builder: (_) => const VendorDashboardScreen()),
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
    final state = VendorStateProvider.of(context);
    final isHi = state.isHindi;

    return Scaffold(
      appBar: AppBar(
        title: Text(
          isHi ? 'दुकानदार पंजीकरण (8 चरण)' : 'Store Onboarding (8 Steps)',
          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
        ),
      ),
      body: SafeArea(
        child: Stepper(
          currentStep: _currentStep,
          onStepContinue: _isSubmitting ? null : _nextStep,
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
            // Step 0: Owner & Contact Information
            Step(
              title: Text(isHi ? '1. मालिक व संपर्क' : '1. Owner & Contact'),
              isActive: _currentStep >= 0,
              content: Column(
                children: [
                  TextField(
                    controller: _ownerNameCtrl,
                    decoration: InputDecoration(
                      labelText: isHi ? 'मालिक का पूरा नाम *' : 'Owner Full Name *',
                      prefixIcon: const Icon(Icons.person_outline),
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _phoneCtrl,
                    keyboardType: TextInputType.phone,
                    decoration: InputDecoration(
                      labelText: isHi ? 'मोबाइल नंबर *' : 'Primary Mobile Number *',
                      prefixIcon: const Icon(Icons.phone_android),
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _altPhoneCtrl,
                    keyboardType: TextInputType.phone,
                    decoration: InputDecoration(
                      labelText: isHi ? 'वैकल्पिक संपर्क नंबर (वैकल्पिक)' : 'Alternate Contact Number (Optional)',
                      prefixIcon: const Icon(Icons.phone_outlined),
                    ),
                  ),
                ],
              ),
            ),

            // Step 1: Shop Information & Category
            Step(
              title: Text(isHi ? '2. दुकान की जानकारी' : '2. Shop & Category'),
              isActive: _currentStep >= 1,
              content: Column(
                children: [
                  TextField(
                    controller: _shopNameCtrl,
                    decoration: InputDecoration(
                      labelText: isHi ? 'दुकान का नाम *' : 'Shop Name *',
                      prefixIcon: const Icon(Icons.storefront),
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _tradeNameCtrl,
                    decoration: InputDecoration(
                      labelText: isHi ? 'बोर्ड पर लिखा नाम / Trade Name' : 'Trade Name / Board Name',
                      prefixIcon: const Icon(Icons.badge_outlined),
                    ),
                  ),
                  const SizedBox(height: 12),
                  DropdownButtonFormField<String>(
                    value: _category,
                    decoration: InputDecoration(
                      labelText: isHi ? 'दुकान की श्रेणी *' : 'Store Category *',
                      prefixIcon: const Icon(Icons.category_outlined),
                    ),
                    items: _categories.map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),
                    onChanged: (v) => setState(() => _category = v!),
                  ),
                ],
              ),
            ),

            // Step 2: Operating Village & GPS Location
            Step(
              title: Text(isHi ? '3. गाँव व स्थान' : '3. Village & Location'),
              isActive: _currentStep >= 2,
              content: Column(
                children: [
                  DropdownButtonFormField<String>(
                    value: _pilotVillages.any((v) => v['name'] == _villageCtrl.text)
                        ? _villageCtrl.text
                        : _pilotVillages.first['name'].toString(),
                    decoration: InputDecoration(
                      labelText: isHi ? 'पायलट गाँव / टोला चुनें *' : 'Select Pilot Village / Locality *',
                      prefixIcon: const Icon(Icons.location_city_outlined),
                    ),
                    items: _pilotVillages
                        .map((v) => DropdownMenuItem(
                              value: v['name'] as String,
                              child: Text(v['name'] as String),
                            ))
                        .toList(),
                    onChanged: (v) => setState(() => _villageCtrl.text = v!),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _landmarkCtrl,
                    decoration: InputDecoration(
                      labelText: isHi ? 'प्रमुख लैंडमार्क (उदा. पंचायत भवन)' : 'Prominent Landmark (e.g. Near Shiv Mandir)',
                      prefixIcon: const Icon(Icons.pin_drop_outlined),
                    ),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _blockCtrl,
                          decoration: InputDecoration(
                            labelText: isHi ? 'प्रखंड (Block)' : 'Block',
                            enabled: false,
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: TextField(
                          controller: _districtCtrl,
                          decoration: InputDecoration(
                            labelText: isHi ? 'ज़िला (District)' : 'District',
                            enabled: false,
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            // Step 3: Business Type & Registration
            Step(
              title: Text(isHi ? '4. व्यवसाय प्रकार' : '4. Business Type'),
              isActive: _currentStep >= 3,
              content: Column(
                children: [
                  DropdownButtonFormField<String>(
                    value: _businessType,
                    decoration: InputDecoration(
                      labelText: isHi ? 'व्यवसाय का स्वरूप *' : 'Business Structure *',
                      prefixIcon: const Icon(Icons.business_outlined),
                    ),
                    items: const [
                      DropdownMenuItem(
                        value: 'Sole Proprietorship / एकल स्वामित्व',
                        child: Text('एकल स्वामित्व (Sole Proprietorship)'),
                      ),
                      DropdownMenuItem(
                        value: 'Partnership / साझेदारी',
                        child: Text('साझेदारी (Partnership)'),
                      ),
                      DropdownMenuItem(
                        value: 'Rural Kirana / ग्रामीण किराना',
                        child: Text('ग्रामीण किराना (Rural Kirana)'),
                      ),
                    ],
                    onChanged: (v) => setState(() => _businessType = v!),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _gstinCtrl,
                    textCapitalization: TextCapitalization.characters,
                    decoration: InputDecoration(
                      labelText: isHi ? 'जीएसटीआईएन (वैकल्पिक)' : 'GSTIN (Optional)',
                      prefixIcon: const Icon(Icons.receipt_outlined),
                      hintText: '22AAAAA0000A1Z5',
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _fssaiCtrl,
                    keyboardType: TextInputType.number,
                    decoration: InputDecoration(
                      labelText: isHi ? 'एफएसएसएआई लाइसेंस / पंजीकरण (वैकल्पिक)' : 'FSSAI License / Reg. (Optional)',
                      prefixIcon: const Icon(Icons.verified_outlined),
                    ),
                  ),
                ],
              ),
            ),

            // Step 4: Digital Verification / KYC (TEST MODE)
            Step(
              title: Text(isHi ? '5. डिजिटल सत्यापन (KYC)' : '5. Digital Verification (KYC)'),
              isActive: _currentStep >= 4,
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
                                    : 'Staging environment simulation. Please do not submit real Aadhaar/PAN documents.',
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
                  const SizedBox(height: 12),
                  TextField(
                    controller: _panCtrl,
                    textCapitalization: TextCapitalization.characters,
                    maxLength: 10,
                    decoration: InputDecoration(
                      labelText: isHi ? 'पैन कार्ड नंबर (वैकल्पिक)' : 'PAN Card Number (Optional)',
                      hintText: 'ABCDE1234F',
                      prefixIcon: const Icon(Icons.assignment_ind_outlined),
                    ),
                  ),
                  CheckboxListTile(
                    contentPadding: EdgeInsets.zero,
                    value: _digiLockerConsented,
                    onChanged: (v) => setState(() => _digiLockerConsented = v ?? false),
                    title: Text(
                      isHi
                          ? 'मैं डिजिटल केवाईसी सत्यापन और व्यावसायिक नियमों के अनुपालन की सहमति देता/देती हूँ।'
                          : 'I consent to digital KYC verification and commercial policy compliance.',
                      style: const TextStyle(fontSize: 12),
                    ),
                    controlAffinity: ListTileControlAffinity.leading,
                  ),
                ],
              ),
            ),

            // Step 5: Bank Account & Payout Setup
            Step(
              title: Text(isHi ? '6. बैंक खाता व पेआउट' : '6. Bank & Payout Setup'),
              isActive: _currentStep >= 5,
              content: Column(
                children: [
                  TextField(
                    controller: _upiCtrl,
                    decoration: InputDecoration(
                      labelText: isHi ? 'यूपीआई आईडी (त्वरित 0% सेटलमेंट हेतु) *' : 'UPI ID (For instant 0% settlement) *',
                      hintText: 'sharma@oksbi',
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

            // Step 6: Operating Hours & Handover
            Step(
              title: Text(isHi ? '7. दुकान समय व तैयारी' : '7. Hours & Prep Time'),
              isActive: _currentStep >= 6,
              content: Column(
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: DropdownButtonFormField<String>(
                          value: _openingTime,
                          decoration: InputDecoration(
                            labelText: isHi ? 'खुलने का समय' : 'Opening Time',
                          ),
                          items: const [
                            DropdownMenuItem(value: '06:00 AM', child: Text('06:00 AM')),
                            DropdownMenuItem(value: '07:00 AM', child: Text('07:00 AM')),
                            DropdownMenuItem(value: '08:00 AM', child: Text('08:00 AM')),
                          ],
                          onChanged: (v) => setState(() => _openingTime = v!),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: DropdownButtonFormField<String>(
                          value: _closingTime,
                          decoration: InputDecoration(
                            labelText: isHi ? 'बंद होने का समय' : 'Closing Time',
                          ),
                          items: const [
                            DropdownMenuItem(value: '08:00 PM', child: Text('08:00 PM')),
                            DropdownMenuItem(value: '09:00 PM', child: Text('09:00 PM')),
                            DropdownMenuItem(value: '10:00 PM', child: Text('10:00 PM')),
                          ],
                          onChanged: (v) => setState(() => _closingTime = v!),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  DropdownButtonFormField<String>(
                    value: _prepTime,
                    decoration: InputDecoration(
                      labelText: isHi ? 'ऑर्डर पैकिंग समय (Prep Time)' : 'Order Preparation Time',
                      prefixIcon: const Icon(Icons.timer_outlined),
                    ),
                    items: const [
                      DropdownMenuItem(value: '5-10 मिनट (Minutes)', child: Text('5-10 Min')),
                      DropdownMenuItem(value: '10-15 मिनट (Minutes)', child: Text('10-15 Min')),
                    ],
                    onChanged: (v) => setState(() => _prepTime = v!),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _handoverNotesCtrl,
                    decoration: InputDecoration(
                      labelText: isHi ? 'डिलीवरी रनर हेतु निर्देश' : 'Runner Handover Instructions',
                      hintText: isHi ? 'काउंटर नंबर 1 से पैकेट उठाएं' : 'Pick packed orders at counter 1',
                      prefixIcon: const Icon(Icons.notes_outlined),
                    ),
                  ),
                ],
              ),
            ),

            // Step 7: Agreement Review & Verification
            Step(
              title: Text(isHi ? '8. समीक्षा व सहमति' : '8. Agreement & Submit'),
              isActive: _currentStep >= 7,
              content: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: GBColors.primary.withOpacity(0.08),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: GBColors.primary.withOpacity(0.2)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          isHi ? 'दुकानदार नीति प्रतिज्ञा:' : 'Shopkeeper Partner Pledge:',
                          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 13, color: GBColors.primary),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          isHi
                              ? '• गाँव बाज़ार प्लेटफ़ॉर्म 0% कमीशन मॉडल पर कार्य करता है।\n• केवल ताज़ा और शुद्ध सामग्री ग्राहकों को आपूर्ति की जाएगी।\n• ऑर्डर प्राप्त होने पर 10 मिनट में पैकिंग अनिवार्य है।'
                              : '• GaonBazaar operates on a 0% commission marketplace policy.\n• Only authentic, fresh and unadulterated products will be supplied.\n• Packing completed within 10 minutes of acceptance.',
                          style: const TextStyle(fontSize: 12, height: 1.4),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 12),
                  CheckboxListTile(
                    contentPadding: EdgeInsets.zero,
                    value: _agreedToAuthenticGoods,
                    onChanged: (v) => setState(() => _agreedToAuthenticGoods = v ?? false),
                    title: Text(
                      isHi
                          ? 'मैं प्रमाणित करता/करती हूँ कि मेरी दुकान के सभी उत्पाद उच्च गुणवत्ता और उचित मूल्य के हैं।'
                          : 'I declare that all products listed from my shop are of genuine quality and fair pricing.',
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
                          ? 'मैंने गाँव बाज़ार की विक्रेता नीति और नियमों को पढ़ लिया है और स्वीकार करता/करती हूँ।'
                          : 'I have read and agree to the GaonBazaar Vendor Terms & Conditions.',
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
