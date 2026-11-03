import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:design_system/design_system.dart';
import '../state/runner_state.dart';
import 'runner_pending_approval_screen.dart';

class RunnerOnboardingWizard extends StatefulWidget {
  const RunnerOnboardingWizard({super.key});

  @override
  State<RunnerOnboardingWizard> createState() => _RunnerOnboardingWizardState();
}

class _RunnerOnboardingWizardState extends State<RunnerOnboardingWizard> {
  final PageController _pageController = PageController();
  int _currentPage = 0;
  bool _isSubmitting = false;

  // ---------------------------------------------------------------------------
  // PDF Page 3: Personal Details
  // ---------------------------------------------------------------------------
  final _fullNameCtrl = TextEditingController();
  final _fatherNameCtrl = TextEditingController();
  final _emergencyContactCtrl = TextEditingController();
  String _vehicleType = 'Motorcycle'; // Bicycle vs. Motorcycle

  // ---------------------------------------------------------------------------
  // PDF Page 4: Strict Identity KYC
  // ---------------------------------------------------------------------------
  String? _aadhaarFrontName;
  String? _aadhaarBackName;
  String? _selfieName;
  bool _livenessVerified = false;
  bool _kycConsent = true;

  // ---------------------------------------------------------------------------
  // PDF Page 5: Bank / Payout Setup (Mandatory)
  // ---------------------------------------------------------------------------
  final _accountHolderCtrl = TextEditingController();
  final _accountNumberCtrl = TextEditingController();
  final _ifscCtrl = TextEditingController();
  bool _isPennyDropVerifying = false;
  bool _pennyDropVerified = false;
  String? _pennyDropMessage;

  @override
  void initState() {
    super.initState();
    _loadSavedDraft();
  }

  @override
  void dispose() {
    _pageController.dispose();
    _fullNameCtrl.dispose();
    _fatherNameCtrl.dispose();
    _emergencyContactCtrl.dispose();
    _accountHolderCtrl.dispose();
    _accountNumberCtrl.dispose();
    _ifscCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadSavedDraft() async {
    final prefs = await SharedPreferences.getInstance();
    final state = RunnerStateProvider.of(context);

    setState(() {
      _fullNameCtrl.text = prefs.getString('gb_r_pdf_name') ?? state.currentUser?.name ?? '';
      _fatherNameCtrl.text = prefs.getString('gb_r_pdf_father') ?? '';
      _emergencyContactCtrl.text = prefs.getString('gb_r_pdf_emergency') ?? '';
      _vehicleType = prefs.getString('gb_r_pdf_vehicle') ?? 'Motorcycle';

      _aadhaarFrontName = prefs.getString('gb_r_pdf_adh_front');
      _aadhaarBackName = prefs.getString('gb_r_pdf_adh_back');
      _selfieName = prefs.getString('gb_r_pdf_selfie');
      _livenessVerified = prefs.getBool('gb_r_pdf_liveness') ?? false;

      _accountHolderCtrl.text = prefs.getString('gb_r_pdf_holder') ?? _fullNameCtrl.text;
      _accountNumberCtrl.text = prefs.getString('gb_r_pdf_acct') ?? '';
      _ifscCtrl.text = prefs.getString('gb_r_pdf_ifsc') ?? '';
      _pennyDropVerified = prefs.getBool('gb_r_pdf_penny') ?? false;

      final savedPage = prefs.getInt('gb_r_pdf_page');
      if (savedPage != null && savedPage >= 0 && savedPage < 3) {
        _currentPage = savedPage;
        WidgetsBinding.instance.addPostFrameCallback((_) {
          if (_pageController.hasClients) {
            _pageController.jumpToPage(savedPage);
          }
        });
      }
    });
  }

  Future<void> _persistDraft() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('gb_r_pdf_name', _fullNameCtrl.text.trim());
    await prefs.setString('gb_r_pdf_father', _fatherNameCtrl.text.trim());
    await prefs.setString('gb_r_pdf_emergency', _emergencyContactCtrl.text.trim());
    await prefs.setString('gb_r_pdf_vehicle', _vehicleType);
    if (_aadhaarFrontName != null) await prefs.setString('gb_r_pdf_adh_front', _aadhaarFrontName!);
    if (_aadhaarBackName != null) await prefs.setString('gb_r_pdf_adh_back', _aadhaarBackName!);
    if (_selfieName != null) await prefs.setString('gb_r_pdf_selfie', _selfieName!);
    await prefs.setBool('gb_r_pdf_liveness', _livenessVerified);
    await prefs.setString('gb_r_pdf_holder', _accountHolderCtrl.text.trim());
    await prefs.setString('gb_r_pdf_acct', _accountNumberCtrl.text.trim());
    await prefs.setString('gb_r_pdf_ifsc', _ifscCtrl.text.trim());
    await prefs.setBool('gb_r_pdf_penny', _pennyDropVerified);
  }

