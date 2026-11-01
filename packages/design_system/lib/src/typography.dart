import 'package:flutter/material.dart';
import 'colors.dart';

class GBTypography {
  // Mobile-first clear typography for village users and sunlight readability
  static TextStyle displayLarge(BuildContext context) => TextStyle(
    fontSize: 26,
    fontWeight: FontWeight.w800,
    letterSpacing: -0.5,
    color: Theme.of(context).brightness == Brightness.dark
        ? GBColors.textPrimaryDark
        : GBColors.textPrimaryLight,
  );

  static TextStyle titleLarge(BuildContext context) => TextStyle(
    fontSize: 20,
    fontWeight: FontWeight.w700,
    color: Theme.of(context).brightness == Brightness.dark
        ? GBColors.textPrimaryDark
        : GBColors.textPrimaryLight,
  );

  static TextStyle titleMedium(BuildContext context) => TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.w600,
    color: Theme.of(context).brightness == Brightness.dark
        ? GBColors.textPrimaryDark
        : GBColors.textPrimaryLight,
  );

  static TextStyle bodyMedium(BuildContext context) => TextStyle(
    fontSize: 14,
    fontWeight: FontWeight.w400,
    height: 1.4,
    color: Theme.of(context).brightness == Brightness.dark
        ? GBColors.textSecondaryDark
        : GBColors.textSecondaryLight,
  );

  static TextStyle bodySmall(BuildContext context) => TextStyle(
    fontSize: 12,
    fontWeight: FontWeight.w400,
    color: Theme.of(context).brightness == Brightness.dark
        ? GBColors.textMutedDark
        : GBColors.textMutedLight,
  );

  static TextStyle priceTag(BuildContext context) => const TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.w800,
    color: GBColors.primary,
  );

  static TextStyle strikethroughMRP(BuildContext context) => TextStyle(
    fontSize: 12,
    fontWeight: FontWeight.w400,
    decoration: TextDecoration.lineThrough,
    color: Theme.of(context).brightness == Brightness.dark
        ? GBColors.textMutedDark
        : GBColors.textMutedLight,
  );
}
