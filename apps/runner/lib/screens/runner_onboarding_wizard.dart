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

  // Page 1: Partner & Vehicle Type
  final _fullNameCtrl = TextEditingController();
  final _phoneCtrl = TextEditingController();
  String _vehicleType = 'Motorcycle';

  // Page 2: Delivery Area & Vehicle Eligibility
  final _preferredVillageCtrl = TextEditingController();
  final _vehicleNoCtrl = TextEditingController();
  final _dlCtrl = TextEditingController();

  // Page 3: Digital Identity Verification & Declaration
  final _aadhaarCtrl = TextEditingController();
  bool _digitalConsent = false;
  bool _safetyAgreement = false;

  bool get _isMotorized => _vehicleType == 'Motorcycle' || _vehicleType == 'Scooter';

  final List<Map<String, dynamic>> _vehicleOptions = [
    {
      'id': 'Motorcycle',
      'nameHi': 'मोटरसाइकिल (Motorcycle)',
      'nameEn': 'Motorcycle',
      'descHi': 'त्वरित लंबी दूरी डिलीवरी (लाइसेंस आवश्यक)',
      'descEn': 'Fast rural delivery (DL required)',
      'icon': Icons.two_wheeler,
    },
    {
      'id': 'Scooter',
      'nameHi': 'स्कूटर (Scooter)',
      'nameEn': 'Scooter',
      'descHi': 'आस-पास के टोलों में डिलीवरी (लाइसेंस आवश्यक)',
      'descEn': 'Cluster delivery (DL required)',
      'icon': Icons.moped,
    },
    {
      'id': 'Bicycle',
      'nameHi': 'साइकिल (Bicycle)',
      'nameEn': 'Bicycle',
      'descHi': 'गाँव के अंदर डिलीवरी (लाइसेंस आवश्यक नहीं)',
      'descEn': 'Intra-village delivery (No DL needed)',
      'icon': Icons.pedal_bike,
    },
    {
      'id': 'Electric Cycle',
      'nameHi': 'इलेक्ट्रिक साइकिल (Electric Cycle)',
      'nameEn': 'Electric Cycle / EV',
      'descHi': 'पर्यावरण अनुकूल डिलीवरी (लाइसेंस आवश्यक नहीं)',
      'descEn': 'Eco delivery (No DL needed)',
      'icon': Icons.electric_bike,
    },
  ];

  @override
  void initState() {
    super.initState();
    _loadSavedDraft();
  }

  Future<void> _loadSavedDraft() async {
    final prefs = await SharedPreferences.getInstance();
    final state = RunnerStateProvider.of(context);

    setState(() {
      _fullNameCtrl.text = prefs.getString('gb_r_draft_name') ?? state.currentUser?.name ?? '';
      _phoneCtrl.text = state.currentUser?.phone ?? prefs.getString('gb_r_draft_phone') ?? '';
      _vehicleType = prefs.getString('gb_r_draft_vehicle') ?? 'Motorcycle';

      _preferredVillageCtrl.text = prefs.getString('gb_r_draft_village') ?? '';
      _vehicleNoCtrl.text = prefs.getString('gb_r_draft_veh_no') ?? '';
      _dlCtrl.text = prefs.getString('gb_r_draft_dl') ?? '';

      _aadhaarCtrl.text = prefs.getString('gb_r_draft_aadhaar') ?? '';
      _digitalConsent = prefs.getBool('gb_r_draft_consent') ?? false;
      _safetyAgreement = prefs.getBool('gb_r_draft_safety') ?? false;
    });
  }

  Future<void> _persistDraft() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('gb_r_draft_name', _fullNameCtrl.text.trim());
    await prefs.setString('gb_r_draft_phone', _phoneCtrl.text.trim());
    await prefs.setString('gb_r_draft_vehicle', _vehicleType);
    await prefs.setString('gb_r_draft_village', _preferredVillageCtrl.text.trim());
    await prefs.setString('gb_r_draft_veh_no', _vehicleNoCtrl.text.trim());
    await prefs.setString('gb_r_draft_dl', _dlCtrl.text.trim());
    await prefs.setString('gb_r_draft_aadhaar', _aadhaarCtrl.text.trim());
    await prefs.setBool('gb_r_draft_consent', _digitalConsent);
    await prefs.setBool('gb_r_draft_safety', _safetyAgreement);
  }

  Future<void> _clearDraft() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('gb_r_draft_name');
    await prefs.remove('gb_r_draft_phone');
    await prefs.remove('gb_r_draft_vehicle');
    await prefs.remove('gb_r_draft_village');
    await prefs.remove('gb_r_draft_veh_no');
    await prefs.remove('gb_r_draft_dl');
    await prefs.remove('gb_r_draft_aadhaar');
    await prefs.remove('gb_r_draft_consent');
    await prefs.remove('gb_r_draft_safety');
  }

  @override
  void dispose() {
    _pageController.dispose();
    _fullNameCtrl.dispose();
    _phoneCtrl.dispose();
    _preferredVillageCtrl.dispose();
    _vehicleNoCtrl.dispose();
    _dlCtrl.dispose();
    _aadhaarCtrl.dispose();
    super.dispose();
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: GBColors.error),
    );
  }

  void _onNext() async {
    final state = RunnerStateProvider.of(context);
    final isHi = state.isHindi;

    await _persistDraft();

    if (_currentPage == 0) {
      if (_fullNameCtrl.text.trim().isEmpty) {
        _showError(isHi ? 'कृपया अपना पूरा नाम दर्ज करें' : 'Please enter full name');
        return;
      }
      _pageController.nextPage(duration: const Duration(milliseconds: 300), curve: Curves.easeInOut);
      setState(() => _currentPage = 1);
    } else if (_currentPage == 1) {
      if (_preferredVillageCtrl.text.trim().isEmpty) {
        _showError(isHi ? 'कृपया कार्य क्षेत्र / गाँव दर्ज करें' : 'Please enter working village/cluster');
        return;
      }
      if (_isMotorized) {
        if (_vehicleNoCtrl.text.trim().isEmpty) {
          _showError(isHi ? 'कृपया वाहन पंजीकरण संख्या दर्ज करें' : 'Please enter vehicle registration number');
          return;
        }
        if (_dlCtrl.text.trim().isEmpty) {
          _showError(isHi ? 'कृपया ड्राइविंग लाइसेंस संख्या दर्ज करें' : 'Please enter driving license number');
          return;
        }
      }
      _pageController.nextPage(duration: const Duration(milliseconds: 300), curve: Curves.easeInOut);
      setState(() => _currentPage = 2);
    } else if (_currentPage == 2) {
      if (_aadhaarCtrl.text.trim().isEmpty) {
        _showError(isHi ? 'कृपया 12-अंकीय आधार पहचान संख्या दर्ज करें' : 'Please enter 12-digit Aadhaar number');
        return;
      }
      if (!_digitalConsent) {
        _showError(isHi ? 'कृपया डिजिटल पहचान सत्यापन सहमति स्वीकार करें' : 'Please accept digital verification consent');
        return;
      }
      if (!_safetyAgreement) {
        _showError(isHi ? 'कृपया सड़क सुरक्षा एवं सीओडी नकद सेटलमेंट वचन स्वीकार करें' : 'Please accept safety and COD agreement');
        return;
      }
      _submitRegistration(state);
    }
  }

  void _onBack() {
    if (_currentPage > 0) {
      _pageController.previousPage(duration: const Duration(milliseconds: 300), curve: Curves.easeInOut);
      setState(() => _currentPage--);
    } else {
      Navigator.of(context).maybePop();
    }
  }

  Future<void> _submitRegistration(RunnerAppState state) async {
    final isHi = state.isHindi;
    setState(() => _isSubmitting = true);

    final payload = {
      'full_name': _fullNameCtrl.text.trim(),
      'vehicle_type': _vehicleType,
      'vehicle_number': _isMotorized
          ? _vehicleNoCtrl.text.trim().toUpperCase()
          : 'BICYCLE-${_fullNameCtrl.text.trim().toUpperCase().replaceAll(' ', '')}',
      'driving_licence_no': _isMotorized ? _dlCtrl.text.trim().toUpperCase() : 'EXEMPT-BICYCLE',
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
            ? 'पंजीकरण जमा करने में विफल। कृपया नेटवर्क जाँचें या पुनः प्रयास करें।'
            : 'Failed to submit registration. Please check your connection and try again.',
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = RunnerStateProvider.of(context);
    final isHi = state.isHindi;

    final titles = [
      isHi ? 'व्यक्तिगत विवरण व वाहन' : 'Personal & Vehicle Details',
      isHi ? 'कार्य क्षेत्र व दस्तावेज' : 'Work Area & Eligibility',
      isHi ? 'पहचान सत्यापन व सुरक्षा' : 'Identity Verification & Safety',
    ];

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: _onBack,
        ),
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              isHi ? 'डिलीवरी साथी पंजीकरण' : 'Runner Onboarding',
              style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
            ),
            Text(
              '${isHi ? "चरण" : "Step"} ${_currentPage + 1} / 3: ${titles[_currentPage]}',
              style: const TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ],
        ),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(4),
          child: LinearProgressIndicator(
            value: (_currentPage + 1) / 3,
            backgroundColor: Colors.grey.shade200,
            valueColor: const AlwaysStoppedAnimation<Color>(GBColors.primary),
          ),
        ),
      ),
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: PageView(
                controller: _pageController,
                physics: const NeverScrollableScrollPhysics(),
                children: [
                  _buildPage1(isHi),
                  _buildPage2(isHi),
                  _buildPage3(isHi),
                ],
              ),
            ),
            _buildBottomActionBar(isHi),
          ],
        ),
      ),
    );
  }

  // --------------------------------------------------------------------------
  // PAGE 1: PARTNER PROFILE & VEHICLE SELECTION
  // --------------------------------------------------------------------------
  Widget _buildPage1(bool isHi) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: GBColors.primary.withValues(alpha: 0.08),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: GBColors.primary.withValues(alpha: 0.25)),
            ),
            child: Row(
              children: [
                const Icon(Icons.two_wheeler_outlined, color: GBColors.primary, size: 28),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    isHi
                        ? 'गाँव बाज़ार डिलीवरी नेटवर्क से जुड़ें — पारदर्शी दूरी पेआउट और तत्काल बैंक/यूपीआई सेटलमेंट।'
                        : 'Join GaonBazaar Delivery Network with transparent 5-tier distance payouts and direct settlements.',
                    style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),

          // Full Name
          Text(
            isHi ? 'साथी का पूरा नाम (आधार अनुसार) *' : 'Partner Full Name (as per Aadhaar) *',
            style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
          ),
          const SizedBox(height: 6),
          TextField(
            controller: _fullNameCtrl,
            decoration: InputDecoration(
              hintText: isHi ? 'उदा. संतोष कुमार' : 'e.g. Santosh Kumar',
              prefixIcon: const Icon(Icons.person_outline),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              filled: true,
              fillColor: Theme.of(context).cardColor,
            ),
          ),
          const SizedBox(height: 16),

          // Verified Mobile Number
          Text(
            isHi ? 'सत्यापित मोबाइल नंबर' : 'Verified Mobile Number',
            style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
          ),
          const SizedBox(height: 6),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
            decoration: BoxDecoration(
              color: Colors.green.withValues(alpha: 0.08),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: Colors.green.withValues(alpha: 0.3)),
            ),
            child: Row(
              children: [
                const Icon(Icons.verified, color: Colors.green, size: 20),
                const SizedBox(width: 10),
                Text(
                  _phoneCtrl.text.isNotEmpty ? _phoneCtrl.text : '+91 98222 22222',
                  style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
                ),
                const Spacer(),
                Text(
                  isHi ? 'ओटीपी सत्यापित ✓' : 'OTP Verified ✓',
                  style: const TextStyle(color: Colors.green, fontWeight: FontWeight.w700, fontSize: 11),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),

          // Vehicle Type Selector Cards
          Text(
            isHi ? 'डिलीवरी वाहन चुनें *' : 'Select Delivery Vehicle *',
            style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
          ),
          const SizedBox(height: 10),
          ..._vehicleOptions.map((opt) {
            final isSelected = _vehicleType == opt['id'];
            return Container(
              margin: const EdgeInsets.only(bottom: 10),
              decoration: BoxDecoration(
                color: isSelected ? GBColors.primary.withValues(alpha: 0.08) : Theme.of(context).cardColor,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: isSelected ? GBColors.primary : Colors.grey.shade300,
                  width: isSelected ? 1.8 : 1.0,
                ),
              ),
              child: ListTile(
                leading: Icon(opt['icon'] as IconData, color: isSelected ? GBColors.primary : Colors.grey),
                title: Text(
                  isHi ? opt['nameHi']! : opt['nameEn']!,
                  style: TextStyle(fontWeight: isSelected ? FontWeight.w800 : FontWeight.w600, fontSize: 14),
                ),
                subtitle: Text(
                  isHi ? opt['descHi']! : opt['descEn']!,
                  style: const TextStyle(fontSize: 11, color: Colors.grey),
                ),
                trailing: Radio<String>(
                  value: opt['id'] as String,
                  groupValue: _vehicleType,
                  activeColor: GBColors.primary,
                  onChanged: (val) {
                    if (val != null) setState(() => _vehicleType = val);
                  },
                ),
                onTap: () => setState(() => _vehicleType = opt['id'] as String),
              ),
            );
          }),
        ],
      ),
    );
  }

  // --------------------------------------------------------------------------
  // PAGE 2: WORK AREA & VEHICLE ELIGIBILITY
  // --------------------------------------------------------------------------
  Widget _buildPage2(bool isHi) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Preferred Village / Working Area
          Text(
            isHi ? 'प्राथमिक डिलीवरी कार्य क्षेत्र (गाँव / टोला) *' : 'Primary Delivery Area (Village / Cluster) *',
            style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
          ),
          const SizedBox(height: 6),
          TextField(
            controller: _preferredVillageCtrl,
            decoration: InputDecoration(
              hintText: isHi ? 'उदा. चतुरसी, मीनापुर क्लस्टर' : 'e.g. Chatursi, Minapur Cluster',
              prefixIcon: const Icon(Icons.location_on_outlined),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              filled: true,
              fillColor: Theme.of(context).cardColor,
            ),
          ),
          const SizedBox(height: 20),

          // Vehicle Eligibility Details
          if (_isMotorized) ...[
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.blue.withValues(alpha: 0.08),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: Colors.blue.withValues(alpha: 0.3)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.info_outline, color: Colors.blue, size: 20),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      isHi
                          ? 'मोटरसाइकिल/स्कूटर से डिलीवरी हेतु वैध वाहन नंबर और ड्राइविंग लाइसेंस अनिवार्य है।'
                          : 'Valid vehicle registration and driving license are required for motorized delivery.',
                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Colors.blue),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            Text(
              isHi ? 'वाहन पंजीकरण संख्या (गाड़ी नंबर) *' : 'Vehicle Registration Number *',
              style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
            ),
            const SizedBox(height: 6),
            TextField(
              controller: _vehicleNoCtrl,
              textCapitalization: TextCapitalization.characters,
              decoration: InputDecoration(
                hintText: 'BR-06-AB-1234',
                prefixIcon: const Icon(Icons.pin_outlined),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                filled: true,
                fillColor: Theme.of(context).cardColor,
              ),
            ),
            const SizedBox(height: 16),

            Text(
              isHi ? 'ड्राइविंग लाइसेंस (DL) संख्या *' : 'Driving Licence Number *',
              style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
            ),
            const SizedBox(height: 6),
            TextField(
              controller: _dlCtrl,
              textCapitalization: TextCapitalization.characters,
              decoration: InputDecoration(
                hintText: 'DL-06-20220012345',
                prefixIcon: const Icon(Icons.credit_card_outlined),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                filled: true,
                fillColor: Theme.of(context).cardColor,
              ),
            ),
          ] else ...[
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.green.withValues(alpha: 0.08),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.green.withValues(alpha: 0.3)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.check_circle_outline, color: Colors.green, size: 28),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          isHi ? 'लाइसेंस की आवश्यकता नहीं' : 'Driving Licence Exempt',
                          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14, color: Colors.green),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          isHi
                              ? 'साइकिल / ई-साइकिल डिलीवरी हेतु ड्राइविंग लाइसेंस आवश्यक नहीं है। आप तुरंत स्थानीय डिलीवरी साथी बन सकते हैं।'
                              : 'Bicycle and e-cycle deliveries are exempt from driving license requirements.',
                          style: const TextStyle(fontSize: 12, color: Colors.black87),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],

          const SizedBox(height: 24),
          Text(
            isHi
                ? 'नोट: बैंक एवं यूपीआई सेटिंग्स पंजीकरण के बाद अकाउंट सेक्शन में जोड़ी जा सकती हैं।'
                : 'Note: Bank and UPI settlement accounts can be configured in the Account tab after submission.',
            style: const TextStyle(fontSize: 11, color: Colors.grey),
          ),
        ],
      ),
    );
  }

  // --------------------------------------------------------------------------
  // PAGE 3: DIGITAL IDENTITY VERIFICATION & SAFETY AGREEMENT
  // --------------------------------------------------------------------------
  Widget _buildPage3(bool isHi) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: Colors.amber.shade50,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.amber.shade300),
            ),
            child: Row(
              children: [
                Icon(Icons.shield_outlined, color: Colors.amber.shade900, size: 28),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    isHi
                        ? 'त्वरित डिजिटल सत्यापन — सुपर एडमिन द्वारा अनुमोदन के बाद ही आपकी आईडी सक्रिय होगी।'
                        : 'Instant Verification — Application will be reviewed and approved by Super Admin.',
                    style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Colors.amber.shade900),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),

          // Aadhaar Number
          Text(
            isHi ? '12-अंकीय आधार पहचान संख्या *' : '12-Digit Aadhaar Number *',
            style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
          ),
          const SizedBox(height: 6),
          TextField(
            controller: _aadhaarCtrl,
            keyboardType: TextInputType.number,
            maxLength: 12,
            decoration: InputDecoration(
              hintText: '1234 5678 9012',
              prefixIcon: const Icon(Icons.badge_outlined),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              filled: true,
              fillColor: Theme.of(context).cardColor,
            ),
          ),
          const SizedBox(height: 20),

          // Digital Consent Checkbox
          CheckboxListTile(
            contentPadding: EdgeInsets.zero,
            value: _digitalConsent,
            activeColor: GBColors.primary,
            title: Text(
              isHi
                  ? 'मैं गाँव बाज़ार डिजिटल सत्यापन एवं पहचान पत्र जाँच के लिए पूर्ण सहमति देता हूँ।'
                  : 'I authorize GaonBazaar to verify my identity records for delivery partner registration.',
              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
            ),
            controlAffinity: ListTileControlAffinity.leading,
            onChanged: (val) => setState(() => _digitalConsent = val ?? false),
          ),
          const SizedBox(height: 8),

          // Road Safety & COD Remittance Commitment
          CheckboxListTile(
            contentPadding: EdgeInsets.zero,
            value: _safetyAgreement,
            activeColor: GBColors.primary,
            title: Text(
              isHi
                  ? 'मैं सड़क सुरक्षा नियमों का पालन करूँगा एवं ग्राहकों से प्राप्त सभी सीओडी नकद उसी दिन सिस्टम में सेटल करने का वचन देता हूँ।'
                  : 'I commit to safe driving guidelines and agree to reconcile all cash collected from COD orders daily.',
              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
            ),
            controlAffinity: ListTileControlAffinity.leading,
            onChanged: (val) => setState(() => _safetyAgreement = val ?? false),
          ),
          const SizedBox(height: 20),

          // Distance Payout reminder
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: GBColors.primary.withValues(alpha: 0.05),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Row(
              children: [
                const Icon(Icons.currency_rupee, color: GBColors.primary, size: 20),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    isHi
                        ? 'पारदर्शी 5-स्तरीय दूरी पेआउट: ₹10 (0-1 किमी) से ₹28 (6-8 किमी)।'
                        : 'Transparent distance payouts: ₹10 (0-1 km) up to ₹28 (6-8 km).',
                    style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: GBColors.primary),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // --------------------------------------------------------------------------
  // BOTTOM ACTION BAR
  // --------------------------------------------------------------------------
  Widget _buildBottomActionBar(bool isHi) {
    final isLastPage = _currentPage == 2;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        boxShadow: [
          BoxShadow(color: Colors.black.withValues(alpha: 0.05), blurRadius: 6, offset: const Offset(0, -2)),
        ],
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
              ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
              : Text(
                  isLastPage
                      ? (isHi ? 'आवेदन जमा करें' : 'Submit Application')
                      : (isHi ? 'आगे बढ़ें (Continue) →' : 'Continue →'),
                  style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15, color: Colors.white),
                ),
        ),
      ),
    );
  }
}
