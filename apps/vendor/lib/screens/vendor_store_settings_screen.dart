import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
import '../state/vendor_state.dart';

class VendorStoreSettingsScreen extends StatefulWidget {
  const VendorStoreSettingsScreen({super.key});

  @override
  State<VendorStoreSettingsScreen> createState() => _VendorStoreSettingsScreenState();
}

class _VendorStoreSettingsScreenState extends State<VendorStoreSettingsScreen> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _shopNameCtrl;
  late TextEditingController _ownerNameCtrl;
  late TextEditingController _villageCtrl;
  late TextEditingController _landmarkCtrl;
  late TextEditingController _blockCtrl;
  late TextEditingController _districtCtrl;
  late TextEditingController _openingTimeCtrl;
  late TextEditingController _closingTimeCtrl;
  late String _category;
  bool _isSaving = false;

  @override
  void initState() {
    super.initState();
    final state = VendorStateProvider.of(context);
    final store = state.myStore;
    _shopNameCtrl = TextEditingController(text: store?.shopName ?? '');
    _ownerNameCtrl = TextEditingController(text: store?.ownerName ?? state.currentUser?.name ?? '');
    _villageCtrl = TextEditingController(text: store?.village ?? '');
    _landmarkCtrl = TextEditingController(text: store?.landmark ?? '');
    _blockCtrl = TextEditingController(text: store?.block ?? '');
    _districtCtrl = TextEditingController(text: store?.district ?? '');
    _openingTimeCtrl = TextEditingController(text: '07:00 AM');
    _closingTimeCtrl = TextEditingController(text: '09:00 PM');
    _category = store?.category ?? 'Grocery';
  }

  @override
  void dispose() {
    _shopNameCtrl.dispose();
    _ownerNameCtrl.dispose();
    _villageCtrl.dispose();
    _landmarkCtrl.dispose();
    _blockCtrl.dispose();
    _districtCtrl.dispose();
    _openingTimeCtrl.dispose();
    _closingTimeCtrl.dispose();
    super.dispose();
  }

  Future<void> _saveSettings(VendorAppState state) async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _isSaving = true);

    // Update store state and call profile refresh
    if (state.myStore != null) {
      final updated = state.myStore!.copyWith(
        shopName: _shopNameCtrl.text.trim(),
        ownerName: _ownerNameCtrl.text.trim(),
        category: _category,
        village: _villageCtrl.text.trim(),
        landmark: _landmarkCtrl.text.trim(),
        block: _blockCtrl.text.trim(),
        district: _districtCtrl.text.trim(),
      );
      state.updateStore(updated);
    }

    setState(() => _isSaving = false);
    final loc = GBLocalizations.of(context);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(loc.isHindi ? 'दुकान की जानकारी सुरक्षित हो गई' : 'Store settings updated successfully'),
        backgroundColor: GBColors.success,
      ),
    );
    Navigator.of(context).pop();
  }

  @override
  Widget build(BuildContext context) {
    final state = VendorStateProvider.of(context);
    final loc = GBLocalizations.of(context);
    final isHi = loc.isHindi;

    return Scaffold(
      appBar: AppBar(
        title: Text(
          isHi ? 'दुकान प्रबंधन व सेटिंग्स' : 'Store Profile & Settings',
          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 17),
        ),
        elevation: 1,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Verification Status Banner
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: state.isStoreApproved
                      ? GBColors.success.withValues(alpha: 0.1)
                      : Colors.amber.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(
                    color: state.isStoreApproved
                        ? GBColors.success.withValues(alpha: 0.3)
                        : Colors.amber.shade700,
                  ),
                ),
                child: Row(
                  children: [
                    Icon(
                      state.isStoreApproved ? Icons.verified : Icons.hourglass_top,
                      color: state.isStoreApproved ? GBColors.success : Colors.amber.shade800,
                      size: 26,
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            state.isStoreApproved
                                ? (isHi ? 'सत्यापित गाँव बाज़ार स्टोर' : 'Verified GaonBazaar Store')
                                : (isHi ? 'सत्यापन समीक्षाधीन' : 'Verification Under Review'),
                            style: TextStyle(
                              fontWeight: FontWeight.w800,
                              fontSize: 14,
                              color: state.isStoreApproved ? GBColors.success : Colors.amber.shade900,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            state.isStoreApproved
                                ? (isHi ? '0% कमीशन पर ग्रामीण बिक्री हेतु अधिकृत' : 'Authorized for 0% commission local commerce')
                                : (isHi ? 'सुपर एडमिन द्वारा अनुमोदन के बाद पूर्ण बिक्री शुरू होगी' : 'Full operations unlock after Admin verification'),
                            style: const TextStyle(fontSize: 12, color: Colors.grey),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 20),
              Text(
                isHi ? 'दुकान का विवरण' : 'Store Information',
                style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
              ),
              const SizedBox(height: 12),

              TextFormField(
                controller: _shopNameCtrl,
                decoration: InputDecoration(
                  labelText: isHi ? 'दुकान का नाम *' : 'Shop Name *',
                  prefixIcon: const Icon(Icons.storefront_outlined),
                ),
                validator: (v) => v == null || v.trim().isEmpty ? (isHi ? 'नाम आवश्यक है' : 'Required') : null,
              ),
              const SizedBox(height: 14),

              TextFormField(
                controller: _ownerNameCtrl,
                decoration: InputDecoration(
                  labelText: isHi ? 'दुकानदार का नाम *' : 'Owner Name *',
                  prefixIcon: const Icon(Icons.person_outline),
                ),
                validator: (v) => v == null || v.trim().isEmpty ? (isHi ? 'नाम आवश्यक है' : 'Required') : null,
              ),
              const SizedBox(height: 14),

              DropdownButtonFormField<String>(
                value: _category,
                decoration: InputDecoration(
                  labelText: isHi ? 'व्यापार श्रेणी' : 'Business Category',
                  prefixIcon: const Icon(Icons.category_outlined),
                ),
                items: [
                  'Grocery',
                  'General Store',
                  'Vegetables',
                  'Dairy',
                  'Pooja',
                  'Hardware',
                ].map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),
                onChanged: (v) => setState(() => _category = v ?? 'Grocery'),
              ),

              const SizedBox(height: 24),
              Text(
                isHi ? 'दुकान का वास्तविक पता' : 'Actual Store Location',
                style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
              ),
              const SizedBox(height: 12),

              TextFormField(
                controller: _villageCtrl,
                decoration: InputDecoration(
                  labelText: isHi ? 'गाँव / कस्बा *' : 'Village / Town *',
                  prefixIcon: const Icon(Icons.home_outlined),
                ),
                validator: (v) => v == null || v.trim().isEmpty ? (isHi ? 'गाँव आवश्यक है' : 'Required') : null,
              ),
              const SizedBox(height: 14),

              TextFormField(
                controller: _landmarkCtrl,
                decoration: InputDecoration(
                  labelText: isHi ? 'प्रमुख पहचान चिह्न (लैंडमार्क)' : 'Landmark',
                  prefixIcon: const Icon(Icons.place_outlined),
                ),
              ),
              const SizedBox(height: 14),

              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _blockCtrl,
                      decoration: InputDecoration(
                        labelText: isHi ? 'प्रखंड / ब्लॉक *' : 'Block *',
                      ),
                      validator: (v) => v == null || v.trim().isEmpty ? (isHi ? 'आवश्यक' : 'Required') : null,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: TextFormField(
                      controller: _districtCtrl,
                      decoration: InputDecoration(
                        labelText: isHi ? 'जिला *' : 'District *',
                      ),
                      validator: (v) => v == null || v.trim().isEmpty ? (isHi ? 'आवश्यक' : 'Required') : null,
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 24),
              Text(
                isHi ? 'दुकान संचालन समय' : 'Operating Hours',
                style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
              ),
              const SizedBox(height: 12),

              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _openingTimeCtrl,
                      decoration: InputDecoration(
                        labelText: isHi ? 'खुलने का समय' : 'Opening Time',
                        prefixIcon: const Icon(Icons.access_time),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: TextFormField(
                      controller: _closingTimeCtrl,
                      decoration: InputDecoration(
                        labelText: isHi ? 'बंद होने का समय' : 'Closing Time',
                        prefixIcon: const Icon(Icons.access_time_filled),
                      ),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 32),
              ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: GBColors.primary,
                  minimumSize: const Size.fromHeight(50),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
                onPressed: _isSaving ? null : () => _saveSettings(state),
                child: _isSaving
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                      )
                    : Text(
                        isHi ? 'जानकारी सुरक्षित करें' : 'Save Store Profile',
                        style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
                      ),
              ),
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }
}
