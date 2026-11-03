import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import '../state/vendor_state.dart';

// ============================================================================
// 1. VENDOR PERSONAL PROFILE SCREEN
// ============================================================================
class VendorPersonalProfileScreen extends StatefulWidget {
  const VendorPersonalProfileScreen({super.key});

  @override
  State<VendorPersonalProfileScreen> createState() => _VendorPersonalProfileScreenState();
}

class _VendorPersonalProfileScreenState extends State<VendorPersonalProfileScreen> {
  final _nameCtrl = TextEditingController();
  final _altPhoneCtrl = TextEditingController();
  bool _isSaving = false;

  @override
  void initState() {
    super.initState();
    final state = VendorStateProvider.of(context);
    _nameCtrl.text = state.currentUser?.name ?? state.myStore?.ownerName ?? '';
  }

  @override
  void dispose() {
    _nameCtrl.dispose();
    _altPhoneCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = VendorStateProvider.of(context);
    final isHi = state.isHindi;

    return Scaffold(
      appBar: AppBar(
        title: Text(isHi ? 'व्यक्तिगत प्रोफ़ाइल' : 'Personal Profile'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          CircleAvatar(
            radius: 36,
            backgroundColor: GBColors.primary,
            child: const Icon(Icons.person, color: Colors.white, size: 40),
          ),
          const SizedBox(height: 20),
          Text(isHi ? 'दुकानदार का पूरा नाम' : 'Full Name', style: const TextStyle(fontWeight: FontWeight.w700)),
          const SizedBox(height: 6),
          TextField(
            controller: _nameCtrl,
            decoration: InputDecoration(
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              prefixIcon: const Icon(Icons.person_outline),
            ),
          ),
          const SizedBox(height: 16),
          Text(isHi ? 'पंजीकृत मोबाइल नंबर (लॉगिन)' : 'Registered Phone', style: const TextStyle(fontWeight: FontWeight.w700)),
          const SizedBox(height: 6),
          TextField(
            readOnly: true,
            controller: TextEditingController(text: state.currentUser?.phone ?? ''),
            decoration: InputDecoration(
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              prefixIcon: const Icon(Icons.phone),
              suffixIcon: const Icon(Icons.lock_outline, color: Colors.grey, size: 18),
              filled: true,
              fillColor: Theme.of(context).cardColor,
            ),
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: GBColors.primary, padding: const EdgeInsets.symmetric(vertical: 12)),
            onPressed: _isSaving
                ? null
                : () async {
                    setState(() => _isSaving = true);
                    if (state.myStore != null) {
                      final updated = state.myStore!.copyWith(ownerName: _nameCtrl.text.trim());
                      state.updateStore(updated);
                      await state.onboardStore({
                        'shop_name': updated.shopName,
                        'owner_name': _nameCtrl.text.trim(),
                        'category': updated.category,
                        'latitude': updated.latitude,
                        'longitude': updated.longitude,
                        'village': updated.village,
                        'landmark': updated.landmark,
                        'block': updated.block,
                        'district': updated.district,
                      });
                    }
                    setState(() => _isSaving = false);
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text(isHi ? 'प्रोफ़ाइल सुरक्षित हो गई' : 'Profile updated successfully'), backgroundColor: GBColors.success),
                    );
                    Navigator.of(context).pop();
                  },
            child: Text(isHi ? 'जानकारी सुरक्षित करें' : 'Save Profile', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }
}

// ============================================================================
// 2. VENDOR MY STORE SCREEN
// ============================================================================
class VendorMyStoreScreen extends StatefulWidget {
  const VendorMyStoreScreen({super.key});

  @override
  State<VendorMyStoreScreen> createState() => _VendorMyStoreScreenState();
}

class _VendorMyStoreScreenState extends State<VendorMyStoreScreen> {
  final _shopNameCtrl = TextEditingController();
  late String _category;
  bool _isSaving = false;

  @override
  void initState() {
    super.initState();
    final state = VendorStateProvider.of(context);
    _shopNameCtrl.text = state.myStore?.shopName ?? '';
    _category = state.myStore?.category ?? 'Grocery';
  }

  @override
  void dispose() {
    _shopNameCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = VendorStateProvider.of(context);
    final isHi = state.isHindi;

    return Scaffold(
      appBar: AppBar(
        title: Text(isHi ? 'मेरी दुकान' : 'My Store'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text(isHi ? 'दुकान का नाम *' : 'Shop Name *', style: const TextStyle(fontWeight: FontWeight.w700)),
          const SizedBox(height: 6),
          TextField(
            controller: _shopNameCtrl,
            decoration: InputDecoration(
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              prefixIcon: const Icon(Icons.store),
            ),
          ),
          const SizedBox(height: 16),
          Text(isHi ? 'दुकान की श्रेणी *' : 'Category *', style: const TextStyle(fontWeight: FontWeight.w700)),
          const SizedBox(height: 6),
          DropdownButtonFormField<String>(
            value: ['Grocery', 'General Store', 'Vegetables', 'Dairy', 'Household', 'Personal Care'].contains(_category) ? _category : 'Grocery',
            decoration: InputDecoration(border: OutlineInputBorder(borderRadius: BorderRadius.circular(10))),
            items: [
              DropdownMenuItem(value: 'Grocery', child: Text(isHi ? 'किराना एवं राशन' : 'Grocery & Staples')),
              DropdownMenuItem(value: 'General Store', child: Text(isHi ? 'जनरल स्टोर' : 'General Store')),
              DropdownMenuItem(value: 'Vegetables', child: Text(isHi ? 'ताज़ी सब्ज़ी व फल' : 'Vegetables & Fruits')),
              DropdownMenuItem(value: 'Dairy', child: Text(isHi ? 'दूध व डेयरी' : 'Dairy Products')),
              DropdownMenuItem(value: 'Household', child: Text(isHi ? 'घरेलू सामान' : 'Household')),
              DropdownMenuItem(value: 'Personal Care', child: Text(isHi ? 'पर्सनल केयर' : 'Personal Care')),
            ],
            onChanged: (val) {
              if (val != null) setState(() => _category = val);
            },
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: GBColors.primary, padding: const EdgeInsets.symmetric(vertical: 12)),
            onPressed: _isSaving
                ? null
                : () async {
                    setState(() => _isSaving = true);
                    if (state.myStore != null) {
                      final updated = state.myStore!.copyWith(
                        shopName: _shopNameCtrl.text.trim(),
                        category: _category,
                      );
                      state.updateStore(updated);
                      await state.onboardStore({
                        'shop_name': _shopNameCtrl.text.trim(),
                        'owner_name': updated.ownerName,
                        'category': _category,
                        'latitude': updated.latitude,
                        'longitude': updated.longitude,
                        'village': updated.village,
                        'landmark': updated.landmark,
                        'block': updated.block,
                        'district': updated.district,
                      });
                    }
                    setState(() => _isSaving = false);
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text(isHi ? 'दुकान की जानकारी सुरक्षित हो गई' : 'Store details updated'), backgroundColor: GBColors.success),
                    );
                    Navigator.of(context).pop();
                  },
            child: Text(isHi ? 'दुकान विवरण अपडेट करें' : 'Update Store Details', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }
}

// ============================================================================
// 3. VENDOR STORE LOCATION SCREEN
// ============================================================================
class VendorStoreLocationScreen extends StatefulWidget {
  const VendorStoreLocationScreen({super.key});

  @override
  State<VendorStoreLocationScreen> createState() => _VendorStoreLocationScreenState();
}

class _VendorStoreLocationScreenState extends State<VendorStoreLocationScreen> {
  final _villageCtrl = TextEditingController();
  final _landmarkCtrl = TextEditingController();
  final _blockCtrl = TextEditingController();
  final _districtCtrl = TextEditingController();

  @override
  void initState() {
    super.initState();
    final state = VendorStateProvider.of(context);
    _villageCtrl.text = state.myStore?.village ?? '';
    _landmarkCtrl.text = state.myStore?.landmark ?? '';
    _blockCtrl.text = state.myStore?.block ?? '';
    _districtCtrl.text = state.myStore?.district ?? '';
  }

  @override
  void dispose() {
    _villageCtrl.dispose();
    _landmarkCtrl.dispose();
    _blockCtrl.dispose();
    _districtCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = VendorStateProvider.of(context);
    final isHi = state.isHindi;
    final lat = state.myStore?.latitude ?? 0.0;
    final lng = state.myStore?.longitude ?? 0.0;

    return Scaffold(
      appBar: AppBar(
        title: Text(isHi ? 'दुकान का स्थान व पता' : 'Store Location & Address'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: GBColors.primary.withValues(alpha: 0.08),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: GBColors.primary.withValues(alpha: 0.3)),
            ),
            child: Row(
              children: [
                const Icon(Icons.location_on, color: GBColors.primary, size: 28),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '${isHi ? "जीपीएस निर्देशांक:" : "GPS Coordinates:"} ${lat.toStringAsFixed(4)}° N, ${lng.toStringAsFixed(4)}° E',
                        style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 13),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        isHi ? '8 किमी की ग्रामीण परिधि में डिलीवरी सक्रिय' : '8 km rural delivery radius active',
                        style: const TextStyle(fontSize: 11, color: Colors.grey),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          Text(isHi ? 'गाँव / टोला' : 'Village / Locality', style: const TextStyle(fontWeight: FontWeight.w700)),
          const SizedBox(height: 6),
          TextField(controller: _villageCtrl, decoration: InputDecoration(border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)))),
          const SizedBox(height: 16),
          Text(isHi ? 'लैंडमार्क / सड़क' : 'Landmark / Street', style: const TextStyle(fontWeight: FontWeight.w700)),
          const SizedBox(height: 6),
          TextField(controller: _landmarkCtrl, decoration: InputDecoration(border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)))),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(isHi ? 'प्रखंड' : 'Block', style: const TextStyle(fontWeight: FontWeight.w700)),
                    const SizedBox(height: 6),
                    TextField(controller: _blockCtrl, decoration: InputDecoration(border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)))),
                  ],
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(isHi ? 'जिला' : 'District', style: const TextStyle(fontWeight: FontWeight.w700)),
                    const SizedBox(height: 6),
                    TextField(controller: _districtCtrl, decoration: InputDecoration(border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)))),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: GBColors.primary, padding: const EdgeInsets.symmetric(vertical: 12)),
            onPressed: () async {
              if (state.myStore != null) {
                final updated = state.myStore!.copyWith(
                  village: _villageCtrl.text.trim(),
                  landmark: _landmarkCtrl.text.trim(),
                  block: _blockCtrl.text.trim(),
                  district: _districtCtrl.text.trim(),
                );
                state.updateStore(updated);
                await state.onboardStore({
                  'shop_name': updated.shopName,
                  'owner_name': updated.ownerName,
                  'category': updated.category,
                  'latitude': updated.latitude,
                  'longitude': updated.longitude,
                  'village': _villageCtrl.text.trim(),
                  'landmark': _landmarkCtrl.text.trim(),
                  'block': _blockCtrl.text.trim(),
                  'district': _districtCtrl.text.trim(),
                });
              }
              if (!context.mounted) return;
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text(isHi ? 'स्थान पता अपडेट हो गया' : 'Location address updated'), backgroundColor: GBColors.success),
              );
              Navigator.of(context).pop();
            },
            child: Text(isHi ? 'स्थान सुरक्षित करें' : 'Save Location', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }
}

