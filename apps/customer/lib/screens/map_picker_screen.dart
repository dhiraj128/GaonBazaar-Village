import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:geolocator/geolocator.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
import 'package:shared_models/shared_models.dart';
import '../state/app_state.dart';

class MapPickerScreen extends StatefulWidget {
  const MapPickerScreen({super.key});

  @override
  State<MapPickerScreen> createState() => _MapPickerScreenState();
}

class _MapPickerScreenState extends State<MapPickerScreen> {
  // Step 0: Choose Delivery Location on Map
  // Step 1: Add Address Details
  int _step = 0;

  GoogleMapController? _mapController;
  bool _isLocating = false;
  bool _isSaving = false;

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

  void _updateCoordinates(double lat, double lng) {
    setState(() {
      _currentLat = lat;
      _currentLng = lng;
      String nearestVillage = 'Minapur Rural Locality';
      String nearestLandmark = 'Near Village Road Pin';
      double minD = 9999.0;
      for (final p in _pilotLocations) {
        final d = _haversineKm(lat, lng, p['lat'] as double, p['lng'] as double);
        if (d < minD) {
          minD = d;
          if (d <= 2.5) {
            nearestVillage = p['village'] as String;
            nearestLandmark = p['landmark'] as String;
          }
        }
      }
      _selectedVillage = nearestVillage;
      _landmark = nearestLandmark;
      _calculateServiceability();
    });
    if (_mapController != null) {
      _mapController!.animateCamera(
        CameraUpdate.newLatLng(LatLng(lat, lng)),
      );
    }
  }

  void _selectPilotLocation(Map<String, dynamic> loc) {
    _updateCoordinates(loc['lat'] as double, loc['lng'] as double);
  }

