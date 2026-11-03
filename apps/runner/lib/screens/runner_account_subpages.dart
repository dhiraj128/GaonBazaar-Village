import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import '../state/runner_state.dart';

// ============================================================================
// 1. RUNNER PERSONAL PROFILE SCREEN
// ============================================================================
class RunnerPersonalProfileScreen extends StatefulWidget {
  const RunnerPersonalProfileScreen({super.key});

  @override
  State<RunnerPersonalProfileScreen> createState() => _RunnerPersonalProfileScreenState();
}

class _RunnerPersonalProfileScreenState extends State<RunnerPersonalProfileScreen> {
  final _nameCtrl = TextEditingController();
  final _emergencyPhoneCtrl = TextEditingController();
  bool _isSaving = false;

  @override
  void initState() {
    super.initState();
    final state = RunnerStateProvider.of(context);
    _nameCtrl.text = state.runnerProfile?['full_name'] ?? state.currentUser?.name ?? '';
  }

  @override
  void dispose() {
    _nameCtrl.dispose();
    _emergencyPhoneCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = RunnerStateProvider.of(context);
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
            child: const Icon(Icons.two_wheeler, color: Colors.white, size: 40),
          ),
          const SizedBox(height: 20),
          Text(isHi ? 'डिलीवरी साथी का पूरा नाम' : 'Full Name', style: const TextStyle(fontWeight: FontWeight.w700)),
          const SizedBox(height: 6),
          TextField(
            controller: _nameCtrl,
            decoration: InputDecoration(
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              prefixIcon: const Icon(Icons.person_outline),
            ),
          ),
          const SizedBox(height: 16),
          Text(isHi ? 'पंजीकृत मोबाइल नंबर (लॉगिन)' : 'Registered Mobile Number', style: const TextStyle(fontWeight: FontWeight.w700)),
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
                    await state.updateRunnerProfile({'full_name': _nameCtrl.text.trim()});
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
// 2. RUNNER VEHICLE DETAILS SCREEN
// ============================================================================
class RunnerVehicleDetailsScreen extends StatefulWidget {
  const RunnerVehicleDetailsScreen({super.key});

  @override
  State<RunnerVehicleDetailsScreen> createState() => _RunnerVehicleDetailsScreenState();
}

class _RunnerVehicleDetailsScreenState extends State<RunnerVehicleDetailsScreen> {
  late String _vehicleType;
  final _vehNoCtrl = TextEditingController();
  final _dlCtrl = TextEditingController();
  bool _isSaving = false;

  @override
  void initState() {
    super.initState();
    final state = RunnerStateProvider.of(context);
    _vehicleType = state.runnerProfile?['vehicle_type'] ?? 'Motorcycle';
    _vehNoCtrl.text = state.runnerProfile?['vehicle_number'] ?? '';
    _dlCtrl.text = state.runnerProfile?['dl_number'] ?? state.runnerProfile?['driving_licence_no'] ?? '';
  }

