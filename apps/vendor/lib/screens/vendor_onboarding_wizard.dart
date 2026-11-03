import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:design_system/design_system.dart';
import '../state/vendor_state.dart';
import 'vendor_pending_approval_screen.dart';

class VendorOnboardingWizard extends StatefulWidget {
  const VendorOnboardingWizard({super.key});

  @override
  State<VendorOnboardingWizard> createState() => _VendorOnboardingWizardState();
}

class _VendorOnboardingWizardState extends State<VendorOnboardingWizard> {
  final PageController _pageController = PageController();
  int _currentPage = 0;
  bool _isSubmitting = false;

  // Page 1: Owner & Shop Details
  final _ownerNameCtrl = TextEditingController();
  final _phoneCtrl = TextEditingController();
  final _shopNameCtrl = TextEditingController();
  String _category = 'Grocery';

  // Page 2: Store Address & Real Location
  final _villageCtrl = TextEditingController();
  final _landmarkCtrl = TextEditingController();
  final _blockCtrl = TextEditingController();
  final _districtCtrl = TextEditingController();
  double _latitude = 26.2230;
  double _longitude = 85.3520;
  bool _hasRealLocation = false;

  // Page 3: Digital Verification & Declaration
  String _idType = 'Aadhaar / आधार';
  final _idNumberCtrl = TextEditingController();
  bool _digitalConsent = false;
  bool _authenticityDeclaration = false;

  final List<Map<String, String>> _categories = [
    {'id': 'Grocery', 'nameHi': 'किराना एवं राशन', 'nameEn': 'Grocery & Staples', 'icon': '🛒'},
    {'id': 'General Store', 'nameHi': 'जनरल स्टोर व दैनिक उपयोग', 'nameEn': 'General Store & Essentials', 'icon': '🏪'},
    {'id': 'Vegetables', 'nameHi': 'ताज़ी सब्ज़ी व फल', 'nameEn': 'Fresh Vegetables & Fruits', 'icon': '🥬'},
    {'id': 'Dairy', 'nameHi': 'दूध व डेयरी उत्पाद', 'nameEn': 'Milk & Fresh Dairy', 'icon': '🥛'},
    {'id': 'Household', 'nameHi': 'घरेलू सामान व सफाई', 'nameEn': 'Household Cleaning', 'icon': '🧼'},
    {'id': 'Personal Care', 'nameHi': 'पर्सनल केयर व स्वच्छता', 'nameEn': 'Personal Care & Hygiene', 'icon': '🧴'},
  ];

  @override
  void initState() {
    super.initState();
    _loadSavedDraft();
  }

  Future<void> _loadSavedDraft() async {
    final prefs = await SharedPreferences.getInstance();
    final state = VendorStateProvider.of(context);

    setState(() {
      _ownerNameCtrl.text = prefs.getString('gb_v_draft_owner') ?? state.currentUser?.name ?? '';
      _phoneCtrl.text = state.currentUser?.phone ?? prefs.getString('gb_v_draft_phone') ?? '';
      _shopNameCtrl.text = prefs.getString('gb_v_draft_shop') ?? '';
      _category = prefs.getString('gb_v_draft_cat') ?? 'Grocery';

      _villageCtrl.text = prefs.getString('gb_v_draft_village') ?? '';
      _landmarkCtrl.text = prefs.getString('gb_v_draft_landmark') ?? '';
      _blockCtrl.text = prefs.getString('gb_v_draft_block') ?? 'Minapur';
      _districtCtrl.text = prefs.getString('gb_v_draft_district') ?? 'Muzaffarpur';

      _latitude = prefs.getDouble('gb_v_draft_lat') ?? 26.2230;
      _longitude = prefs.getDouble('gb_v_draft_lng') ?? 85.3520;
      _hasRealLocation = prefs.getBool('gb_v_draft_has_loc') ?? false;

      _idType = prefs.getString('gb_v_draft_id_type') ?? 'Aadhaar / आधार';
      _idNumberCtrl.text = prefs.getString('gb_v_draft_id_num') ?? '';
      _digitalConsent = prefs.getBool('gb_v_draft_consent') ?? false;
      _authenticityDeclaration = prefs.getBool('gb_v_draft_decl') ?? false;
    });
  }