  Future<void> _fetchDeviceGpsLocation() async {
    setState(() => _isLocating = true);
    try {
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Device location services are disabled. Please turn on GPS in phone settings.'),
            backgroundColor: GBColors.warning,
          ),
        );
        setState(() => _isLocating = false);
        return;
      }
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
      }
      if (permission == LocationPermission.deniedForever && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Location permission is permanently denied. Please allow location in App Settings.'),
            backgroundColor: GBColors.error,
          ),
        );
        setState(() => _isLocating = false);
        return;
      }
      if (permission == LocationPermission.whileInUse || permission == LocationPermission.always) {
        final pos = await Geolocator.getCurrentPosition(
          desiredAccuracy: LocationAccuracy.high,
          timeLimit: const Duration(seconds: 8),
        );
        _updateCoordinates(pos.latitude, pos.longitude);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('GPS updated: ${pos.latitude.toStringAsFixed(4)}, ${pos.longitude.toStringAsFixed(4)} (${_distanceKm} km from Minapur Hub)'),
              backgroundColor: _isServiceable ? GBColors.success : GBColors.warning,
              duration: const Duration(seconds: 3),
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Could not obtain GPS location: $e'),
            backgroundColor: GBColors.error,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isLocating = false);
      }
    }
  }

  void _proceedToAddressDetails() {
    if (!_isServiceable) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Delivery is limited to within 8.0 km of Minapur Hub.'),
          backgroundColor: GBColors.error,
        ),
      );
      return;
    }
    // Pre-populate village and landmark from chosen map pin
    _villageController.text = _selectedVillage;
    _landmarkController.text = _landmark;
    setState(() {
      _step = 1;
    });
  }

  Future<void> _saveAndConfirmAddress() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isSaving = true);
    try {
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
        village: _villageController.text.trim().isNotEmpty ? _villageController.text.trim() : _selectedVillage,
        landmark: _landmarkController.text.trim().isNotEmpty ? _landmarkController.text.trim() : _landmark,
        houseNumber: _houseController.text.trim(),
        panchayat: _panchayatController.text.trim(),
        postOffice: _postOfficeController.text.trim(),
        block: _blockController.text.trim().isNotEmpty ? _blockController.text.trim() : _block,
        district: _districtController.text.trim().isNotEmpty ? _districtController.text.trim() : _district,
        state: _stateController.text.trim().isNotEmpty ? _stateController.text.trim() : _state,
        pinCode: _pinController.text.trim().isNotEmpty ? _pinController.text.trim() : _pinCode,
        isDefault: true,
      );

      final success = await state.saveAddress(addr);
      state.setAddress(addr);
      if (!mounted) return;

      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Address saved successfully (पता सफलतापूर्वक सहेजा गया)'),
            backgroundColor: GBColors.success,
          ),
        );
        Navigator.of(context).pop();
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Address selected locally (ऑफलाइन सहेजा गया)'),
            backgroundColor: GBColors.primary,
          ),
        );
        Navigator.of(context).pop();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error saving address: $e'),
            backgroundColor: GBColors.error,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isSaving = false);
      }
    }
  }

  void _showSavedAddressesSheet(GBLocalizations loc, bool isDark) {
    final state = AppStateProvider.of(context);
    final saved = state.savedAddresses;

    showModalBottomSheet(
      context: context,
      isScrollable: true,
      backgroundColor: isDark ? GBColors.cardDark : Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
          constraints: BoxConstraints(maxHeight: MediaQuery.of(context).size.height * 0.7),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(Icons.bookmark_outline, color: GBColors.primary),
                  const SizedBox(width: 8),
                  Text(
                    loc.isHindi ? 'सहेजे गए पते (${saved.length})' : 'Saved Addresses (${saved.length})',
                    style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
                  ),
                  const Spacer(),
                  IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () => Navigator.of(ctx).pop(),
                  ),
                ],
              ),
              const Divider(height: 20),
              if (saved.isEmpty)
                Padding(
                  padding: const EdgeInsets.all(24),
                  child: Center(
                    child: Text(
                      loc.isHindi ? 'कोई सहेजा गया पता नहीं मिला' : 'No saved addresses found',
                      style: const TextStyle(color: Colors.grey),
                    ),
                  ),
                )
              else
                Expanded(
                  child: ListView.builder(
                    itemCount: saved.length,
                    itemBuilder: (context, idx) {
                      final item = saved[idx];
                      final isSelected = item.id == state.selectedAddress.id;
                      return Container(
                        margin: const EdgeInsets.only(bottom: 10),
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(
                            color: isSelected ? GBColors.primary : Colors.grey.shade300,
                            width: isSelected ? 2 : 1,
                          ),
                          color: isSelected ? GBColors.primary.withOpacity(0.05) : null,
                        ),
                        child: Row(
                          children: [
                            Icon(
                              item.title.toLowerCase() == 'work' ? Icons.work_outline : Icons.home_outlined,
                              color: GBColors.primary,
                            ),
                            const SizedBox(width: 10),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    children: [
                                      Text(
                                        item.title,
                                        style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
                                      ),
                                      if (isSelected) ...[
                                        const SizedBox(width: 8),
                                        Container(
                                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                          decoration: BoxDecoration(
                                            color: GBColors.primary.withOpacity(0.12),
                                            borderRadius: BorderRadius.circular(4),
                                          ),
                                          child: Text(
                                            loc.isHindi ? 'सक्रिय' : 'Active',
                                            style: const TextStyle(fontSize: 10, color: GBColors.primary, fontWeight: FontWeight.bold),
                                          ),
                                        ),
                                      ],
                                    ],
                                  ),
                                  const SizedBox(height: 3),
                                  Text(
                                    item.readableAddress,
                                    maxLines: 2,
                                    overflow: TextOverflow.ellipsis,
                                    style: const TextStyle(fontSize: 11, color: Colors.grey),
                                  ),
                                ],
                              ),
                            ),
                            TextButton(
                              onPressed: () {
                                state.setAddress(item);
                                Navigator.of(ctx).pop();
                                Navigator.of(context).pop();
                              },
                              child: Text(
                                loc.isHindi ? 'चुनें' : 'Select',
                                style: const TextStyle(fontWeight: FontWeight.bold),
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                ),
            ],
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final state = AppStateProvider.of(context);

    return PopScope(
      canPop: _step == 0,
      onPopInvokedWithResult: (didPop, _) {
        if (!didPop && _step == 1) {
          setState(() => _step = 0);
        }
      },
      child: Scaffold(
        appBar: AppBar(
          title: Text(
            _step == 0
                ? (loc.isHindi ? 'डिलीवरी स्थान चुनें' : 'Choose Delivery Location')
                : (loc.isHindi ? 'पते का विवरण जोड़ें' : 'Add Address Details'),
            style: const TextStyle(fontWeight: FontWeight.w800),
          ),
          leading: IconButton(
            icon: const Icon(Icons.arrow_back),
            onPressed: () {
              if (_step == 1) {
                setState(() => _step = 0);
              } else {
                Navigator.of(context).pop();
              }
            },
          ),
          actions: [
            if (_step == 0 && state.savedAddresses.isNotEmpty)
              TextButton.icon(
                icon: const Icon(Icons.bookmark_outline, size: 18),
                label: Text(
                  loc.isHindi ? 'सहेजे गए (${state.savedAddresses.length})' : 'Saved (${state.savedAddresses.length})',
                  style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                ),
                onPressed: () => _showSavedAddressesSheet(loc, isDark),
              ),
          ],
        ),
        body: _step == 0 ? _buildStep0LocationPicker(loc, isDark) : _buildStep1AddressDetails(loc, isDark),
      ),
    );
  }

  // STEP 0: Interactive Map & Delivery Pin
  Widget _buildStep0LocationPicker(GBLocalizations loc, bool isDark) {
    return Column(
      children: [
        // Quick Village Chips
        Container(
          height: 48,
          padding: const EdgeInsets.symmetric(vertical: 6),
          color: isDark ? GBColors.cardDark : Colors.grey.shade50,
          child: ListView.separated(
            padding: const EdgeInsets.symmetric(horizontal: 14),
            scrollDirection: Axis.horizontal,
            itemCount: _pilotLocations.length,
            separatorBuilder: (_, __) => const SizedBox(width: 8),
            itemBuilder: (context, idx) {
              final item = _pilotLocations[idx];
              final isSelected = item['village'] == _selectedVillage;
              final dist = _haversineKm(hubLat, hubLng, item['lat'] as double, item['lng'] as double);
              final isWithin = dist <= 8.0;

              return ActionChip(
                avatar: Icon(
                  isWithin ? Icons.location_on : Icons.location_off,
                  size: 14,
                  color: isSelected ? Colors.white : (isWithin ? GBColors.primary : GBColors.error),
                ),
                label: Text(
                  loc.isHindi ? item['village_hi'] : item['village'],
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: isSelected ? FontWeight.w800 : FontWeight.w500,
                    color: isSelected ? Colors.white : null,
                  ),
                ),
                backgroundColor: isSelected ? GBColors.primary : (isDark ? GBColors.backgroundDark : Colors.white),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                  side: BorderSide(
                    color: isSelected ? GBColors.primary : Colors.grey.shade300,
                  ),
                ),
                onPressed: () => _selectPilotLocation(item),
              );
            },
          ),
        ),

        // Interactive Google Map View
        Expanded(
          child: Stack(
            children: [
              GoogleMap(
                initialCameraPosition: CameraPosition(
                  target: LatLng(_currentLat, _currentLng),
                  zoom: 14.5,
                ),
                onMapCreated: (ctrl) => _mapController = ctrl,
                markers: {
                  Marker(
                    markerId: const MarkerId('delivery_pin'),
                    position: LatLng(_currentLat, _currentLng),
                    draggable: true,
                    onDragEnd: (pos) => _updateCoordinates(pos.latitude, pos.longitude),
                    infoWindow: InfoWindow(
                      title: _selectedVillage,
                      snippet: '${_currentLat.toStringAsFixed(4)}, ${_currentLng.toStringAsFixed(4)} (${_distanceKm} km from Minapur Hub)',
                    ),
                  ),
                },
                onTap: (pos) => _updateCoordinates(pos.latitude, pos.longitude),
                myLocationEnabled: true,
                myLocationButtonEnabled: false,
                zoomControlsEnabled: false,
              ),

              // 8km Geofence Indicator Badge
              Positioned(
                left: 14,
                top: 14,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
                  decoration: BoxDecoration(
                    color: isDark ? GBColors.cardDark.withOpacity(0.95) : Colors.white.withOpacity(0.95),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                      color: _isServiceable ? GBColors.success : GBColors.error,
                      width: 1.5,
                    ),
                    boxShadow: const [
                      BoxShadow(color: Colors.black12, blurRadius: 4, offset: Offset(0, 2)),
                    ],
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
                            ? (loc.isHindi ? 'डिलीवरी क्षेत्र के अंदर (${_distanceKm} किमी)' : 'Within 8.0 km Zone (${_distanceKm} km)')
                            : (loc.isHindi ? 'डिलीवरी क्षेत्र से बाहर (${_distanceKm} किमी)' : 'Outside 8.0 km Zone (${_distanceKm} km)'),
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w700,
                          color: _isServiceable ? GBColors.success : GBColors.error,
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              // "Use My Current Location" GPS FAB
              Positioned(
                right: 14,
                bottom: 14,
                child: FloatingActionButton.extended(
                  heroTag: 'gps_fab',
                  backgroundColor: isDark ? GBColors.cardDark : Colors.white,
                  foregroundColor: GBColors.primary,
                  elevation: 4,
                  onPressed: _isLocating ? null : _fetchDeviceGpsLocation,
                  icon: _isLocating
                      ? const SizedBox(
                          width: 18,
                          height: 18,
                          child: CircularProgressIndicator(strokeWidth: 2, color: GBColors.primary),
                        )
                      : const Icon(Icons.my_location, size: 20),
                  label: Text(
                    _isLocating
                        ? (loc.isHindi ? 'खोज रहे हैं...' : 'Locating...')
                        : (loc.isHindi ? 'वर्तमान स्थान' : 'Use Current GPS'),
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                  ),
                ),
              ),
            ],
          ),
        ),

        // Bottom Confirmation Panel
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: isDark ? GBColors.cardDark : Colors.white,
            borderRadius: const BorderRadius.vertical(top: Radius.circular(18)),
            boxShadow: [
              BoxShadow(color: Colors.black.withOpacity(0.08), blurRadius: 8, offset: const Offset(0, -3)),
            ],
          ),
          child: SafeArea(
            top: false,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.location_on, color: GBColors.primary, size: 24),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            _selectedVillage,
                            style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            _landmark,
                            style: TextStyle(
                              fontSize: 12,
                              color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            'GPS: ${_currentLat.toStringAsFixed(4)}, ${_currentLng.toStringAsFixed(4)} • ${_distanceKm} km to Minapur Hub',
                            style: const TextStyle(fontSize: 11, color: Colors.grey),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 14),
                GBPrimaryButton(
                  label: _isServiceable
                      ? (loc.isHindi ? 'स्थान पक्का करें और पता जोड़ें' : 'Confirm Pin & Add Address Details')
                      : (loc.isHindi ? '8.0 किमी सीमा से बाहर (डिलीवरी अनुपलब्ध)' : 'Outside 8.0 km Delivery Boundary'),
                  onPressed: _isServiceable ? _proceedToAddressDetails : null,
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  // STEP 1: Compact Address Details Form
  Widget _buildStep1AddressDetails(GBLocalizations loc, bool isDark) {
    return Form(
      key: _formKey,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Selected Location Banner
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: GBColors.primary.withOpacity(0.08),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: GBColors.primary.withOpacity(0.3)),
            ),
            child: Row(
              children: [
                const Icon(Icons.check_circle, color: GBColors.primary, size: 22),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        _selectedVillage,
                        style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
                      ),
                      Text(
                        '${_currentLat.toStringAsFixed(4)}, ${_currentLng.toStringAsFixed(4)} (${_distanceKm} km from Minapur Hub)',
                        style: const TextStyle(fontSize: 11, color: Colors.grey),
                      ),
                    ],
                  ),
                ),
                TextButton(
                  onPressed: () => setState(() => _step = 0),
                  child: Text(
                    loc.isHindi ? 'बदलें' : 'Change Pin',
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          Text(
            loc.isHindi ? 'प्राप्तकर्ता का विवरण' : 'Recipient Details',
            style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
          ),
          const SizedBox(height: 10),

          // Name
          TextFormField(
            controller: _nameController,
            decoration: InputDecoration(
              labelText: loc.tr('contact_name'),
              prefixIcon: const Icon(Icons.person_outline),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
            ),
            validator: (val) => (val == null || val.trim().isEmpty) ? 'Name is required' : null,
          ),
          const SizedBox(height: 12),

          // Phone
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
              if (val == null || val.trim().isEmpty) return 'Phone number is required';
              if (!RegExp(r'^[6-9]\d{9}$').hasMatch(val.trim())) return 'Enter a valid 10-digit mobile number';
              return null;
            },
          ),
          const SizedBox(height: 16),

          Text(
            loc.isHindi ? 'ग्रामीण घर एवं टोला विवरण' : 'House, Tola & Village Details',
            style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
          ),
          const SizedBox(height: 10),

          // House / Tola
          TextFormField(
            controller: _houseController,
            decoration: InputDecoration(
              labelText: loc.isHindi ? 'मकान नं. / टोला / वार्ड' : 'House No. / Tola / Ward (e.g. Ward 4, Purab Tola)',
              prefixIcon: const Icon(Icons.home_outlined),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
            ),
          ),
          const SizedBox(height: 12),

          // Village
          TextFormField(
            controller: _villageController,
            decoration: InputDecoration(
              labelText: loc.tr('village_name'),
              prefixIcon: const Icon(Icons.location_city_outlined),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
            ),
            validator: (val) => (val == null || val.trim().isEmpty) ? 'Village name is required' : null,
          ),
          const SizedBox(height: 12),

          // Landmark
          TextFormField(
            controller: _landmarkController,
            decoration: InputDecoration(
              labelText: loc.tr('landmark'),
              prefixIcon: const Icon(Icons.place_outlined),
              hintText: 'e.g. Near Middle School / Shiv Mandir',
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
            ),
            validator: (val) => (val == null || val.trim().isEmpty) ? 'Landmark is required for village delivery' : null,
          ),
          const SizedBox(height: 12),

          // Panchayat & Post Office
          Row(
            children: [
              Expanded(
                child: TextFormField(
                  controller: _panchayatController,
                  decoration: InputDecoration(
                    labelText: loc.isHindi ? 'ग्राम पंचायत' : 'Gram Panchayat',
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: TextFormField(
                  controller: _postOfficeController,
                  decoration: InputDecoration(
                    labelText: loc.isHindi ? 'डाकघर' : 'Post Office',
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Block, District, PIN
          Row(
            children: [
              Expanded(
                child: TextFormField(
                  controller: _blockController,
                  decoration: InputDecoration(
                    labelText: loc.tr('block'),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: TextFormField(
                  controller: _districtController,
                  decoration: InputDecoration(
                    labelText: loc.tr('district'),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                ),
              ),
              const SizedBox(width: 8),
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
            label: _isSaving
                ? (loc.isHindi ? 'सहेज रहे हैं...' : 'Saving Address...')
                : (loc.isHindi ? 'पता सहेजें और इस पर मंगाएं' : 'Save & Deliver to this Address'),
            onPressed: _isSaving ? null : _saveAndConfirmAddress,
          ),
          const SizedBox(height: 24),
        ],
      ),
    );
  }
}
