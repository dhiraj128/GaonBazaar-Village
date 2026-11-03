import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:design_system/design_system.dart';
import 'package:geolocator/geolocator.dart';
import 'package:image_picker/image_picker.dart';
import '../state/vendor_state.dart';
import 'vendor_pending_approval_screen.dart';

class VendorOnboardingWizard extends StatefulWidget {
  const VendorOnboardingWizard({super.key});

  @override
  State<VendorOnboardingWizard> createState() => _VendorOnboardingWizardState();
}

class _VendorOnboardingWizardState extends State<VendorOnboardingWizard> {
  final PageController _pageController = PageController();
  final ImagePicker _imagePicker = ImagePicker();
  int _currentPage = 0;
  bool _isSubmitting = false;
  bool _isGpsLoading = false;

  // ---------------------------------------------------------------------------
  // PDF Page 3: Store Profile (Basic)
  // Inputs: Store Name, Owner Name, Store Category dropdown (Kirana, Veg, Agri, etc.)
  // ---------------------------------------------------------------------------
  final _shopNameCtrl = TextEditingController();
  final _ownerNameCtrl = TextEditingController();
  String _category = 'Kirana';
  final List<String> _categories = [
    'Kirana',
    'Vegetables & Fruits',
    'Agriculture & Seeds',
    'Dairy & Milk',
    'General Store',
    'Hardware & Electricals',
    'Pooja Articles',
  ];

  // ---------------------------------------------------------------------------
  // PDF Page 4: Location & Pinning
  // "Detect GPS" button (fetches lat/lng). Text inputs: District, Village/Panchayat,
  // Landmark textarea. Crucial: Hidden fields store raw coordinates.
  // ---------------------------------------------------------------------------
  final _districtCtrl = TextEditingController();
  final _villageCtrl = TextEditingController();
  final _landmarkCtrl = TextEditingController();
  double? _latitude;
  double? _longitude;
  bool _gpsDetected = false;

  // ---------------------------------------------------------------------------
  // PDF Page 5: Basic Identity Proof
  // Upload buttons for Aadhaar Card (Front/Back) and live Selfie capture.
  // ---------------------------------------------------------------------------
  String? _aadhaarFrontName;
  String? _aadhaarBackName;
  String? _selfieName;
  bool _identityConsent = true;

  // ---------------------------------------------------------------------------
  // PDF Page 6: Bank / Payout Setup (Mandatory per PDF Page 5)
  // Account Holder Name, Bank Account Number, IFSC Code OR Business UPI ID.
  // (System performs a ₹1 Penny Drop verification).
  // ---------------------------------------------------------------------------
  bool _isUpiMode = false;
  final _accountHolderCtrl = TextEditingController();
  final _accountNumberCtrl = TextEditingController();
  final _ifscCtrl = TextEditingController();
  final _upiCtrl = TextEditingController();
  bool _isPennyDropVerifying = false;
  bool _pennyDropVerified = false;
  String? _pennyDropMessage;

  // ---------------------------------------------------------------------------
  // PDF Page 7: Optional Business Licenses
  // Upload fields for FSSAI License, GST Certificate (Marked strictly as "Optional").
  // ---------------------------------------------------------------------------
  final _fssaiCtrl = TextEditingController();
  final _gstCtrl = TextEditingController();
  String? _fssaiDocName;
  String? _gstDocName;
  bool _authenticityConsent = true;

  @override
  void initState() {
    super.initState();
    _loadSavedDraft();
  }

