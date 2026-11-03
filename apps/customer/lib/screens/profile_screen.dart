import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
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
  late TextEditingController _villageController;
  late TextEditingController _panchayatController;
  bool _isSaving = false;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController();
    _emailController = TextEditingController();
    _villageController = TextEditingController();
    _panchayatController = TextEditingController();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final state = AppStateProvider.of(context);
      _nameController.text = state.currentUser?.name ?? '';
      _emailController.text = state.currentUser?.email ?? '';
      _villageController.text = state.currentUser?.primaryVillage ?? 'Chaturshi (Ward 4)';
      _panchayatController.text = state.currentUser?.primaryPanchayat ?? 'Minapur Gram Panchayat';
    });
  }

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _villageController.dispose();
    _panchayatController.dispose();
    super.dispose();
  }

  Future<void> _pickAvatar() async {
    final loc = GBLocalizations.of(context);
    final isHi = loc.isHindi;

    try {
      final picker = ImagePicker();
      final picked = await picker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 512,
        maxHeight: 512,
        imageQuality: 85,
      );

      if (picked != null) {
        setState(() => _isSaving = true);
        final bytes = await picked.readAsBytes();
        final base64Str = base64Encode(bytes);
        final mime = picked.name.toLowerCase().endsWith('.png') ? 'image/png' : 'image/jpeg';
        final dataUri = 'data:$mime;base64,$base64Str';

        final state = AppStateProvider.of(context);
        final ok = await state.uploadAvatar(dataUri);
        setState(() => _isSaving = false);

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                ok
                    ? (isHi ? 'प्रोफ़ाइल फ़ोटो सफलतापूर्वक अपडेट हो गई!' : 'Profile photo updated successfully!')
                    : (isHi ? 'फ़ोटो अपलोड विफल रहा' : 'Failed to update photo'),
              ),
              backgroundColor: ok ? GBColors.success : GBColors.error,
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isSaving = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error selecting photo: $e'), backgroundColor: GBColors.error),
        );
      }
    }
  }

  Future<void> _handleSave() async {
    final state = AppStateProvider.of(context);
    final loc = GBLocalizations.of(context);

    setState(() => _isSaving = true);
    final success = await state.updateProfile(
      name: _nameController.text.trim(),
      email: _emailController.text.trim(),
      primaryVillage: _villageController.text.trim(),
      primaryPanchayat: _panchayatController.text.trim(),
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

  ImageProvider? _getAvatarImage(String? avatarUrl) {
    if (avatarUrl == null || avatarUrl.isEmpty) return null;
    if (avatarUrl.startsWith('data:image')) {
      try {
        final commaIdx = avatarUrl.indexOf(',');
        if (commaIdx != -1) {
          final base64Data = avatarUrl.substring(commaIdx + 1);
          return MemoryImage(base64Decode(base64Data));
        }
      } catch (_) {}
    } else if (avatarUrl.startsWith('http')) {
      return NetworkImage(avatarUrl);
    }
    return null;
  }

  @override
  Widget build(BuildContext context) {
    final state = AppStateProvider.of(context);
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    final user = state.currentUser;
    final phone = user?.phone ?? '';
    final avatarImg = _getAvatarImage(user?.avatarUrl);

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          tooltip: loc.isHindi ? 'पीछे जाएं' : 'Back',
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: Text(loc.tr('profile_title'), style: const TextStyle(fontWeight: FontWeight.w800)),
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
          children: [
            // Avatar with Active Camera Icon
            Center(
              child: Stack(
                children: [
                  GestureDetector(
                    onTap: _pickAvatar,
                    child: Container(
                      width: 96,
                      height: 96,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: GBColors.primary.withAlpha(25),
                        border: Border.all(color: GBColors.primary, width: 2.5),
                        image: avatarImg != null
                            ? DecorationImage(image: avatarImg, fit: BoxFit.cover)
                            : null,
                      ),
                      child: avatarImg == null
                          ? Center(
                              child: Text(
                                _nameController.text.isNotEmpty
                                    ? _nameController.text[0].toUpperCase()
                                    : (phone.isNotEmpty ? phone.substring(phone.length - 2) : 'GB'),
                                style: const TextStyle(
                                  fontSize: 34,
                                  fontWeight: FontWeight.w900,
                                  color: GBColors.primary,
                                ),
                              ),
                            )
                          : null,
                    ),
                  ),
                  Positioned(
                    bottom: 0,
                    right: 0,
                    child: GestureDetector(
                      onTap: _pickAvatar,
                      child: Container(
                        padding: const EdgeInsets.all(7),
                        decoration: BoxDecoration(
                          color: GBColors.primary,
                          shape: BoxShape.circle,
                          border: Border.all(color: Colors.white, width: 2),
                          boxShadow: const [BoxShadow(color: Colors.black26, blurRadius: 4)],
                        ),
                        child: const Icon(Icons.camera_alt, size: 16, color: Colors.white),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

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
            const SizedBox(height: 18),

            // Primary Village & Panchayat (Rural Identity - Fully Editable)
            Text(
              loc.isHindi ? 'प्राथमिक गाँव व टोला' : 'Primary Village & Tola',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w700,
                color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
              ),
            ),
            const SizedBox(height: 6),
            TextField(
              controller: _villageController,
              decoration: InputDecoration(
                prefixIcon: const Icon(Icons.holiday_village_outlined),
                hintText: loc.isHindi ? 'उदा. चतुर्शी (वार्ड 4)' : 'e.g. Chaturshi (Ward 4)',
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
              ),
            ),
            const SizedBox(height: 14),

            Text(
              loc.isHindi ? 'ग्राम पंचायत' : 'Gram Panchayat',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w700,
                color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
              ),
            ),
            const SizedBox(height: 6),
            TextField(
              controller: _panchayatController,
              decoration: InputDecoration(
                prefixIcon: const Icon(Icons.account_balance_outlined),
                hintText: loc.isHindi ? 'उदा. मीनापुर ग्राम पंचायत' : 'e.g. Minapur Gram Panchayat',
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
              ),
            ),
            const SizedBox(height: 24),

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
