import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'vendor_dashboard_screen.dart';

class VendorOnboardingWizard extends StatefulWidget {
  const VendorOnboardingWizard({super.key});

  @override
  State<VendorOnboardingWizard> createState() => _VendorOnboardingWizardState();
}

class _VendorOnboardingWizardState extends State<VendorOnboardingWizard> {
  int _currentStep = 0;

  // Form controllers
  final _ownerNameCtrl = TextEditingController(text: 'Raju Sharma');
  final _shopNameCtrl = TextEditingController(text: 'माँ शारदा किराना स्टोर');
  final _villageCtrl = TextEditingController(text: 'Chaturshi / Chatursi');
  final _landmarkCtrl = TextEditingController(text: 'Near Gram Panchayat Bhavan');
  final _upiCtrl = TextEditingController(text: 'rajusharma@upi');
  String _category = 'Grocery';
  bool _digiLockerConsented = false;

  void _nextStep() {
    if (_currentStep < 3) {
      setState(() => _currentStep++);
    } else {
      // Completed -> Submit for Admin Review
      showDialog(
        context: context,
        builder: (ctx) => AlertDialog(
          title: const Text('समीक्षा हेतु जमा (Submitted for Review)'),
          content: const Text(
            'आपकी दुकान का विवरण सफलतापूर्वक जमा हो गया है। सुपर एडमिन सत्यापन के बाद आपकी दुकान 0% कमीशन पर ऑनलाइन हो जाएगी।',
          ),
          actions: [
            ElevatedButton(
              onPressed: () {
                Navigator.of(ctx).pop();
                Navigator.of(context).pushReplacement(
                  MaterialPageRoute(builder: (_) => const VendorDashboardScreen()),
                );
              },
              child: const Text('डैशबोर्ड पर जाएँ'),
            ),
          ],
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('दुकान पंजीकरण (Shop Registration)', style: TextStyle(fontWeight: FontWeight.w800, fontSize: 16)),
      ),
      body: SafeArea(
        child: Stepper(
          currentStep: _currentStep,
          onStepContinue: _nextStep,
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
                      label: _currentStep == 3 ? 'आवेदन जमा करें (Submit)' : 'आगे बढ़ें (Next)',
                      onPressed: details.onStepContinue,
                    ),
                  ),
                  if (_currentStep > 0) ...[
                    const SizedBox(width: 12),
                    OutlinedButton(
                      onPressed: details.onStepCancel,
                      child: const Text('पीछे'),
                    ),
                  ],
                ],
              ),
            );
          },
          steps: [
            // Step 1: Shop & Owner Details
            Step(
              title: const Text('दुकान की जानकारी'),
              isActive: _currentStep >= 0,
              content: Column(
                children: [
                  TextField(controller: _ownerNameCtrl, decoration: const InputDecoration(labelText: 'मालिक का नाम (Owner Name)')),
                  const SizedBox(height: 12),
                  TextField(controller: _shopNameCtrl, decoration: const InputDecoration(labelText: 'दुकान का नाम (Shop Name)')),
                  const SizedBox(height: 12),
                  DropdownButtonFormField<String>(
                    value: _category,
                    items: const [
                      DropdownMenuItem(value: 'Grocery', child: Text('किराना व राशन (Grocery)')),
                      DropdownMenuItem(value: 'Vegetables', child: Text('ताज़ी सब्ज़ी व फल')),
                      DropdownMenuItem(value: 'Dairy', child: Text('डेयरी उत्पाद')),
                      DropdownMenuItem(value: 'Pooja', child: Text('पूजा सामग्री')),
                      DropdownMenuItem(value: 'General', child: Text('जनरल स्टोर')),
                    ],
                    onChanged: (v) => setState(() => _category = v!),
                    decoration: const InputDecoration(labelText: 'श्रेणी (Category)'),
                  ),
                ],
              ),
            ),

            // Step 2: Location & GPS
            Step(
              title: const Text('गाँव का पता व स्थान'),
              isActive: _currentStep >= 1,
              content: Column(
                children: [
                  TextField(controller: _villageCtrl, decoration: const InputDecoration(labelText: 'गाँव / टोला (Village)')),
                  const SizedBox(height: 12),
                  TextField(controller: _landmarkCtrl, decoration: const InputDecoration(labelText: 'नज़दीकी पहचान / लैंडमार्क (Landmark)')),
                  const SizedBox(height: 12),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: GBColors.primary.withOpacity(0.08),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Row(
                      children: [
                        Icon(Icons.gps_fixed, color: GBColors.primary),
                        SizedBox(width: 8),
                        Text('GPS: 26.2230° N, 85.3520° E (Minapur)', style: TextStyle(fontWeight: FontWeight.w700, fontSize: 13)),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            // Step 3: Identity & DigiLocker
            Step(
              title: const Text('पहचान सत्यापन'),
              isActive: _currentStep >= 2,
              content: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('डिजीलॉकर (DigiLocker) सहमति-आधारित सत्यापन:'),
                  const SizedBox(height: 8),
                  CheckboxListTile(
                    value: _digiLockerConsented,
                    activeColor: GBColors.primary,
                    contentPadding: EdgeInsets.zero,
                    title: const Text('मैं अपनी पहचान विवरण प्रमाणित करने की सहमति देता हूँ।'),
                    onChanged: (v) => setState(() => _digiLockerConsented = v ?? false),
                  ),
                ],
              ),
            ),

            // Step 4: Bank Payout Info
            Step(
              title: const Text('भुगतान खाता (Payout Details)'),
              isActive: _currentStep >= 3,
              content: Column(
                children: [
                  TextField(controller: _upiCtrl, decoration: const InputDecoration(labelText: 'यूपीआई आईडी (UPI ID for Payout)')),
                  const SizedBox(height: 8),
                  const Text('दैनिक बिक्री का भुगतान सीधे आपके खाते में बिना किसी कमीशन (0% Fee) के भेजा जाता है।', style: TextStyle(fontSize: 12, color: Colors.grey)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