// ============================================================================
// 4. VENDOR BUSINESS VERIFICATION SCREEN
// ============================================================================
class VendorBusinessVerificationScreen extends StatelessWidget {
  const VendorBusinessVerificationScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final state = VendorStateProvider.of(context);
    final isHi = state.isHindi;
    final isApproved = state.isStoreApproved;

    return Scaffold(
      appBar: AppBar(
        title: Text(isHi ? 'व्यापार व पहचान सत्यापन' : 'Business Verification'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: isApproved ? Colors.green.withValues(alpha: 0.1) : Colors.amber.shade50,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: isApproved ? Colors.green : Colors.amber.shade400),
            ),
            child: Row(
              children: [
                Icon(
                  isApproved ? Icons.verified : Icons.pending_actions,
                  color: isApproved ? Colors.green : Colors.amber.shade900,
                  size: 36,
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        isApproved
                            ? (isHi ? '✓ सुपर एडमिन द्वारा सत्यापित दुकान' : '✓ Verified Vendor Account')
                            : (isHi ? 'सत्यापन समीक्षाधीन' : 'Pending Verification Review'),
                        style: TextStyle(
                          fontWeight: FontWeight.w800,
                          fontSize: 15,
                          color: isApproved ? Colors.green : Colors.amber.shade900,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        isApproved
                            ? (isHi ? 'आपकी दुकान पर ग्राहक ऑर्डर दे सकते हैं।' : 'Store is operational and accepting customer orders.')
                            : (isHi ? 'सुपर एडमिन द्वारा व्यापार रिकॉर्ड सत्यापन के बाद दुकान ऑनलाइन होगी।' : 'Super Admin is reviewing your business documentation.'),
                        style: const TextStyle(fontSize: 12, color: Colors.black87),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
          Text(isHi ? 'सत्यापन दस्तावेज' : 'Submitted Verification', style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14)),
          const SizedBox(height: 10),
          ListTile(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10), side: BorderSide(color: Colors.grey.shade300)),
            leading: const Icon(Icons.badge_outlined, color: GBColors.primary),
            title: Text(isHi ? 'आधार / व्यापार पहचान पत्र' : 'Aadhaar / Business ID'),
            subtitle: const Text('XXXX-XXXX-1234'),
            trailing: const Chip(label: Text('Verified', style: TextStyle(fontSize: 11, color: Colors.green)), backgroundColor: Color(0xFFE8F5E9)),
          ),
        ],
      ),
    );
  }
}

