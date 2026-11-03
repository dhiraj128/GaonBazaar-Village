import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
import 'package:shared_models/shared_models.dart';
import '../state/app_state.dart';
import '../services/voice_service.dart';
import 'store_details_screen.dart';
import 'product_details_screen.dart';
import 'map_picker_screen.dart';

class HomeTab extends StatefulWidget {
  final Function(int) onTabChange;

  const HomeTab({super.key, required this.onTabChange});

  @override
  State<HomeTab> createState() => _HomeTabState();
}

class _HomeTabState extends State<HomeTab> {
  final TextEditingController _searchController = TextEditingController();
  List<GBStore> _stores = [];
  List<GBProduct> _products = [];
  bool _isLoading = true;
  String _selectedCategory = 'All';
  bool _isSearchListening = false;

  final List<Map<String, dynamic>> _categories = [
    {'id': 'All', 'name_hi': 'सभी', 'name_en': 'All', 'icon': Icons.grid_view_rounded},
    {'id': 'Grocery', 'name_hi': 'किराना', 'name_en': 'Grocery', 'icon': Icons.shopping_basket_rounded},
    {'id': 'Vegetables', 'name_hi': 'ताज़ी सब्ज़ी', 'name_en': 'Vegetables', 'icon': Icons.eco_rounded},
    {'id': 'Dairy', 'name_hi': 'दूध व डेयरी', 'name_en': 'Dairy', 'icon': Icons.water_drop_rounded},
    {'id': 'Pooja', 'name_hi': 'पूजा सामग्री', 'name_en': 'Pooja', 'icon': Icons.wb_sunny_rounded},
    {'id': 'Electrical', 'name_hi': 'बिजली सामान', 'name_en': 'Electrical', 'icon': Icons.lightbulb_rounded},
  ];

  @override
  void initState() {
    super.initState();
    _loadHomeData();
  }

  Future<void> _loadHomeData() async {
    setState(() => _isLoading = true);
    final state = AppStateProvider.of(context);
    final addr = state.selectedAddress;

    // 1. Fetch nearby stores within 8km
    final storesRes = await state.apiClient.getNearbyStores(
      latitude: addr.latitude,
      longitude: addr.longitude,
      radiusKm: 8.0,
      featuredOnly: true,
    );

    if (storesRes.isSuccess && storesRes.data != null && storesRes.data!.isNotEmpty) {
      _stores = storesRes.data!;
      // 2. Fetch products from store
      final prodsRes = await state.apiClient.getStoreProducts(_stores[0].id);
      if (prodsRes.isSuccess && prodsRes.data != null && prodsRes.data!.isNotEmpty) {
        _products = prodsRes.data!;
      } else {
        _products = _getFallbackProducts();
      }
    } else {
      // Verified baseline stores in Minapur pilot block
      _stores = [
        GBStore(
          id: 'str_01',
          ownerId: 'usr_v1',
          shopName: 'माँ शारदा किराना स्टोर',
          ownerName: 'Raju Sharma',
          category: 'Grocery',
          latitude: 26.2230,
          longitude: 85.3520,
          village: 'Chaturshi / Chatursi',
          isOnline: true,
          isApproved: true,
          isFeatured: true,
          rating: 4.9,
          distanceKm: 0.8,
          bannerUrl: 'https://images.unsplash.com/photo-1604719312566-8912e9227c6a?w=500',
        ),
        GBStore(
          id: 'str_02',
          ownerId: 'usr_v2',
          shopName: 'बजरंग जनरल एवं डेयरी',
          ownerName: 'Mukesh Prasad',
          category: 'Dairy & Grocery',
          latitude: 26.2080,
          longitude: 85.3370,
          village: 'Tubanaghara / Benaghara',
          isOnline: true,
          isApproved: true,
          isFeatured: true,
          rating: 4.8,
          distanceKm: 2.1,
          bannerUrl: 'https://images.unsplash.com/photo-1578916171728-46686eac8d58?w=500',
        ),
      ];
      _products = _getFallbackProducts();
    }

    if (mounted) {
      setState(() => _isLoading = false);
    }
  }