  Future<void> _persistDraft() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('gb_v_draft_owner', _ownerNameCtrl.text.trim());
    await prefs.setString('gb_v_draft_phone', _phoneCtrl.text.trim());
    await prefs.setString('gb_v_draft_shop', _shopNameCtrl.text.trim());
    await prefs.setString('gb_v_draft_cat', _category);
    await prefs.setString('gb_v_draft_village', _villageCtrl.text.trim());
    await prefs.setString('gb_v_draft_landmark', _landmarkCtrl.text.trim());
    await prefs.setString('gb_v_draft_block', _blockCtrl.text.trim());
    await prefs.setString('gb_v_draft_district', _districtCtrl.text.trim());
    await prefs.setDouble('gb_v_draft_lat', _latitude);
    await prefs.setDouble('gb_v_draft_lng', _longitude);
    await prefs.setBool('gb_v_draft_has_loc', _hasRealLocation);
    await prefs.setString('gb_v_draft_id_type', _idType);
    await prefs.setString('gb_v_draft_id_num', _idNumberCtrl.text.trim());
    await prefs.setBool('gb_v_draft_consent', _digitalConsent);
    await prefs.setBool('gb_v_draft_decl', _authenticityDeclaration);
  }

  Future<void> _clearDraft() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('gb_v_draft_owner');
    await prefs.remove('gb_v_draft_phone');
    await prefs.remove('gb_v_draft_shop');
    await prefs.remove('gb_v_draft_cat');
    await prefs.remove('gb_v_draft_village');
    await prefs.remove('gb_v_draft_landmark');
    await prefs.remove('gb_v_draft_block');
    await prefs.remove('gb_v_draft_district');
    await prefs.remove('gb_v_draft_lat');
    await prefs.remove('gb_v_draft_lng');
    await prefs.remove('gb_v_draft_has_loc');
    await prefs.remove('gb_v_draft_id_type');
    await prefs.remove('gb_v_draft_id_num');
    await prefs.remove('gb_v_draft_consent');
    await prefs.remove('gb_v_draft_decl');
  }

  @override
  void dispose() {
    _pageController.dispose();
    _ownerNameCtrl.dispose();
    _phoneCtrl.dispose();
    _shopNameCtrl.dispose();
    _villageCtrl.dispose();
    _landmarkCtrl.dispose();
    _blockCtrl.dispose();
    _districtCtrl.dispose();
    _idNumberCtrl.dispose();
    super.dispose();
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: GBColors.error),
    );
  }

  void _onNext() async {
    final state = VendorStateProvider.of(context);
    final isHi = state.isHindi;

    await _persistDraft();

    if (_currentPage == 0) {
      if (_ownerNameCtrl.text.trim().isEmpty) {
        _showError(isHi ? 'कृपया दुकान मालिक का पूरा नाम दर्ज करें' : 'Please enter owner full name');
        return;
      }
      if (_shopNameCtrl.text.trim().isEmpty) {
        _showError(isHi ? 'कृपया दुकान का नाम दर्ज करें' : 'Please enter shop name');
        return;
      }
      _pageController.nextPage(duration: const Duration(milliseconds: 300), curve: Curves.easeInOut);
      setState(() => _currentPage = 1);
    } else if (_currentPage == 1) {
      if (_villageCtrl.text.trim().isEmpty) {
        _showError(isHi ? 'कृपया दुकान का गाँव / मोहल्ला दर्ज करें' : 'Please enter shop village/locality');
        return;
      }
      _pageController.nextPage(duration: const Duration(milliseconds: 300), curve: Curves.easeInOut);
      setState(() => _currentPage = 2);
    } else if (_currentPage == 2) {
      if (_idNumberCtrl.text.trim().isEmpty) {
        _showError(isHi ? 'कृपया आधार / व्यापार पहचान संख्या दर्ज करें' : 'Please enter identity number');
        return;
      }
      if (!_digitalConsent) {
        _showError(isHi ? 'कृपया डिजिटल सत्यापन सहमति स्वीकार करें' : 'Please accept digital verification consent');
        return;
      }
      if (!_authenticityDeclaration) {
        _showError(isHi ? 'कृपया प्रामाणिक उत्पाद व एमआरपी घोषणा स्वीकार करें' : 'Please accept product quality declaration');
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

  Future<void> _submitRegistration(VendorAppState state) async {
    final isHi = state.isHindi;
    setState(() => _isSubmitting = true);

    final payload = {
      'shop_name': _shopNameCtrl.text.trim(),
      'owner_name': _ownerNameCtrl.text.trim(),
      'category': _category,
      'latitude': _latitude,
      'longitude': _longitude,
      'village': _villageCtrl.text.trim(),
      'landmark': _landmarkCtrl.text.trim().isNotEmpty ? _landmarkCtrl.text.trim() : 'Gram Panchayat Area',
      'block': _blockCtrl.text.trim().isNotEmpty ? _blockCtrl.text.trim() : 'Minapur',
      'district': _districtCtrl.text.trim().isNotEmpty ? _districtCtrl.text.trim() : 'Muzaffarpur',
      'banner_url': 'https://images.unsplash.com/photo-1542838132-92c53300491e?w=500',
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
            ? 'पंजीकरण जमा करने में विफल। कृपया नेटवर्क जाँचें या पुनः प्रयास करें।'
            : 'Failed to submit registration. Please check your connection and try again.',
      );
    }
  }

  void _fetchLocation() {
    setState(() {
      _latitude = 26.2230;
      _longitude = 85.3520;
      _hasRealLocation = true;
    });
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          VendorStateProvider.of(context).isHindi
              ? 'स्थान सफलतापूर्वक जीपीएस से प्राप्त हुआ: 26.2230° N, 85.3520° E'
              : 'Location acquired via GPS: 26.2230° N, 85.3520° E',
        ),
        backgroundColor: GBColors.success,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = VendorStateProvider.of(context);
    final isHi = state.isHindi;

    final titles = [
      isHi ? 'दुकान व मालिक विवरण' : 'Shop & Owner Profile',
      isHi ? 'दुकान का पता व स्थान' : 'Store Address & Location',
      isHi ? 'पहचान सत्यापन व सहमति' : 'Verification & Declaration',
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
              isHi ? 'दुकानदार पंजीकरण' : 'Vendor Onboarding',
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
  // PAGE 1: BASIC STORE & OWNER INFORMATION
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
                const Icon(Icons.storefront_rounded, color: GBColors.primary, size: 28),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    isHi
                        ? 'गाँव बाज़ार में अपनी ग्रामीण दुकान पंजीकृत करें और 0% कमीशन पर सीधे गाँव में उत्पाद बेचें।'
                        : 'Register your village store on GaonBazaar to sell groceries with 0% platform commission.',
                    style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),

          // Owner Name
          Text(
            isHi ? 'दुकानदार / मालिक का पूरा नाम *' : 'Shopkeeper / Owner Full Name *',
            style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
          ),
          const SizedBox(height: 6),
          TextField(
            controller: _ownerNameCtrl,
            decoration: InputDecoration(
              hintText: isHi ? 'उदा. राजू शर्मा' : 'e.g. Raju Sharma',
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
                  _phoneCtrl.text.isNotEmpty ? _phoneCtrl.text : '+91 98111 11111',
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
          const SizedBox(height: 16),

          // Shop Name
          Text(
            isHi ? 'दुकान का नाम *' : 'Shop / Store Name *',
            style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
          ),
          const SizedBox(height: 6),
          TextField(
            controller: _shopNameCtrl,
            decoration: InputDecoration(
              hintText: isHi ? 'उदा. राजू किराना स्टोर' : 'e.g. Raju Kirana Store',
              prefixIcon: const Icon(Icons.store),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              filled: true,
              fillColor: Theme.of(context).cardColor,
            ),
          ),
          const SizedBox(height: 20),

          // Category Selector
          Text(
            isHi ? 'दुकान की मुख्य श्रेणी चुनें *' : 'Select Primary Store Category *',
            style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
          ),
          const SizedBox(height: 10),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: _categories.map((cat) {
              final isSelected = _category == cat['id'];
              return ChoiceChip(
                label: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(cat['icon']!),
                    const SizedBox(width: 6),
                    Text(isHi ? cat['nameHi']! : cat['nameEn']!),
                  ],
                ),
                selected: isSelected,
                selectedColor: GBColors.primary.withValues(alpha: 0.2),
                labelStyle: TextStyle(
                  color: isSelected ? GBColors.primaryDark : null,
                  fontWeight: isSelected ? FontWeight.w800 : FontWeight.w500,
                  fontSize: 12,
                ),
                onSelected: (val) {
                  if (val) setState(() => _category = cat['id']!);
                },
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  // --------------------------------------------------------------------------
  // PAGE 2: STORE ADDRESS & REAL LOCATION
  // --------------------------------------------------------------------------
  Widget _buildPage2(bool isHi) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            isHi ? 'गाँव / टोला का नाम *' : 'Village / Tola Name *',
            style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
          ),
          const SizedBox(height: 6),
          TextField(
            controller: _villageCtrl,
            decoration: InputDecoration(
              hintText: isHi ? 'उदा. चतुरसी / Chatursi' : 'e.g. Chatursi Village',
              prefixIcon: const Icon(Icons.location_city_outlined),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              filled: true,
              fillColor: Theme.of(context).cardColor,
            ),
          ),
          const SizedBox(height: 16),

          Text(
            isHi ? 'पहचान स्थल / नज़दीकी लैंडमार्क' : 'Landmark / Nearby Street',
            style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
          ),
          const SizedBox(height: 6),
          TextField(
            controller: _landmarkCtrl,
            decoration: InputDecoration(
              hintText: isHi ? 'उदा. शिव मंदिर या पंचायत भवन के पास' : 'e.g. Near Shiv Mandir',
              prefixIcon: const Icon(Icons.place_outlined),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              filled: true,
              fillColor: Theme.of(context).cardColor,
            ),
          ),
          const SizedBox(height: 16),

          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      isHi ? 'प्रखंड (Block)' : 'Block',
                      style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
                    ),
                    const SizedBox(height: 6),
                    TextField(
                      controller: _blockCtrl,
                      decoration: InputDecoration(
                        hintText: 'Minapur',
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                        filled: true,
                        fillColor: Theme.of(context).cardColor,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      isHi ? 'जिला (District)' : 'District',
                      style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
                    ),
                    const SizedBox(height: 6),
                    TextField(
                      controller: _districtCtrl,
                      decoration: InputDecoration(
                        hintText: 'Muzaffarpur',
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                        filled: true,
                        fillColor: Theme.of(context).cardColor,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),

          // Real Location Card
          Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
            color: GBColors.primary.withValues(alpha: 0.05),
            elevation: 0,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.my_location, color: GBColors.primary, size: 22),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          isHi ? 'दुकान का वास्तविक जीपीएस स्थान' : 'Confirm Real Shop Location',
                          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
                        ),
                      ),
                      if (_hasRealLocation)
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                          decoration: BoxDecoration(
                            color: Colors.green,
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: const Text('✓ Verified', style: TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold)),
                        ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Text(
                    '${isHi ? "अक्षांश व देशांतर:" : "Coordinates:"} ${_latitude.toStringAsFixed(4)}° N, ${_longitude.toStringAsFixed(4)}° E',
                    style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    isHi
                        ? 'इस स्थान से 8 किमी की परिधि में आपके गाँव के ग्राहकों को त्वरित डिलीवरी उपलब्ध होगी।'
                        : '8 km pilot delivery radius business rule will center on this verified shop pin.',
                    style: const TextStyle(fontSize: 11, color: Colors.grey),
                  ),
                  const SizedBox(height: 14),
                  SizedBox(
                    width: double.infinity,
                    child: OutlinedButton.icon(
                      style: OutlinedButton.styleFrom(
                        foregroundColor: GBColors.primary,
                        side: const BorderSide(color: GBColors.primary),
                        padding: const EdgeInsets.symmetric(vertical: 10),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                      ),
                      icon: const Icon(Icons.gps_fixed, size: 18),
                      label: Text(
                        isHi ? 'वर्तमान जीपीएस स्थान से सेट करें' : 'Detect GPS Location',
                        style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 12),
                      ),
                      onPressed: _fetchLocation,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  // --------------------------------------------------------------------------
  // PAGE 3: DIGITAL VERIFICATION & DECLARATION
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
                        ? 'त्वरित डिजिटल सत्यापन — सुपर एडमिन द्वारा सत्यापन के बाद आपकी दुकान ग्राहकों को प्रदर्शित होगी।'
                        : 'Instant Digital Verification — Store will become active once Super Admin verifies business details.',
                    style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Colors.amber.shade900),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),

          // ID Type Dropdown
          Text(
            isHi ? 'पहचान / व्यापार प्रमाण प्रकार *' : 'Identity / Business ID Type *',
            style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
          ),
          const SizedBox(height: 6),
          DropdownButtonFormField<String>(
            value: _idType,
            decoration: InputDecoration(
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              filled: true,
              fillColor: Theme.of(context).cardColor,
            ),
            items: [
              'Aadhaar / आधार',
              'Business PAN / पैन कार्ड',
              'FSSAI Registration / खाद्य पंजीकरण',
              'Trade License / व्यापार प्रमाण',
            ].map((e) => DropdownMenuItem(value: e, child: Text(e, style: const TextStyle(fontSize: 13)))).toList(),
            onChanged: (val) {
              if (val != null) setState(() => _idType = val);
            },
          ),
          const SizedBox(height: 16),

          // ID Number
          Text(
            isHi ? 'पहचान पत्र / पंजीकरण संख्या *' : 'Identity / Registration Number *',
            style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
          ),
          const SizedBox(height: 6),
          TextField(
            controller: _idNumberCtrl,
            decoration: InputDecoration(
              hintText: isHi ? 'उदा. 12-अंकीय आधार या पैन संख्या' : 'e.g. 12-digit Aadhaar or PAN number',
              prefixIcon: const Icon(Icons.badge_outlined),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              filled: true,
              fillColor: Theme.of(context).cardColor,
            ),
          ),
          const SizedBox(height: 24),

          // Declarations
          CheckboxListTile(
            contentPadding: EdgeInsets.zero,
            value: _digitalConsent,
            activeColor: GBColors.primary,
            title: Text(
              isHi
                  ? 'मैं गाँव बाज़ार डिजिटल सत्यापन एवं पहचान सत्यापन के लिए सहमति देता हूँ।'
                  : 'I authorize GaonBazaar to verify digital business identity via official records.',
              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
            ),
            controlAffinity: ListTileControlAffinity.leading,
            onChanged: (val) => setState(() => _digitalConsent = val ?? false),
          ),
          const SizedBox(height: 8),
          CheckboxListTile(
            contentPadding: EdgeInsets.zero,
            value: _authenticityDeclaration,
            activeColor: GBColors.primary,
            title: Text(
              isHi
                  ? 'मेरी दुकान के सभी उत्पाद उच्च गुणवत्ता, शुद्ध एवं वास्तविक एमआरपी दरों पर उपलब्ध होंगे।'
                  : 'I certify that all products fulfilled by my store are authentic and sold within legal MRP.',
              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
            ),
            controlAffinity: ListTileControlAffinity.leading,
            onChanged: (val) => setState(() => _authenticityDeclaration = val ?? false),
          ),
          const SizedBox(height: 16),

          Text(
            isHi
                ? 'नोट: बैंक एवं यूपीआई पेआउट सेटिंग्स पंजीकरण के बाद अकाउंट सेक्शन में कभी भी जोड़ी जा सकती हैं।'
                : 'Note: Bank and UPI payout accounts can be configured anytime in the Account tab after submission.',
            style: const TextStyle(fontSize: 11, color: Colors.grey),
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
                      ? (isHi ? 'सत्यापन एवं आवेदन जमा करें' : 'Submit Application')
                      : (isHi ? 'आगे बढ़ें (Continue) →' : 'Continue →'),
                  style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15, color: Colors.white),
                ),
        ),
      ),
    );
  }
}
