import 'package:flutter_test/flutter_test.dart';
import 'package:runner/main.dart';

void main() {
  testWidgets('Runner app boots to splash and renders GaonBazaar Runner brand', (WidgetTester tester) async {
    await tester.pumpWidget(const GaonBazaarRunnerApp());
    expect(find.text('गाँव बाज़ार डिलीवरी साथी'), findsOneWidget);
    expect(find.text('GaonBazaar Delivery Partner'), findsOneWidget);

    await tester.pump(const Duration(seconds: 2));
    await tester.pumpAndSettle();
  });
}
