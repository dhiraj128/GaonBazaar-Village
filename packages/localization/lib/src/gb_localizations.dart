import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'strings_en.dart';
import 'strings_hi.dart';

class GBLocalizations {
  final Locale locale;

  GBLocalizations(this.locale);

  static GBLocalizations of(BuildContext context) {
    return Localizations.of<GBLocalizations>(context, GBLocalizations) ??
        GBLocalizations(const Locale('hi'));
  }

  static const LocalizationsDelegate<GBLocalizations> delegate =
      _GBLocalizationsDelegate();

  bool get isHindi => locale.languageCode == 'hi';

  String tr(String key) {
    if (isHindi) {
      return stringsHi[key] ?? stringsEn[key] ?? key;
    }
    return stringsEn[key] ?? stringsHi[key] ?? key;
  }
}

class _GBLocalizationsDelegate extends LocalizationsDelegate<GBLocalizations> {
  const _GBLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) => ['hi', 'en'].contains(locale.languageCode);

  @override
  Future<GBLocalizations> load(Locale locale) {
    return SynchronousFuture<GBLocalizations>(GBLocalizations(locale));
  }

  @override
  bool shouldReload(_GBLocalizationsDelegate old) => false;
}
