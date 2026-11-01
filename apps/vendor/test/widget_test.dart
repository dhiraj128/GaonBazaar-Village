import 'package:flutter_test/flutter_test.dart';
import 'package:vendor/main.dart';

void main() {
  testWidgets('Vendor app boots to splash and displays GaonBazaar Vendor brand', (WidgetTester tester) async {
    await tester.pumpWidget(const GaonBazaarVendorApp());
    expect(find.text('गाँव बाज़ार विक्रेता'), findsOneWidget);
    expect(find.text('GaonBazaar Shopkeeper Partner'), findsOneWidget);

    await tester.pump(const Duration(seconds: 2));
    await tester.pumpAndSettle();
  });
}
