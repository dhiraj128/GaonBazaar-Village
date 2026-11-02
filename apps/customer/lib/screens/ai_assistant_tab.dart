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

class _AiAssistantTabState extends State<AiAssistantTab> {
  final TextEditingController _textController = TextEditingController();
  final List<Map<String, dynamic>> _messages = [];
  bool _isListening = false;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final loc = GBLocalizations.of(context);
      _messages.add({
        'isUser': false,
        'text': loc.tr('ai_welcome_msg'),
      });
      if (mounted) setState(() {});
    });
  }

  List<String> _getSuggestions(bool isHindi) {
    if (isHindi) {
      return [
        '2 किलो आटा जोड़ो',
        '1 लीटर गाय का दूध जोड़ो',
        'मेरा कार्ट दिखाओ',
        '1 लीटर सरसों तेल जोड़ो',
        'ताज़ा टमाटर जोड़ो',
        'दूध हटा दो',
      ];
    }
    return [
      'Add 2 kg atta',
      'Add 1 litre milk',
      'Show my cart',
      'Add 1L mustard oil',
      'Add fresh tomato',
      'Remove milk',
    ];
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
      language: state.isHindi ? 'hi' : 'en',
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

      // Execute Cart Actions
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
              : 'Sorry, I did not catch that. Please try again or tap one of the suggested items below.',
        });
      });
    }
  }

  void _openVoiceInputDialog() {
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final state = AppStateProvider.of(context);
    final voice = VoiceService.instance;

    setState(() => _isListening = true);

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) {
        String liveTranscript = '';
        return StatefulBuilder(
          builder: (context, setSheetState) {
            voice.startListening(
              localeId: state.isHindi ? 'hi_IN' : 'en_IN',
              onResult: (text, isFinal) {
                if (ctx.mounted) {
                  setSheetState(() => liveTranscript = text);
                  if (isFinal && text.trim().isNotEmpty) {
                    voice.stopListening();
                    Navigator.of(ctx).pop();
                    _handleUserMessage(text.trim());
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
                    loc.tr('ai_listening'),
                    style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    loc.isHindi
                        ? 'हिंदी या English में बोलें: "2 किलो आटा", "1 लीटर दूध", "कार्ट दिखाओ"'
                        : 'Speak in English or Hindi: "Add 2 kg atta", "1 litre milk", "Show cart"',
                    textAlign: TextAlign.center,
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
                  // Spoken action suggestions
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    alignment: WrapAlignment.center,
                    children: _getSuggestions(state.isHindi).map((phrase) {
                      return ActionChip(
                        avatar: const Icon(Icons.mic_none, size: 16, color: GBColors.primary),
                        label: Text(phrase, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
                        backgroundColor: GBColors.primary.withAlpha(15),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(20),
                          side: BorderSide(color: GBColors.primary.withAlpha(50)),
                        ),
                        onPressed: () {
                          voice.stopListening();
                          Navigator.of(ctx).pop();
                          _handleUserMessage(phrase);
                        },
                      );
                    }).toList(),
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
      if (mounted) setState(() => _isListening = false);
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = AppStateProvider.of(context);
    final loc = GBLocalizations.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final suggestions = _getSuggestions(state.isHindi);

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
                  loc.tr('ai_assistant_title'),
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800),
                ),
                Text(
                  loc.tr('ai_subtitle'),
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
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                itemCount: _messages.length,
                itemBuilder: (context, index) {
                  final msg = _messages[index];
                  final isUser = msg['isUser'] as bool;

                  return Align(
                    alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                    child: Container(
                      margin: const EdgeInsets.only(bottom: 12),
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
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
                            color: Colors.black.withAlpha(isDark ? 40 : 10),
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
                itemCount: suggestions.length,
                itemBuilder: (context, index) {
                  final s = suggestions[index];
                  return Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 4),
                    child: ActionChip(
                      label: Text(s, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
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

            // Bottom Input Bar with Working Microphone
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
                              ? 'यहाँ लिखें या माइक दबाकर बोलें...'
                              : 'Type message or tap mic to speak...',
                          hintStyle: TextStyle(
                            fontSize: 13,
                            color: isDark ? GBColors.textMutedDark : GBColors.textMutedLight,
                          ),
                          border: InputBorder.none,
                          contentPadding: const EdgeInsets.symmetric(vertical: 10),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  // Dedicated AI Microphone
                  GBVoiceMicButton(
                    isListening: _isListening,
                    onTap: _openVoiceInputDialog,
                  ),
                  const SizedBox(width: 6),
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