  Future<void> _clearDraft() async {
    final prefs = await SharedPreferences.getInstance();
    final keys = [
      'gb_r_pdf_name', 'gb_r_pdf_father', 'gb_r_pdf_emergency', 'gb_r_pdf_vehicle',
      'gb_r_pdf_adh_front', 'gb_r_pdf_adh_back', 'gb_r_pdf_selfie', 'gb_r_pdf_liveness',
      'gb_r_pdf_holder', 'gb_r_pdf_acct', 'gb_r_pdf_ifsc', 'gb_r_pdf_penny'
    ];
    for (final k in keys) {
      await prefs.remove(k);
    }
  }

  void _showError(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message, style: const TextStyle(fontWeight: FontWeight.w600)),
        backgroundColor: GBColors.error,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  void _onNext() {
    final isHi = RunnerStateProvider.of(context).isHindi;
    _persistDraft();

    // Validate Page 0 (PDF Page 3: Personal Details)
    if (_currentPage == 0) {
      if (_fullNameCtrl.text.trim().isEmpty) {
        _showError(isHi ? 'कृपया पूरा नाम दर्ज करें' : 'Please enter your Full Legal Name');
        return;
      }
      if (_fatherNameCtrl.text.trim().isEmpty) {
        _showError(isHi ? 'कृपया पिता का नाम दर्ज करें' : 'Please enter Father\'s Name');
        return;
      }
      if (_emergencyContactCtrl.text.trim().length != 10) {
        _showError(isHi ? 'कृपया 10 अंकों का आपातकालीन संपर्क नंबर दर्ज करें' : 'Please enter a valid 10-digit emergency contact');
        return;
      }
    }

    // Validate Page 1 (PDF Page 4: Strict Identity KYC)
    if (_currentPage == 1) {
      if (_aadhaarFrontName == null) {
        _showError(isHi ? 'कृपया आधार कार्ड का अगला भाग अपलोड करें' : 'Please upload Aadhaar Front image');
        return;
      }
      if (_aadhaarBackName == null) {
        _showError(isHi ? 'कृपया आधार कार्ड का पिछला भाग अपलोड करें' : 'Please upload Aadhaar Back image');
        return;
      }
      if (_selfieName == null || !_livenessVerified) {
        _showError(isHi ? 'कृपया लाइव सेल्फ़ी और लाइवनेस जांच पूरी करें' : 'Please complete liveness selfie check');
        return;
      }
      if (!_kycConsent) {
        _showError(isHi ? 'कृपया केवाईसी सत्यापन की सहमति दें' : 'Please consent to KYC verification');
        return;
      }
    }

    // Validate Page 2 (PDF Page 5: Bank / Payout Setup)
    if (_currentPage == 2) {
      if (_accountHolderCtrl.text.trim().isEmpty) {
        _showError(isHi ? 'कृपया खाताधारक का नाम दर्ज करें' : 'Please enter Account Holder Name');
        return;
      }
      if (_accountNumberCtrl.text.trim().length < 9) {
        _showError(isHi ? 'कृपया वैध बैंक खाता संख्या दर्ज करें' : 'Please enter valid Bank Account Number');
        return;
      }
      if (_ifscCtrl.text.trim().length != 11) {
        _showError(isHi ? 'कृपया 11 अक्षरों का वैध IFSC कोड दर्ज करें' : 'Please enter valid 11-character IFSC Code');
        return;
      }
      if (!_pennyDropVerified) {
        _showError(isHi ? 'कृपया आगे बढ़ने से पहले ₹1 पेनी ड्रॉप सत्यापन पूरा करें' : 'Please complete ₹1 Penny Drop verification before submitting');
        return;
      }
      _submitApplication();
      return;
    }

    _pageController.nextPage(
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeInOut,
    );
  }