  @override
  void dispose() {
    _vehNoCtrl.dispose();
    _dlCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = RunnerStateProvider.of(context);
    final isHi = state.isHindi;
    final isMotorized = _vehicleType == 'Motorcycle' || _vehicleType == 'Scooter';

    return Scaffold(
      appBar: AppBar(
        title: Text(isHi ? 'वाहन विवरण' : 'Vehicle Details'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text(isHi ? 'डिलीवरी वाहन प्रकार *' : 'Vehicle Type *', style: const TextStyle(fontWeight: FontWeight.w700)),
          const SizedBox(height: 6),
          DropdownButtonFormField<String>(
            value: ['Motorcycle', 'Scooter', 'Bicycle', 'Electric Cycle'].contains(_vehicleType) ? _vehicleType : 'Motorcycle',
            decoration: InputDecoration(border: OutlineInputBorder(borderRadius: BorderRadius.circular(10))),
            items: [
              DropdownMenuItem(value: 'Motorcycle', child: Text(isHi ? 'मोटरसाइकिल' : 'Motorcycle')),
              DropdownMenuItem(value: 'Scooter', child: Text(isHi ? 'स्कूटर' : 'Scooter')),
              DropdownMenuItem(value: 'Bicycle', child: Text(isHi ? 'साइकिल' : 'Bicycle')),
              DropdownMenuItem(value: 'Electric Cycle', child: Text(isHi ? 'इलेक्ट्रिक साइकिल' : 'Electric Cycle')),
            ],
            onChanged: (val) {
              if (val != null) setState(() => _vehicleType = val);
            },
          ),
          const SizedBox(height: 16),
          if (isMotorized) ...[
            Text(isHi ? 'गाड़ी नंबर *' : 'Vehicle Number *', style: const TextStyle(fontWeight: FontWeight.w700)),
            const SizedBox(height: 6),
            TextField(
              controller: _vehNoCtrl,
              textCapitalization: TextCapitalization.characters,
              decoration: InputDecoration(hintText: 'BR-06-AB-1234', border: OutlineInputBorder(borderRadius: BorderRadius.circular(10))),
            ),
            const SizedBox(height: 16),
            Text(isHi ? 'ड्राइविंग लाइसेंस नंबर *' : 'Driving Licence Number *', style: const TextStyle(fontWeight: FontWeight.w700)),
            const SizedBox(height: 6),
            TextField(
              controller: _dlCtrl,
              textCapitalization: TextCapitalization.characters,
              decoration: InputDecoration(hintText: 'DL-06-20220012345', border: OutlineInputBorder(borderRadius: BorderRadius.circular(10))),
            ),
          ] else ...[
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(color: Colors.green.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(10)),
              child: Text(
                isHi ? 'साइकिल डिलीवरी हेतु ड्राइविंग लाइसेंस आवश्यक नहीं है।' : 'Driving licence is exempt for bicycle delivery.',
                style: const TextStyle(color: Colors.green, fontWeight: FontWeight.bold, fontSize: 12),
              ),
            ),
          ],
          const SizedBox(height: 24),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: GBColors.primary, padding: const EdgeInsets.symmetric(vertical: 12)),
            onPressed: _isSaving
                ? null
                : () async {
                    setState(() => _isSaving = true);
                    await state.updateRunnerProfile({
                      'full_name': state.runnerProfile?['full_name'] ?? state.currentUser?.name ?? 'Runner',
                      'vehicle_type': _vehicleType,
                      'vehicle_number': isMotorized ? _vehNoCtrl.text.trim().toUpperCase() : 'BICYCLE',
                      'driving_licence_no': isMotorized ? _dlCtrl.text.trim().toUpperCase() : 'EXEMPT',
                    });
                    setState(() => _isSaving = false);
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text(isHi ? 'वाहन विवरण सुरक्षित हो गया' : 'Vehicle details updated'), backgroundColor: GBColors.success),
                    );
                    Navigator.of(context).pop();
                  },
            child: Text(isHi ? 'वाहन सुरक्षित करें' : 'Save Vehicle Details', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }
}

// ============================================================================
// 3. RUNNER IDENTITY & DOCUMENTS SCREEN
// ============================================================================
class RunnerIdentityDocumentsScreen extends StatelessWidget {
  const RunnerIdentityDocumentsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final state = RunnerStateProvider.of(context);
    final isHi = state.isHindi;
    final isApproved = state.isApproved;

    return Scaffold(
      appBar: AppBar(
        title: Text(isHi ? 'पहचान एवं सत्यापन दस्तावेज' : 'Identity & Documents'),
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
                            ? (isHi ? '✓ सत्यापित डिलीवरी साथी' : '✓ Verified Delivery Partner')
                            : (isHi ? 'दस्तावेज समीक्षाधीन' : 'Documents Under Review'),
                        style: TextStyle(
                          fontWeight: FontWeight.w800,
                          fontSize: 15,
                          color: isApproved ? Colors.green : Colors.amber.shade900,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        isApproved
                            ? (isHi ? 'आपकी पहचान सत्यापित है। आप ड्यूटी ऑन कर सकते हैं।' : 'Identity verified. You are authorized to accept delivery jobs.')
                            : (isHi ? 'सुपर एडमिन द्वारा ड्राइविंग लाइसेंस व आधार समीक्षा की जा रही है।' : 'Super Admin is reviewing identity and driving credentials.'),
                        style: const TextStyle(fontSize: 12, color: Colors.black87),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
          ListTile(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10), side: BorderSide(color: Colors.grey.shade300)),
            leading: const Icon(Icons.badge_outlined, color: GBColors.primary),
            title: Text(isHi ? 'आधार पहचान संख्या' : 'Aadhaar Identification'),
            subtitle: const Text('XXXX-XXXX-5678'),
            trailing: const Chip(label: Text('Verified', style: TextStyle(fontSize: 11, color: Colors.green)), backgroundColor: Color(0xFFE8F5E9)),
          ),
          const SizedBox(height: 12),
          ListTile(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10), side: BorderSide(color: Colors.grey.shade300)),
            leading: const Icon(Icons.credit_card_outlined, color: GBColors.secondary),
            title: Text(isHi ? 'ड्राइविंग लाइसेंस' : 'Driving License'),
            subtitle: Text(state.runnerProfile?['dl_number'] ?? 'EXEMPT-BICYCLE'),
            trailing: Chip(
              label: Text(isApproved ? 'Approved' : 'Pending', style: TextStyle(fontSize: 11, color: isApproved ? Colors.green : Colors.amber.shade900)),
              backgroundColor: isApproved ? const Color(0xFFE8F5E9) : Colors.amber.shade100,
            ),
          ),
        ],
      ),
    );
  }
}

// ============================================================================
// 4. RUNNER DELIVERY AREA SCREEN
// ============================================================================
class RunnerDeliveryAreaScreen extends StatefulWidget {
  const RunnerDeliveryAreaScreen({super.key});

  @override
  State<RunnerDeliveryAreaScreen> createState() => _RunnerDeliveryAreaScreenState();
}

class _RunnerDeliveryAreaScreenState extends State<RunnerDeliveryAreaScreen> {
  final _areaCtrl = TextEditingController();

