import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import 'package:localization/localization.dart';
import 'package:shared_models/shared_models.dart';
import '../state/app_state.dart';

class AiAssistantTab extends StatefulWidget {
  final Function(int) onTabChange;

  const AiAssistantTab({super.key, required this.onTabChange});

  @override
  State<AiAssistantTab> createState() => _AiAssistantTabState();
}

class _AiAssistantTabState extends State<AiAssistantTab> {
  final TextEditingController _textController = TextEditingController();
  final List<Map<String, dynamic>> _messages = [];
  bool _isListening = false;
  bool _isLoading = false;

  final List<String> _quickSuggestions = [
    '२ किलो आटा जोड़ो (Add 2 kg Atta)',
    '१ लीटर दूध चाहिए (1L Milk)',
    'कार्ट दिखाओ (Show Cart)',
    '१ किलो सरसों तेल (Mustard Oil)',
    'देशी टमाटर जोड़ो (Add Tomato)',
  ];

  @override
  void initState() {
    super.initState();
    _messages.add({
      'isUser': false,
      'text':
          'नमस्ते! मैं गाँव बाज़ार का एआई सहायक हूँ।\nआप हिंदी, English या Hinglish में बोलकर या लिखकर सामान मंगा सकते हैं।\n\nउदाहरण: "दो किलो आटा जोड़ो", "1 litre milk", "Cart dikhao"',
    });
  }

  Future<void> _handleUserMessage(String query) async {
    final text = query.trim();
    if (text.isEmpty) return;

    setState(() {
      _messages.add({'isUser': true, 'text': text});
      _isLoading = true;
    });
    _textController.clear();

    final state = AppStateProvider.of(context);
    final response = await state.apiClient.queryAI(
      query: text,
      storeId: state.currentCartStoreId,
    );

    setState(() => _isLoading = false);

    if (response.isSuccess && response.data != null) {
      final data = response.data!;
      final intent = data['intent'] as String;
      final reply = state.isHindi
          ? (data['reply_hi'] as String? ?? 'कार्य पूरा हुआ।')
          : (data['reply_en'] as String? ?? 'Action completed.');

      setState(() {
        _messages.add({'isUser': false, 'text': reply});
      });

      // Execute Cart Mutator
      if (intent == 'ADD_TO_CART' && data['matched_product'] != null) {
        final prodJson = data['matched_product'] as Map<String, dynamic>;
        final qty = (data['quantity'] as num?)?.toInt() ?? 1;

        final prod = GBProduct(
          id: prodJson['id'] as String,
          storeId: state.currentCartStoreId ?? 'str_01',
          nameEn: prodJson['name_en'] as String,
          nameHi: prodJson['name_hi'] as String,
          category: 'Grocery',
          unit: prodJson['unit'] as String,
          price: (prodJson['price'] as num).toDouble(),
          imageUrl: prodJson['image_url'] as String,
        );

        for (int i = 0; i < qty; i++) {
          state.addToCart(prod, state.currentCartStoreName ?? 'माँ शारदा किराना स्टोर');
        }
      } else if (intent == 'SHOW_CART') {
        // Switch to Cart Tab (Index 2)
        widget.onTabChange(2);
      } else if (intent == 'REMOVE_FROM_CART' && data['matched_product'] != null) {
        final prodJson = data['matched_product'] as Map<String, dynamic>;
        state.decrementItem(prodJson['id'] as String);
      }
    } else {
      setState(() {
        _messages.add({
          'isUser': false,
          'text': state.isHindi
              ? 'क्षमा करें, मैं समझ नहीं पाया। कृपया दोबारा बोलें या नीचे दिए गए विकल्पों में से चुनें।'
              : 'Sorry, I did not catch that. Please try again or tap a suggestion below.',
        });
      });
    }
  }

  void _simulateVoiceInput() {
    // Toggles microphone listening mode
    setState(() => _isListening = !_isListening);
    if (_isListening) {
      Future.delayed(const Duration(milliseconds: 1400), () {
        if (!mounted || !_isListening) return;
        setState(() => _isListening = false);
        _handleUserMessage('दो किलो आटा जोड़ो');
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = AppStateProvider.of(context);
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
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
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  loc.isHindi ? 'गाँव बाज़ार एआई सहायक' : 'GaonBazaar AI',
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800),
                ),
                Text(
                  loc.isHindi ? 'हिंदी, English व Hinglish सपोर्ट' : 'Multilingual Voice & Text',
                  style: TextStyle(
                    fontSize: 11,
                    color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Chat message list
            Expanded(
              child: ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: _messages.length,
                itemBuilder: (context, index) {
                  final msg = _messages[index];
                  final isUser = msg['isUser'] as bool;

                  return Align(
                    alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                    child: Container(
                      margin: const EdgeInsets.only(bottom: 12),
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                      constraints: BoxConstraints(
                        maxWidth: MediaQuery.of(context).size.width * 0.78,
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
                            color: Colors.black.withOpacity(0.04),
                            blurRadius: 4,
                            offset: const Offset(0, 1),
                          ),
                        ],
                      ),
                      child: Text(
                        msg['text'] as String,
                        style: TextStyle(
                          color: isUser
                              ? Colors.white
                              : (isDark ? GBColors.textPrimaryDark : GBColors.textPrimaryLight),
                          fontSize: 14,
                          height: 1.4,
                        ),
                      ),
                    ),
                  );
                },
              ),
            ),

            if (_isLoading)
              const Padding(
                padding: EdgeInsets.symmetric(vertical: 8),
                child: SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2, color: GBColors.primary),
                ),
              ),

            // Quick suggestion chips
            SizedBox(
              height: 38,
              child: ListView.builder(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.symmetric(horizontal: 12),
                itemCount: _quickSuggestions.length,
                itemBuilder: (context, index) {
                  final s = _quickSuggestions[index];
                  return Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 4),
                    child: ActionChip(
                      label: Text(s, style: const TextStyle(fontSize: 12)),
                      backgroundColor: isDark ? GBColors.surfaceDark : Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(18),
                        side: BorderSide(
                          color: isDark ? GBColors.borderDark : GBColors.borderLight,
                        ),
                      ),
                      onPressed: () => _handleUserMessage(s),
                    ),
                  );
                },
              ),
            ),
            const SizedBox(height: 8),

            // Bottom Input Bar with Microphone
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
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
                  GBVoiceMicButton(
                    isListening: _isListening,
                    onTap: _simulateVoiceInput,
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: TextField(
                      controller: _textController,
                      onSubmitted: _handleUserMessage,
                      decoration: InputDecoration(
                        hintText: _isListening
                            ? (loc.isHindi ? 'सुन रहे हैं... बोलिए' : 'Listening... speak now')
                            : (loc.isHindi ? 'लिखें या माइक से बोलें...' : 'Type or speak your order...'),
                        border: InputBorder.none,
                        enabledBorder: InputBorder.none,
                        focusedBorder: InputBorder.none,
                        contentPadding: const EdgeInsets.symmetric(horizontal: 8, vertical: 10),
                      ),
                    ),
                  ),
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
    );
  }
}