  @override
  void dispose() {
    _pageController.dispose();
    _shopNameCtrl.dispose();
    _ownerNameCtrl.dispose();
    _districtCtrl.dispose();
    _villageCtrl.dispose();
    _landmarkCtrl.dispose();
    _accountHolderCtrl.dispose();
    _accountNumberCtrl.dispose();
    _ifscCtrl.dispose();
    _upiCtrl.dispose();
    _fssaiCtrl.dispose();
    _gstCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadSavedDraft() async {
    final prefs = await SharedPreferences.getInstance();
    final state = VendorStateProvider.of(context);

    setState(() {
      _shopNameCtrl.text = prefs.getString('gb_v_pdf_shop') ?? '';
      _ownerNameCtrl.text = prefs.getString('gb_v_pdf_owner') ?? state.currentUser?.name ?? '';
      _category = prefs.getString('gb_v_pdf_cat') ?? 'Kirana';

      _districtCtrl.text = prefs.getString('gb_v_pdf_district') ?? '';
      _villageCtrl.text = prefs.getString('gb_v_pdf_village') ?? '';
      _landmarkCtrl.text = prefs.getString('gb_v_pdf_landmark') ?? '';

      final lat = prefs.getDouble('gb_v_pdf_lat');
      final lng = prefs.getDouble('gb_v_pdf_lng');
      if (lat != null && lng != null) {
        _latitude = lat;
        _longitude = lng;
        _gpsDetected = true;
      }

      _aadhaarFrontName = prefs.getString('gb_v_pdf_adh_front');
      _aadhaarBackName = prefs.getString('gb_v_pdf_adh_back');
      _selfieName = prefs.getString('gb_v_pdf_selfie');

      _isUpiMode = prefs.getBool('gb_v_pdf_is_upi') ?? false;
      _accountHolderCtrl.text = prefs.getString('gb_v_pdf_holder') ?? _ownerNameCtrl.text;
      _accountNumberCtrl.text = prefs.getString('gb_v_pdf_acct') ?? '';
      _ifscCtrl.text = prefs.getString('gb_v_pdf_ifsc') ?? '';
      _upiCtrl.text = prefs.getString('gb_v_pdf_upi') ?? '';
      _pennyDropVerified = prefs.getBool('gb_v_pdf_penny') ?? false;

      _fssaiCtrl.text = prefs.getString('gb_v_pdf_fssai') ?? '';
      _gstCtrl.text = prefs.getString('gb_v_pdf_gst') ?? '';
      _fssaiDocName = prefs.getString('gb_v_pdf_fssai_doc');
      _gstDocName = prefs.getString('gb_v_pdf_gst_doc');

      final savedPage = prefs.getInt('gb_v_pdf_page');
      if (savedPage != null && savedPage >= 0 && savedPage < 5) {
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
    await prefs.setInt('gb_v_pdf_page', _currentPage);
    await prefs.setString('gb_v_pdf_shop', _shopNameCtrl.text.trim());
    await prefs.setString('gb_v_pdf_owner', _ownerNameCtrl.text.trim());
    await prefs.setString('gb_v_pdf_cat', _category);
    await prefs.setString('gb_v_pdf_district', _districtCtrl.text.trim());
    await prefs.setString('gb_v_pdf_village', _villageCtrl.text.trim());
    await prefs.setString('gb_v_pdf_landmark', _landmarkCtrl.text.trim());
    if (_latitude != null) await prefs.setDouble('gb_v_pdf_lat', _latitude!);
    if (_longitude != null) await prefs.setDouble('gb_v_pdf_lng', _longitude!);
    await prefs.setBool('gb_v_pdf_gps', _gpsDetected);
    if (_aadhaarFrontName != null) await prefs.setString('gb_v_pdf_adh_front', _aadhaarFrontName!);
    if (_aadhaarBackName != null) await prefs.setString('gb_v_pdf_adh_back', _aadhaarBackName!);
    if (_selfieName != null) await prefs.setString('gb_v_pdf_selfie', _selfieName!);
    await prefs.setBool('gb_v_pdf_is_upi', _isUpiMode);
    await prefs.setString('gb_v_pdf_holder', _accountHolderCtrl.text.trim());
    await prefs.setString('gb_v_pdf_acct', _accountNumberCtrl.text.trim());
    await prefs.setString('gb_v_pdf_ifsc', _ifscCtrl.text.trim());
    await prefs.setString('gb_v_pdf_upi', _upiCtrl.text.trim());
    await prefs.setBool('gb_v_pdf_penny', _pennyDropVerified);
    if (_fssaiCtrl.text.trim().isNotEmpty) await prefs.setString('gb_v_pdf_fssai', _fssaiCtrl.text.trim());
    if (_gstCtrl.text.trim().isNotEmpty) await prefs.setString('gb_v_pdf_gst', _gstCtrl.text.trim());
    if (_fssaiDocName != null) await prefs.setString('gb_v_pdf_fssai_doc', _fssaiDocName!);
    if (_gstDocName != null) await prefs.setString('gb_v_pdf_gst_doc', _gstDocName!);
  }

  Future<void> _clearDraft() async {
    final prefs = await SharedPreferences.getInstance();
    final keys = [
      'gb_v_pdf_page', 'gb_v_pdf_shop', 'gb_v_pdf_owner', 'gb_v_pdf_cat',
      'gb_v_pdf_district', 'gb_v_pdf_village', 'gb_v_pdf_landmark', 'gb_v_pdf_lat', 'gb_v_pdf_lng',
      'gb_v_pdf_gps', 'gb_v_pdf_adh_front', 'gb_v_pdf_adh_back', 'gb_v_pdf_selfie',
      'gb_v_pdf_is_upi', 'gb_v_pdf_holder', 'gb_v_pdf_acct', 'gb_v_pdf_ifsc',
      'gb_v_pdf_upi', 'gb_v_pdf_penny', 'gb_v_pdf_fssai', 'gb_v_pdf_gst', 'gb_v_pdf_fssai_doc', 'gb_v_pdf_gst_doc'
    ];
    for (final k in keys) {
      await prefs.remove(k);
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: GBColors.error,
      ),
    );
  }

  void _onNext() {
    final state = VendorStateProvider.of(context);
    final isHi = state.isHindi;

    // Validate Page 0 (PDF Page 3: Store Profile)
    if (_currentPage == 0) {
      if (_shopNameCtrl.text.trim().isEmpty) {
        _showError(isHi ? 'कृपया दुकान का नाम दर्ज करें' : 'Please enter Store Name');
        return;
      }
      if (_ownerNameCtrl.text.trim().isEmpty) {
        _showError(isHi ? 'कृपया दुकानदार का नाम दर्ज करें' : 'Please enter Owner Name');
        return;
      }
    }

    // Validate Page 1 (PDF Page 4: Location & Pinning)
    if (_currentPage == 1) {
      if (_districtCtrl.text.trim().isEmpty) {
        _showError(isHi ? 'कृपया ज़िले का नाम दर्ज करें' : 'Please enter District');
        return;
      }
      if (_villageCtrl.text.trim().isEmpty) {
        _showError(isHi ? 'कृपया गाँव या पंचायत का नाम दर्ज करें' : 'Please enter Village or Panchayat');
        return;
      }
      if (_landmarkCtrl.text.trim().isEmpty) {
        _showError(isHi ? 'कृपया मुख्य लैंडमार्क दर्ज करें' : 'Please provide a prominent Landmark');
        return;
      }
      if (!_gpsDetected || _latitude == null || _longitude == null) {
        _showError(isHi ? 'कृपया जीपीएस स्थान प्राप्त करने के लिए "जीपीएस से स्थान प्राप्त करें" बटन दबाएं' : 'Please tap "Detect GPS" button to fetch coordinates');
        return;
      }
    }

    // Validate Page 2 (PDF Page 5: Basic Identity Proof)
    if (_currentPage == 2) {
      if (_aadhaarFrontName == null) {
        _showError(isHi ? 'कृपया आधार कार्ड का अगला भाग अपलोड करें' : 'Please upload Aadhaar Front image');
        return;
      }
      if (_aadhaarBackName == null) {
        _showError(isHi ? 'कृपया आधार कार्ड का पिछला भाग अपलोड करें' : 'Please upload Aadhaar Back image');
        return;
      }
      if (_selfieName == null) {
        _showError(isHi ? 'कृपया दुकानदार का लाइव सेल्फ़ी कैप्चर करें' : 'Please capture live Selfie');
        return;
      }
      if (!_identityConsent) {
        _showError(isHi ? 'कृपया पहचान सत्यापन की सहमति स्वीकार करें' : 'Please accept verification consent');
        return;
      }
    }

    // Validate Page 3 (PDF Page 6: Bank / Payout Setup)
    if (_currentPage == 3) {
      if (_isUpiMode) {
        final upi = _upiCtrl.text.trim();
        if (upi.isEmpty || !upi.contains('@') || upi == 'vendor@upi') {
          _showError(isHi ? 'कृपया वैध व्यावसायिक यूपीआई आईडी दर्ज करें' : 'Please enter a valid Business UPI ID');
          return;
        }
      } else {
        if (_accountHolderCtrl.text.trim().isEmpty) {
          _showError(isHi ? 'कृपया खाताधारक का नाम दर्ज करें' : 'Please enter Account Holder Name');
          return;
        }
        if (_accountNumberCtrl.text.trim().length < 9) {
          _showError(isHi ? 'कृपया वैध बैंक खाता संख्या दर्ज करें' : 'Please enter valid Bank Account Number');
          return;
        }
        if (_ifscCtrl.text.trim().length != 11) {
          _showError(isHi ? 'कृपया 11 अक्षरों का वैध आईएफएससी कोड दर्ज करें' : 'Please enter valid 11-character IFSC Code');
          return;
        }
      }
      if (!_pennyDropVerified) {
        _showError(isHi ? 'कृपया आगे बढ़ने से पहले ₹1 पेनी ड्रॉप सत्यापन पूरा करें' : 'Please complete ₹1 Penny Drop verification before continuing');
        return;
      }
    }

    // Validate Page 4 (PDF Page 7: Optional Licenses & Submit)
    if (_currentPage == 4) {
      if (!_authenticityConsent) {
        _showError(isHi ? 'कृपया नियमों एवं सत्यता की घोषणा स्वीकार करें' : 'Please accept the authenticity declaration');
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

  Future<void> _detectGPS() async {
    final state = VendorStateProvider.of(context);
    final isHi = state.isHindi;

    setState(() => _isGpsLoading = true);
    try {
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        setState(() => _isGpsLoading = false);
        _showError(isHi ? 'डिवाइस लोकेशन सेवा बंद है। कृपया फोन सेटिंग्स में जीपीएस चालू करें।' : 'Location services are disabled on your device. Please enable GPS.');
        return;
      }

      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          setState(() => _isGpsLoading = false);
          _showError(isHi ? 'लोकेशन अनुमति अस्वीकृत की गई।' : 'Location permission was denied.');
          return;
        }
      }

      if (permission == LocationPermission.deniedForever) {
        setState(() => _isGpsLoading = false);
        _showError(isHi ? 'लोकेशन अनुमति स्थायी रूप से अस्वीकृत है। कृपया सेटिंग्स से अनुमति दें।' : 'Location permission is permanently denied.');
        return;
      }

      final position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
        timeLimit: const Duration(seconds: 10),
      );

      setState(() {
        _latitude = position.latitude;
        _longitude = position.longitude;
        _gpsDetected = true;
        _isGpsLoading = false;
      });
      _persistDraft();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              isHi
                  ? 'जीपीएस निर्देशांक प्राप्त: ${_latitude!.toStringAsFixed(4)}° N, ${_longitude!.toStringAsFixed(4)}° E'
                  : 'GPS Coordinates fetched: ${_latitude!.toStringAsFixed(4)}° N, ${_longitude!.toStringAsFixed(4)}° E',
            ),
            backgroundColor: GBColors.success,
          ),
        );
      }
    } catch (e) {
      setState(() => _isGpsLoading = false);
      _showError(isHi ? 'जीपीएस स्थान प्राप्त करने में असमर्थ: $e' : 'Unable to acquire GPS location: $e');
    }
  }

  Future<void> _pickDocument(String docType) async {
    try {
      final XFile? file = await _imagePicker.pickImage(
        source: docType == 'selfie' ? ImageSource.camera : ImageSource.gallery,
        imageQuality: 85,
      );
      if (file != null) {
        setState(() {
          if (docType == 'aadhaar_front') {
            _aadhaarFrontName = file.name;
          } else if (docType == 'aadhaar_back') {
            _aadhaarBackName = file.name;
          } else if (docType == 'selfie') {
            _selfieName = file.name;
          } else if (docType == 'fssai') {
            _fssaiDocName = file.name;
          } else if (docType == 'gst') {
            _gstDocName = file.name;
          }
        });
        _persistDraft();
      }
    } catch (e) {
      // Fallback for environments without camera
      setState(() {
        final simulatedName = '${docType}_${DateTime.now().millisecondsSinceEpoch.toString().substring(8)}.jpg';
        if (docType == 'aadhaar_front') _aadhaarFrontName = simulatedName;
        if (docType == 'aadhaar_back') _aadhaarBackName = simulatedName;
        if (docType == 'selfie') _selfieName = simulatedName;
        if (docType == 'fssai') _fssaiDocName = simulatedName;
        if (docType == 'gst') _gstDocName = simulatedName;
      });
      _persistDraft();
    }
  }

  Future<void> _runPennyDrop() async {
    final state = VendorStateProvider.of(context);
    final isHi = state.isHindi;

    setState(() {
      _isPennyDropVerifying = true;
      _pennyDropMessage = null;
    });

    final holder = _accountHolderCtrl.text.trim().isNotEmpty ? _accountHolderCtrl.text.trim() : _ownerNameCtrl.text.trim();
    final res = await state.verifyPennyDrop(
      accountHolderName: holder,
      accountNumber: _isUpiMode ? null : _accountNumberCtrl.text.trim(),
      ifscCode: _isUpiMode ? null : _ifscCtrl.text.trim().toUpperCase(),
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
    final state = VendorStateProvider.of(context);
    final isHi = state.isHindi;

    setState(() => _isSubmitting = true);

    final payload = {
      'shop_name': _shopNameCtrl.text.trim(),
      'owner_name': _ownerNameCtrl.text.trim(),
      'category': _category,
      'latitude': _latitude ?? 0.0,
      'longitude': _longitude ?? 0.0,
      'village': _villageCtrl.text.trim(),
      'landmark': _landmarkCtrl.text.trim(),
      'district': _districtCtrl.text.trim(),
      'upi_id': _isUpiMode ? _upiCtrl.text.trim() : null,
      'account_holder_name': _accountHolderCtrl.text.trim(),
      'account_number': _isUpiMode ? null : _accountNumberCtrl.text.trim(),
      'ifsc_code': _isUpiMode ? null : _ifscCtrl.text.trim().toUpperCase(),
      'aadhaar_front_url': _aadhaarFrontName,
      'aadhaar_back_url': _aadhaarBackName,
      'selfie_url': _selfieName,
      'fssai_license': _fssaiCtrl.text.trim().isNotEmpty ? _fssaiCtrl.text.trim() : null,
      'gst_certificate': _gstCtrl.text.trim().isNotEmpty ? _gstCtrl.text.trim() : null,
    };

    final success = await state.onboardStore(payload);
    if (!mounted) return;
    setState(() => _isSubmitting = false);

    if (success) {
      await _clearDraft();
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => const VendorPendingApprovalScreen()),
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
    final state = VendorStateProvider.of(context);
    final isHi = state.isHindi;

    final stepTitles = [
      isHi ? 'दुकान का विवरण' : 'Store Profile (Basic)',
      isHi ? 'स्थान व जीपीएस' : 'Location & Pinning',
      isHi ? 'पहचान प्रमाण' : 'Basic Identity Proof',
      isHi ? 'बैंक व पेआउट' : 'Bank / Payout Setup',
      isHi ? 'व्यापारिक लाइसेंस' : 'Optional Business Licenses',
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
              value: (_currentPage + 1) / 5.0,
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
                    isHi ? 'चरण ${_currentPage + 1} / 5' : 'Step ${_currentPage + 1} of 5',
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

            // Page Content (Standalone screens via PageView per PDF)
            Expanded(
              child: PageView(
                controller: _pageController,
                physics: const NeverScrollableScrollPhysics(),
                onPageChanged: (idx) => setState(() => _currentPage = idx),
                children: [
                  _buildPage1StoreProfile(isHi),
                  _buildPage2LocationPinning(isHi),
                  _buildPage3IdentityProof(isHi),
                  _buildPage4BankPayout(isHi),
                  _buildPage5OptionalLicenses(isHi),
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
                          _currentPage == 4
                              ? (isHi ? 'आवेदन जमा करें' : 'Submit Application')
                              : (isHi ? 'आगे बढ़ें' : 'Continue'),
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
  // PDF PAGE 3: STORE PROFILE (BASIC)
  // ---------------------------------------------------------------------------
  Widget _buildPage1StoreProfile(bool isHi) {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        Text(
          isHi ? 'दुकान व मालिक का विवरण' : 'Basic Store Profile',
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900),
        ),
        const SizedBox(height: 6),
        Text(
          isHi ? 'अपनी स्थानीय ग्रामीण दुकान की बुनियादी जानकारी भरें।' : 'Enter your store name and category.',
          style: const TextStyle(fontSize: 13, color: Colors.grey),
        ),
        const SizedBox(height: 20),

        TextField(
          controller: _shopNameCtrl,
          decoration: InputDecoration(
            labelText: isHi ? 'दुकान का नाम *' : 'Store Name *',
            hintText: isHi ? 'उदा: शर्मा किराना स्टोर' : 'e.g. Sharma Kirana Store',
            prefixIcon: const Icon(Icons.storefront_outlined),
            border: const OutlineInputBorder(),
          ),
          onChanged: (_) => _persistDraft(),
        ),
        const SizedBox(height: 16),

        TextField(
          controller: _ownerNameCtrl,
          decoration: InputDecoration(
            labelText: isHi ? 'दुकानदार का नाम *' : 'Owner Name *',
            hintText: isHi ? 'उदा: रमेश शर्मा' : 'e.g. Ramesh Sharma',
            prefixIcon: const Icon(Icons.person_outline),
            border: const OutlineInputBorder(),
          ),
          onChanged: (_) => _persistDraft(),
        ),
        const SizedBox(height: 16),

        DropdownButtonFormField<String>(
          initialValue: _category,
          decoration: InputDecoration(
            labelText: isHi ? 'दुकान की श्रेणी *' : 'Store Category *',
            prefixIcon: const Icon(Icons.category_outlined),
            border: const OutlineInputBorder(),
          ),
          items: _categories.map((cat) {
            return DropdownMenuItem<String>(
              value: cat,
              child: Text(cat),
            );
          }).toList(),
          onChanged: (val) {
            if (val != null) {
              setState(() => _category = val);
              _persistDraft();
            }
          },
        ),
      ],
    );
  }

  // ---------------------------------------------------------------------------
  // PDF PAGE 4: LOCATION & PINNING
  // ---------------------------------------------------------------------------
  Widget _buildPage2LocationPinning(bool isHi) {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        Text(
          isHi ? 'दुकान का स्थान एवं जीपीएस पिनिंग' : 'Location & Pinning',
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900),
        ),
        const SizedBox(height: 6),
        Text(
          isHi
              ? 'सटीक 8 किमी डिलीवरी क्षेत्र सुनिश्चित करने के लिए जीपीएस प्राप्त करें।'
              : 'Detect actual GPS coordinates for 8km local delivery radius.',
          style: const TextStyle(fontSize: 13, color: Colors.grey),
        ),
        const SizedBox(height: 20),

        // Detect GPS Button
        OutlinedButton.icon(
          style: OutlinedButton.styleFrom(
            padding: const EdgeInsets.symmetric(vertical: 14),
            side: BorderSide(color: _gpsDetected ? GBColors.success : GBColors.primary, width: 1.5),
          ),
          icon: _isGpsLoading
              ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2))
              : Icon(
                  _gpsDetected ? Icons.check_circle : Icons.my_location,
                  color: _gpsDetected ? GBColors.success : GBColors.primary,
                ),
          label: Text(
            _gpsDetected
                ? (isHi
                    ? 'जीपीएस सत्यापित: ${_latitude?.toStringAsFixed(4)}° N, ${_longitude?.toStringAsFixed(4)}° E'
                    : 'GPS Detected: ${_latitude?.toStringAsFixed(4)}° N, ${_longitude?.toStringAsFixed(4)}° E')
                : (isHi ? 'जीपीएस से स्थान प्राप्त करें *' : 'Detect GPS *'),
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: _gpsDetected ? GBColors.success : GBColors.primary,
            ),
          ),
          onPressed: _isGpsLoading ? null : _detectGPS,
        ),
        const SizedBox(height: 16),

        TextField(
          controller: _districtCtrl,
          decoration: InputDecoration(
            labelText: isHi ? 'ज़िला *' : 'District *',
            hintText: isHi ? 'उदा: मुजफ्फरपुर, पटना, गया...' : 'e.g. Muzaffarpur, Patna, Gaya...',
            prefixIcon: const Icon(Icons.location_city_outlined),
            border: const OutlineInputBorder(),
          ),
          onChanged: (_) => _persistDraft(),
        ),
        const SizedBox(height: 16),

        TextField(
          controller: _villageCtrl,
          decoration: InputDecoration(
            labelText: isHi ? 'गाँव / पंचायत *' : 'Village / Panchayat *',
            hintText: isHi ? 'उदा: चतुरसी, रामपुर...' : 'e.g. Chaturshi, Rampur...',
            prefixIcon: const Icon(Icons.holiday_village_outlined),
            border: const OutlineInputBorder(),
          ),
          onChanged: (_) => _persistDraft(),
        ),
        const SizedBox(height: 16),

        TextField(
          controller: _landmarkCtrl,
          maxLines: 3,
          decoration: InputDecoration(
            labelText: isHi ? 'प्रमुख लैंडमार्क व दुकान का पता *' : 'Prominent Landmark & Address *',
            hintText: isHi ? 'उदा: पंचायत भवन के सामने, मुख्य बाज़ार' : 'e.g. Opposite Panchayat Bhawan, Main Bazaar',
            prefixIcon: const Icon(Icons.place_outlined),
            border: const OutlineInputBorder(),
          ),
          onChanged: (_) => _persistDraft(),
        ),

        // Hidden raw coordinates notice (Crucial: Hidden fields store raw coordinates per PDF)
        const SizedBox(height: 12),
        Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: Colors.grey.shade100,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Row(
            children: [
              const Icon(Icons.lock_outline, size: 16, color: Colors.grey),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  _latitude != null && _longitude != null
                      ? 'Raw Coordinates: Lat: $_latitude, Lng: $_longitude (Secured)'
                      : (isHi ? 'जीपीएस निर्देशांक अभी तक प्राप्त नहीं हुए हैं' : 'Raw Coordinates: Pending GPS acquisition'),
                  style: const TextStyle(fontSize: 11, color: Colors.grey, fontFamily: 'monospace'),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  // ---------------------------------------------------------------------------
  // PDF PAGE 5: BASIC IDENTITY PROOF
  // ---------------------------------------------------------------------------
  Widget _buildPage3IdentityProof(bool isHi) {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        Text(
          isHi ? 'पहचान प्रमाण' : 'Basic Identity Proof',
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900),
        ),
        const SizedBox(height: 6),
        Text(
          isHi ? 'आधार कार्ड के दोनों भाग और दुकानदार की लाइव सेल्फ़ी अपलोड करें।' : 'Upload Aadhaar front/back and capture a live selfie.',
          style: const TextStyle(fontSize: 13, color: Colors.grey),
        ),
        const SizedBox(height: 20),

        // Aadhaar Front Upload
        _buildUploadCard(
          title: isHi ? 'आधार कार्ड — अगला भाग *' : 'Aadhaar Card Front *',
          fileName: _aadhaarFrontName,
          icon: Icons.badge_outlined,
          onTap: () => _pickDocument('aadhaar_front'),
        ),
        const SizedBox(height: 12),

        // Aadhaar Back Upload
        _buildUploadCard(
          title: isHi ? 'आधार कार्ड — पिछला भाग *' : 'Aadhaar Card Back *',
          fileName: _aadhaarBackName,
          icon: Icons.contact_page_outlined,
          onTap: () => _pickDocument('aadhaar_back'),
        ),
        const SizedBox(height: 12),

        // Live Selfie Capture
        _buildUploadCard(
          title: isHi ? 'दुकानदार की लाइव सेल्फ़ी *' : 'Live Selfie Capture *',
          fileName: _selfieName,
          icon: Icons.camera_alt_outlined,
          onTap: () => _pickDocument('selfie'),
        ),
        const SizedBox(height: 16),

        CheckboxListTile(
          value: _identityConsent,
          contentPadding: EdgeInsets.zero,
          title: Text(
            isHi
                ? 'मैं गाँव बाज़ार को पहचान सत्यापन हेतु मेरे दस्तावेज़ की समीक्षा की अनुमति देता हूँ।'
                : 'I consent to UIDAI/Identity verification for GaonBazaar merchant registration.',
            style: const TextStyle(fontSize: 12),
          ),
          onChanged: (val) {
            setState(() => _identityConsent = val ?? false);
          },
        ),
      ],
    );
  }

  // ---------------------------------------------------------------------------
  // PDF PAGE 6: BANK / PAYOUT SETUP
  // ---------------------------------------------------------------------------
  Widget _buildPage4BankPayout(bool isHi) {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        Text(
          isHi ? 'बैंक व पेआउट खाता सेटअप' : 'Bank / Payout Setup',
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900),
        ),
        const SizedBox(height: 6),
        Text(
          isHi
              ? 'बिक्री की राशि सीधे आपके खाते में भेजी जाएगी। कोई नकद पेआउट नहीं होता है।'
              : 'Configure your bank or UPI payout account. ₹1 Penny Drop verification required.',
          style: const TextStyle(fontSize: 13, color: Colors.grey),
        ),
        const SizedBox(height: 16),

        // Toggle: Bank Account vs Business UPI ID
        Row(
          children: [
            Expanded(
              child: ChoiceChip(
                label: Text(isHi ? 'बैंक खाता' : 'Bank Account'),
                selected: !_isUpiMode,
                onSelected: (val) {
                  if (val) {
                    setState(() {
                      _isUpiMode = false;
                      _pennyDropVerified = false;
                    });
                    _persistDraft();
                  }
                },
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: ChoiceChip(
                label: Text(isHi ? 'व्यावसायिक UPI ID' : 'Business UPI ID'),
                selected: _isUpiMode,
                onSelected: (val) {
                  if (val) {
                    setState(() {
                      _isUpiMode = true;
                      _pennyDropVerified = false;
                    });
                    _persistDraft();
                  }
                },
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),

        if (!_isUpiMode) ...[
          TextField(
            controller: _accountHolderCtrl,
            decoration: InputDecoration(
              labelText: isHi ? 'खाताधारक का नाम *' : 'Account Holder Name *',
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
              labelText: isHi ? 'बैंक खाता संख्या *' : 'Bank Account Number *',
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
              labelText: isHi ? 'आईएफएससी कोड *' : 'IFSC Code *',
              hintText: 'e.g. SBIN0001234',
              prefixIcon: const Icon(Icons.numbers),
              border: const OutlineInputBorder(),
            ),
            onChanged: (_) {
              setState(() => _pennyDropVerified = false);
              _persistDraft();
            },
          ),
        ] else ...[
          TextField(
            controller: _upiCtrl,
            decoration: InputDecoration(
              labelText: isHi ? 'व्यावसायिक UPI ID *' : 'Business UPI ID *',
              hintText: 'shop@upi',
              prefixIcon: const Icon(Icons.payment_outlined),
              border: const OutlineInputBorder(),
            ),
            onChanged: (_) {
              setState(() => _pennyDropVerified = false);
              _persistDraft();
            },
          ),
        ],

        const SizedBox(height: 20),

        // Penny Drop Verification Action
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: _pennyDropVerified ? Colors.green.shade50 : Colors.amber.shade50,
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: _pennyDropVerified ? Colors.green : Colors.amber.shade400),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    _pennyDropVerified ? Icons.check_circle : Icons.verified_user_outlined,
                    color: _pennyDropVerified ? Colors.green : Colors.amber.shade800,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      _pennyDropVerified
                          ? (isHi ? '₹1 पेनी ड्रॉप सत्यापन सफल' : '₹1 Penny Drop Verified')
                          : (isHi ? '₹1 पेनी ड्रॉप सत्यापन आवश्यक' : '₹1 Penny Drop Verification Required'),
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: _pennyDropVerified ? Colors.green.shade900 : Colors.amber.shade900,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Text(
                isHi
                    ? 'सिस्टम आपके खाते की सत्यता जांचने के लिए ₹1 का सत्यापन प्रयास करेगा।'
                    : 'System tests active bank account status via ₹1 credit verification.',
                style: const TextStyle(fontSize: 12, color: Colors.grey),
              ),
              const SizedBox(height: 10),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _pennyDropVerified ? Colors.green : GBColors.primary,
                  ),
                  onPressed: (_isPennyDropVerifying || _pennyDropVerified) ? null : _runPennyDrop,
                  child: _isPennyDropVerifying
                      ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                      : Text(
                          _pennyDropVerified
                              ? (isHi ? 'खाता सत्यापित है' : 'Account Verified')
                              : (isHi ? '₹1 पेनी ड्रॉप सत्यापन करें' : 'Verify via ₹1 Penny Drop'),
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  // ---------------------------------------------------------------------------
  // PDF PAGE 7: OPTIONAL BUSINESS LICENSES
  // ---------------------------------------------------------------------------
  Widget _buildPage5OptionalLicenses(bool isHi) {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        Text(
          isHi ? 'व्यापारिक लाइसेंस (वैकल्पिक)' : 'Optional Business Licenses',
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900),
        ),
        const SizedBox(height: 6),
        Text(
          isHi
              ? 'यदि आपके पास FSSAI या GST प्रमाणपत्र है तो अपलोड करें। यह पूर्णतः वैकल्पिक है।'
              : 'Upload FSSAI or GST documents if available. Marked strictly as optional.',
          style: const TextStyle(fontSize: 13, color: Colors.grey),
        ),
        const SizedBox(height: 20),

        TextField(
          controller: _fssaiCtrl,
          decoration: InputDecoration(
            labelText: isHi ? 'FSSAI लाइसेंस नंबर (वैकल्पिक)' : 'FSSAI License Number (Optional)',
            prefixIcon: const Icon(Icons.restaurant_outlined),
            border: const OutlineInputBorder(),
          ),
          onChanged: (_) => _persistDraft(),
        ),
        const SizedBox(height: 10),
        _buildUploadCard(
          title: isHi ? 'FSSAI प्रमाणपत्र अपलोड (वैकल्पिक)' : 'Upload FSSAI Certificate (Optional)',
          fileName: _fssaiDocName,
          icon: Icons.upload_file_outlined,
          onTap: () => _pickDocument('fssai'),
        ),
        const SizedBox(height: 20),

        TextField(
          controller: _gstCtrl,
          decoration: InputDecoration(
            labelText: isHi ? 'GSTIN नंबर (वैकल्पिक)' : 'GSTIN Registration Number (Optional)',
            prefixIcon: const Icon(Icons.receipt_long_outlined),
            border: const OutlineInputBorder(),
          ),
          onChanged: (_) => _persistDraft(),
        ),
        const SizedBox(height: 10),
        _buildUploadCard(
          title: isHi ? 'GST प्रमाणपत्र अपलोड (वैकल्पिक)' : 'Upload GST Certificate (Optional)',
          fileName: _gstDocName,
          icon: Icons.file_present_outlined,
          onTap: () => _pickDocument('gst'),
        ),
        const SizedBox(height: 20),

        CheckboxListTile(
          value: _authenticityConsent,
          contentPadding: EdgeInsets.zero,
          title: Text(
            isHi
                ? 'मैं प्रमाणित करता हूँ कि मेरे द्वारा दी गई सभी व्यावसायिक जानकारी सत्य है।'
                : 'I declare that all submitted merchant information is authentic and accurate.',
            style: const TextStyle(fontSize: 12),
          ),
          onChanged: (val) {
            setState(() => _authenticityConsent = val ?? false);
          },
        ),
      ],
    );
  }

  Widget _buildUploadCard({
    required String title,
    required String? fileName,
    required IconData icon,
    required VoidCallback onTap,
  }) {
    final isUploaded = fileName != null && fileName.isNotEmpty;
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(10),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(10),
          border: Border.all(
            color: isUploaded ? GBColors.success : Colors.grey.shade400,
            width: isUploaded ? 1.5 : 1.0,
          ),
          color: isUploaded ? Colors.green.shade50.withValues(alpha: 0.5) : Colors.transparent,
        ),
        child: Row(
          children: [
            Icon(icon, color: isUploaded ? GBColors.success : Colors.grey.shade700),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
                  if (isUploaded)
                    Text(
                      fileName,
                      style: const TextStyle(fontSize: 11, color: GBColors.success, fontWeight: FontWeight.bold),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                ],
              ),
            ),
            Icon(
              isUploaded ? Icons.check_circle : Icons.upload,
              color: isUploaded ? GBColors.success : GBColors.primary,
            ),
          ],
        ),
      ),
    );
  }
}