  @override
  void initState() {
    super.initState();
    final state = RunnerStateProvider.of(context);
    _areaCtrl.text = state.runnerProfile?['village'] ?? '';
  }

  @override
  void dispose() {
    _areaCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = RunnerStateProvider.of(context);
    final isHi = state.isHindi;

    return Scaffold(
      appBar: AppBar(
        title: Text(isHi ? 'डिलीवरी कार्य क्षेत्र' : 'Delivery Area'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text(isHi ? 'प्राथमिक डिलीवरी क्लस्टर / गाँव' : 'Primary Delivery Cluster', style: const TextStyle(fontWeight: FontWeight.w700)),
          const SizedBox(height: 6),
          TextField(
            controller: _areaCtrl,
            decoration: InputDecoration(
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              prefixIcon: const Icon(Icons.location_on_outlined),
            ),
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: GBColors.primary.withValues(alpha: 0.08),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  isHi ? 'पारदर्शी 5-स्तरीय दूरी पेआउट' : '5-Tier Distance Payouts Active',
                  style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 13, color: GBColors.primary),
                ),
                const SizedBox(height: 4),
                Text(
                  isHi ? '0 - 1.0 किमी: ₹10 • 1.0 - 2.0 किमी: ₹14 • 2.0 - 4.0 किमी: ₹18 • 4.0 - 6.0 किमी: ₹22 • 6.0 - 8.0 किमी: ₹28' : '0-1km: ₹10 • 1-2km: ₹14 • 2-4km: ₹18 • 4-6km: ₹22 • 6-8km: ₹28',
                  style: const TextStyle(fontSize: 11, color: Colors.grey),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: GBColors.primary, padding: const EdgeInsets.symmetric(vertical: 12)),
            onPressed: () async {
              await state.updateRunnerProfile({
                'village': _areaCtrl.text.trim(),
              });
              if (!context.mounted) return;
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text(isHi ? 'कार्य क्षेत्र सुरक्षित हो गया' : 'Delivery area saved'), backgroundColor: GBColors.success),
              );
              Navigator.of(context).pop();
            },
            child: Text(isHi ? 'क्षेत्र सुरक्षित करें' : 'Save Area', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }
}

// ============================================================================
// 5. RUNNER BANK & UPI PAYOUT SETTINGS (Zero Fake UPI)
// ============================================================================
class RunnerBankPayoutScreen extends StatefulWidget {
  const RunnerBankPayoutScreen({super.key});

  @override
  State<RunnerBankPayoutScreen> createState() => _RunnerBankPayoutScreenState();
}

class _RunnerBankPayoutScreenState extends State<RunnerBankPayoutScreen> {
  final _upiCtrl = TextEditingController();
  bool _isSaving = false;

  @override
  void initState() {
    super.initState();
    final state = RunnerStateProvider.of(context);
    _upiCtrl.text = state.linkedUpiId;
  }

  @override
  void dispose() {
    _upiCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = RunnerStateProvider.of(context);
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
                            ? (isHi ? 'दैनिक यूपीआई सेटलमेंट सक्रिय' : 'Daily UPI Settlement Active')
                            : (isHi ? 'पेआउट खाता अधूरा (सेटअप आवश्यक)' : 'Payout Account Missing (Setup Required)'),
                        style: TextStyle(fontWeight: FontWeight.w800, fontSize: 13, color: hasUpi ? Colors.green : Colors.red),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        isHi
                            ? 'आपकी पूर्ण की गई ट्रिप्स का पेआउट अगले दिन (T+1) सीधे इसी यूपीआई आईडी में भेजा जाएगा।'
                            : 'All trip payouts will be remitted to this verified UPI ID daily.',
                        style: const TextStyle(fontSize: 11, color: Colors.grey),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),

          Text(isHi ? 'व्यक्तिगत यूपीआई आईडी *' : 'Personal UPI ID for Payouts *', style: const TextStyle(fontWeight: FontWeight.w700)),
          const SizedBox(height: 6),
          TextField(
            controller: _upiCtrl,
            decoration: InputDecoration(
              hintText: 'runner@okhdfcbank',
              prefixIcon: const Icon(Icons.currency_rupee),
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
                        SnackBar(content: Text(isHi ? 'कृपया वैध यूपीआई आईडी दर्ज करें' : 'Please enter valid UPI ID'), backgroundColor: GBColors.error),
                      );
                      return;
                    }
                    setState(() => _isSaving = true);
                    await state.updateRunnerProfile({
                      'full_name': state.runnerProfile?['full_name'] ?? state.currentUser?.name ?? 'Runner',
                      'vehicle_type': state.runnerProfile?['vehicle_type'] ?? 'Motorcycle',
                      'upi_id': upi,
                    });
                    setState(() => _isSaving = false);
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text(isHi ? 'पेआउट सेटिंग्स सुरक्षित हो गईं' : 'Payout settings updated'), backgroundColor: GBColors.success),
                    );
                    Navigator.of(context).pop();
                  },
            child: Text(isHi ? 'पेआउट सुरक्षित करें' : 'Save Payout Details', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }
}
