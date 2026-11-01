import 'package:flutter_test/flutter_test.dart';
import 'package:customer/main.dart';

void main() {
  testWidgets('Customer app boots to splash and renders GaonBazaar brand', (WidgetTester tester) async {
    await tester.pumpWidget(const GaonBazaarCustomerApp());
    expect(find.text('गाँव बाज़ार'), findsOneWidget);
    expect(find.text('GaonBazaar'), findsOneWidget);
    
    // Advance timer past splash duration
    await tester.pump(const Duration(seconds: 2));
    await tester.pumpAndSettle();
  });
}
