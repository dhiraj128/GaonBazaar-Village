import 'package:flutter/foundation.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;

class VoiceService {
  static final VoiceService instance = VoiceService._internal();
  VoiceService._internal();

  final stt.SpeechToText _speech = stt.SpeechToText();
  bool _isInitialized = false;

  bool get isAvailable => _isInitialized;
  bool get isListening => _speech.isListening;

  Future<bool> initialize() async {
    if (_isInitialized) return true;
    try {
      _isInitialized = await _speech.initialize(
        onStatus: (status) => debugPrint('Speech status: $status'),
        onError: (errorNotification) => debugPrint('Speech error: $errorNotification'),
      );
      return _isInitialized;
    } catch (e) {
      debugPrint('Speech initialize exception: $e');
      _isInitialized = false;
      return false;
    }
  }

  Future<void> startListening({
    required Function(String recognizedText, bool isFinal) onResult,
    String? localeId,
  }) async {
    final available = await initialize();
    if (!available) return;

    await _speech.listen(
      onResult: (result) {
        onResult(result.recognizedWords, result.finalResult);
      },
      localeId: localeId ?? 'hi_IN',
      listenFor: const Duration(seconds: 15),
      pauseFor: const Duration(seconds: 3),
      cancelOnError: true,
      listenMode: stt.ListenMode.confirmation,
    );
  }

  Future<void> stopListening() async {
    if (_speech.isListening) {
      await _speech.stop();
    }
  }
}
