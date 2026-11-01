import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'runner_dashboard_screen.dart';

class RunnerOnboardingWizard extends StatefulWidget {
  const RunnerOnboardingWizard({super.key});

  @override
  State<RunnerOnboardingWizard> createState() => _RunnerOnboardingWizardState();
}

class _RunnerOnboardingWizardState extends State<RunnerOnboardingWizard> {
  int _currentStep = 0;

  final _fullNameCtrl = TextEditingController(text: 'Santosh Kumar');
  final _phoneCtrl = TextEditingController(text: '9800000003');
  final _bikeNoCtrl = TextEditingController(text: 'BR-06-AB-1234');
  final _dlCtrl = TextEditingController(text: 'DL-062024009876');
  final _upiCtrl = TextEditingController(text: 'santosh@upi');
  String _vehicleType = 'Motorcycle';
  bool _digiLockerConsented = false;

  void _nextStep() {
    if (_currentStep < 3) {
      setState(() => _currentStep++);
    } else {
      showDialog(
        context: context,
        builder: (ctx) => AlertDialog(
          title: const Text('आवेदन समीक्षाधीन है (Under Review)'),
          content: const Text(
            'आपका डिलीवरी पार्टनर आवेदन सुपर एडमिन के पास समीक्षा के लिए जमा कर दिया गया है। अनुमोदन के बाद आप डिलीवरी जॉब्स प्राप्त कर सकेंगे।',
          ),
          actions: [
            ElevatedButton(
              onPressed: () {
                Navigator.of(ctx).pop();
                Navigator.of(context).pushReplacement(
                  MaterialPageRoute(builder: (_) => const RunnerDashboardScreen()),
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
        title: const Text('डिलीवरी साथी पंजीकरण (Partner Registration)', style: TextStyle(fontWeight: FontWeight.w800, fontSize: 15)),
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
                    OutlinedButton(onPressed: details.onStepCancel, child: const Text('पीछे')),
                  ],
                ],
              ),
            );
          },
          steps: [
            // Step 1: Personal Details
            Step(
              title: const Text('व्यक्तिगत जानकारी'),
              isActive: _currentStep >= 0,
              content: Column(
                children: [
                  TextField(controller: _fullNameCtrl, decoration: const InputDecoration(labelText: 'पूरा नाम (Full Name)')),
                  const SizedBox(height: 12),
                  TextField(controller: _phoneCtrl, decoration: const InputDecoration(labelText: 'मोबाइल नंबर (Phone Number)')),
                ],
              ),
            ),

            // Step 2: Vehicle & Driving Licence
            Step(
              title: const Text('वाहन व ड्राइविंग लाइसेंस'),
              isActive: _currentStep >= 1,
              content: Column(
                children: [
                  DropdownButtonFormField<String>(
                    value: _vehicleType,
                    items: const [
                      DropdownMenuItem(value: 'Motorcycle', child: Text('मोटरसाइकिल / बाइक (Motorcycle)')),
                      DropdownMenuItem(value: 'Bicycle', child: Text('साइकिल (Bicycle)')),
                    ],
                    onChanged: (v) => setState(() => _vehicleType = v!),
                    decoration: const InputDecoration(labelText: 'वाहन का प्रकार (Vehicle Type)'),
                  ),
                  const SizedBox(height: 12),
                  TextField(controller: _bikeNoCtrl, decoration: const InputDecoration(labelText: 'बाइक रजिस्ट्रेशन नंबर (e.g. BR-06-AB-1234)')),
                  const SizedBox(height: 12),
                  TextField(controller: _dlCtrl, decoration: const InputDecoration(labelText: 'ड्राइविंग लाइसेंस नंबर (Driving Licence No.)')),
                ],
              ),
            ),

            // Step 3: Identity & DigiLocker
            Step(
              title: const Text('आधार व पहचान सत्यापन'),
              isActive: _currentStep >= 2,
              content: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('डिजिटल आधार / डिजीलॉकर सत्यापन सहमति:'),
                  const SizedBox(height: 8),
                  CheckboxListTile(
                    value: _digiLockerConsented,
                    activeColor: GBColors.primary,
                    contentPadding: EdgeInsets.zero,
                    title: const Text('मैं अपने ड्राइविंग लाइसेंस एवं आधार सत्यापन हेतु सहमति प्रदान करता हूँ।'),
                    onChanged: (v) => setState(() => _digiLockerConsented = v ?? false),
                  ),
                ],
              ),
            ),

            // Step 4: Payout Details
            Step(
              title: const Text('कमाई भुगतान खाता (Payout)'),
              isActive: _currentStep >= 3,
              content: Column(
                children: [
                  TextField(controller: _upiCtrl, decoration: const InputDecoration(labelText: 'यूपीआई आईडी (UPI ID for Payouts)')),
                  const SizedBox(height: 8),
                  const Text('प्रति डिलीवरी शुल्क सीधे आपके बैंक / यूपीआई खाते में बिना किसी कटौती के भेजा जाता है।', style: TextStyle(fontSize: 12, color: Colors.grey)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