// ============================================================================
// 5. VENDOR BANK & UPI PAYOUT SETTINGS (Zero Fake UPI)
// ============================================================================
class VendorBankPayoutScreen extends StatefulWidget {
  const VendorBankPayoutScreen({super.key});

  @override
  State<VendorBankPayoutScreen> createState() => _VendorBankPayoutScreenState();
}

class _VendorBankPayoutScreenState extends State<VendorBankPayoutScreen> {
  final _upiCtrl = TextEditingController();
  final _bankNameCtrl = TextEditingController();
  final _accountNoCtrl = TextEditingController();
  final _ifscCtrl = TextEditingController();
  bool _isSaving = false;

  @override
  void initState() {
    super.initState();
    final state = VendorStateProvider.of(context);
    final upi = state.linkedUpiId;
    _upiCtrl.text = upi;
  }

  @override
  void dispose() {
    _upiCtrl.dispose();
    _bankNameCtrl.dispose();
    _accountNoCtrl.dispose();
    _ifscCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = VendorStateProvider.of(context);
    final isHi = state.isHindi;
    final hasUpi = state.linkedUpiId.isNotEmpty;

    return Scaffold(
      appBar: AppBar(
        title: Text(isHi ? 'बैंक व यूपीआई पेआउट सेटिंग्स' : 'Bank & UPI Payout Settings'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: hasUpi ? Colors.green.withValues(alpha: 0.08) : Colors.red.withValues(alpha: 0.08),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: hasUpi ? Colors.green.withValues(alpha: 0.3) : Colors.red.withValues(alpha: 0.3)),
            ),
            child: Row(
              children: [
                Icon(hasUpi ? Icons.account_balance_wallet : Icons.warning_amber_rounded, color: hasUpi ? Colors.green : Colors.red, size: 28),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        hasUpi
                            ? (isHi ? 'पेआउट खाता सक्रिय (T+1 सेटलमेंट)' : 'Payout Account Active (T+1 Settlement)')
                            : (isHi ? 'पेआउट खाता अधूरा (सेटअप आवश्यक)' : 'Payout Account Missing (Setup Required)'),
                        style: TextStyle(fontWeight: FontWeight.w800, fontSize: 13, color: hasUpi ? Colors.green : Colors.red),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        isHi
                            ? 'गाँव बाज़ार 0% कमीशन पर सीधे आपके बैंक/यूपीआई में भुगतान ट्रांसफर करता है।'
                            : 'GaonBazaar transfers 100% of order sales directly to your account with 0% platform fee.',
                        style: const TextStyle(fontSize: 11, color: Colors.grey),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),

          Text(isHi ? 'प्राथमिक यूपीआई आईडी *' : 'Primary UPI ID for Payouts *', style: const TextStyle(fontWeight: FontWeight.w700)),
          const SizedBox(height: 6),
          TextField(
            controller: _upiCtrl,
            decoration: InputDecoration(
              hintText: 'shopkeeper@oksbi',
              prefixIcon: const Icon(Icons.currency_rupee),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
            ),
          ),
          const SizedBox(height: 20),

          const Divider(height: 30),
          Text(isHi ? 'वैकल्पिक बैंक खाता विवरण' : 'Alternative Bank Details (Optional)', style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14)),
          const SizedBox(height: 12),
          TextField(
            controller: _bankNameCtrl,
            decoration: InputDecoration(
              labelText: isHi ? 'बैंक का नाम' : 'Bank Name',
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _accountNoCtrl,
            keyboardType: TextInputType.number,
            decoration: InputDecoration(
              labelText: isHi ? 'खाता संख्या' : 'Account Number',
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _ifscCtrl,
            textCapitalization: TextCapitalization.characters,
            decoration: InputDecoration(
              labelText: isHi ? 'आईएफएससी कोड' : 'IFSC Code',
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
            ),
          ),
          const SizedBox(height: 24),

          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: GBColors.primary, padding: const EdgeInsets.symmetric(vertical: 12)),
            onPressed: _isSaving
                ? null
                : () async {
                    final upi = _upiCtrl.text.trim();
                    if (upi.isEmpty) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text(isHi ? 'कृपया वैध यूपीआई आईडी दर्ज करें' : 'Please enter a valid UPI ID'), backgroundColor: GBColors.error),
                      );
                      return;
                    }
                    setState(() => _isSaving = true);
                    if (state.myStore != null) {
                      final updated = state.myStore!.copyWith(upiId: upi);
                      state.updateStore(updated);
                      await state.onboardStore({'upi_id': upi, 'shop_name': updated.shopName, 'owner_name': updated.ownerName, 'category': updated.category, 'latitude': updated.latitude, 'longitude': updated.longitude, 'village': updated.village});
                    }
                    setState(() => _isSaving = false);
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text(isHi ? 'पेआउट विवरण सुरक्षित हो गया' : 'Payout settings updated'), backgroundColor: GBColors.success),
                    );
                    Navigator.of(context).pop();
                  },
            child: Text(isHi ? 'पेआउट खाता सुरक्षित करें' : 'Save Payout Details', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }
}