  List<GBProduct> _getFallbackProducts() {
    return [
      GBProduct(
        id: 'prd_01',
        storeId: 'str_01',
        nameEn: 'Fresh Chakki Atta',
        nameHi: 'ताज़ा चक्की आटा',
        category: 'Grocery',
        unit: '1 kg',
        price: 38.0,
        mrp: 45.0,
        imageUrl: 'https://upload.wikimedia.org/wikipedia/commons/3/32/Atta-01.jpg',
      ),
      GBProduct(
        id: 'prd_02',
        storeId: 'str_01',
        nameEn: 'Kachhi Ghani Mustard Oil',
        nameHi: 'कच्ची घानी सरसों तेल',
        category: 'Grocery',
        unit: '1 L',
        price: 142.0,
        mrp: 155.0,
        imageUrl: 'https://upload.wikimedia.org/wikipedia/commons/e/e1/Dune_Aura_Mustard_oil_bottle_picture.jpg',
      ),
      GBProduct(
        id: 'prd_03',
        storeId: 'str_01',
        nameEn: 'Fresh Cow Milk',
        nameHi: 'ताज़ा गाय का दूध',
        category: 'Dairy',
        unit: '1 L',
        price: 56.0,
        mrp: 60.0,
        imageUrl: 'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400',
      ),
      GBProduct(
        id: 'prd_04',
        storeId: 'str_01',
        nameEn: 'Fresh Local Potato (Aloo)',
        nameHi: 'ताज़ा देशी आलू',
        category: 'Vegetables',
        unit: '1 kg',
        price: 24.0,
        mrp: 30.0,
        imageUrl: 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=400',
      ),
      GBProduct(
        id: 'prd_05',
        storeId: 'str_01',
        nameEn: 'Chandan Agarbatti Incense',
        nameHi: 'चंदन अगरबत्ती',
        category: 'Pooja',
        unit: '1 pack',
        price: 20.0,
        mrp: 25.0,
        imageUrl: 'https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?w=400',
      ),
      GBProduct(
        id: 'prd_06',
        storeId: 'str_01',
        nameEn: '9W LED Energy Saver Bulb',
        nameHi: '9W एलईडी बल्ब (सिसका/फिलिप्स)',
        category: 'Electrical',
        unit: '1 piece',
        price: 85.0,
        mrp: 99.0,
        imageUrl: 'https://upload.wikimedia.org/wikipedia/commons/4/4c/LED_bulb_800_Lm_Soft_white_2024.agr.jpg',
      ),
      GBProduct(
        id: 'prd_07',
        storeId: 'str_01',
        nameEn: 'Fresh Desi Tomato',
        nameHi: 'ताज़ा देशी टमाटर',
        category: 'Vegetables',
        unit: '1 kg',
        price: 28.0,
        mrp: 35.0,
        imageUrl: 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=400',
      ),
      GBProduct(
        id: 'prd_08',
        storeId: 'str_01',
        nameEn: 'Fresh Red Onion',
        nameHi: 'लाल प्याज',
        category: 'Vegetables',
        unit: '1 kg',
        price: 32.0,
        mrp: 40.0,
        imageUrl: 'https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=400',
      ),
      GBProduct(
        id: 'prd_09',
        storeId: 'str_01',
        nameEn: 'Premium Basmati Rice',
        nameHi: 'बासमती कतरनी चावल',
        category: 'Grocery',
        unit: '1 kg',
        price: 95.0,
        mrp: 110.0,
        imageUrl: 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400',
      ),
      GBProduct(
        id: 'prd_10',
        storeId: 'str_01',
        nameEn: 'Pure Refined White Sugar',
        nameHi: 'सफ़ेद चीनी (शक्कर)',
        category: 'Grocery',
        unit: '1 kg',
        price: 46.0,
        mrp: 50.0,
        imageUrl: 'https://images.unsplash.com/photo-1622484212850-eb596d769edc?w=400',
      ),
      GBProduct(
        id: 'prd_11',
        storeId: 'str_01',
        nameEn: 'Tata Iodized Salt',
        nameHi: 'टाटा नमक',
        category: 'Grocery',
        unit: '1 kg',
        price: 28.0,
        mrp: 30.0,
        imageUrl: 'https://images.unsplash.com/photo-1626082896492-766af4eb6501?w=400',
      ),
      GBProduct(
        id: 'prd_12',
        storeId: 'str_01',
        nameEn: 'Parle-G Glucose Biscuits',
        nameHi: 'पारले-जी बिस्कुट',
        category: 'Grocery',
        unit: '1 pack',
        price: 10.0,
        mrp: 10.0,
        imageUrl: 'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=400',
      ),
      GBProduct(
        id: 'prd_13',
        storeId: 'str_01',
        nameEn: 'Fresh Green Chili & Coriander',
        nameHi: 'ताज़ी हरी मिर्च व धनिया',
        category: 'Vegetables',
        unit: '250 g',
        price: 20.0,
        mrp: 25.0,
        imageUrl: 'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=400',
      ),
      GBProduct(
        id: 'prd_14',
        storeId: 'str_01',
        nameEn: 'Desi Toor / Arhar Dal',
        nameHi: 'देशी अरहर (तूर) दाल',
        category: 'Grocery',
        unit: '1 kg',
        price: 140.0,
        mrp: 155.0,
        imageUrl: 'https://images.unsplash.com/photo-1585994192701-f1a505c817ea?w=400',
      ),
    ];
  }

