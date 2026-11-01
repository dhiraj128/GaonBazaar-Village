import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
import '../state/app_state.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  late TextEditingController _nameController;
  late TextEditingController _emailController;
  bool _isSaving = false;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController();
    _emailController = TextEditingController();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final state = AppStateProvider.of(context);
      _nameController.text = state.currentUser?.name ?? '';
      _emailController.text = state.currentUser?.email ?? '';
    });
  }

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    super.dispose();
  }

  Future<void> _handleSave() async {
    final state = AppStateProvider.of(context);
    final loc = GBLocalizations.of(context);

    setState(() => _isSaving = true);
    final success = await state.updateProfile(
      name: _nameController.text.trim(),
      email: _emailController.text.trim(),
    );
    setState(() => _isSaving = false);

    if (mounted) {
      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(loc.tr('profile_updated'))),
        );
        Navigator.of(context).pop();
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(loc.tr('network_error')), backgroundColor: GBColors.error),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = AppStateProvider.of(context);
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    final phone = state.currentUser?.phone ?? '';

    return Scaffold(
      appBar: AppBar(
        title: Text(loc.tr('profile_title'), style: const TextStyle(fontWeight: FontWeight.w800)),
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
          children: [
            // Avatar Center
            Center(
              child: Stack(
                children: [
                  Container(
                    width: 90,
                    height: 90,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: GBColors.primary.withAlpha(25),
                      border: Border.all(color: GBColors.primary, width: 2),
                    ),
                    child: Center(
                      child: Text(
                        _nameController.text.isNotEmpty
                            ? _nameController.text[0].toUpperCase()
                            : (phone.isNotEmpty ? phone.substring(phone.length - 2) : 'GB'),
                        style: const TextStyle(
                          fontSize: 32,
                          fontWeight: FontWeight.w900,
                          color: GBColors.primary,
                        ),
                      ),
                    ),
                  ),
                  Positioned(
                    bottom: 0,
                    right: 0,
                    child: Container(
                      padding: const EdgeInsets.all(6),
                      decoration: const BoxDecoration(
                        color: GBColors.primary,
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.camera_alt, size: 16, color: Colors.white),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 28),

            // Form Fields
            Text(
              loc.tr('personal_info'),
              style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 14),

            // Full Name Input
            Text(
              loc.tr('full_name'),
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w700,
                color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
              ),
            ),
            const SizedBox(height: 6),
            TextField(
              controller: _nameController,
              decoration: InputDecoration(
                hintText: loc.isHindi ? 'उदा. अनीता देवी' : 'e.g. Anita Devi',
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
              ),
            ),
            const SizedBox(height: 18),

            // Mobile Number (Verified & Read-Only)
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  loc.tr('mobile_number'),
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                    color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
                  ),
                ),
                Text(
                  loc.tr('mobile_verified'),
                  style: const TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                    color: GBColors.primary,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 6),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
              decoration: BoxDecoration(
                color: isDark ? GBColors.surfaceDark : Colors.grey.withAlpha(25),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: isDark ? GBColors.borderDark : GBColors.borderLight),
              ),
              child: Row(
                children: [
                  const Icon(Icons.verified, color: GBColors.primary, size: 18),
                  const SizedBox(width: 10),
                  Text(
                    phone.isNotEmpty ? '+91 $phone' : '+91 (Not Signed In)',
                    style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 15),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 18),

            // Email Address (Optional)
            Text(
              loc.tr('email_address'),
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w700,
                color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
              ),
            ),
            const SizedBox(height: 6),
            TextField(
              controller: _emailController,
              keyboardType: TextInputType.emailAddress,
              decoration: InputDecoration(
                hintText: 'user@example.com',
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
              ),
            ),
            const SizedBox(height: 32),

            // Save Changes Button
            GBPrimaryButton(
              label: loc.tr('save_changes'),
              isLoading: _isSaving,
              onPressed: _handleSave,
            ),
          ],
        ),
      ),
    );
  }
}