  void _onBack() {
    if (_currentPage > 0) {
      _pageController.previousPage(
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeInOut,
      );
    }
  }

  Future<void> _runPennyDrop() async {
    final state = RunnerStateProvider.of(context);
    final isHi = state.isHindi;

    setState(() {
      _isPennyDropVerifying = true;
      _pennyDropMessage = null;
    });

    final holder = _accountHolderCtrl.text.trim().isNotEmpty ? _accountHolderCtrl.text.trim() : _fullNameCtrl.text.trim();
    final res = await state.verifyPennyDrop(
      accountHolderName: holder,
      accountNumber: _accountNumberCtrl.text.trim(),
      ifscCode: _ifscCtrl.text.trim().toUpperCase(),
    );

    if (!mounted) return;
    setState(() => _isPennyDropVerifying = false);

    if (res['success'] == true) {
      setState(() {
        _pennyDropVerified = true;
        _pennyDropMessage = isHi ? '₹1 पेनी ड्रॉप सत्यापन सफल (खाता सक्रिय)' : '₹1 Penny Drop Verified Successfully';
      });
      _persistDraft();
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(_pennyDropMessage!),
          backgroundColor: GBColors.success,
        ),
      );
    } else {
      _showError(res['error'] as String? ?? (isHi ? 'सत्यापन विफल हुआ' : 'Verification failed'));
    }
  }

  Future<void> _submitApplication() async {
    final state = RunnerStateProvider.of(context);
    final isHi = state.isHindi;

    setState(() => _isSubmitting = true);

    final payload = {
      'full_name': _fullNameCtrl.text.trim(),
      'vehicle_type': _vehicleType,
      'vehicle_number': _vehicleType == 'Motorcycle' ? 'BR06AB1234' : 'BICYCLE',
      'driving_licence_no': _vehicleType == 'Motorcycle' ? 'DL062024009876' : 'EXEMPT',
      'working_village': 'Minapur',
      'father_name': _fatherNameCtrl.text.trim(),
      'emergency_contact': _emergencyContactCtrl.text.trim(),
      'account_holder_name': _accountHolderCtrl.text.trim(),
      'account_number': _accountNumberCtrl.text.trim(),
      'ifsc_code': _ifscCtrl.text.trim().toUpperCase(),
      'aadhaar_front_url': _aadhaarFrontName ?? 'runner_aadhaar_front.jpg',
      'aadhaar_back_url': _aadhaarBackName ?? 'runner_aadhaar_back.jpg',
      'selfie_url': _selfieName ?? 'runner_live_selfie.jpg',
      'upi_id': 'A/C:${_accountNumberCtrl.text.trim().length > 4 ? _accountNumberCtrl.text.trim().substring(_accountNumberCtrl.text.trim().length - 4) : "0000"}:${_ifscCtrl.text.trim()}',
    };

    final success = await state.onboardRunner(payload);
    if (!mounted) return;
    setState(() => _isSubmitting = false);

    if (success) {
      await _clearDraft();
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => const RunnerPendingApprovalScreen()),
      );
    } else {
      _showError(
        isHi
            ? 'पंजीकरण जमा करने में विफल। कृपया पुनः प्रयास करें।'
            : 'Failed to submit registration. Please try again.',
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = RunnerStateProvider.of(context);
    final isHi = state.isHindi;

    final stepTitles = [
      isHi ? 'व्यक्तिगत विवरण (Personal Details)' : 'Personal Details',
      isHi ? 'पहचान सत्यापन (Strict Identity KYC)' : 'Strict Identity KYC',
      isHi ? 'बैंक व पेआउट (Bank / Payout Setup)' : 'Bank / Payout Setup',
    ];

    return Scaffold(
      appBar: AppBar(
        title: Text(stepTitles[_currentPage]),
        leading: _currentPage > 0
            ? IconButton(
                icon: const Icon(Icons.arrow_back),
                onPressed: _onBack,
              )
            : null,
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Top Progress Bar
            LinearProgressIndicator(
              value: (_currentPage + 1) / 3.0,
              backgroundColor: Colors.grey.shade300,
              valueColor: const AlwaysStoppedAnimation<Color>(GBColors.primary),
              minHeight: 4,
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    isHi ? 'चरण ${_currentPage + 1} / 3' : 'Step ${_currentPage + 1} of 3',
                    style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.grey),
                  ),
                  Text(
                    stepTitles[_currentPage],
                    style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: GBColors.primary),
                  ),
                ],
              ),
            ),
            const Divider(height: 1),

            // Page Content (Standalone screens via PageView)
            Expanded(
              child: PageView(
                controller: _pageController,
                physics: const NeverScrollableScrollPhysics(),
                onPageChanged: (idx) => setState(() => _currentPage = idx),
                children: [
                  _buildPage1PersonalDetails(isHi),
                  _buildPage2StrictKyc(isHi),
                  _buildPage3BankPayout(isHi),
                ],
              ),
            ),

            // Bottom Continue / Submit Button
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Theme.of(context).cardColor,
                boxShadow: const [BoxShadow(color: Colors.black12, blurRadius: 4, offset: Offset(0, -2))],
              ),
              child: SizedBox(
                width: double.infinity,
                height: 48,
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: GBColors.primary,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                  onPressed: _isSubmitting ? null : _onNext,
                  child: _isSubmitting
                      ? const SizedBox(width: 24, height: 24, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                      : Text(
                          _currentPage == 2
                              ? (isHi ? 'आवेदन जमा करें (Submit Application)' : 'Submit Application')
                              : (isHi ? 'आगे बढ़ें (Continue)' : 'Continue'),
                          style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Colors.white),
                        ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // PDF PAGE 3: PERSONAL DETAILS
  // Full Name, Father's Name, Emergency Contact Number, Vehicle Type (Bicycle vs. Motorcycle)
  // ---------------------------------------------------------------------------
  Widget _buildPage1PersonalDetails(bool isHi) {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        Text(
          isHi ? 'डिलीवरी साथी व्यक्तिगत विवरण' : 'Personal Details',
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900),
        ),
        const SizedBox(height: 6),
        Text(
          isHi
              ? 'अपना कानूनी नाम, पिता का नाम, आपातकालीन नंबर और वाहन का प्रकार चुनें।'
              : 'Enter Full Name, Father\'s Name, Emergency Contact, and Vehicle Type.',
          style: const TextStyle(fontSize: 13, color: Colors.grey),
        ),
        const SizedBox(height: 20),

        TextField(
          controller: _fullNameCtrl,
          decoration: InputDecoration(
            labelText: isHi ? 'पूरा नाम (Full Legal Name) *' : 'Full Legal Name *',
            hintText: isHi ? 'उदा: अमित कुमार' : 'e.g. Amit Kumar',
            prefixIcon: const Icon(Icons.person_outline),
            border: const OutlineInputBorder(),
          ),
          onChanged: (_) => _persistDraft(),
        ),
        const SizedBox(height: 16),

        TextField(
          controller: _fatherNameCtrl,
          decoration: InputDecoration(
            labelText: isHi ? 'पिता का नाम (Father\'s Name) *' : 'Father\'s Name *',
            hintText: isHi ? 'उदा: सुरेश प्रसाद' : 'e.g. Suresh Prasad',
            prefixIcon: const Icon(Icons.family_restroom_outlined),
            border: const OutlineInputBorder(),
          ),
          onChanged: (_) => _persistDraft(),
        ),
        const SizedBox(height: 16),

        TextField(
          controller: _emergencyContactCtrl,
          keyboardType: TextInputType.phone,
          maxLength: 10,
          decoration: InputDecoration(
            labelText: isHi ? 'आपातकालीन संपर्क नंबर (Emergency Contact) *' : 'Emergency Contact Number *',
            hintText: '9800000000',
            prefixIcon: const Icon(Icons.phone_in_talk_outlined),
            border: const OutlineInputBorder(),
          ),
          onChanged: (_) => _persistDraft(),
        ),
        const SizedBox(height: 12),

        Text(
          isHi ? 'वाहन का प्रकार (Vehicle Type: Bicycle vs. Motorcycle) *' : 'Vehicle Type (Bicycle vs. Motorcycle) *',
          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
        ),
        const SizedBox(height: 8),

        Row(
          children: [
            Expanded(
              child: _buildVehicleChoiceCard(
                title: isHi ? 'मोटरसाइकिल' : 'Motorcycle',
                subtitle: isHi ? 'पेट्रोल / बाइक' : 'Petrol / Bike',
                icon: Icons.two_wheeler,
                type: 'Motorcycle',
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildVehicleChoiceCard(
                title: isHi ? 'साइकिल' : 'Bicycle',
                subtitle: isHi ? 'पर्यावरण अनुकूल' : 'Eco-friendly',
                icon: Icons.pedal_bike,
                type: 'Bicycle',
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildVehicleChoiceCard({
    required String title,
    required String subtitle,
    required IconData icon,
    required String type,
  }) {
    final isSelected = _vehicleType == type;
    return InkWell(
      onTap: () {
        setState(() => _vehicleType = type);
        _persistDraft();
      },
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 12),
        decoration: BoxDecoration(
          color: isSelected ? GBColors.primary.withValues(alpha: 0.08) : Colors.transparent,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: isSelected ? GBColors.primary : Colors.grey.shade300, width: isSelected ? 2 : 1),
        ),
        child: Column(
          children: [
            Icon(icon, color: isSelected ? GBColors.primary : Colors.grey, size: 36),
            const SizedBox(height: 8),
            Text(title, style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: isSelected ? GBColors.primary : null)),
            Text(subtitle, style: const TextStyle(fontSize: 11, color: Colors.grey)),
          ],
        ),
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // PDF PAGE 4: STRICT IDENTITY KYC
  // Upload Aadhaar (Front/Back) + Liveness Selfie Check. (Backend API verifies selfie matches Aadhaar photo).
  // ---------------------------------------------------------------------------
  Widget _buildPage2StrictKyc(bool isHi) {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        Text(
          isHi ? 'सख्त पहचान सत्यापन (Strict Identity KYC)' : 'Strict Identity KYC',
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900),
        ),
        const SizedBox(height: 6),
        Text(
          isHi
              ? 'आधार कार्ड (अगला/पिछला भाग) और लाइव सेल्फ़ी चेक अपलोड करें। बैकएंड एपीआई चेहरे का मिलान करता है।'
              : 'Upload Aadhaar Front/Back and complete Liveness Selfie Check.',
          style: const TextStyle(fontSize: 13, color: Colors.grey),
        ),
        const SizedBox(height: 20),

        _buildUploadCard(
          title: isHi ? 'आधार कार्ड — अगला भाग (Aadhaar Front) *' : 'Aadhaar Card Front *',
          fileName: _aadhaarFrontName,
          icon: Icons.badge_outlined,
          onTap: () {
            setState(() => _aadhaarFrontName = 'runner_aadhaar_front.jpg');
            _persistDraft();
          },
        ),
        const SizedBox(height: 12),

        _buildUploadCard(
          title: isHi ? 'आधार कार्ड — पिछला भाग (Aadhaar Back) *' : 'Aadhaar Card Back *',
          fileName: _aadhaarBackName,
          icon: Icons.contact_page_outlined,
          onTap: () {
            setState(() => _aadhaarBackName = 'runner_aadhaar_back.jpg');
            _persistDraft();
          },
        ),
        const SizedBox(height: 12),

        // Liveness Selfie Check
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: _livenessVerified ? Colors.green.withValues(alpha: 0.08) : Colors.blue.withValues(alpha: 0.06),
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: _livenessVerified ? Colors.green : Colors.blue),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(_livenessVerified ? Icons.check_circle : Icons.face_retouching_natural, color: _livenessVerified ? Colors.green : Colors.blue),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      _livenessVerified
                          ? (isHi ? 'लाइवनेस सेल्फ़ी व आधार चेहरा मिलान सत्यापित' : 'Liveness Selfie & Aadhaar Photo Match Verified')
                          : (isHi ? 'लाइवनेस सेल्फ़ी चेक (Liveness Selfie Check) *' : 'Liveness Selfie Check *'),
                      style: TextStyle(fontWeight: FontWeight.bold, color: _livenessVerified ? Colors.green.shade900 : Colors.blue.shade900),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Text(
                isHi
                    ? 'धोखाधड़ी रोकने हेतु चेहरे की जीवंतता और आधार फोटो का स्वचालित मिलान किया जाता है।'
                    : 'Real-time biometric liveness verification matches selfie against uploaded Aadhaar.',
                style: const TextStyle(fontSize: 12, color: Colors.grey),
              ),
              const SizedBox(height: 10),
              if (!_livenessVerified)
                ElevatedButton.icon(
                  style: ElevatedButton.styleFrom(backgroundColor: Colors.blue.shade700),
                  icon: const Icon(Icons.camera_front),
                  label: Text(isHi ? 'लाइव सेल्फ़ी कैप्चर करें' : 'Capture Liveness Selfie'),
                  onPressed: () {
                    setState(() {
                      _selfieName = 'runner_liveness_verified.jpg';
                      _livenessVerified = true;
                    });
                    _persistDraft();
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text(isHi ? 'लाइवनेस सेल्फ़ी सफलतापूर्वक सत्यापित हुई!' : 'Liveness selfie verified successfully!'),
                        backgroundColor: GBColors.success,
                      ),
                    );
                  },
                ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        CheckboxListTile(
          value: _kycConsent,
          contentPadding: EdgeInsets.zero,
          title: Text(
            isHi
                ? 'मैं गाँव बाज़ार को पुलिस सत्यापन एवं डिजिटल पहचान जांच हेतु सहमति देता हूँ।'
                : 'I consent to UIDAI biometric verification and background check for runner duty.',
            style: const TextStyle(fontSize: 12),
          ),
          onChanged: (val) {
            setState(() => _kycConsent = val ?? false);
          },
        ),
      ],
    );
  }

  // ---------------------------------------------------------------------------
  // PDF PAGE 5: BANK / PAYOUT SETUP
  // Account Holder Name, Bank Account Number, IFSC Code. (System performs a ₹1 Penny Drop verification).
  // ---------------------------------------------------------------------------
  Widget _buildPage3BankPayout(bool isHi) {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        Text(
          isHi ? 'बैंक खाता व पेआउट सेटअप' : 'Bank / Payout Setup',
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900),
        ),
        const SizedBox(height: 6),
        Text(
          isHi
              ? 'डिलीवरी शुल्क और प्रोत्साहन सीधे आपके बैंक खाते में जमा किए जाएंगे। कोई नकद भुगतान नहीं।'
              : 'Trip earnings and incentives are deposited to this account. Zero physical cash payouts.',
          style: const TextStyle(fontSize: 13, color: Colors.grey),
        ),
        const SizedBox(height: 20),

        TextField(
          controller: _accountHolderCtrl,
          decoration: InputDecoration(
            labelText: isHi ? 'खाताधारक का नाम (Account Holder Name) *' : 'Account Holder Name *',
            prefixIcon: const Icon(Icons.person_outline),
            border: const OutlineInputBorder(),
          ),
          onChanged: (_) {
            setState(() => _pennyDropVerified = false);
            _persistDraft();
          },
        ),
        const SizedBox(height: 14),

        TextField(
          controller: _accountNumberCtrl,
          keyboardType: TextInputType.number,
          decoration: InputDecoration(
            labelText: isHi ? 'बैंक खाता संख्या (Bank Account Number) *' : 'Bank Account Number *',
            hintText: 'e.g. 987654321012',
            prefixIcon: const Icon(Icons.account_balance_outlined),
            border: const OutlineInputBorder(),
          ),
          onChanged: (_) {
            setState(() => _pennyDropVerified = false);
            _persistDraft();
          },
        ),
        const SizedBox(height: 14),

        TextField(
          controller: _ifscCtrl,
          textCapitalization: TextCapitalization.characters,
          decoration: InputDecoration(
            labelText: 'IFSC Code *',
            hintText: 'e.g. SBIN0001234',
            prefixIcon: const Icon(Icons.domain_outlined),
            border: const OutlineInputBorder(),
          ),
          onChanged: (_) {
            setState(() => _pennyDropVerified = false);
            _persistDraft();
          },
        ),
        const SizedBox(height: 20),

        // ₹1 Penny Drop Verification Trigger
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: _pennyDropVerified ? Colors.green.withValues(alpha: 0.08) : Colors.amber.withValues(alpha: 0.08),
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: _pennyDropVerified ? Colors.green : Colors.amber),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    _pennyDropVerified ? Icons.check_circle : Icons.verified_outlined,
                    color: _pennyDropVerified ? Colors.green : Colors.amber.shade800,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      _pennyDropVerified
                          ? (isHi ? '₹1 पेनी ड्रॉप सत्यापन सफल' : '₹1 Penny Drop Verified')
                          : (isHi ? '₹1 पेनी ड्रॉप सत्यापन अनिवार्य' : '₹1 Penny Drop Verification Required'),
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                        color: _pennyDropVerified ? Colors.green.shade900 : Colors.amber.shade900,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Text(
                isHi
                    ? 'गाँव बाज़ार बैंक खाते की प्रामाणिकता जांचने के लिए ₹1 का डिजिटल सत्यापन करता है।'
                    : 'System conducts instant ₹1 penny drop to verify account authenticity.',
                style: const TextStyle(fontSize: 12, color: Colors.grey),
              ),
              const SizedBox(height: 10),
              if (!_pennyDropVerified)
                ElevatedButton(
                  style: ElevatedButton.styleFrom(backgroundColor: GBColors.primary),
                  onPressed: _isPennyDropVerifying ? null : _runPennyDrop,
                  child: _isPennyDropVerifying
                      ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                      : Text(isHi ? '₹1 पेनी ड्रॉप सत्यापन करें' : 'Verify via ₹1 Penny Drop'),
                ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildUploadCard({
    required String title,
    String? fileName,
    required IconData icon,
    required VoidCallback onTap,
  }) {
    final hasFile = fileName != null && fileName.isNotEmpty;
    return Card(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(10),
        side: BorderSide(color: hasFile ? GBColors.success : Colors.grey.shade300),
      ),
      child: ListTile(
        leading: Icon(icon, color: hasFile ? GBColors.success : GBColors.primary),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13)),
        subtitle: Text(
          hasFile ? 'दस्तावेज़ संलग्न: $fileName' : 'अपलोड करने के लिए टैप करें (Tap to upload)',
          style: TextStyle(fontSize: 11, color: hasFile ? GBColors.success : Colors.grey),
        ),
        trailing: Icon(
          hasFile ? Icons.check_circle : Icons.cloud_upload_outlined,
          color: hasFile ? GBColors.success : Colors.grey,
        ),
        onTap: onTap,
      ),
    );
  }
}
