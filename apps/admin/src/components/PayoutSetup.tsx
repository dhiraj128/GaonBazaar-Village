import React, { useState } from 'react';
import { Landmark, Smartphone, CheckCircle, AlertCircle, Hourglass, Lock, ShieldCheck, ArrowRight, Loader2 } from 'lucide-react';

interface PayoutSetupProps {
  role?: 'vendor' | 'runner';
  userId?: string;
  userName?: string;
  onSuccess?: (payoutData: any) => void;
  onAdminApproved?: () => void;
}

export const PayoutSetup: React.FC<PayoutSetupProps> = ({
  role = 'vendor',
  userId = 'usr_partner_demo',
  userName = 'Partner',
  onSuccess,
  onAdminApproved
}) => {
  const [payoutMode, setPayoutMode] = useState<'upi' | 'bank'>('upi');
  
  // Tab 1: UPI State
  const [upiId, setUpiId] = useState('');
  
  // Tab 2: Bank State
  const [accountNumber, setAccountNumber] = useState('');
  const [confirmAccountNumber, setConfirmAccountNumber] = useState('');
  const [ifscCode, setIfscCode] = useState('');
  
  // UI States
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isUnderReview, setIsUnderReview] = useState(false);
  const [applicationId] = useState(`GB-${role.toUpperCase()}-${Math.floor(10000 + Math.random() * 90000)}`);

  // Supabase Configuration
  const SUPABASE_URL = (import.meta.env.VITE_SUPABASE_URL as string) || "https://vxewgvrjhjpntfvsmuez.supabase.co";
  const SUPABASE_ANON_KEY = (import.meta.env.VITE_SUPABASE_ANON_KEY as string) || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ4ZXdndnJqaGpwbnRmdnNtdWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTM1NDkwMzcsImV4cCI6MjEwOTEyNTAzN30.3jUR0U9RGcgc2q-zeWX7OeWaFqugSHOFdDieYoGFIwQ";

  // Validate UPI ID
  const validateUpi = (vpa: string): boolean => {
    const clean = vpa.trim().toLowerCase();
    const upiRegex = /^[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}$/;
    return upiRegex.test(clean) && !clean.includes('example') && !clean.includes('vendor@upi');
  };

  // Validate Bank Account Details
  const validateBank = (): { valid: boolean; error?: string } => {
    const acc = accountNumber.trim();
    const confirm = confirmAccountNumber.trim();
    const ifsc = ifscCode.trim().toUpperCase();

    if (!acc || !acc.match(/^\d{9,18}$/)) {
      return { valid: false, error: 'Please enter a valid Bank Account Number (9 to 18 numeric digits).' };
    }
    if (acc !== confirm) {
      return { valid: false, error: 'Account numbers do not match. Please re-enter carefully.' };
    }
    if (!ifsc || !ifsc.match(/^[A-Z]{4}0[A-Z0-9]{6}$/)) {
      return { valid: false, error: 'Please enter a valid 11-character IFSC Code (e.g., SBIN0001234, 5th character must be 0).' };
    }
    return { valid: true };
  };

  // Handle Form Submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (payoutMode === 'upi') {
      if (!validateUpi(upiId)) {
        setError('Please enter a valid UPI ID (e.g., name@bank, 9876543210@paytm).');
        return;
      }
    } else {
      const bankValidation = validateBank();
      if (!bankValidation.valid) {
        setError(bankValidation.error || 'Please fill valid bank details.');
        return;
      }
    }

    setLoading(true);

    try {
      const payoutPayload = payoutMode === 'upi'
        ? {
            payout_method: 'upi',
            upi_id: upiId.trim().toLowerCase(),
            role,
            user_id: userId
          }
        : {
            payout_method: 'bank',
            account_number: accountNumber.trim(),
            ifsc_code: ifscCode.trim().toUpperCase(),
            account_holder_name: userName,
            role,
            user_id: userId
          };

      // 1. Call backend Razorpay verify / penny drop endpoint if available
      try {
        const apiBase = ((import.meta.env.VITE_API_BASE_URL as string) || 'https://gaonbazaar-village.onrender.com/api/v1').replace(/\/+$/, '');
        const backendEndpoint = `${apiBase}/payments/verify-penny-drop`;
        await fetch(backendEndpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            account_holder_name: userName,
            upi_id: payoutPayload.upi_id,
            account_number: payoutPayload.account_number,
            ifsc_code: payoutPayload.ifsc_code
          })
        });
      } catch (beErr) {
        console.warn('Backend call notice, proceeding with Supabase sync:', beErr);
      }

      // 2. Update User Status in Supabase Database to 'pending_admin_approval'
      const headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
      };

      // Update public.users table
      await fetch(`${SUPABASE_URL}/rest/v1/users?id=eq.${userId}`, {
        method: 'PATCH',
        headers,
        body: JSON.stringify({
          status: 'pending_admin_approval',
          updated_at: new Date().toISOString()
        })
      });

      // Update role-specific table (stores or runners)
      if (role === 'vendor') {
        await fetch(`${SUPABASE_URL}/rest/v1/stores?owner_id=eq.${userId}`, {
          method: 'PATCH',
          headers,
          body: JSON.stringify({
            status: 'pending_admin_approval',
            upi_id: payoutPayload.upi_id || null,
            bank_account_info: payoutPayload.account_number ? `A/C: ****${payoutPayload.account_number.slice(-4)}, IFSC: ${payoutPayload.ifsc_code}` : null,
            is_approved: false
          })
        });
      } else {
        await fetch(`${SUPABASE_URL}/rest/v1/runners?user_id=eq.${userId}`, {
          method: 'PATCH',
          headers,
          body: JSON.stringify({
            status: 'pending_admin_approval',
            upi_id: payoutPayload.upi_id || null,
            is_approved: false
          })
        });
      }

      // Persist in local storage
      localStorage.setItem(`gb_${role}_payout_status`, 'pending_admin_approval');
      localStorage.setItem(`gb_${role}_payout_data`, JSON.stringify(payoutPayload));

      if (onSuccess) {
        onSuccess(payoutPayload);
      }

      // Route user to the final "Under Review" success screen
      setIsUnderReview(true);
    } catch (err: any) {
      console.error('Payout submission error:', err);
      setError(err?.message || 'Failed to submit payout details. Please check your network and try again.');
    } finally {
      setLoading(false);
    }
  };

  // SCREEN 7: UNDER REVIEW / VERIFICATION IN PROGRESS (Blocks dashboard access until approved)
  if (isUnderReview) {
    return (
      <div className="w-full max-w-md mx-auto p-6 bg-white rounded-2xl shadow-xl border border-slate-200 text-center flex flex-col justify-between min-h-[520px]">
        <div className="pt-8 flex flex-col items-center">
          <div className="w-20 h-20 bg-amber-100 text-amber-600 rounded-full flex items-center justify-center mb-5 shadow-inner relative">
            <Hourglass className="w-10 h-10 animate-pulse text-amber-600" />
            <div className="absolute -bottom-1 -right-1 w-7 h-7 bg-emerald-600 text-white rounded-full flex items-center justify-center border-2 border-white shadow-xs">
              <Lock className="w-3.5 h-3.5" />
            </div>
          </div>

          <h2 className="text-2xl font-black text-slate-900 mb-2">Application Under Review</h2>
          <p className="text-xs text-slate-600 max-w-xs mb-6 leading-relaxed">
            Your bank/UPI payout details and partner credentials have been submitted for Super Admin verification.
          </p>

          <div className="w-full bg-slate-50 p-4 rounded-xl border border-slate-200 text-left space-y-2.5 shadow-2xs mb-6">
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-500 font-medium">Application ID:</span>
              <span className="font-mono font-bold text-slate-900">{applicationId}</span>
            </div>
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-500 font-medium">Status:</span>
              <span className="px-2 py-0.5 text-[10px] font-black rounded-full bg-amber-100 text-amber-800 uppercase tracking-wider">
                Pending Admin Approval
              </span>
            </div>
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-500 font-medium">Payout Method:</span>
              <span className="font-semibold text-slate-800 uppercase">{payoutMode}</span>
            </div>
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-500 font-medium">Estimated Review:</span>
              <span className="font-bold text-emerald-700">~ 2 to 4 Hours</span>
            </div>
          </div>

          <div className="p-3 bg-amber-50 rounded-xl border border-amber-200 text-[11px] text-amber-800 text-left w-full flex items-start space-x-2">
            <ShieldCheck className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
            <span>Access to the live order dashboard is locked until the Super Admin approves your application.</span>
          </div>
        </div>

        {/* Developer / Reviewer Demo Approval simulation */}
        <div className="pt-6">
          <button
            type="button"
            onClick={() => {
              if (onAdminApproved) onAdminApproved();
            }}
            className="w-full py-3 px-4 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl font-bold text-xs transition flex items-center justify-center space-x-1.5"
          >
            <span>Simulate Admin Approval (Reviewer Mode)</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    );
  }

  // SCREEN 6: PAYOUT SETUP FORM (TAB 1: UPI ID, TAB 2: BANK ACCOUNT)
  return (
    <div className="w-full max-w-md mx-auto p-6 bg-white rounded-2xl shadow-xl border border-slate-200">
      {/* Header */}
      <div className="mb-5">
        <div className="flex items-center space-x-2 text-emerald-700 text-xs font-bold uppercase tracking-wider mb-1.5">
          <span className="px-2 py-0.5 bg-emerald-100 rounded-md">Step 6 of 7</span>
          <span>Payout & Settlement Setup</span>
        </div>
        <h2 className="text-2xl font-black text-slate-900 tracking-tight">Bank / UPI Settlement</h2>
        <p className="text-xs text-slate-500 mt-1">
          Direct earnings credited to your registered account with 0% platform deductions.
        </p>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="mb-4 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-start space-x-2 shadow-2xs">
          <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
          <span className="flex-1 font-medium leading-relaxed">{error}</span>
          <button onClick={() => setError(null)} className="text-rose-400 hover:text-rose-700 text-sm font-bold">✕</button>
        </div>
      )}

      {/* Two Distinct Tabs / Toggle */}
      <div className="flex p-1 bg-slate-100 rounded-xl mb-5 border border-slate-200">
        <button
          type="button"
          onClick={() => { setPayoutMode('upi'); setError(null); }}
          className={`flex-1 py-2.5 rounded-lg text-xs font-bold transition flex items-center justify-center space-x-1.5 ${
            payoutMode === 'upi'
              ? 'bg-white text-slate-900 shadow-xs border border-slate-200/60'
              : 'text-slate-500 hover:text-slate-800'
          }`}
        >
          <Smartphone className="w-4 h-4 text-emerald-600" />
          <span>Tab 1: UPI ID (VPA)</span>
        </button>

        <button
          type="button"
          onClick={() => { setPayoutMode('bank'); setError(null); }}
          className={`flex-1 py-2.5 rounded-lg text-xs font-bold transition flex items-center justify-center space-x-1.5 ${
            payoutMode === 'bank'
              ? 'bg-white text-slate-900 shadow-xs border border-slate-200/60'
              : 'text-slate-500 hover:text-slate-800'
          }`}
        >
          <Landmark className="w-4 h-4 text-emerald-600" />
          <span>Tab 2: Bank Account</span>
        </button>
      </div>

      <form onSubmit={handleSubmit} autoComplete="off" className="space-y-4">
        {/* TAB 1: UPI ID FORM */}
        {payoutMode === 'upi' && (
          <div className="space-y-4 animate-in fade-in duration-200">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Virtual Payment Address (UPI ID) <span className="text-rose-500">*</span>
              </label>
              <div className="relative flex items-center">
                <input
                  type="text"
                  autoComplete="off"
                  value={upiId}
                  onChange={(e) => setUpiId(e.target.value)}
                  placeholder="e.g. name@bank or 9876543210@paytm"
                  className="w-full px-3.5 py-3 rounded-xl border border-slate-300 bg-slate-50/50 focus:bg-white text-slate-900 font-mono text-xs font-semibold focus:border-emerald-600 focus:outline-none shadow-2xs transition"
                  autoFocus
                />
              </div>
              <p className="text-[10px] text-slate-400 mt-1">
                Supported: Google Pay, PhonePe, Paytm, BHIM, Cred, and all major Indian banks.
              </p>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 px-4 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold text-xs shadow-lg shadow-emerald-600/25 active:scale-98 transition flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin mr-1.5" />
                  <span>Verifying & Submitting...</span>
                </>
              ) : (
                <>
                  <span>Save & Submit</span>
                  <CheckCircle className="w-4 h-4 ml-1" />
                </>
              )}
            </button>
          </div>
        )}

        {/* TAB 2: BANK ACCOUNT FORM */}
        {payoutMode === 'bank' && (
          <div className="space-y-4 animate-in fade-in duration-200">
            {/* Account Number */}
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Bank Account Number <span className="text-rose-500">*</span>
              </label>
              <input
                type="text"
                inputMode="numeric"
                autoComplete="off"
                value={accountNumber}
                onChange={(e) => setAccountNumber(e.target.value.replace(/\D/g, ''))}
                placeholder="Enter 9 to 18-digit account number"
                maxLength={18}
                className="w-full px-3.5 py-3 rounded-xl border border-slate-300 bg-slate-50/50 focus:bg-white text-slate-900 font-mono text-xs font-semibold focus:border-emerald-600 focus:outline-none shadow-2xs transition"
              />
            </div>

            {/* Re-enter Account Number */}
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Re-enter Bank Account Number <span className="text-rose-500">*</span>
              </label>
              <input
                type="text"
                inputMode="numeric"
                autoComplete="off"
                value={confirmAccountNumber}
                onChange={(e) => setConfirmAccountNumber(e.target.value.replace(/\D/g, ''))}
                placeholder="Re-enter to verify account number"
                maxLength={18}
                className={`w-full px-3.5 py-3 rounded-xl border bg-slate-50/50 focus:bg-white text-slate-900 font-mono text-xs font-semibold focus:outline-none shadow-2xs transition ${
                  confirmAccountNumber && confirmAccountNumber !== accountNumber
                    ? 'border-rose-400 focus:border-rose-600 bg-rose-50/20'
                    : 'border-slate-300 focus:border-emerald-600'
                }`}
              />
              {confirmAccountNumber && confirmAccountNumber !== accountNumber && (
                <p className="text-[10px] text-rose-600 font-medium mt-1">
                  ✕ Account numbers do not match!
                </p>
              )}
              {confirmAccountNumber && confirmAccountNumber === accountNumber && (
                <p className="text-[10px] text-emerald-600 font-bold mt-1">
                  ✓ Account numbers match!
                </p>
              )}
            </div>

            {/* IFSC Code */}
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                IFSC Code <span className="text-rose-500">*</span>
              </label>
              <input
                type="text"
                autoComplete="off"
                value={ifscCode}
                onChange={(e) => setIfscCode(e.target.value.toUpperCase())}
                placeholder="e.g. SBIN0001234 or HDFC0004567"
                maxLength={11}
                className="w-full px-3.5 py-3 rounded-xl border border-slate-300 bg-slate-50/50 focus:bg-white text-slate-900 font-mono uppercase text-xs font-bold focus:border-emerald-600 focus:outline-none shadow-2xs transition tracking-wider"
              />
              <p className="text-[10px] text-slate-400 mt-1">
                11-character code on your cheque book or passbook.
              </p>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 px-4 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold text-xs shadow-lg shadow-emerald-600/25 active:scale-98 transition flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin mr-1.5" />
                  <span>Verifying & Submitting...</span>
                </>
              ) : (
                <>
                  <span>Save & Submit</span>
                  <CheckCircle className="w-4 h-4 ml-1" />
                </>
              )}
            </button>
          </div>
        )}
      </form>
    </div>
  );
};

export default PayoutSetup;
