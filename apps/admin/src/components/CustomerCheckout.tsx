import React, { useState, useEffect } from 'react';
import { ShieldCheck, ArrowRight, Zap, CheckCircle2, QrCode, Copy } from 'lucide-react';

interface CustomerCheckoutProps {
  orderId: string;
  amount: number;
  customerName: string;
  customerPhone: string;
  onPaymentSuccess: (paymentId: string) => void;
  onPaymentFailure: (error: string) => void;
  onCancel?: () => void;
}

export const CustomerCheckout: React.FC<CustomerCheckoutProps> = ({
  orderId,
  amount,
  onPaymentSuccess,
  onPaymentFailure,
  onCancel
}) => {
  const [selectedUpiApp, setSelectedUpiApp] = useState<'gpay' | 'phonepe' | 'paytm' | 'bhim' | 'generic'>('gpay');
  const [isProcessing, setIsProcessing] = useState(false);
  const [utrNumber, setUtrNumber] = useState('');
  const [isVerifyingUtr, setIsVerifyingUtr] = useState(false);
  const [isQrOpen, setIsQrOpen] = useState(false);
  const [paymentPending, setPaymentPending] = useState(false);

  const payeeVpa = 'gaonbazaar@icici';
  const payeeName = 'Apna GaonBazaar';
  const transactionNote = `Order_${orderId.slice(-6)}`;
  const formattedAmount = amount.toFixed(2);

  const standardUpiUrl = `upi://pay?pa=${payeeVpa}&pn=${encodeURIComponent(payeeName)}&tr=${orderId}&am=${formattedAmount}&cu=INR&tn=${encodeURIComponent(transactionNote)}`;

  const upiApps = [
    {
      id: 'gpay',
      name: 'Google Pay',
      tagline: 'Instant Zero MDR',
      icon: 'GPay',
      color: 'border-blue-500 bg-blue-50/50 text-blue-700',
      badgeColor: 'bg-blue-100 text-blue-800',
      scheme: `tez://upi/pay?pa=${payeeVpa}&pn=${encodeURIComponent(payeeName)}&tr=${orderId}&am=${formattedAmount}&cu=INR&tn=${encodeURIComponent(transactionNote)}`
    },
    {
      id: 'phonepe',
      name: 'PhonePe',
      tagline: 'Fastest 1-Click Pay',
      icon: 'PhonePe',
      color: 'border-purple-500 bg-purple-50/50 text-purple-700',
      badgeColor: 'bg-purple-100 text-purple-800',
      scheme: `phonepe://pay?pa=${payeeVpa}&pn=${encodeURIComponent(payeeName)}&tr=${orderId}&am=${formattedAmount}&cu=INR&tn=${encodeURIComponent(transactionNote)}`
    },
    {
      id: 'paytm',
      name: 'Paytm UPI',
      tagline: 'Bank Account or Wallet',
      icon: 'Paytm',
      color: 'border-sky-500 bg-sky-50/50 text-sky-700',
      badgeColor: 'bg-sky-100 text-sky-800',
      scheme: `paytmmp://pay?pa=${payeeVpa}&pn=${encodeURIComponent(payeeName)}&tr=${orderId}&am=${formattedAmount}&cu=INR&tn=${encodeURIComponent(transactionNote)}`
    },
    {
      id: 'bhim',
      name: 'BHIM UPI',
      tagline: 'Official NPCI Gateway',
      icon: 'BHIM',
      color: 'border-emerald-500 bg-emerald-50/50 text-emerald-700',
      badgeColor: 'bg-emerald-100 text-emerald-800',
      scheme: standardUpiUrl
    }
  ];

  // Auto-polling for status updates
  useEffect(() => {
    let pollInterval: any;
    if (paymentPending) {
      pollInterval = setInterval(async () => {
        try {
          const res = await fetch(`/api/v1/payments/upi-status/${orderId}`);
          if (res.ok) {
            const data = await res.json();
            if (data.payment_status === 'PAID') {
              clearInterval(pollInterval);
              onPaymentSuccess(data.transaction_id || 'UPI_CONFIRMED');
            }
          }
        } catch {
          // Retry next poll
        }
      }, 3000);
    }
    return () => clearInterval(pollInterval);
  }, [paymentPending, orderId, onPaymentSuccess]);

  const triggerUpiIntent = async () => {
    setIsProcessing(true);
    setPaymentPending(true);

    try {
      // 1. Notify backend of UPI intent initiation
      try {
        await fetch('/api/v1/payments/verify-upi', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            order_id: orderId,
            upi_app: selectedUpiApp,
            amount: amount
          })
        });
      } catch {
        // Continue to app launch
      }

      // 2. Launch selected UPI App Intent
      const appObj = upiApps.find(a => a.id === selectedUpiApp);
      const appScheme = appObj?.scheme || standardUpiUrl;

      const isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
      if (isMobile) {
        window.location.href = appScheme;
      } else {
        // Desktop / Laptop: Show Dynamic QR Code
        setIsQrOpen(true);
      }
    } catch (err: any) {
      onPaymentFailure(err.message || 'UPI Payment initiation failed');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleVerifyUtr = async () => {
    if (!utrNumber || utrNumber.trim().length < 8) {
      alert('Please enter a valid 12-digit UTR or Bank Reference Number');
      return;
    }
    setIsVerifyingUtr(true);
    try {
      const res = await fetch('/api/v1/payments/verify-upi', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          order_id: orderId,
          utr_number: utrNumber.trim().toUpperCase(),
          amount: amount,
          upi_app: selectedUpiApp
        })
      });
      const data = await res.json();
      if (res.ok && data.status === 'SUCCESS') {
        onPaymentSuccess(data.utr_number || utrNumber);
      } else {
        alert(data.message || 'Payment verification pending bank confirmation');
      }
    } catch {
      alert('Verification request failed. Please check your network and retry.');
    } finally {
      setIsVerifyingUtr(false);
    }
  };

  const copyVpa = () => {
    navigator.clipboard.writeText(payeeVpa);
    alert('UPI ID copied to clipboard: ' + payeeVpa);
  };

  const qrImageUrl = `https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=${encodeURIComponent(standardUpiUrl)}`;

  return (
    <div className="bg-white rounded-3xl p-5 shadow-xl border border-slate-100 max-w-md w-full mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-100">
        <div>
          <span className="text-[11px] font-bold tracking-wider text-emerald-700 uppercase bg-emerald-50 px-2 py-0.5 rounded-full">
            Direct UPI 0% Fee
          </span>
          <h2 className="text-base font-extrabold text-slate-900 mt-1">
            Pay via UPI
          </h2>
          <p className="text-xs text-slate-500">
            Direct bank transfer without third-party surcharge
          </p>
        </div>
        <div className="text-right">
          <p className="text-[11px] text-slate-400 font-medium">To Pay</p>
          <p className="text-xl font-black text-slate-900 font-mono">₹{formattedAmount}</p>
        </div>
      </div>

      {/* UPI App Selection Cards */}
      <div className="space-y-2.5 my-4">
        {upiApps.map((app) => {
          const isSelected = selectedUpiApp === app.id;
          return (
            <div
              key={app.id}
              onClick={() => setSelectedUpiApp(app.id as any)}
              className={`p-3.5 rounded-2xl border-2 transition-all cursor-pointer flex items-center justify-between ${
                isSelected
                  ? `${app.color} shadow-sm scale-[1.01]`
                  : 'border-slate-200 bg-white hover:border-slate-300'
              }`}
            >
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-xl bg-white border border-slate-200 flex items-center justify-center font-black text-xs shadow-2xs">
                  {app.icon}
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-bold text-slate-900">{app.name}</span>
                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${app.badgeColor}`}>
                      {app.tagline}
                    </span>
                  </div>
                  <p className="text-[10px] text-slate-500">Pre-filled ₹{formattedAmount} Intent</p>
                </div>
              </div>
              {isSelected ? (
                <CheckCircle2 className="w-5 h-5 text-emerald-600" />
              ) : (
                <div className="w-4 h-4 rounded-full border-2 border-slate-300" />
              )}
            </div>
          );
        })}
      </div>

      {/* Dynamic QR Toggle & Container */}
      <div className="mb-4">
        <button
          type="button"
          onClick={() => setIsQrOpen(!isQrOpen)}
          className="w-full py-2 px-3 bg-slate-50 hover:bg-slate-100 rounded-xl border border-slate-200 text-xs font-bold text-slate-700 flex items-center justify-center space-x-2 transition"
        >
          <QrCode className="w-4 h-4 text-emerald-600" />
          <span>{isQrOpen ? 'Hide UPI QR Code' : 'Show Dynamic UPI QR Code (Scan to Pay)'}</span>
        </button>

        {isQrOpen && (
          <div className="mt-3 p-4 bg-slate-50 border border-slate-200 rounded-2xl flex flex-col items-center space-y-2.5">
            <div className="w-44 h-44 bg-white p-2 rounded-xl border border-slate-200 shadow-sm flex items-center justify-center">
              <img src={qrImageUrl} alt="UPI QR" className="w-full h-full object-contain" />
            </div>
            <div className="flex items-center space-x-2 text-xs">
              <span className="text-slate-500">UPI ID:</span>
              <strong className="font-mono text-slate-900">{payeeVpa}</strong>
              <button
                type="button"
                onClick={copyVpa}
                className="p-1 hover:bg-slate-200 rounded text-slate-600"
                title="Copy UPI ID"
              >
                <Copy className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Manual 12-Digit UTR Input (When payment is pending or after returning from app) */}
      {paymentPending && (
        <div className="mb-4 p-3.5 bg-amber-50/70 border border-amber-200 rounded-2xl space-y-2">
          <div className="flex items-center justify-between text-xs font-bold text-amber-900">
            <span>Payment In Progress</span>
            <span className="text-[10px] font-mono text-amber-700">Awaiting UTR</span>
          </div>
          <p className="text-[11px] text-amber-800">
            Approved payment in your UPI app? Enter the 12-digit UTR reference number from receipt:
          </p>
          <div className="flex space-x-2">
            <input
              type="text"
              value={utrNumber}
              onChange={(e) => setUtrNumber(e.target.value)}
              placeholder="e.g. 431829103842"
              maxLength={20}
              className="flex-1 px-3 py-2 bg-white border border-amber-300 rounded-xl text-xs font-mono font-bold uppercase tracking-wider text-slate-900 focus:outline-none focus:border-emerald-600"
            />
            <button
              type="button"
              onClick={handleVerifyUtr}
              disabled={isVerifyingUtr}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-xs transition disabled:opacity-50"
            >
              {isVerifyingUtr ? 'Verifying...' : 'Verify'}
            </button>
          </div>
        </div>
      )}

      {/* Security Guarantee Notice */}
      <div className="flex items-center space-x-2 bg-emerald-50/70 p-2.5 rounded-xl border border-emerald-100 text-[11px] text-emerald-800 mb-4">
        <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
        <span>Direct NPCI Regulated Bank-to-Bank Transfer (0% MDR).</span>
      </div>

      {/* Action Buttons */}
      <div className="space-y-2">
        <button
          onClick={triggerUpiIntent}
          disabled={isProcessing}
          className="w-full py-3.5 bg-emerald-600 hover:bg-emerald-700 active:scale-[0.99] text-white rounded-2xl font-bold text-sm shadow-lg shadow-emerald-600/25 flex items-center justify-center space-x-2 transition disabled:opacity-50"
        >
          {isProcessing ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              <span>Connecting to UPI App...</span>
            </>
          ) : (
            <>
              <Zap className="w-4 h-4 fill-white" />
              <span>Pay ₹{formattedAmount} via Direct UPI</span>
              <ArrowRight className="w-4 h-4 ml-1" />
            </>
          )}
        </button>

        {onCancel && (
          <button
            onClick={onCancel}
            disabled={isProcessing}
            className="w-full py-2.5 text-xs font-semibold text-slate-500 hover:text-slate-700 transition"
          >
            Cancel & Return to Cart
          </button>
        )}
      </div>
    </div>
  );
};
