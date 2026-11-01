# GaonBazaar — Screen Registry & Navigation Map

## 1. Customer Application (`apps/customer`)
| Screen ID | Screen Name | Route Path | Core Elements / UX Behaviors |
|---|---|---|---|
| `CUST-01` | Splash Screen | `/splash` | Animated GaonBazaar emblem, brand tagline "गाँव का अपना बाज़ार", persistent auth & locale check |
| `CUST-02` | Language Selection | `/language-select` | First-launch prompt for Hindi (हिंदी) vs. English. Saves preference to device storage |
| `CUST-03` | Phone Number Entry | `/login` | 10-digit Indian phone input, privacy consent, OTP request trigger |
| `CUST-04` | OTP Verification | `/verify-otp` | 6-digit PIN input, countdown resend timer (60s), auto-submission on 6 digits |
| `CUST-05` | Main Shell / BottomNav | `/main` | 5 tabs: Home, AI Assistant, Cart, My Orders, Account |
| `CUST-06` | Home Screen | `/home` | Header (Logo, Location picker, Notification bell), Search bar + working mic, category horizontal scroll, **exactly TWO featured stores**, 2-column product grid with Add buttons |
| `CUST-07` | Store Details | `/store/:id` | Store banner, operating status, village location, catalog grouped by categories |
| `CUST-08` | Product Details | `/product/:id` | High-res product photo, localized name, weight/unit, vendor price, in-stock badge, quantity increment/decrement |
| `CUST-09` | Voice & Text AI Assistant | `/ai-assistant` | Hindi/English/Hinglish speech recognition, NLP command parser, cart mutator, smart product search |
| `CUST-10` | Cart Screen | `/cart` | Store items, bill breakdown (Subtotal, Delivery Fee, Platform Fee ₹3), applied coupon, Proceed to Checkout |
| `CUST-11` | Address Manager | `/addresses` | Saved addresses list (Home, Shop, Other), Add/Edit/Delete, Default address selection |
| `CUST-12` | Map & Location Picker | `/map-picker` | Interactive map, current GPS button, draggable pin, reverse geocoding showing Village, Landmark, Block, District |
| `CUST-13` | Checkout & Payment | `/checkout` | Delivery address confirmation, payment method (COD vs. Online UPI), order summary, 1-click Place Order |
| `CUST-14` | Live Order Tracking | `/order-track/:id` | 7-stage visual pipeline, 180s cancellation timer (if newly placed), delivery OTP badge, runner contact |
| `CUST-15` | Order History & Details | `/orders` & `/orders/:id` | Past orders, itemized receipts, reorder button, invoice download, dispute/ticket trigger |
| `CUST-16` | Account Screen | `/account` | Exactly 7 primary entries: Profile, Saved Addresses, Payment Settings, App Settings (Theme/Lang), Help & Support, Policies & Legal, Logout |

---

## 2. Vendor Application (`apps/vendor`)
| Screen ID | Screen Name | Route Path | Core Elements / UX Behaviors |
|---|---|---|---|
| `VEND-01` | Vendor Splash & Lang | `/splash` | Brand welcome & language selection |
| `VEND-02` | Vendor Auth | `/auth` | Phone number entry & OTP verification |
| `VEND-03` | Store Profile Setup | `/onboarding/store` | Shop name, owner name, category, opening/closing hours |
| `VEND-04` | Store GPS & Address | `/onboarding/location`| Map pin location, Village name, Landmark, Block, District |
| `VEND-05` | KYC & Bank Payout | `/onboarding/kyc` | Consent-based verification, UPI VPA or Bank Account details |
| `VEND-06` | Approval Status | `/onboarding/status`| Pending review, Approved, or Resubmission required screens |
| `VEND-07` | Dashboard Home | `/dashboard` | Online/Offline toggle, daily earnings, pending orders badge, quick inventory alerts |
| `VEND-08` | Order Management | `/orders` | Tabs: New Orders, In Packing, Ready for Pickup, Completed. Accept/Reject actions |
| `VEND-09` | Central Product Library | `/catalog/library` | Visual search of common village items (Atta, Oil, Milk, Sabzi) with pre-curated images |
| `VEND-10` | My Store Inventory | `/catalog/my-products`| Toggle in-stock/out-of-stock, set custom price, set unit quantity, add custom item |
| `VEND-11` | Earnings & Settlements | `/settlements` | Daily sales, weekly settlement ledger, payout history |
| `VEND-12` | Vendor Settings | `/settings` | Store timings, vacation mode, contact support, sound alerts |

---

## 3. Runner Application (`apps/runner`)
| Screen ID | Screen Name | Route Path | Core Elements / UX Behaviors |
|---|---|---|---|
| `RUNN-01` | Runner Splash & Lang | `/splash` | Language choice & runner branding |
| `RUNN-02` | Runner Auth | `/auth` | Phone number OTP login |
| `RUNN-03` | Runner Registration | `/onboarding/personal`| Full name, phone, emergency contact |
| `RUNN-04` | Vehicle & Licence | `/onboarding/vehicle` | Vehicle type (Motorcycle/Bicycle), Registration No., Driving Licence verification |
| `RUNN-05` | Payout Setup | `/onboarding/payout` | Bank Account / UPI ID for instant delivery fee payouts |
| `RUNN-06` | Verification Review | `/onboarding/status` | Real-time approval badge by Admin |
| `RUNN-07` | Runner Dashboard | `/dashboard` | Duty Status (Online/Offline), Earnings Today, Active Job banner |
| `RUNN-08` | Job Broadcast Screen | `/jobs/available` | Incoming job alert, pickup distance, drop distance, guaranteed payout, Accept/Decline timer |
| `RUNN-09` | Navigation to Store | `/delivery/pickup` | Map route to vendor shop, vendor phone dialer, "Confirm Package Picked Up" |
| `RUNN-10` | Navigation to Customer | `/delivery/drop` | Route to village destination, customer phone dialer, landmark guide |
| `RUNN-11` | Delivery OTP Verification| `/delivery/verify` | Enter customer's 4-digit OTP to finalize drop-off, cash collection confirm for COD |
| `RUNN-12` | Earnings & Trip History | `/earnings` | Daily trips completed, cash collected to remit, incentives earned |

---

## 4. Super Admin Web Dashboard (`apps/admin`)
| Screen ID | Screen Name | Route Path | Core Capabilities |
|---|---|---|---|
| `ADMN-01` | Admin Login | `/login` | High-security administrator credentials & 2FA |
| `ADMN-02` | Dashboard Overview | `/` | GMV, order volume, active runners, active stores, live order status cards |
| `ADMN-03` | Vendor KYC Approvals | `/vendors/approvals`| Review shop documents, location verification, Approve / Reject with remarks |
| `ADMN-04` | Runner Approvals | `/runners/approvals`| Review DL, vehicle details, identity verification, Approve / Reject |
| `ADMN-05` | Live Order Ops | `/orders` | Real-time map & table of all placed, packing, in-transit, delivered orders |
| `ADMN-06` | Service Zones & Fees | `/zones` | 8.0 km radius management, Minapur pilot bounds, delivery fee formulas, platform fee |
| `ADMN-07` | Master Product Library | `/catalog` | Global central product catalog with high quality images and suggested MRPs |
| `ADMN-08` | Payouts & Settlements| `/finance` | Vendor payouts (subtotals) and Runner settlements |
| `ADMN-09` | Support & Audit Logs | `/audit` | Support dispute resolution, system audit trails, access logs |
