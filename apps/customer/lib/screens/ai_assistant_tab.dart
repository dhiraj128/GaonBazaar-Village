import 'dart:async';
import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
import 'package:shared_models/shared_models.dart';
import '../services/voice_service.dart';
import '../state/app_state.dart';

class AiAssistantTab extends StatefulWidget {
  final Function(int) onTabChange;

  const AiAssistantTab({super.key, required this.onTabChange});

  @override
  State<AiAssistantTab> createState() => _AiAssistantTabState();
}

enum AiVoiceState {
  idle,
  listening,
  processing,
  matched,
  error,
}

class _AiAssistantTabState extends State<AiAssistantTab> with SingleTickerProviderStateMixin {
  final TextEditingController _textController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final List<Map<String, dynamic>> _messages = [];

  late AnimationController _pulseController;
  late Animation<double> _pulseAnimation;

  AiVoiceState _voiceState = AiVoiceState.idle;
  String _liveTranscript = '';
  String _statusMessage = '';
  GBProduct? _lastMatchedProduct;
  String? _lastActionType; // 'ADD', 'REMOVE', 'SHOW_CART', 'SEARCH'

  // Client-side fallback catalog for zero-latency instant offline matching
  static const List<Map<String, dynamic>> _catalogKnowledge = [
    {
      'id': 'cat_atta',
      'name_en': 'Chakki Fresh Atta',
      'name_hi': 'ताज़ा चक्की आटा',
      'unit': '1 kg',
      'price': 38.0,
      'image_url': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=500&q=80',
      'keywords': ['atta', 'aata', 'flour', 'wheat', 'gehu', 'आटा', 'चक्की']
    },
    {
      'id': 'cat_mustard_oil',
      'name_en': 'Kachhi Ghani Mustard Oil',
      'name_hi': 'कच्ची घानी सरसों तेल',
      'unit': '1 L',
      'price': 142.0,
      'image_url': 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=500&q=80',
      'keywords': ['mustard', 'oil', 'tel', 'sarson', 'सरसों', 'तेल']
    },
    {
      'id': 'cat_milk',
      'name_en': 'Fresh Cow Milk',
      'name_hi': 'ताज़ा गाय का दूध',
      'unit': '1 L',
      'price': 56.0,
      'image_url': 'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400',
      'keywords': ['milk', 'doodh', 'dudh', 'गाय', 'दूध']
    },
    {
      'id': 'cat_potato',
      'name_en': 'Fresh Local Potato (Aloo)',
      'name_hi': 'ताज़ा देशी आलू',
      'unit': '1 kg',
      'price': 24.0,
      'image_url': 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=400',
      'keywords': ['potato', 'aloo', 'alu', 'आलू']
    },
    {
      'id': 'cat_tomato',
      'name_en': 'Desi Tomato (Tamatar)',
      'name_hi': 'देशी लाल टमाटर',
      'unit': '1 kg',
      'price': 28.0,
      'image_url': 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=500&q=80',
      'keywords': ['tomato', 'tamatar', 'टमाटर']
    },
    {
      'id': 'cat_biscuits',
      'name_en': 'Parle-G Glucose Biscuits',
      'name_hi': 'पारले-जी ग्लूकोज बिस्कुट',
      'unit': '1 pack',
      'price': 10.0,
      'image_url': 'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=400',
      'keywords': ['biscuit', 'biscuits', 'parle', 'बिस्कुट', 'बिस्किट']
    },
    {
      'id': 'cat_detergent',
      'name_en': 'Ghadi / Surf Washing Powder',
      'name_hi': 'डिटर्जेंट पाउडर (घड़ी/सर्फ)',
      'unit': '1 kg',
      'price': 75.0,
      'image_url': 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400',
      'keywords': ['surf', 'detergent', 'ghadi', 'powder', 'washing', 'सर्फ', 'घड़ी']
    },
    {
      'id': 'cat_led_bulb',
      'name_en': '9W LED Energy Saver Bulb',
      'name_hi': '९ वॉट एलईडी बल्ब',
      'unit': '1 piece',
      'price': 85.0,
      'image_url': 'https://images.unsplash.com/photo-1550985543-f47f38aeee65?w=500&q=80',
      'keywords': ['bulb', 'led', 'light', 'बल्ब', 'बिजली']
    },
    {
      'id': 'cat_bath_soap',
      'name_en': 'Dettol / Lifebuoy Bath Soap',
      'name_hi': 'नहाने का साबुन (डेटॉल/लाइफ़बॉय)',
      'unit': '75 g',
      'price': 36.0,
      'image_url': 'https://images.unsplash.com/photo-1600857544200-b2f666a9a2ec?w=500&q=80',
      'keywords': ['soap', 'bath', 'dettol', 'lifebuoy', 'साबुन', 'डेटॉल']
    },
    {
      'id': 'cat_toothpaste',
      'name_en': 'Colgate Dental Toothpaste',
      'name_hi': 'कोलगेट टूथपेस्ट / मंजन',
      'unit': '100 g',
      'price': 58.0,
      'image_url': 'https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?w=500&q=80',
      'keywords': ['paste', 'toothpaste', 'colgate', 'dant', 'कोलगेट', 'पेस्ट']
    },
    {
      'id': 'cat_notebook',
      'name_en': 'School Notebook Copy',
      'name_hi': 'क्लासमेट कॉपी / नोटबुक',
      'unit': '1 book',
      'price': 45.0,
      'image_url': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&q=80',
      'keywords': ['copy', 'notebook', 'book', 'stationery', 'कॉपी', 'किताब']
    },
  ];

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat(reverse: true);
    _pulseAnimation = Tween<double>(begin: 1.0, end: 1.25).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );

    WidgetsBinding.instance.addPostFrameCallback((_) {
      final loc = GBLocalizations.of(context);
      _messages.add({
        'isUser': false,
        'text': loc.tr('ai_welcome_msg'),
        'product': null,
      });
      if (mounted) setState(() {});
    });
  }

  @override
  void dispose() {
    _pulseController.dispose();
    _textController.dispose();
    _scrollController.dispose();
    VoiceService.instance.stopListening();
    super.dispose();
  }

  List<String> _getSuggestions(bool isHindi) {
    if (isHindi) {
      return [
        '2 किलो आटा जोड़ो',
        '1 लीटर गाय का दूध जोड़ो',
        '1 लीटर सरसों तेल जोड़ो',
        'सर्फ एक्सेल खोजो',
        'बिस्कुट हटाओ',
        'मेरा कार्ट दिखाओ',
      ];
    }
    return [
      'Add 2 kg atta',
      'Add 1 litre milk',
      'Add 1L mustard oil',
      'Search Surf Excel',
      'Remove biscuits',
      'Show my cart',
    ];
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  // Parse quantity and product intent locally if backend is unavailable or for instant feedback
  Map<String, dynamic> _parseLocalIntent(String text) {
    final lower = text.toLowerCase();

    // Check show cart
    if (lower.contains('cart') || lower.contains('कार्ट') || lower.contains('दिखाओ') || lower.contains('show')) {
      if (lower.contains('show') || lower.contains('दिखा') || lower.contains('open') || lower.contains('view') || lower.contains('मेरा')) {
        return {'intent': 'SHOW_CART', 'quantity': 1, 'product': null};
      }
    }

    // Check remove
    final isRemove = lower.contains('remove') || lower.contains('हटा') || lower.contains('delete') || lower.contains('कम');

    // Parse quantity
    int qty = 1;
    final numMatch = RegExp(r'\b(\d+)\b').firstMatch(lower);
    if (numMatch != null) {
      qty = int.tryParse(numMatch.group(1)!) ?? 1;
    } else {
      if (lower.contains('दो') || lower.contains('do') || lower.contains('two')) qty = 2;
      if (lower.contains('तीन') || lower.contains('teen') || lower.contains('three')) qty = 3;
      if (lower.contains('चार') || lower.contains('char') || lower.contains('four')) qty = 4;
      if (lower.contains('पांच') || lower.contains('पाँच') || lower.contains('five')) qty = 5;
    }

    // Match product from knowledge
    Map<String, dynamic>? matched;
    for (final p in _catalogKnowledge) {
      final keywords = p['keywords'] as List<String>;
      for (final kw in keywords) {
        if (lower.contains(kw.toLowerCase())) {
          matched = p;
          break;
        }
      }
      if (matched != null) break;
    }

    if (matched != null) {
      if (isRemove) {
        return {'intent': 'REMOVE_FROM_CART', 'quantity': qty, 'product': matched};
      }
      if (lower.contains('search') || lower.contains('खोज') || lower.contains('ढूंढ')) {
        return {'intent': 'SEARCH_PRODUCT', 'quantity': qty, 'product': matched};
      }
      return {'intent': 'ADD_TO_CART', 'quantity': qty, 'product': matched};
    }

    return {'intent': 'UNKNOWN', 'quantity': 1, 'product': null};
  }

  Future<void> _handleUserMessage(String query) async {
    final text = query.trim();
    if (text.isEmpty) return;

    setState(() {
      _messages.add({'isUser': true, 'text': text, 'product': null});
      _voiceState = AiVoiceState.processing;
      _liveTranscript = text;
      _statusMessage = 'Analyzing query...';
    });
    _textController.clear();
    _scrollToBottom();

    final state = AppStateProvider.of(context);

    // Try backend AI API first
    Map<String, dynamic>? aiData;
    try {
      final response = await state.apiClient.queryAI(
        query: text,
        storeId: state.currentCartStoreId,
        language: state.isHindi ? 'hi' : 'en',
      ).timeout(const Duration(seconds: 4));

      if (response.isSuccess && response.data != null) {
        aiData = response.data!;
      }
    } catch (_) {
      // Fallback to client-side NLP
    }

    // If backend was empty/failed, use client NLP
    aiData ??= _parseLocalIntent(text);

    final intent = aiData['intent'] as String? ?? 'UNKNOWN';
    final qty = (aiData['quantity'] as num?)?.toInt() ?? 1;
    final matchedRaw = aiData['matched_product'] ?? aiData['product'];

    GBProduct? matchedProduct;
    if (matchedRaw != null && matchedRaw is Map<String, dynamic>) {
      matchedProduct = GBProduct(
        id: (matchedRaw['id'] as String?) ?? 'cat_item',
        storeId: state.currentCartStoreId ?? 'str_01',
        nameEn: (matchedRaw['name_en'] as String?) ?? 'Product',
        nameHi: (matchedRaw['name_hi'] as String?) ?? 'उत्पाद',
        category: (matchedRaw['category'] as String?) ?? 'Grocery',
        unit: (matchedRaw['unit'] as String?) ?? '1 unit',
        price: ((matchedRaw['price'] ?? matchedRaw['suggested_price'] ?? 40.0) as num).toDouble(),
        imageUrl: (matchedRaw['image_url'] as String?) ?? 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=500&q=80',
      );
    }

    String botReply;

    if (intent == 'ADD_TO_CART' && matchedProduct != null) {
      for (int i = 0; i < qty; i++) {
        state.addToCart(matchedProduct, state.currentCartStoreName ?? 'माँ शारदा किराना स्टोर');
      }
      _lastMatchedProduct = matchedProduct;
      _lastActionType = 'ADD';
      _voiceState = AiVoiceState.matched;

      botReply = state.isHindi
          ? '✓ ${matchedProduct.nameHi} ($qty ${matchedProduct.unit}) कार्ट में जोड़ा गया।'
          : '✓ Added $qty ${matchedProduct.unit} of ${matchedProduct.nameEn} to your cart.';
      _statusMessage = botReply;
    } else if (intent == 'SHOW_CART') {
      _lastActionType = 'SHOW_CART';
      _voiceState = AiVoiceState.matched;
      botReply = state.isHindi
          ? 'आपका कार्ट खोला जा रहा है...'
          : 'Opening your cart...';
      _statusMessage = botReply;
      Future.delayed(const Duration(milliseconds: 600), () {
        if (mounted) widget.onTabChange(2);
      });
    } else if (intent == 'REMOVE_FROM_CART' && matchedProduct != null) {
      state.decrementItem(matchedProduct.id);
      _lastMatchedProduct = matchedProduct;
      _lastActionType = 'REMOVE';
      _voiceState = AiVoiceState.matched;
      botReply = state.isHindi
          ? '✓ ${matchedProduct.nameHi} कार्ट से हटा दिया गया।'
          : '✓ Removed ${matchedProduct.nameEn} from your cart.';
      _statusMessage = botReply;
    } else if (intent == 'SEARCH_PRODUCT' && matchedProduct != null) {
      _lastMatchedProduct = matchedProduct;
      _lastActionType = 'SEARCH';
      _voiceState = AiVoiceState.matched;
      botReply = state.isHindi
          ? 'उत्पाद मिला: ${matchedProduct.nameHi} (₹${matchedProduct.price.toStringAsFixed(0)}/${matchedProduct.unit})'
          : 'Found product: ${matchedProduct.nameEn} (₹${matchedProduct.price.toStringAsFixed(0)}/${matchedProduct.unit})';
      _statusMessage = botReply;
    } else {
      _voiceState = AiVoiceState.error;
      botReply = state.isHindi
          ? 'क्षमा करें, मैं समझ नहीं पाया। कृपया नीचे दिए गए सुझावों में से चुनें या स्पष्ट बोलें।'
          : 'Could not recognize product. Please choose a suggestion below or try again.';
      _statusMessage = botReply;
    }

    setState(() {
      _messages.add({
        'isUser': false,
        'text': botReply,
        'product': matchedProduct,
      });
    });
    _scrollToBottom();
  }

  Future<void> _startVoiceRecognition() async {
    final state = AppStateProvider.of(context);
    final voice = VoiceService.instance;

    setState(() {
      _voiceState = AiVoiceState.processing;
      _liveTranscript = '';
      _statusMessage = state.isHindi ? 'माइक्रोफ़ोन प्रारंभ हो रहा है...' : 'Initializing microphone...';
    });

    try {
      final available = await voice.initialize();
      if (!available) {
        if (mounted) {
          setState(() {
            _voiceState = AiVoiceState.error;
            _statusMessage = state.isHindi
                ? 'माइक्रोफ़ोन की अनुमति आवश्यक है या वेब स्पीच समर्थित नहीं है। कृपया नीचे लिखकर पूछें।'
                : 'Microphone permission required or Web Speech API not supported. Please type your query.';
          });
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(_statusMessage),
              backgroundColor: GBColors.warning,
            ),
          );
        }
        return;
      }

      if (mounted) {
        setState(() {
          _voiceState = AiVoiceState.listening;
          _statusMessage = state.isHindi ? 'सुन रहे हैं... बोलिए' : 'Listening... speak now';
        });
      }

      await voice.startListening(
        localeId: state.isHindi ? 'hi_IN' : 'en_IN',
        onResult: (text, isFinal) {
          if (mounted) {
            setState(() {
              _liveTranscript = text;
              _statusMessage = '"$text"';
            });
            if (isFinal && text.trim().isNotEmpty) {
              voice.stopListening();
              _handleUserMessage(text.trim());
            }
          }
        },
      );
    } catch (e) {
      if (mounted) {
        setState(() {
          _voiceState = AiVoiceState.error;
          _statusMessage = 'Speech error: $e';
        });
      }
    }
  }

  void _stopVoiceRecognition() {
    VoiceService.instance.stopListening();
    if (_voiceState == AiVoiceState.listening) {
      if (_liveTranscript.trim().isNotEmpty) {
        _handleUserMessage(_liveTranscript.trim());
      } else {
        setState(() {
          _voiceState = AiVoiceState.idle;
          _statusMessage = '';
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = AppStateProvider.of(context);
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final suggestions = _getSuggestions(state.isHindi);

    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, _) {
        if (!didPop) {
          widget.onTabChange(0); // Return to Home tab
        }
      },
      child: Scaffold(
        appBar: AppBar(
          leading: IconButton(
            icon: const Icon(Icons.arrow_back),
            tooltip: loc.isHindi ? 'होम पर वापस जाएं' : 'Back to Home',
            onPressed: () => widget.onTabChange(0),
          ),
          title: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(
                  color: GBColors.primary,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(Icons.auto_awesome, color: Colors.white, size: 18),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      loc.tr('ai_assistant_title'),
                      style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800),
                    ),
                    Text(
                      loc.isHindi ? 'आवाज से स्मार्ट खरीदारी' : 'Voice Shopping & Ordering',
                      style: TextStyle(
                        fontSize: 11,
                        color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          actions: [
            IconButton(
              icon: const Icon(Icons.delete_sweep_outlined),
              tooltip: loc.isHindi ? 'चैट साफ़ करें' : 'Clear Chat',
              onPressed: () {
                setState(() {
                  _messages.clear();
                  _voiceState = AiVoiceState.idle;
                  _statusMessage = '';
                  _liveTranscript = '';
                  _lastMatchedProduct = null;
                  _messages.add({
                    'isUser': false,
                    'text': loc.tr('ai_welcome_msg'),
                    'product': null,
                  });
                });
              },
            ),
          ],
        ),
        body: SafeArea(
          child: Column(
            children: [
              // Visibly Centered Prominent Pulsing Microphone Section
              _buildCenteredMicrophoneHero(loc, isDark),

              // Conversation Chat Stream
              Expanded(
                child: ListView.builder(
                  controller: _scrollController,
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  itemCount: _messages.length,
                  itemBuilder: (context, index) {
                    final msg = _messages[index];
                    final isUser = msg['isUser'] as bool;
                    final prod = msg['product'] as GBProduct?;

                    return Align(
                      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                      child: Container(
                        margin: const EdgeInsets.only(bottom: 12),
                        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                        constraints: BoxConstraints(
                          maxWidth: MediaQuery.of(context).size.width * 0.82,
                        ),
                        decoration: BoxDecoration(
                          color: isUser
                              ? GBColors.primary
                              : (isDark ? GBColors.cardDark : Colors.white),
                          borderRadius: BorderRadius.only(
                            topLeft: const Radius.circular(16),
                            topRight: const Radius.circular(16),
                            bottomLeft: Radius.circular(isUser ? 16 : 4),
                            bottomRight: Radius.circular(isUser ? 4 : 16),
                          ),
                          border: isUser
                              ? null
                              : Border.all(
                                  color: isDark ? GBColors.borderDark : GBColors.borderLight,
                                ),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(isDark ? 0.2 : 0.06),
                              blurRadius: 4,
                              offset: const Offset(0, 1),
                            ),
                          ],
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              msg['text'] as String,
                              style: TextStyle(
                                color: isUser
                                    ? Colors.white
                                    : (isDark ? GBColors.textPrimaryDark : GBColors.textPrimaryLight),
                                fontSize: 13.5,
                                height: 1.4,
                              ),
                            ),
                            // Show product action card if available
                            if (prod != null) ...[
                              const SizedBox(height: 8),
                              Container(
                                padding: const EdgeInsets.all(8),
                                decoration: BoxDecoration(
                                  color: isDark ? GBColors.surfaceDark : Colors.grey.shade50,
                                  borderRadius: BorderRadius.circular(8),
                                  border: Border.all(color: Colors.grey.shade300),
                                ),
                                child: Row(
                                  children: [
                                    ClipRRect(
                                      borderRadius: BorderRadius.circular(6),
                                      child: Image.network(
                                        prod.imageUrl,
                                        width: 44,
                                        height: 44,
                                        fit: BoxFit.cover,
                                        errorBuilder: (_, __, ___) => const Icon(Icons.shopping_bag, size: 28),
                                      ),
                                    ),
                                    const SizedBox(width: 10),
                                    Expanded(
                                      child: Column(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        children: [
                                          Text(
                                            state.isHindi ? prod.nameHi : prod.nameEn,
                                            style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 12),
                                          ),
                                          Text(
                                            '₹${prod.price.toStringAsFixed(0)} / ${prod.unit}',
                                            style: const TextStyle(fontSize: 11, color: GBColors.primary, fontWeight: FontWeight.bold),
                                          ),
                                        ],
                                      ),
                                    ),
                                    IconButton(
                                      icon: const Icon(Icons.add_shopping_cart, size: 20, color: GBColors.primary),
                                      onPressed: () {
                                        state.addToCart(prod, state.currentCartStoreName ?? 'माँ शारदा किराना स्टोर');
                                        ScaffoldMessenger.of(context).showSnackBar(
                                          SnackBar(
                                            content: Text('Added ${prod.nameEn} to Cart'),
                                            duration: const Duration(seconds: 1),
                                          ),
                                        );
                                      },
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ],
                        ),
                      ),
                    );
                  },
                ),
              ),

              // Horizontal Voice Action Suggestions
              Container(
                height: 42,
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: ListView.separated(
                  scrollDirection: Axis.horizontal,
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  itemCount: suggestions.length,
                  separatorBuilder: (_, __) => const SizedBox(width: 6),
                  itemBuilder: (context, idx) {
                    final phrase = suggestions[idx];
                    return ActionChip(
                      avatar: const Icon(Icons.mic, size: 14, color: GBColors.primary),
                      label: Text(
                        phrase,
                        style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600),
                      ),
                      backgroundColor: isDark ? GBColors.cardDark : Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                        side: BorderSide(
                          color: isDark ? GBColors.borderDark : GBColors.borderLight,
                        ),
                      ),
                      onPressed: () => _handleUserMessage(phrase),
                    );
                  },
                ),
              ),
              const SizedBox(height: 6),

              // Bottom Text Input Bar
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: isDark ? GBColors.surfaceDark : Colors.white,
                  border: Border(
                    top: BorderSide(
                      color: isDark ? GBColors.borderDark : GBColors.borderLight,
                    ),
                  ),
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 14),
                        decoration: BoxDecoration(
                          color: isDark ? GBColors.cardDark : GBColors.surfaceLight,
                          borderRadius: BorderRadius.circular(24),
                          border: Border.all(
                            color: isDark ? GBColors.borderDark : GBColors.borderLight,
                          ),
                        ),
                        child: TextField(
                          controller: _textController,
                          onSubmitted: _handleUserMessage,
                          decoration: InputDecoration(
                            hintText: loc.isHindi
                                ? 'यहाँ टाइप करें (उदा. "2 किलो आटा")...'
                                : 'Type query (e.g. "Add 2 kg atta")...',
                            hintStyle: TextStyle(
                              fontSize: 12.5,
                              color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
                            ),
                            border: InputBorder.none,
                            contentPadding: const EdgeInsets.symmetric(vertical: 10),
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    IconButton(
                      icon: const Icon(Icons.send_rounded, color: GBColors.primary),
                      onPressed: () => _handleUserMessage(_textController.text),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // Centered Pulsing Microphone Hero Card
  Widget _buildCenteredMicrophoneHero(GBLocalizations loc, bool isDark) {
    final state = AppStateProvider.of(context);
    final isListening = _voiceState == AiVoiceState.listening;

    return Container(
      width: double.infinity,
      margin: const EdgeInsets.fromLTRB(16, 12, 16, 8),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      decoration: BoxDecoration(
        color: isDark ? GBColors.cardDark : Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: isListening ? GBColors.primary : (isDark ? GBColors.borderDark : GBColors.borderLight),
          width: isListening ? 2 : 1,
        ),
        boxShadow: [
          BoxShadow(
            color: isListening
                ? GBColors.primary.withOpacity(0.18)
                : Colors.black.withOpacity(isDark ? 0.2 : 0.04),
            blurRadius: isListening ? 14 : 6,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Centered Animated Microphone Button
          GestureDetector(
            onTap: isListening ? _stopVoiceRecognition : _startVoiceRecognition,
            child: AnimatedBuilder(
              animation: _pulseAnimation,
              builder: (context, child) {
                final scale = isListening ? _pulseAnimation.value : 1.0;
                return Transform.scale(
                  scale: scale,
                  child: Container(
                    width: 76,
                    height: 76,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      gradient: LinearGradient(
                        colors: isListening
                            ? [GBColors.primary, const Color(0xFF1B8A44)]
                            : [GBColors.primary.withOpacity(0.15), GBColors.primary.withOpacity(0.08)],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      border: Border.all(
                        color: GBColors.primary,
                        width: isListening ? 3 : 2,
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: GBColors.primary.withOpacity(isListening ? 0.4 : 0.1),
                          blurRadius: isListening ? 18 : 6,
                          spreadRadius: isListening ? 3 : 0,
                        ),
                      ],
                    ),
                    child: Center(
                      child: Icon(
                        isListening ? Icons.mic : Icons.mic_none,
                        size: 38,
                        color: isListening ? Colors.white : GBColors.primary,
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
          const SizedBox(height: 10),

          // Voice Status Label
          Text(
            isListening
                ? (state.isHindi ? 'सुन रहे हैं... बोलिए' : 'Listening... Speak now')
                : (state.isHindi ? 'माइक दबाकर आवाज से ऑर्डर करें' : 'Tap Microphone to Voice Order'),
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w800,
              color: isListening ? GBColors.primary : null,
            ),
          ),

          if (_statusMessage.isNotEmpty && !isListening) ...[
            const SizedBox(height: 4),
            Text(
              _statusMessage,
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: _voiceState == AiVoiceState.error ? GBColors.error : GBColors.primary,
              ),
            ),
          ],

          if (_lastMatchedProduct != null && _lastActionType == 'ADD') ...[
            const SizedBox(height: 8),
            InkWell(
              onTap: () => widget.onTabChange(2), // Jump to cart
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: GBColors.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: GBColors.primary),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.shopping_cart_checkout, size: 16, color: GBColors.primary),
                    const SizedBox(width: 6),
                    Text(
                      loc.isHindi
                          ? 'कार्ट देखें (${state.cartCount} सामान)'
                          : 'View Cart (${state.cartCount} items)',
                      style: const TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w800,
                        color: GBColors.primary,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
