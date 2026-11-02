import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';
import '../state/vendor_state.dart';

class VendorSettlementsScreen extends StatefulWidget {
  const VendorSettlementsScreen({super.key});

  @override
  State<VendorSettlementsScreen> createState() => _VendorSettlementsScreenState();
}

class _VendorSettlementsScreenState extends State<VendorSettlementsScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      VendorStateProvider.of(context).fetchFinances();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = VendorStateProvider.of(context);
    final isHi = state.isHindi;
    final finances = state.finances;

    final totalSales = (finances?['total_sales'] as num?)?.toDouble() ?? 0.0;
    final commissionRate = (finances?['commission_rate'] as num?)?.toDouble() ?? 0.0;
    final netPayoutDue = (finances?['net_payout_due'] as num?)?.toDouble() ?? totalSales;
    final upiId = (finances?['upi_id'] as String?) ?? state.myStore?.upiId ?? 'Not Configured';
    final completedOrdersCount = (finances?['total_delivered_orders'] as int?) ?? 0;
    final recentSettlements = (finances?['recent_settlements'] as List<dynamic>?) ?? [];

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          tooltip: isHi ? 'पीछे जाएं' : 'Back',
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: Text(
          isHi ? 'कमाई व बैंक सेटलमेंट' : 'Earnings & Settlements',
          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
        ),
      ),
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: () => state.fetchFinances(),
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              // Top Earnings Card
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [GBColors.primary, GBColors.primaryDark],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [
                    BoxShadow(color: GBColors.primary.withOpacity(0.3), blurRadius: 10, offset: const Offset(0, 4)),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      isHi ? 'आज की कुल बिक्री' : "Today's Gross Sales",
                      style: const TextStyle(color: Colors.white70, fontSize: 13),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      '₹${totalSales.toStringAsFixed(2)}',
                      style: const TextStyle(color: Colors.white, fontSize: 32, fontWeight: FontWeight.w900),
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: Colors.white.withOpacity(0.2),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            isHi
                                ? 'दुकानदार कमीशन: ${commissionRate.toStringAsFixed(1)}%'
                                : 'Store Commission: ${commissionRate.toStringAsFixed(1)}%',
                            style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.w700),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: GBColors.secondary.withOpacity(0.85),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            isHi ? 'डिलीवर: $completedOrdersCount ऑर्डर' : 'Delivered: $completedOrdersCount orders',
                            style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.w700),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),

              // Net Payout Due Card
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Theme.of(context).cardColor,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: Colors.grey.shade300),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          isHi ? 'देय भुगतान राशि' : 'Net Payout Due',
                          style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
                        ),
                        Text(
                          '₹${netPayoutDue.toStringAsFixed(2)}',
                          style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 18, color: GBColors.success),
                        ),
                      ],
                    ),
                    const Divider(height: 20),
                    Row(
                      children: [
                        const Icon(Icons.account_balance, color: GBColors.primary, size: 20),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Text(
                            'UPI VPA: $upiId',
                            style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                          decoration: BoxDecoration(
                            color: GBColors.success.withOpacity(0.12),
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            isHi ? 'सक्रिय' : 'Active',
                            style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: GBColors.success),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      isHi
                          ? 'दैनिक बिक्री की राशि रात 11:59 बजे सीधे आपके बैंक खाते में भेजी जाती है।'
                          : 'Daily sales amount is automatically remitted to your bank account at 11:59 PM.',
                      style: const TextStyle(fontSize: 12, color: Colors.grey),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),

              // Settlement History
              Text(
                isHi ? 'हालिया भुगतान इतिहास' : 'Settlement History',
                style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15),
              ),
              const SizedBox(height: 10),
              if (recentSettlements.isEmpty)
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: Theme.of(context).cardColor,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: Colors.grey.shade200),
                  ),
                  child: Center(
                    child: Text(
                      isHi
                          ? 'अभी कोई पूर्ण ऑर्डर या सेटलमेंट नहीं है। ऑर्डर डिलीवर होने पर राशि स्वतः सेटल होगी।'
                          : 'No completed orders or settlements yet. Completed orders will appear here automatically.',
                      textAlign: TextAlign.center,
                      style: const TextStyle(fontSize: 12, color: Colors.grey),
                    ),
                  ),
                )
              else
                ...recentSettlements.map((item) {
                  final s = item as Map<String, dynamic>;
                  final isSettled = s['status'].toString().contains('Settled') || s['status'].toString().contains('Paid');
                  return _buildHistoryItem(
                    date: s['date'] as String? ?? 'Today',
                    amount: s['amount'] as String? ?? '₹0.00',
                    status: s['status'] as String? ?? 'Pending',
                    statusColor: isSettled ? GBColors.success : Colors.amber.shade800,
                  );
                }),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHistoryItem({
    required String date,
    required String amount,
    required String status,
    required Color statusColor,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(date, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13)),
              const SizedBox(height: 3),
              Text(status, style: TextStyle(color: statusColor, fontSize: 11, fontWeight: FontWeight.w700)),
            ],
          ),
          Text(amount, style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15)),
        ],
      ),
    );
  }
}
