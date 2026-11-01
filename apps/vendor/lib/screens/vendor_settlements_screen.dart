import 'package:flutter/material.dart';
import 'package:design_system/design_system.dart';

class VendorSettlementsScreen extends StatelessWidget {
  const VendorSettlementsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('कमाई व बैंक सेटलमेंट (Settlements)', style: TextStyle(fontWeight: FontWeight.w800, fontSize: 16)),
      ),
      body: SafeArea(
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
                  const Text('आज की कुल बिक्री (Today\'s Sales)', style: TextStyle(color: Colors.white70, fontSize: 13)),
                  const SizedBox(height: 6),
                  const Text('₹1,480.00', style: TextStyle(color: Colors.white, fontSize: 32, fontWeight: FontWeight.w900)),
                  const SizedBox(height: 14),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: const Text(
                      'दुकानदार कमीशन दर: 0.0% (Introductory Offer)',
                      style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.w700),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // Payout Details
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: Colors.grey.shade300),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('पंजीकृत भुगतान खाता (Payout Account)', style: TextStyle(fontWeight: FontWeight.w800, fontSize: 14)),
                  const SizedBox(height: 10),
                  const Row(
                    children: [
                      Icon(Icons.account_balance, color: GBColors.primary),
                      SizedBox(width: 10),
                      Text('UPI VPA: rajusharma@upi (Active)', style: TextStyle(fontWeight: FontWeight.w700, fontSize: 13)),
                    ],
                  ),
                  const SizedBox(height: 6),
                  const Text('दैनिक बिक्री की राशि रात 11:59 बजे स्वतः बैंक खाते में भेज दी जाती है।', style: TextStyle(fontSize: 12, color: Colors.grey)),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // Settlement History
            const Text('हालिया भुगतान इतिहास (Settlement History)', style: TextStyle(fontWeight: FontWeight.w800, fontSize: 15)),
            const SizedBox(height: 10),
            _buildHistoryItem('01 Nov 2026', '₹1,480.00', 'PENDING (आज रात प्रोसेस होगा)', Colors.amber.shade800),
            _buildHistoryItem('31 Oct 2026', '₹2,340.00', 'PAID (सफल)', GBColors.success),
            _buildHistoryItem('30 Oct 2026', '₹1,890.00', 'PAID (सफल)', GBColors.success),
          ],
        ),
      ),
    );
  }

  Widget _buildHistoryItem(String date, String amount, String status, Color statusColor) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
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
              Text(status, style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: statusColor)),
            ],
          ),
          Text(amount, style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 16)),
        ],
      ),
    );
  }
}
