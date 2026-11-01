import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
import 'package:shared_models/shared_models.dart';
import '../state/app_state.dart';

class MapPickerScreen extends StatefulWidget {
  const MapPickerScreen({super.key});

  @override
  State<MapPickerScreen> createState() => _MapPickerScreenState();
}

class _MapPickerScreenState extends State<MapPickerScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  // Reference Minapur Hub coordinates
  static const double hubLat = 26.2200;
  static const double hubLng = 85.3500;

  // Selected Pin Coordinates & State
  double _currentLat = 26.2230;
  double _currentLng = 85.3520;
  String _selectedVillage = 'Chaturshi';
  String _landmark = 'Near Gram Panchayat Bhavan';
  String _block = 'Minapur';
  String _district = 'Muzaffarpur';
  String _state = 'Bihar';
  String _pinCode = '843128';
  double _distanceKm = 0.8;
  bool _isServiceable = true;

  // Manual Form Controllers
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _villageController = TextEditingController();
  final _landmarkController = TextEditingController();
  final _houseController = TextEditingController();
  final _panchayatController = TextEditingController();
  final _postOfficeController = TextEditingController();
  final _blockController = TextEditingController(text: 'Minapur');
  final _districtController = TextEditingController(text: 'Muzaffarpur');
  final _stateController = TextEditingController(text: 'Bihar');
  final _pinController = TextEditingController(text: '843128');
  String _addressLabel = 'Home';

  // Pilot Localities in Minapur Block
  final List<Map<String, dynamic>> _pilotLocations = [
    {
      'village': 'Chaturshi',
      'village_hi': 'चतुर्शी',
      'landmark': 'Near Gram Panchayat Bhavan',
      'landmark_hi': 'ग्राम पंचायत भवन के पास',
      'lat': 26.2230,
      'lng': 85.3520,
    },
    {
      'village': 'Tubanaghara',
      'village_hi': 'तुबानाघरा (बेनाघरा)',
      'landmark': 'Near Middle School Chowk',
      'landmark_hi': 'मिडिल स्कूल चौक के पास',
      'lat': 26.2080,
      'lng': 85.3370,
    },
    {
      'village': 'Sivay Patti',
      'village_hi': 'सिवाय पट्टी',
      'landmark': 'Near Shiv Mandir Chowk',
      'landmark_hi': 'शिव मंदिर चौक के पास',
      'lat': 26.2310,
      'lng': 85.3610,
    },
    {
      'village': 'Tulsi Ganj',
      'village_hi': 'तुलसी गंज (बनगांव)',
      'landmark': 'Near Market Chowk',
      'landmark_hi': 'बाजार चौक के पास',
      'lat': 26.1980,
      'lng': 85.3420,
    },
    {
      'village': 'Kanti Border (Outside 8.0 km)',
      'village_hi': 'कांटी बॉर्डर (8.0 किमी बाहर)',
      'landmark': 'Highway Toll Plaza',
      'landmark_hi': 'हाईवे टोल प्लाजा के पास',
      'lat': 26.2900,
      'lng': 85.4400,
    },
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _calculateServiceability();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final state = AppStateProvider.of(context);
    if (_nameController.text.isEmpty && state.currentUser != null) {
      final currentUserName = state.currentUser?.name;
      _nameController.text = (currentUserName != null && currentUserName.isNotEmpty)
          ? currentUserName
          : 'Customer';
      _phoneController.text = state.currentUser!.phone;
    }
  }

  @override
  void dispose() {
    _tabController.dispose();
    _nameController.dispose();
    _phoneController.dispose();
    _villageController.dispose();
    _landmarkController.dispose();
    _houseController.dispose();
    _panchayatController.dispose();
    _postOfficeController.dispose();
    _blockController.dispose();
    _districtController.dispose();
    _stateController.dispose();
    _pinController.dispose();
    super.dispose();
  }

  double _haversineKm(double lat1, double lon1, double lat2, double lon2) {
    const p = 0.017453292519943295;
    final a = 0.5 -
        math.cos((lat2 - lat1) * p) / 2 +
        math.cos(lat1 * p) * math.cos(lat2 * p) * (1 - math.cos((lon2 - lon1) * p)) / 2;
    return 12742 * math.asin(math.sqrt(a));
  }

  void _calculateServiceability() {
    final dist = _haversineKm(hubLat, hubLng, _currentLat, _currentLng);
    setState(() {
      _distanceKm = double.parse(dist.toStringAsFixed(1));
      _isServiceable = _distanceKm <= 8.0;
    });
  }

  void _selectPilotLocation(Map<String, dynamic> loc) {
    setState(() {
      _currentLat = loc['lat'] as double;
      _currentLng = loc['lng'] as double;
      _selectedVillage = loc['village'] as String;
      _landmark = loc['landmark'] as String;
      _calculateServiceability();
    });
  }

  void _confirmAndSaveCurrent() async {
    if (!_isServiceable) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Cannot deliver beyond 8.0 km service area! (8.0 किमी सीमा से बाहर)'),
          backgroundColor: GBColors.error,
        ),
      );
      return;
    }

    final state = AppStateProvider.of(context);
    final addr = GBAddress(
      id: 'addr_${DateTime.now().millisecondsSinceEpoch}',
      userId: state.currentUser?.id ?? 'usr_guest',
      title: _addressLabel,
      recipientName: _nameController.text.trim().isNotEmpty
          ? _nameController.text.trim()
          : (state.currentUser?.name ?? 'Customer'),
      phone: _phoneController.text.trim().isNotEmpty
          ? _phoneController.text.trim()
          : (state.currentUser?.phone ?? '9876543210'),
      latitude: _currentLat,
      longitude: _currentLng,
      village: _selectedVillage,
      landmark: _landmark,
      block: _block,
      district: _district,
      state: _state,
      pinCode: _pinCode,
      isDefault: true,
    );

    await state.saveAddress(addr);
    state.setAddress(addr);
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Address saved successfully (पता सफलतापूर्वक सहेजा गया)'),
        backgroundColor: GBColors.success,
      ),
    );
    Navigator.of(context).pop();
  }

  void _saveManualAddress() async {
    if (!_formKey.currentState!.validate()) return;

    final state = AppStateProvider.of(context);
    final addr = GBAddress(
      id: 'addr_${DateTime.now().millisecondsSinceEpoch}',
      userId: state.currentUser?.id ?? 'usr_guest',
      title: _addressLabel,
      recipientName: _nameController.text.trim(),
      phone: _phoneController.text.trim(),
      latitude: _currentLat,
      longitude: _currentLng,
      village: _villageController.text.trim(),
      landmark: _landmarkController.text.trim(),
      houseNumber: _houseController.text.trim(),
      panchayat: _panchayatController.text.trim(),
      postOffice: _postOfficeController.text.trim(),
      block: _blockController.text.trim(),
      district: _districtController.text.trim(),
      state: _stateController.text.trim(),
      pinCode: _pinController.text.trim(),
      isDefault: true,
    );

    await state.saveAddress(addr);
    state.setAddress(addr);
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Manual address saved successfully'),
        backgroundColor: GBColors.success,
      ),
    );
    Navigator.of(context).pop();
  }

  @override
  Widget build(BuildContext context) {
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: Text(
          loc.tr('addresses_title'),
          style: const TextStyle(fontWeight: FontWeight.w800),
        ),
        bottom: TabBar(
          controller: _tabController,
          isScrollable: true,
          labelColor: GBColors.primary,
          unselectedLabelColor: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
          indicatorColor: GBColors.primary,
          indicatorWeight: 3,
          tabs: [
            Tab(icon: const Icon(Icons.gps_fixed, size: 20), text: loc.tr('method_gps')),
            Tab(icon: const Icon(Icons.map_outlined, size: 20), text: loc.tr('method_map')),
            Tab(icon: const Icon(Icons.edit_note, size: 20), text: loc.tr('method_manual')),
            Tab(icon: const Icon(Icons.bookmark_outline, size: 20), text: loc.tr('method_saved')),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          // 1. GPS Option
          _buildGpsTab(loc, isDark),
          // 2. Map Pin Option
          _buildMapPinTab(loc, isDark),
          // 3. Manual Form Option
          _buildManualFormTab(loc, isDark),
          // 4. Saved Addresses Option
          _buildSavedAddressesTab(loc, isDark),
        ],
      ),
    );
  }

  // TAB 1: GPS Automatic Location
  Widget _buildGpsTab(GBLocalizations loc, bool isDark) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        children: [
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: GBColors.primary.withOpacity(0.12),
            ),
            child: const Icon(Icons.my_location, size: 64, color: GBColors.primary),
          ),
          const SizedBox(height: 24),
          Text(
            loc.isHindi ? 'वर्तमान जीपीएस स्थान का उपयोग करें' : 'Detecting Device GPS Location',
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800),
          ),
          const SizedBox(height: 8),
          Text(
            loc.isHindi
                ? 'मीनापुर में आपका निकटतम गाँव स्वतः खोजा गया है।'
                : 'High-precision village coordinates verified within Minapur Block.',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 13,
              color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
            ),
          ),
          const SizedBox(height: 24),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: isDark ? GBColors.cardDark : Colors.white,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(
                color: isDark ? GBColors.borderDark : GBColors.borderLight,
              ),
            ),
            child: Column(
              children: [
                _buildAddressInfoRow(Icons.location_city, loc.tr('village_name'), _selectedVillage),
                const Divider(height: 18),
                _buildAddressInfoRow(Icons.place, loc.tr('landmark'), _landmark),
                const Divider(height: 18),
                _buildAddressInfoRow(Icons.domain, loc.tr('block'), '$_block, $_district, $_state - $_pinCode'),
                const Divider(height: 18),
                Row(
                  children: [
                    Icon(
                      _isServiceable ? Icons.check_circle : Icons.error,
                      color: _isServiceable ? GBColors.success : GBColors.error,
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        _isServiceable
                            ? '${loc.tr('distance_check_pass')} ($_distanceKm km)'
                            : '${loc.tr('distance_check_fail')} ($_distanceKm km)',
                        style: TextStyle(
                          fontWeight: FontWeight.w700,
                          fontSize: 13,
                          color: _isServiceable ? GBColors.success : GBColors.error,
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 28),
          GBPrimaryButton(
            label: loc.isHindi ? 'इस जीपीएस पते का उपयोग करें' : 'Confirm & Use This GPS Address',
            onPressed: _confirmAndSaveCurrent,
          ),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            icon: const Icon(Icons.refresh, size: 18),
            label: Text(loc.isHindi ? 'जीपीएस रिफ्रेश करें' : 'Refresh GPS Coordinates'),
            style: OutlinedButton.styleFrom(
              minimumSize: const Size.fromHeight(46),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
            onPressed: () {
              _selectPilotLocation(_pilotLocations[0]);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('GPS coordinates refreshed (26.2230, 85.3520)'),
                  duration: Duration(seconds: 1),
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  // TAB 2: Map Pin Simulation & Localities
  Widget _buildMapPinTab(GBLocalizations loc, bool isDark) {
    return Column(
      children: [
        // Map Representation
        Expanded(
          flex: 4,
          child: Stack(
            alignment: Alignment.center,
            children: [
              Container(
                width: double.infinity,
                color: isDark ? const Color(0xFF1B2838) : const Color(0xFFE5F0E6),
                child: CustomPaint(painter: _MapGridPainter(isDark: isDark)),
              ),
              Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.black.withOpacity(0.8),
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Text(
                      _selectedVillage,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 11,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                  const SizedBox(height: 4),
                  const Icon(Icons.location_pin, size: 48, color: GBColors.primary),
                ],
              ),
              Positioned(
                left: 14,
                top: 14,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.92),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(
                      color: _isServiceable ? GBColors.success : GBColors.error,
                      width: 1.5,
                    ),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        _isServiceable ? Icons.check_circle : Icons.error,
                        size: 16,
                        color: _isServiceable ? GBColors.success : GBColors.error,
                      ),
                      const SizedBox(width: 6),
                      Text(
                        _isServiceable
                            ? 'Within 8.0 km (${_distanceKm} km)'
                            : 'Outside 8.0 km (${_distanceKm} km)',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w700,
                          color: _isServiceable ? GBColors.success : GBColors.error,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),

        // Pilot Localities Selector
        Expanded(
          flex: 5,
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: isDark ? GBColors.cardDark : Colors.white,
              borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
              boxShadow: [
                BoxShadow(color: Colors.black.withOpacity(0.08), blurRadius: 8, offset: const Offset(0, -3)),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  loc.isHindi ? 'मीनापुर पायलट गाँव सूची:' : 'Select Minapur Pilot Locality:',
                  style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
                ),
                const SizedBox(height: 10),
                Expanded(
                  child: ListView.builder(
                    itemCount: _pilotLocations.length,
                    itemBuilder: (context, idx) {
                      final item = _pilotLocations[idx];
                      final isSelected = item['village'] == _selectedVillage;
                      final dist = _haversineKm(hubLat, hubLng, item['lat'] as double, item['lng'] as double);
                      final distStr = dist.toStringAsFixed(1);
                      final isWithin = dist <= 8.0;

                      return InkWell(
                        onTap: () => _selectPilotLocation(item),
                        borderRadius: BorderRadius.circular(10),
                        child: Container(
                          margin: const EdgeInsets.only(bottom: 8),
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                          decoration: BoxDecoration(
                            color: isSelected
                                ? GBColors.primary.withOpacity(0.08)
                                : Colors.transparent,
                            borderRadius: BorderRadius.circular(10),
                            border: Border.all(
                              color: isSelected ? GBColors.primary : Colors.grey.shade300,
                            ),
                          ),
                          child: Row(
                            children: [
                              Icon(
                                isWithin ? Icons.location_on : Icons.location_off,
                                size: 20,
                                color: isWithin ? (isSelected ? GBColors.primary : Colors.grey) : GBColors.error,
                              ),
                              const SizedBox(width: 10),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      loc.isHindi ? item['village_hi'] : item['village'],
                                      style: TextStyle(
                                        fontWeight: FontWeight.w700,
                                        fontSize: 13,
                                        color: isSelected ? GBColors.primary : null,
                                      ),
                                    ),
                                    Text(
                                      loc.isHindi ? item['landmark_hi'] : item['landmark'],
                                      style: const TextStyle(fontSize: 11, color: Colors.grey),
                                    ),
                                  ],
                                ),
                              ),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                decoration: BoxDecoration(
                                  color: isWithin ? Colors.green.withOpacity(0.1) : Colors.red.withOpacity(0.1),
                                  borderRadius: BorderRadius.circular(4),
                                ),
                                child: Text(
                                  '$distStr km',
                                  style: TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.w700,
                                    color: isWithin ? GBColors.success : GBColors.error,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),
                const SizedBox(height: 10),
                GBPrimaryButton(
                  label: _isServiceable
                      ? (loc.isHindi ? 'यह स्थान पक्का करें' : 'Confirm Location')
                      : (loc.isHindi ? '8.0 किमी से बाहर (अनुमति नहीं)' : 'Outside 8.0 km Radius'),
                  onPressed: _isServiceable ? _confirmAndSaveCurrent : null,
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  // TAB 3: Rural Manual Address Form
  Widget _buildManualFormTab(GBLocalizations loc, bool isDark) {
    return Form(
      key: _formKey,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text(
            loc.isHindi ? 'ग्रामीण डिलीवरी पता प्रपत्र' : 'Rural Delivery Address Form',
            style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
          ),
          const SizedBox(height: 6),
          Text(
            loc.isHindi
                ? 'सटीक गांव, टोला और लैंडमार्क भरें ताकि डिलीवरी साथी आसानी से पहुंच सके।'
                : 'Enter accurate village, tola, and landmark for reliable delivery.',
            style: TextStyle(
              fontSize: 12,
              color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
            ),
          ),
          const SizedBox(height: 16),

          // Contact Person Name
          TextFormField(
            controller: _nameController,
            decoration: InputDecoration(
              labelText: loc.tr('contact_name'),
              prefixIcon: const Icon(Icons.person_outline),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
            ),
            validator: (val) => (val == null || val.trim().isEmpty) ? 'Required' : null,
          ),
          const SizedBox(height: 12),

          // Contact Mobile
          TextFormField(
            controller: _phoneController,
            keyboardType: TextInputType.phone,
            decoration: InputDecoration(
              labelText: loc.tr('contact_phone'),
              prefixIcon: const Icon(Icons.phone_outlined),
              prefixText: '+91 ',
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
            ),
            validator: (val) {
              if (val == null || val.trim().isEmpty) return 'Required';
              if (!RegExp(r'^[6-9]\d{9}$').hasMatch(val.trim())) return 'Enter 10-digit mobile';
              return null;
            },
          ),
          const SizedBox(height: 12),

          // Village / Locality
          TextFormField(
            controller: _villageController,
            decoration: InputDecoration(
              labelText: loc.tr('village_name'),
              prefixIcon: const Icon(Icons.location_city_outlined),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
            ),
            validator: (val) => (val == null || val.trim().isEmpty) ? 'Required' : null,
          ),
          const SizedBox(height: 12),

          // Landmark
          TextFormField(
            controller: _landmarkController,
            decoration: InputDecoration(
              labelText: loc.tr('landmark'),
              prefixIcon: const Icon(Icons.place_outlined),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
            ),
            validator: (val) => (val == null || val.trim().isEmpty) ? 'Required' : null,
          ),
          const SizedBox(height: 12),

          // House / Household Name
          TextFormField(
            controller: _houseController,
            decoration: InputDecoration(
              labelText: loc.tr('house_identifier'),
              prefixIcon: const Icon(Icons.home_outlined),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
            ),
          ),
          const SizedBox(height: 12),

          // Gram Panchayat & Post Office in a Row
          Row(
            children: [
              Expanded(
                child: TextFormField(
                  controller: _panchayatController,
                  decoration: InputDecoration(
                    labelText: loc.tr('panchayat'),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: TextFormField(
                  controller: _postOfficeController,
                  decoration: InputDecoration(
                    labelText: loc.tr('post_office'),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Block, District, State & PIN
          Row(
            children: [
              Expanded(
                child: TextFormField(
                  controller: _blockController,
                  decoration: InputDecoration(
                    labelText: loc.tr('block'),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                  validator: (val) => (val == null || val.trim().isEmpty) ? 'Required' : null,
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: TextFormField(
                  controller: _districtController,
                  decoration: InputDecoration(
                    labelText: loc.tr('district'),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                  validator: (val) => (val == null || val.trim().isEmpty) ? 'Required' : null,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          Row(
            children: [
              Expanded(
                child: TextFormField(
                  controller: _stateController,
                  decoration: InputDecoration(
                    labelText: loc.tr('state'),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: TextFormField(
                  controller: _pinController,
                  keyboardType: TextInputType.number,
                  decoration: InputDecoration(
                    labelText: loc.tr('pincode'),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),

          // Address Label Chips
          Text(
            loc.tr('address_label'),
            style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              ChoiceChip(
                label: Text(loc.tr('label_home')),
                selected: _addressLabel == 'Home',
                onSelected: (sel) => setState(() => _addressLabel = 'Home'),
              ),
              const SizedBox(width: 8),
              ChoiceChip(
                label: Text(loc.tr('label_work')),
                selected: _addressLabel == 'Work',
                onSelected: (sel) => setState(() => _addressLabel = 'Work'),
              ),
              const SizedBox(width: 8),
              ChoiceChip(
                label: Text(loc.tr('label_other')),
                selected: _addressLabel == 'Other',
                onSelected: (sel) => setState(() => _addressLabel = 'Other'),
              ),
            ],
          ),
          const SizedBox(height: 24),

          GBPrimaryButton(
            label: loc.tr('save_address_btn'),
            onPressed: _saveManualAddress,
          ),
          const SizedBox(height: 20),
        ],
      ),
    );
  }

  // TAB 4: Saved Addresses List
  Widget _buildSavedAddressesTab(GBLocalizations loc, bool isDark) {
    final state = AppStateProvider.of(context);
    final saved = state.savedAddresses;

    if (saved.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.bookmark_border, size: 56, color: Colors.grey),
              const SizedBox(height: 12),
              Text(
                loc.isHindi ? 'कोई सहेजा गया पता नहीं मिला' : 'No Saved Addresses Found',
                style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 16),
              ),
              const SizedBox(height: 6),
              Text(
                loc.isHindi
                    ? 'जीपीएस, मानचित्र या मैन्युअल फॉर्म से एक नया पता जोड़ें।'
                    : 'Add a new address using GPS, Map Pin, or Manual Form above.',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 12,
                  color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
                ),
              ),
              const SizedBox(height: 18),
              ElevatedButton.icon(
                icon: const Icon(Icons.add_location_alt_outlined, size: 18),
                label: Text(loc.tr('add_new_address')),
                onPressed: () => _tabController.animateTo(2),
              ),
            ],
          ),
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: saved.length,
      itemBuilder: (context, idx) {
        final addr = saved[idx];
        final isSelected = addr.id == state.selectedAddress.id;

        return Container(
          margin: const EdgeInsets.only(bottom: 12),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: isDark ? GBColors.cardDark : Colors.white,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(
              color: isSelected ? GBColors.primary : (isDark ? GBColors.borderDark : GBColors.borderLight),
              width: isSelected ? 2 : 1,
            ),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    addr.title.toLowerCase() == 'work' ? Icons.work_outline : Icons.home_outlined,
                    color: GBColors.primary,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    addr.title,
                    style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
                  ),
                  const Spacer(),
                  if (isSelected)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: GBColors.primary.withOpacity(0.12),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        loc.isHindi ? 'सक्रिय पता' : 'Active Address',
                        style: const TextStyle(
                          fontSize: 10,
                          fontWeight: FontWeight.w700,
                          color: GBColors.primary,
                        ),
                      ),
                    ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                '${addr.recipientName} • +91 ${addr.phone}',
                style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
              ),
              const SizedBox(height: 4),
              Text(
                addr.readableAddress,
                style: TextStyle(
                  fontSize: 12,
                  height: 1.4,
                  color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
                ),
              ),
              const SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  TextButton.icon(
                    icon: const Icon(Icons.delete_outline, size: 16, color: GBColors.error),
                    label: Text(
                      loc.tr('delete_address'),
                      style: const TextStyle(color: GBColors.error, fontSize: 12),
                    ),
                    onPressed: () async {
                      await state.deleteAddress(addr.id);
                    },
                  ),
                  const SizedBox(width: 8),
                  ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: isSelected ? Colors.grey.shade400 : GBColors.primary,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                    ),
                    onPressed: isSelected
                        ? null
                        : () {
                            state.setAddress(addr);
                            Navigator.of(context).pop();
                          },
                    child: Text(
                      isSelected
                          ? (loc.isHindi ? 'चयनित' : 'Selected')
                          : (loc.isHindi ? 'इस पते पर भेजें' : 'Deliver Here'),
                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700),
                    ),
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildAddressInfoRow(IconData icon, String label, String value) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 18, color: GBColors.primary),
        const SizedBox(width: 10),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(label, style: const TextStyle(fontSize: 11, color: Colors.grey)),
              const SizedBox(height: 2),
              Text(value, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13)),
            ],
          ),
        ),
      ],
    );
  }
}

class _MapGridPainter extends CustomPainter {
  final bool isDark;
  _MapGridPainter({required this.isDark});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = isDark ? Colors.white.withOpacity(0.04) : Colors.black.withOpacity(0.04)
      ..strokeWidth = 1;

    for (double i = 0; i < size.width; i += 30) {
      canvas.drawLine(Offset(i, 0), Offset(i, size.height), paint);
    }
    for (double j = 0; j < size.height; j += 30) {
      canvas.drawLine(Offset(0, j), Offset(size.width, j), paint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