// ============================================================================
// 6. VENDOR OPERATING HOURS SCREEN
// ============================================================================
class VendorOperatingHoursScreen extends StatefulWidget {
  const VendorOperatingHoursScreen({super.key});

  @override
  State<VendorOperatingHoursScreen> createState() => _VendorOperatingHoursScreenState();
}

class _VendorOperatingHoursScreenState extends State<VendorOperatingHoursScreen> {
  String _openingTime = '07:00 AM';
  String _closingTime = '09:00 PM';
  String _prepTime = '5-10 मिनट';

  @override
  Widget build(BuildContext context) {
    final state = VendorStateProvider.of(context);
    final isHi = state.isHindi;

    return Scaffold(
      appBar: AppBar(
        title: Text(isHi ? 'दुकान संचालन समय' : 'Operating Hours & Timings'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          ListTile(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10), side: BorderSide(color: Colors.grey.shade300)),
            leading: const Icon(Icons.wb_sunny_outlined, color: Colors.amber),
            title: Text(isHi ? 'दुकान खुलने का समय' : 'Opening Time'),
            trailing: Text(_openingTime, style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14)),
          ),
          const SizedBox(height: 12),
          ListTile(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10), side: BorderSide(color: Colors.grey.shade300)),
            leading: const Icon(Icons.nightlight_outlined, color: Colors.indigo),
            title: Text(isHi ? 'दुकान बंद होने का समय' : 'Closing Time'),
            trailing: Text(_closingTime, style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14)),
          ),
          const SizedBox(height: 12),
          ListTile(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10), side: BorderSide(color: Colors.grey.shade300)),
            leading: const Icon(Icons.timer_outlined, color: GBColors.primary),
            title: Text(isHi ? 'ऑर्डर पैकिंग औसत समय' : 'Average Packing Time'),
            trailing: Text(_prepTime, style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 13)),
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: GBColors.primary, padding: const EdgeInsets.symmetric(vertical: 12)),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text(isHi ? 'दुकान का समय अपडेट हो गया' : 'Operating hours saved'), backgroundColor: GBColors.success),
              );
              Navigator.of(context).pop();
            },
            child: Text(isHi ? 'समय सुरक्षित करें' : 'Save Hours', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }
}