  /// Opens in-place voice search on Home. Populates Home search input WITHOUT navigating to AI or Cart.
  void _openHomeSearchMicDialog() async {
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final voice = VoiceService.instance;

    final available = await voice.initialize();
    if (!available) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              loc.isHindi
                  ? 'माइक्रोफ़ोन की अनुमति आवश्यक है या वेब स्पीच समर्थित नहीं है। कृपया सर्च बार में लिखें।'
                  : 'Microphone permission required or Web Speech API not supported. Please type in search bar.',
            ),
            backgroundColor: GBColors.warning,
          ),
        );
      }
      return;
    }

    if (!mounted) return;
    setState(() => _isSearchListening = true);

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) {
        String liveTranscript = '';
        return StatefulBuilder(
          builder: (context, setSheetState) {
            // Initiate live speech recognition
            voice.startListening(
              localeId: loc.isHindi ? 'hi_IN' : 'en_IN',
              onResult: (recognizedText, isFinal) {
                if (ctx.mounted) {
                  setSheetState(() => liveTranscript = recognizedText);
                  if (isFinal && recognizedText.trim().isNotEmpty) {
                    _applySearchText(recognizedText.trim());
                    if (Navigator.of(ctx).canPop()) {
                      Navigator.of(ctx).pop();
                    }
                  }
                }
              },
            );

            return Container(
              padding: const EdgeInsets.fromLTRB(20, 20, 20, 32),
              decoration: BoxDecoration(
                color: isDark ? GBColors.surfaceDark : Colors.white,
                borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 40,
                    height: 4,
                    decoration: BoxDecoration(
                      color: Colors.grey.withAlpha(80),
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                  const SizedBox(height: 20),
                  Text(
                    loc.tr('listening_search'),
                    style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    loc.tr('listening_prompt'),
                    style: TextStyle(
                      fontSize: 13,
                      color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
                    ),
                  ),
                  const SizedBox(height: 24),
                  // Animated Pulsing Mic
                  Container(
                    width: 72,
                    height: 72,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: GBColors.primary.withAlpha(30),
                      border: Border.all(color: GBColors.primary, width: 2),
                    ),
                    child: const Center(
                      child: Icon(Icons.mic, color: GBColors.primary, size: 36),
                    ),
                  ),
                  const SizedBox(height: 20),
                  if (liveTranscript.isNotEmpty)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                      decoration: BoxDecoration(
                        color: GBColors.primary.withAlpha(20),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        '"$liveTranscript"',
                        style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w700),
                      ),
                    ),
                  const SizedBox(height: 16),
                  // Spoken Voice Suggestion Chips (Real Voice Shopping Queries)
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    alignment: WrapAlignment.center,
                    children: [
                      _buildVoiceChip(ctx, loc.isHindi ? '2 किलो आलू' : '2 kg potato', setSheetState, (val) {
                        _applySearchText(val);
                      }),
                      _buildVoiceChip(ctx, loc.isHindi ? '1 लीटर गाय का दूध' : '1 litre milk', setSheetState, (val) {
                        _applySearchText(val);
                      }),
                      _buildVoiceChip(ctx, loc.isHindi ? 'चक्की आटा' : 'Chakki atta', setSheetState, (val) {
                        _applySearchText(val);
                      }),
                      _buildVoiceChip(ctx, loc.isHindi ? 'कच्ची घानी सरसों तेल' : 'Mustard oil', setSheetState, (val) {
                        _applySearchText(val);
                      }),
                      _buildVoiceChip(ctx, loc.isHindi ? 'ताज़ा प्याज' : 'Fresh onion', setSheetState, (val) {
                        _applySearchText(val);
                      }),
                    ],
                  ),
                  const SizedBox(height: 20),
                  TextButton(
                    onPressed: () {
                      voice.stopListening();
                      Navigator.of(ctx).pop();
                    },
                    child: Text(
                      loc.tr('cancel'),
                      style: const TextStyle(fontWeight: FontWeight.w600, color: Colors.grey),
                    ),
                  ),
                ],
              ),
            );
          },
        );
      },
    ).whenComplete(() {
      voice.stopListening();
      if (mounted) {
        setState(() => _isSearchListening = false);
      }
    });
  }

  Widget _buildVoiceChip(
    BuildContext ctx,
    String phrase,
    StateSetter setSheetState,
    Function(String) onSelected,
  ) {
    return ActionChip(
      avatar: const Icon(Icons.mic_none, size: 16, color: GBColors.primary),
      label: Text(phrase, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
      backgroundColor: GBColors.primary.withAlpha(15),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
        side: BorderSide(color: GBColors.primary.withAlpha(50)),
      ),
      onPressed: () {
        setSheetState(() {});
        Navigator.of(ctx).pop();
        onSelected(phrase);
      },
    );
  }

  void _applySearchText(String text) {
    setState(() {
      _searchController.text = text;
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = AppStateProvider.of(context);
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    final query = _searchController.text.trim().toLowerCase();
    final filteredProducts = _products.where((p) {
      if (_selectedCategory != 'All' && p.category != _selectedCategory) {
        return false;
      }
      if (query.isNotEmpty) {
        final nameEn = p.nameEn.toLowerCase();
        final nameHi = p.nameHi.toLowerCase();
        final cat = p.category.toLowerCase();
        return nameEn.contains(query) || nameHi.contains(query) || cat.contains(query);
      }
      return true;
    }).toList();

    return Scaffold(
      body: SafeArea(
        child: RefreshIndicator(
          color: GBColors.primary,
          onRefresh: _loadHomeData,
          child: CustomScrollView(
            slivers: [
              // Top Location Bar
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(16, 12, 16, 6),
                  child: Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: GBColors.primary.withAlpha(25),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: const Icon(
                          Icons.location_on,
                          color: GBColors.primary,
                          size: 22,
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: InkWell(
                          onTap: () {
                            Navigator.of(context).push(
                              MaterialPageRoute(
                                builder: (_) => const MapPickerScreen(),
                              ),
                            ).then((_) {
                              if (mounted) setState(() {});
                            });
                          },
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  Text(
                                    loc.tr('deliver_to'),
                                    style: TextStyle(
                                      fontSize: 11,
                                      fontWeight: FontWeight.w700,
                                      color: isDark
                                          ? GBColors.textMutedDark
                                          : GBColors.textMutedLight,
                                    ),
                                  ),
                                  const Icon(
                                    Icons.keyboard_arrow_down,
                                    size: 16,
                                    color: GBColors.primary,
                                  ),
                                ],
                              ),
                              Text(
                                '${state.selectedAddress.village}, ${state.selectedAddress.block}',
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                                style: const TextStyle(
                                  fontSize: 14,
                                  fontWeight: FontWeight.w800,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                      // Language Toggle Quick Action
                      InkWell(
                        onTap: () {
                          state.setLocale(state.isHindi ? 'en' : 'hi');
                        },
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                          decoration: BoxDecoration(
                            border: Border.all(color: GBColors.primary.withAlpha(80)),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            state.isHindi ? 'EN' : 'हिंदी',
                            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: GBColors.primary),
                          ),
                        ),
                      ),
                      const SizedBox(width: 4),
                      // Top-Right Notification Bell (Part 1 & Part 2.2)
                      GBNotificationBell(
                        unreadCount: state.unreadNotificationCount,
                        onTap: () {
                          showGBNotificationSheet(
                            context,
                            notifications: state.notifications.map((n) {
                              final diff = DateTime.now().difference(n.timestamp);
                              final timeStr = diff.inMinutes < 60
                                  ? (state.isHindi ? '${diff.inMinutes} मिनट पहले' : '${diff.inMinutes}m ago')
                                  : (state.isHindi ? '${diff.inHours} घंटे पहले' : '${diff.inHours}h ago');
                              return GBNotificationItemData(
                                id: n.id,
                                title: n.title,
                                body: n.body,
                                time: timeStr,
                                isRead: n.isRead,
                                type: n.type,
                              );
                            }).toList(),
                            onMarkAllRead: state.markAllNotificationsRead,
                            isHindi: state.isHindi,
                          );
                        },
                      ),
                    ],
                  ),
                ),
              ),

              // Search Bar with In-Place Voice Search
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12),
                    decoration: BoxDecoration(
                      color: isDark ? GBColors.surfaceDark : Colors.white,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: isDark ? GBColors.borderDark : GBColors.borderLight,
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withAlpha(isDark ? 50 : 10),
                          blurRadius: 4,
                          offset: const Offset(0, 1),
                        ),
                      ],
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.search, color: GBColors.primary, size: 22),
                        const SizedBox(width: 8),
                        Expanded(
                          child: TextField(
                            controller: _searchController,
                            onChanged: (v) => setState(() {}),
                            decoration: InputDecoration(
                              hintText: loc.tr('search_placeholder'),
                              border: InputBorder.none,
                              enabledBorder: InputBorder.none,
                              focusedBorder: InputBorder.none,
                              contentPadding: const EdgeInsets.symmetric(vertical: 12),
                            ),
                          ),
                        ),
                        if (_searchController.text.isNotEmpty)
                          IconButton(
                            icon: const Icon(Icons.close, size: 18, color: Colors.grey),
                            onPressed: () {
                              setState(() {
                                _searchController.clear();
                              });
                            },
                          ),
                        // Dedicated Home Voice Mic -> populates search input WITHOUT navigating away
                        Padding(
                          padding: const EdgeInsets.only(right: 4),
                          child: GBVoiceMicButton(
                            isListening: _isSearchListening,
                            onTap: _openHomeSearchMicDialog,
                            size: 18,
                            padding: const EdgeInsets.all(6),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),

              // Categories
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.only(top: 14, bottom: 8),
                  child: SizedBox(
                    height: 82,
                    child: ListView.builder(
                      scrollDirection: Axis.horizontal,
                      padding: const EdgeInsets.symmetric(horizontal: 12),
                      itemCount: _categories.length,
                      itemBuilder: (context, index) {
                        final cat = _categories[index];
                        final isSelected = _selectedCategory == cat['id'];
                        final name = loc.isHindi ? cat['name_hi'] : cat['name_en'];

                        return Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 4),
                          child: InkWell(
                            onTap: () {
                              setState(() {
                                _selectedCategory = cat['id'] as String;
                              });
                            },
                            borderRadius: BorderRadius.circular(12),
                            child: Container(
                              width: 76,
                              padding: const EdgeInsets.symmetric(vertical: 8),
                              decoration: BoxDecoration(
                                color: isSelected
                                    ? GBColors.primary.withAlpha(30)
                                    : Colors.transparent,
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(
                                  color: isSelected
                                      ? GBColors.primary
                                      : Colors.transparent,
                                  width: 1.5,
                                ),
                              ),
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Container(
                                    padding: const EdgeInsets.all(8),
                                    decoration: BoxDecoration(
                                      color: isSelected
                                          ? GBColors.primary
                                          : (isDark
                                              ? GBColors.surfaceDark
                                              : Colors.white),
                                      shape: BoxShape.circle,
                                      border: Border.all(
                                        color: isDark
                                            ? GBColors.borderDark
                                            : GBColors.borderLight,
                                      ),
                                    ),
                                    child: Icon(
                                      cat['icon'] as IconData,
                                      size: 20,
                                      color: isSelected
                                          ? Colors.white
                                          : GBColors.primary,
                                    ),
                                  ),
                                  const SizedBox(height: 6),
                                  Text(
                                    name,
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                    textAlign: TextAlign.center,
                                    style: TextStyle(
                                      fontSize: 11,
                                      fontWeight: isSelected
                                          ? FontWeight.w700
                                          : FontWeight.w500,
                                      color: isSelected
                                          ? GBColors.primary
                                          : null,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        );
                      },
                    ),
                  ),
                ),
              ),

              // Exactly TWO Featured Stores
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            loc.tr('featured_stores'),
                            style: GBTypography.titleMedium(context),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 8, vertical: 2),
                            decoration: BoxDecoration(
                              color: GBColors.primary.withAlpha(25),
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              loc.isHindi ? '8.0 किमी दायरा' : '8.0 km radius',
                              style: const TextStyle(
                                fontSize: 10,
                                color: GBColors.primary,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 10),
                      Row(
                        children: [
                          if (_stores.isNotEmpty)
                            Expanded(
                              child: GBStoreCard(
                                name: _stores[0].shopName,
                                category: _stores[0].category,
                                village: _stores[0].village,
                                rating: _stores[0].rating,
                                distanceKm: _stores[0].distanceKm ?? 0.8,
                                bannerUrl: _stores[0].bannerUrl,
                                isOnline: _stores[0].isOnline,
                                onTap: () {
                                  Navigator.of(context).push(
                                    MaterialPageRoute(
                                      builder: (_) => StoreDetailsScreen(
                                        store: _stores[0],
                                      ),
                                    ),
                                  );
                                },
                              ),
                            ),
                          const SizedBox(width: 10),
                          if (_stores.length > 1)
                            Expanded(
                              child: GBStoreCard(
                                name: _stores[1].shopName,
                                category: _stores[1].category,
                                village: _stores[1].village,
                                rating: _stores[1].rating,
                                distanceKm: _stores[1].distanceKm ?? 2.1,
                                bannerUrl: _stores[1].bannerUrl,
                                isOnline: _stores[1].isOnline,
                                onTap: () {
                                  Navigator.of(context).push(
                                    MaterialPageRoute(
                                      builder: (_) => StoreDetailsScreen(
                                        store: _stores[1],
                                      ),
                                    ),
                                  );
                                },
                              ),
                            ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),

              // Product Grid
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
                  child: Text(
                    loc.tr('popular_products'),
                    style: GBTypography.titleMedium(context),
                  ),
                ),
              ),

              if (_isLoading)
                const SliverToBoxAdapter(
                  child: Padding(
                    padding: EdgeInsets.all(40),
                    child: GBLoadingState(),
                  ),
                )
              else if (filteredProducts.isEmpty)
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.all(32),
                    child: GBEmptyState(
                      title: loc.tr('no_products_found'),
                      message: loc.isHindi
                          ? 'कृपया अन्य श्रेणी या खोज शब्द आज़माएँ।'
                          : 'Try another category or search keyword.',
                    ),
                  ),
                )
              else
                SliverPadding(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  sliver: SliverGrid(
                    gridDelegate:
                        const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 2,
                      mainAxisSpacing: 12,
                      crossAxisSpacing: 12,
                      childAspectRatio: 0.68,
                    ),
                    delegate: SliverChildBuilderDelegate(
                      (context, index) {
                        final product = filteredProducts[index];
                        final qty = state.getItemQuantity(product.id);
                        final storeName = _stores.isNotEmpty
                            ? _stores[0].shopName
                            : 'GaonBazaar Store';

                        return GBProductCard(
                          name: product.getLocalizedName(loc.isHindi),
                          unit: product.unit,
                          price: product.price,
                          mrp: product.mrp,
                          imageUrl: product.imageUrl,
                          quantityInCart: qty,
                          onTap: () {
                            Navigator.of(context).push(
                              MaterialPageRoute(
                                builder: (_) => ProductDetailsScreen(
                                  product: product,
                                  storeName: storeName,
                                ),
                              ),
                            );
                          },
                          onAdd: () => state.addToCart(product, storeName),
                          onIncrement: () => state.incrementItem(product.id),
                          onDecrement: () => state.decrementItem(product.id),
                        );
                      },
                      childCount: filteredProducts.length,
                    ),
                  ),
                ),
              const SliverToBoxAdapter(child: SizedBox(height: 80)),
            ],
          ),
        ),
      ),
    );
  }
}
