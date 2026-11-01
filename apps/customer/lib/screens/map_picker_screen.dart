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

class _MapPickerScreenState extends State<MapPickerScreen> {
  double _currentLat = 26.2230;
  double _currentLng = 85.3520;
  String _selectedVillage = 'Chaturshi / Chatursi';
  String _landmark = 'Near Gram Panchayat Bhavan';
  String _block = 'Minapur';
  String _district = 'Muzaffarpur';
  bool _isServiceable = true;
  double _distanceKm = 0.8;
  int _tabIndex = 0; // 0 = Map Pin, 1 = Saved Addresses

  // Pilot localities list in Minapur
  final List<Map<String, dynamic>> _pilotLocations = [
    {
      'village': 'Chaturshi / Chatursi',
      'landmark': 'Near Gram Panchayat Bhavan',
      'lat': 26.2230,
      'lng': 85.3520,
      'distance': 0.8,
    },
    {
      'village': 'Tubanaghara / Benaghara',
      'landmark': 'Near Middle School Chowk',
      'lat': 26.2080,
      'lng': 85.3370,
      'distance': 2.1,
    },
    {
      'village': 'Sivay Patti',
      'landmark': 'Near Shiv Mandir Chowk',
      'lat': 26.2310,
      'lng': 85.3610,
      'distance': 3.4,
    },
    {
      'village': 'Tulsi Ganj / Bangaon',
      'landmark': 'Near Market Chowk',
      'lat': 26.1980,
      'lng': 85.3420,
      'distance': 4.2,
    },
  ];

  void _onLocationSelect(Map<String, dynamic> loc) {
    setState(() {
      _currentLat = loc['lat'] as double;
      _currentLng = loc['lng'] as double;
      _selectedVillage = loc['village'] as String;
      _landmark = loc['landmark'] as String;
      _distanceKm = loc['distance'] as double;
      _isServiceable = _distanceKm <= 8.0;
    });
  }

  void _confirmAndSave() {
    final state = AppStateProvider.of(context);
    final addr = GBAddress(
      id: 'addr_${DateTime.now().millisecondsSinceEpoch}',
      userId: state.currentUser?.id ?? 'usr_c1',
      title: 'Home',
      recipientName: state.currentUser?.name ?? 'Ramesh Singh',
      phone: state.currentUser?.phone ?? '9876543210',
      latitude: _currentLat,
      longitude: _currentLng,
      village: _selectedVillage,
      landmark: _landmark,
      block: _block,
      district: _district,
      isDefault: true,
    );

    state.setAddress(addr);
    Navigator.of(context).pop();
  }

  @override
  Widget build(BuildContext context) {
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: Text(
          loc.isHindi ? 'स्थान व गाँव चुनें (Select Village)' : 'Delivery Location',
          style: const TextStyle(fontWeight: FontWeight.w800),
        ),
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Interactive Map simulation with draggable pin & coordinates
            Expanded(
              flex: 5,
              child: Stack(
                alignment: Alignment.center,
                children: [
                  // Stylized rural village map representation
                  Container(
                    width: double.infinity,
                    color: isDark ? const Color(0xFF1B2838) : const Color(0xFFE5F0E6),
                    child: CustomPaint(
                      painter: _MapGridPainter(isDark: isDark),
                    ),
                  ),

                  // Center Draggable Delivery Pin
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
                      const Icon(
                        Icons.location_pin,
                        size: 46,
                        color: GBColors.primary,
                      ),
                    ],
                  ),

                  // Current GPS floating button
                  Positioned(
                    right: 16,
                    bottom: 16,
                    child: FloatingActionButton.small(
                      backgroundColor: Colors.white,
                      foregroundColor: GBColors.primary,
                      onPressed: () {
                        _onLocationSelect(_pilotLocations[0]);
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('वर्तमान स्थान प्राप्त हुआ: चतुर्शी, मीनापुर'),
                            duration: Duration(seconds: 1),
                          ),
                        );
                      },
                      child: const Icon(Icons.my_location),
                    ),
                  ),

                  // 8.0 km radius indicator badge
                  Positioned(
                    left: 16,
                    top: 16,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.9),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: GBColors.primary),
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
                                ? '८ किमी सीमा के अंदर (${_distanceKm} km)'
                                : '८ किमी सीमा से बाहर',
                            style: const TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w700,
                              color: Colors.black87,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),

            // Bottom address details sheet with readable details
            Expanded(
              flex: 6,
              child: Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: isDark ? GBColors.cardDark : Colors.white,
                  borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 10,
                      offset: const Offset(0, -3),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'मीनापुर पायलट गाँव (Minapur Localities):',
                      style: TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
                    ),
                    const SizedBox(height: 10),
                    // Localities chips
                    Expanded(
                      child: ListView.builder(
                        itemCount: _pilotLocations.length,
                        itemBuilder: (context, idx) {
                          final locItem = _pilotLocations[idx];
                          final isSelected = locItem['village'] == _selectedVillage;

                          return InkWell(
                            onTap: () => _onLocationSelect(locItem),
                            borderRadius: BorderRadius.circular(10),
                            child: Container(
                              margin: const EdgeInsets.only(bottom: 8),
                              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                              decoration: BoxDecoration(
                                color: isSelected
                                    ? GBColors.primary.withOpacity(0.1)
                                    : Colors.transparent,
                                borderRadius: BorderRadius.circular(10),
                                border: Border.all(
                                  color: isSelected ? GBColors.primary : Colors.grey.shade300,
                                ),
                              ),
                              child: Row(
                                children: [
                                  Icon(
                                    Icons.location_city,
                                    size: 18,
                                    color: isSelected ? GBColors.primary : Colors.grey,
                                  ),
                                  const SizedBox(width: 10),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          locItem['village'] as String,
                                          style: TextStyle(
                                            fontWeight: FontWeight.w700,
                                            fontSize: 13,
                                            color: isSelected ? GBColors.primary : null,
                                          ),
                                        ),
                                        Text(
                                          locItem['landmark'] as String,
                                          style: const TextStyle(fontSize: 11, color: Colors.grey),
                                        ),
                                      ],
                                    ),
                                  ),
                                  Text(
                                    '${locItem['distance']} km',
                                    style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600),
                                  ),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
                    ),
                    const SizedBox(height: 12),
                    GBPrimaryButton(
                      label: loc.isHindi ? 'यह स्थान पक्का करें (Confirm Location)' : 'Confirm Delivery Location',
                      onPressed: _confirmAndSave,
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
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
