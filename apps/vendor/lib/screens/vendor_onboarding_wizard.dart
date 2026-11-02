import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
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

  // Form controllers
  final _ownerNameCtrl = TextEditingController();
  final _shopNameCtrl = TextEditingController();
  final _villageCtrl = TextEditingController();
  final _landmarkCtrl = TextEditingController();
  final _blockCtrl = TextEditingController(text: 'Minapur');
  final _districtCtrl = TextEditingController(text: 'Muzaffarpur');
  final _aadhaarCtrl = TextEditingController();
  final _panCtrl = TextEditingController();
  final _upiCtrl = TextEditingController();
  String _category = 'Grocery';
  bool _digiLockerConsented = false;

  final List<String> _categories = [
    'Grocery',
    'Dairy',
    'Vegetables',
    'Electrical',
    'Pooja',
    'General',
  ];

  final List<Map<String, dynamic>> _pilotVillages = [
    {'name': 'Chaturshi', 'lat': 26.2230, 'lng': 85.3520},
    {'name': 'Tubanaghara (Benaghara)', 'lat': 26.2080, 'lng': 85.3370},
    {'name': 'Sivay Patti', 'lat': 26.2310, 'lng': 85.3610},
    {'name': 'Tulsi Ganj (Bangaon)', 'lat': 26.1980, 'lng': 85.3420},
  ];

  @override
  void dispose() {
    _ownerNameCtrl.dispose();
    _shopNameCtrl.dispose();
    _villageCtrl.dispose();
    _landmarkCtrl.dispose();
    _blockCtrl.dispose();
    _districtCtrl.dispose();
    _aadhaarCtrl.dispose();
    _panCtrl.dispose();
    _upiCtrl.dispose();
    super.dispose();
  }

  void _nextStep() async {
    final state = VendorStateProvider.of(context);
    final loc = GBLocalizations.of(context);

    if (_currentStep < 3) {
      setState(() => _currentStep++);
    } else {
      // Step 4: Submit to Backend
      setState(() => _isSubmitting = true);

      final selectedVillageObj = _pilotVillages.firstWhere(
        (v) => v['name'].toString().contains(_villageCtrl.text),
        orElse: () => _pilotVillages.first,
      );

      final payload = {
        'shop_name': _shopNameCtrl.text.trim(),
        'owner_name': _ownerNameCtrl.text.trim(),
        'category': _category,
        'latitude': selectedVillageObj['lat'] as double,
        'longitude': selectedVillageObj['lng'] as double,
        'village': _villageCtrl.text.trim(),
        'landmark': _landmarkCtrl.text.trim(),
        'block': _blockCtrl.text.trim(),
        'district': _districtCtrl.text.trim(),
        'upi_id': _upiCtrl.text.trim(),
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
          title: Text(loc.tr('pending_approval_title')),
          content: Text(
            loc.isHindi
                ? 'आपकी दुकान का विवरण सफलतापूर्वक जमा हो गया है। सुपर एडमिन द्वारा सत्यापन के बाद आपकी दुकान 0% कमीशन पर ऑनलाइन हो जाएगी।'
                : 'Your store details have been submitted successfully. Once verified by Super Admin, your shop will go live with 0% commission.',
          ),
          actions: [
            ElevatedButton(
              onPressed: () {
                Navigator.of(ctx).pop();
                Navigator.of(context).pushReplacement(
                  MaterialPageRoute(builder: (_) => const VendorDashboardScreen()),
                );
              },
              child: Text(loc.isHindi ? 'डैशबोर्ड पर जाएँ' : 'Go to Dashboard'),
            ),
          ],
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final loc = GBLocalizations.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(
          loc.tr('vendor_register_store'),
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
                      label: _currentStep == 3
                          ? (loc.isHindi ? 'आवेदन जमा करें' : 'Submit Application')
                          : (loc.isHindi ? 'आगे बढ़ें' : 'Next Step'),
                      isLoading: _isSubmitting,
                      onPressed: details.onStepContinue,
                    ),
                  ),
                  if (_currentStep > 0) ...[
                    const SizedBox(width: 12),
                    OutlinedButton(
                      onPressed: details.onStepCancel,
                      child: Text(loc.isHindi ? 'पीछे' : 'Back'),
                    ),
                  ],
                ],
              ),
            );
          },
          steps: [
            // Step 1: Shop & Owner Details
            Step(
              title: Text(loc.isHindi ? 'दुकान की जानकारी' : 'Shop & Owner Information'),
              isActive: _currentStep >= 0,
              content: Column(
                children: [
                  TextField(
                    controller: _ownerNameCtrl,
                    decoration: InputDecoration(
                      labelText: loc.isHindi ? 'मालिक का नाम *' : 'Owner Full Name *',
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _shopNameCtrl,
                    decoration: InputDecoration(
                      labelText: loc.isHindi ? 'दुकान का नाम *' : 'Shop Name *',
                    ),
                  ),
                  const SizedBox(height: 12),
                  DropdownButtonFormField<String>(
                    value: _category,
                    decoration: InputDecoration(
                      labelText: loc.isHindi ? 'दुकान की श्रेणी *' : 'Store Category *',
                    ),
                    items: _categories.map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),
                    onChanged: (v) => setState(() => _category = v!),
                  ),
                ],
              ),
            ),

            // Step 2: Accurate Village Address
            Step(
              title: Text(loc.isHindi ? 'गाँव व पता विवरण' : 'Village & Location Details'),
              isActive: _currentStep >= 1,
              content: Column(
                children: [
                  DropdownButtonFormField<String>(
                    value: _villageCtrl.text,
                    decoration: InputDecoration(
                      labelText: loc.isHindi ? 'गाँव / टोला चुनें *' : 'Select Village / Locality *',
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
                      labelText: loc.isHindi ? 'निकटतम लैंडमार्क *' : 'Nearby Landmark *',
                    ),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _blockCtrl,
                          decoration: InputDecoration(
                            labelText: loc.isHindi ? 'प्रखंड *' : 'Block *',
                          ),
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: TextField(
                          controller: _districtCtrl,
                          decoration: InputDecoration(
                            labelText: loc.isHindi ? 'ज़िला *' : 'District *',
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            // Step 3: KYC & Identity Verification
            Step(
              title: Text(loc.isHindi ? 'केवाईसी व पहचान सत्यापन' : 'KYC & Verification'),
              isActive: _currentStep >= 2,
              content: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  TextField(
                    controller: _aadhaarCtrl,
                    keyboardType: TextInputType.number,
                    decoration: InputDecoration(
                      labelText: loc.isHindi ? 'आधार नंबर (मास्क किया हुआ)' : 'Aadhaar Number (Masked)',
                      prefixIcon: const Icon(Icons.badge_outlined),
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _panCtrl,
                    textCapitalization: TextCapitalization.characters,
                    decoration: InputDecoration(
                      labelText: loc.isHindi ? 'पैन कार्ड नंबर' : 'PAN Card Number',
                      prefixIcon: const Icon(Icons.credit_card_outlined),
                    ),
                  ),
                  const SizedBox(height: 14),
                  CheckboxListTile(
                    value: _digiLockerConsented,
                    activeColor: GBColors.primary,
                    contentPadding: EdgeInsets.zero,
                    title: Text(
                      loc.isHindi
                          ? 'डिजीलॉकर द्वारा पहचान पत्र सत्यापन सहमति'
                          : 'Consent to verify identity via DigiLocker Government Gateway',
                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                    ),
                    onChanged: (v) => setState(() => _digiLockerConsented = v ?? false),
                  ),
                ],
              ),
            ),

            // Step 4: Bank / UPI Payout Details
            Step(
              title: Text(loc.isHindi ? 'भुगतान व यूपीआई विवरण' : 'Payout UPI & Bank Account'),
              isActive: _currentStep >= 3,
              content: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: GBColors.primary.withOpacity(0.08),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: GBColors.primary.withOpacity(0.3)),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.percent, color: GBColors.primary, size: 22),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            loc.isHindi
                                ? 'गाँव बाज़ार में 0% विक्रेता कमीशन है। आपके सभी ऑर्डर की 100% बिक्री राशि सीधे आपके यूपीआई खाते में भेजी जाएगी।'
                                : 'GaonBazaar charges 0% commission from village vendors. 100% of your sales are remitted directly to your UPI ID.',
                            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 14),
                  TextField(
                    controller: _upiCtrl,
                    decoration: InputDecoration(
                      labelText: loc.isHindi ? 'दुकानदार यूपीआई आईडी *' : 'Vendor Payout UPI ID *',
                      prefixIcon: const Icon(Icons.account_balance_wallet_outlined),
                      hintText: 'name@okhdfcbank / mobile@upi',
                    ),
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
