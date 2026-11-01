import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
import 'package:shared_models/shared_models.dart';
import '../state/app_state.dart';
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
    );

    if (storesRes.isSuccess && storesRes.data != null && storesRes.data!.isNotEmpty) {
      _stores = storesRes.data!;
      // 2. Fetch products from the first store
      final prodsRes = await state.apiClient.getStoreProducts(_stores[0].id);
      if (prodsRes.isSuccess && prodsRes.data != null) {
        _products = prodsRes.data!;
      }
    } else {
      // Fallback baseline stores in Minapur pilot
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
      _products = [
        GBProduct(
          id: 'prd_01',
          storeId: 'str_01',
          nameEn: 'Chakki Fresh Atta',
          nameHi: 'ताज़ा चक्की आटा',
          category: 'Grocery',
          unit: '1 kg',
          price: 38.0,
          mrp: 45.0,
          imageUrl: 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400',
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
          imageUrl: 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400',
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
          nameHi: '९ वॉट एलईडी बल्ब',
          category: 'Electrical',
          unit: '1 piece',
          price: 85.0,
          mrp: 99.0,
          imageUrl: 'https://images.unsplash.com/photo-1550985543-f47f38aeee65?w=400',
        ),
        GBProduct(
          id: 'prd_07',
          storeId: 'str_01',
          nameEn: 'Fresh Desi Tomato (Tamatar)',
          nameHi: 'देशी लाल टमाटर',
          category: 'Vegetables',
          unit: '1 kg',
          price: 28.0,
          mrp: 35.0,
          imageUrl: 'https://images.unsplash.com/photo-1546470427-227c7369a941?w=400',
        ),
        GBProduct(
          id: 'prd_08',
          storeId: 'str_01',
          nameEn: 'Red Onion (Pyaz)',
          nameHi: 'ताज़ा लाल प्याज',
          category: 'Vegetables',
          unit: '1 kg',
          price: 34.0,
          mrp: 40.0,
          imageUrl: 'https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=400',
        ),
        GBProduct(
          id: 'prd_09',
          storeId: 'str_01',
          nameEn: 'Basmati Rice (Minapur)',
          nameHi: 'बासमती चावल',
          category: 'Grocery',
          unit: '1 kg',
          price: 58.0,
          mrp: 65.0,
          imageUrl: 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400',
        ),
        GBProduct(
          id: 'prd_10',
          storeId: 'str_01',
          nameEn: 'Pure Refined Sugar (Cheeni)',
          nameHi: 'सफ़ेद चीनी (शक्कर)',
          category: 'Grocery',
          unit: '1 kg',
          price: 42.0,
          mrp: 46.0,
          imageUrl: 'https://images.unsplash.com/photo-1622484212850-eb596d769edc?w=400',
        ),
        GBProduct(
          id: 'prd_11',
          storeId: 'str_01',
          nameEn: 'Tata Iodized Salt (Namak)',
          nameHi: 'टाटा नमक आयोडीन युक्त',
          category: 'Grocery',
          unit: '1 kg',
          price: 26.0,
          mrp: 28.0,
          imageUrl: 'https://images.unsplash.com/photo-1626082896492-766af4eb6501?w=400',
        ),
        GBProduct(
          id: 'prd_12',
          storeId: 'str_01',
          nameEn: 'Parle-G Glucose Biscuits',
          nameHi: 'पारले-जी बिस्कुट',
          category: 'Grocery',
          unit: '250 g',
          price: 24.0,
          mrp: 25.0,
          imageUrl: 'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=400',
        ),
        GBProduct(
          id: 'prd_13',
          storeId: 'str_01',
          nameEn: 'Green Chili & Coriander',
          nameHi: 'ताज़ा हरी मिर्च और धनिया',
          category: 'Vegetables',
          unit: '250 g',
          price: 18.0,
          mrp: 20.0,
          imageUrl: 'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=400',
        ),
        GBProduct(
          id: 'prd_14',
          storeId: 'str_01',
          nameEn: 'Desi Toor / Arhar Dal',
          nameHi: 'देशी अरहर दाल',
          category: 'Grocery',
          unit: '1 kg',
          price: 138.0,
          mrp: 145.0,
          imageUrl: 'https://images.unsplash.com/photo-1585994192701-f1a505c817ea?w=400',
        ),
      ];
    }

    if (mounted) {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = AppStateProvider.of(context);
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    final filteredProducts = _products.where((p) {
      if (_selectedCategory != 'All' && p.category != _selectedCategory) {
        return false;
      }
      if (_searchController.text.isNotEmpty) {
        final query = _searchController.text.toLowerCase();
        return p.nameEn.toLowerCase().contains(query) ||
            p.nameHi.toLowerCase().contains(query);
      }
      return true;
    }).toList();

    return Scaffold(
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: _loadHomeData,
          color: GBColors.primary,
          child: CustomScrollView(
            slivers: [
              // 1 & 2: Header (Logo, Location picker, Notification bell)
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                  child: Row(
                    children: [
                      // GaonBazaar Logo & Tagline
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: GBColors.primary,
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: const Icon(
                          Icons.local_shipping_rounded,
                          color: Colors.white,
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
                            );
                          },
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  Text(
                                    loc.isHindi ? 'डिलीवरी पता' : 'Deliver to',
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
                      // Notification Bell
                      IconButton(
                        icon: const Icon(Icons.notifications_none_rounded),
                        onPressed: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text('गाँव बाज़ार में कोई नई सूचना नहीं है।'),
                              duration: Duration(seconds: 2),
                            ),
                          );
                        },
                      ),
                    ],
                  ),
                ),
              ),

              // 3: One search bar with working microphone
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
                          color: Colors.black.withOpacity(isDark ? 0.2 : 0.03),
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
                        // Working Mic Icon -> Switches to AI Assistant Tab!
                        GBVoiceMicButton(
                          isListening: false,
                          onTap: () {
                            // Switch to AI Voice Assistant tab (Tab index 1)
                            widget.onTabChange(1);
                          },
                        ),
                      ],
                    ),
                  ),
                ),
              ),

              // 4: Horizontally scrolling categories
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
                                    ? GBColors.primary.withOpacity(0.12)
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

              // 5: Exactly TWO featured nearby store cards in one row
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
                            loc.isHindi
                                ? 'गाँव की प्रमुख दुकानें (Minapur)'
                                : 'Featured Stores (Nearby)',
                            style: GBTypography.titleMedium(context),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 8, vertical: 2),
                            decoration: BoxDecoration(
                              color: GBColors.primary.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: const Text(
                              '8 km radius',
                              style: TextStyle(
                                fontSize: 10,
                                color: GBColors.primary,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 10),
                      // Exactly TWO featured stores in one row
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

              // 6: Two-column real product grid immediately below stores
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
                  child: Text(
                    loc.isHindi
                        ? 'ताज़ा उत्पाद व दैनिक सामान'
                        : 'Village Daily Essentials',
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
                      title: loc.isHindi ? 'कोई सामान नहीं मिला' : 'No Items Found',
                      message: loc.isHindi
                          ? 'अन्य श्रेणी या खोज शब्द आज़माएँ।'
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
