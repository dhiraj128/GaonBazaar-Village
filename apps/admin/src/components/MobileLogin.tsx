import React, { useState, useEffect } from 'react';
import { Send, User, ArrowRight, ShieldCheck, CheckCircle2, AlertCircle } from 'lucide-react';
import {
  sendFirebaseOtp,
  verifyFirebaseOtp,
  resetRecaptchaVerifier,
  type ConfirmationResult
} from '../utils/firebase';

interface MobileLoginProps {
  onSuccess?: (user: { phone: string; name?: string; token?: string }) => void;
  onCancel?: () => void;
  title?: string;
  subtitle?: string;
}

export function MobileLogin({
  onSuccess,
  onCancel,
  title = "Mobile Login",
  subtitle = "Enter your mobile number to receive a secure 6-digit SMS verification code on your phone."
}: MobileLoginProps) {
  // 1. Clear Hardcoded React State: strictly empty strings for new users
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [step, setStep] = useState<'phone' | 'otp'>('phone');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [confirmationResult, setConfirmationResult] = useState<ConfirmationResult | null>(null);

  // Cleanup verifier on unmount
  useEffect(() => {
    return () => {
      resetRecaptchaVerifier();
    };
  }, []);

  const handleSendOtp = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setError(null);
    setStatusMessage(null);

    const clean = phone.replace(/\D/g, '').slice(-10);
    if (!/^[6-9]\d{9}$/.test(clean) && clean !== '9999999999') {
      setError('Please enter a valid 10-digit Indian mobile number (e.g. 9905361711)');
      return;
    }

    // 1. Enforce +91 Country Code Formatting
    const formattedPhoneNumber = `+91${clean}`;

    // Visual loading feedback
    setIsLoading(true);

    try {
      // Global Razorpay Compliance Review Backdoor
      if (clean === '9999999999') {
        setStep('otp');
        setOtp(['1', '2', '3', '4', '5', '6']);
        setStatusMessage('Razorpay Compliance Review: Static code 123456 active');
        return;
      }

      console.log('[Firebase Phone Auth] Initiating OTP dispatch with invisible reCAPTCHA for:', formattedPhoneNumber);

      // Trigger Firebase Phone Auth with invisible RecaptchaVerifier
      const confirmation = await sendFirebaseOtp(clean);
      setConfirmationResult(confirmation);
      setStep('otp');
      setStatusMessage(`Verification code sent to ${formattedPhoneNumber}`);
    } catch (err: any) {
      console.error('[Firebase Phone Auth Error Code]:', err?.code);
      console.error('[Firebase Phone Auth Error Message]:', err?.message);
      console.error('[Firebase Phone Auth Error Stack]:', err);

      const code = err?.code || '';
      const rawMsg = err?.message || 'Failed to dispatch verification code';

      // Explicitly Surface the Real Error without generic masking
      if (code === 'auth/unauthorized-domain' || rawMsg.toLowerCase().includes('unauthorized-domain')) {
        const currentDomain = typeof window !== 'undefined' ? window.location.hostname : 'apnagaonbazaar.in';
        setError(`Firebase Error (auth/unauthorized-domain): Domain '${currentDomain}' is not authorized. Please add it in Firebase Console > Authentication > Settings > Authorized Domains.`);
      } else if (code === 'auth/quota-exceeded' || rawMsg.toLowerCase().includes('quota')) {
        setError(`Firebase Error (auth/quota-exceeded): SMS Quota Exceeded. Free tier limit reached. Please check Firebase SMS billing.`);
      } else if (code === 'auth/too-many-requests') {
        setError(`Firebase Error (auth/too-many-requests): Too many OTP attempts. Please wait 1-2 minutes before trying again.`);
      } else if (code === 'auth/invalid-phone-number' || rawMsg.toLowerCase().includes('invalid-phone')) {
        setError(`Firebase Error (auth/invalid-phone-number): Invalid phone number format. Must be +91 followed by 10 digits.`);
      } else if (code === 'auth/captcha-check-failed' || code === 'auth/invalid-app-credential') {
        setError(`Firebase Error (${code}): Invisible reCAPTCHA verification failed. Please refresh and try again.`);
      } else if (code) {
        setError(`Firebase Error (${code}): ${rawMsg}`);
      } else {
        setError(`Firebase Error: ${rawMsg}`);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyOtp = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setError(null);

    const code = otp.join('');
    if (code.length !== 6) {
      setError('Please enter complete 6-digit OTP');
      return;
    }

    setIsLoading(true);
    try {
      const clean = phone.replace(/\D/g, '').slice(-10);
      const formattedPhoneNumber = `+91${clean}`;

      // Razorpay compliance backdoor
      if (clean === '9999999999' && (code === '123456' || code === '1234')) {
        const complianceUser = {
          phone: '+919999999999',
          name: 'Razorpay Compliance Reviewer',
          role: 'customer',
          token: 'razorpay-compliance-token'
        };
        if (onSuccess) onSuccess(complianceUser);
        return;
      }

      // Verify OTP via Firebase confirmationResult
      console.log('[Firebase Phone Auth] Confirming OTP with Firebase token...');
      const userCred = await verifyFirebaseOtp(code);
      const firebaseUser = userCred.user;
      console.log('[Firebase Phone Auth] OTP successfully verified for UID:', firebaseUser.uid);

      // Attempt optional backend sync
      try {
        const res = await fetch('/api/v1/auth/otp/verify', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            phone: clean,
            otp: code,
            role: 'customer',
            name: name.trim() || undefined
          })
        });

        if (res.ok) {
          const data = await res.json();
          if (onSuccess) onSuccess(data);
          return;
        }
      } catch (backendSyncErr) {
        console.warn('[Backend Sync Notice]:', backendSyncErr);
      }

      // If backend was offline or not reachable, proceed with Firebase authentication
      if (onSuccess) {
        const token = await firebaseUser.getIdToken().catch(() => 'firebase-verified');
        onSuccess({
          phone: formattedPhoneNumber,
          name: name.trim() || undefined,
          token
        });
      }
    } catch (err: any) {
      console.error('[Firebase Verification Error Code]:', err?.code);
      console.error('[Firebase Verification Error Message]:', err?.message);

      const code = err?.code || '';
      const msg = err?.message || 'Verification failed. Please verify the 6-digit code.';

      if (code === 'auth/invalid-verification-code') {
        setError('Firebase Error (auth/invalid-verification-code): Incorrect OTP code entered.');
      } else if (code === 'auth/code-expired') {
        setError('Firebase Error (auth/code-expired): OTP has expired. Please click Resend OTP.');
      } else if (code) {
        setError(`Firebase Error (${code}): ${msg}`);
      } else {
        setError(msg);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleOtpChange = (index: number, val: string) => {
    const cleaned = val.replace(/\D/g, '');
    const newOtp = [...otp];
    if (cleaned.length > 1) {
      // Pasted full 6-digit code
      const pasted = cleaned.slice(0, 6).split('');
      for (let i = 0; i < 6; i++) {
        newOtp[i] = pasted[i] || '';
      }
      setOtp(newOtp);
      const nextEl = document.getElementById(`react-otp-5`);
      nextEl?.focus();
      return;
    }
    newOtp[index] = cleaned;
    setOtp(newOtp);

    if (cleaned && index < 5) {
      const nextEl = document.getElementById(`react-otp-${index + 1}`);
      nextEl?.focus();
    }
  };

  const handleOtpKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      const prevEl = document.getElementById(`react-otp-${index - 1}`);
      prevEl?.focus();
    }
  };

  return (
    <div className="max-w-md w-full mx-auto bg-white rounded-3xl shadow-2xl border border-slate-100 overflow-hidden font-sans relative">
      {/* Invisible Firebase reCAPTCHA Container */}
      <div id="firebase-recaptcha-container" className="hidden" />

      {/* Brand Header */}
      <div className="bg-[#0F9D58] p-6 text-white text-center relative border-b border-emerald-700/50">
        {/* Logo Monogram */}
        <div className="w-14 h-14 mx-auto rounded-2xl bg-white shadow-lg shadow-black/10 flex items-center justify-center mb-3">
          <svg
            className="w-9 h-9 text-[#0F9D58]"
            viewBox="0 0 64 64"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path d="M32 6L8 24H56L32 6Z" fill="#0F9D58" />
            <rect x="14" y="24" width="36" height="28" rx="2" fill="#E8F5E9" />
            <rect x="18" y="28" width="6" height="20" rx="1" fill="#0F9D58" />
            <rect x="29" y="32" width="6" height="16" rx="1" fill="#0F9D58" />
            <rect x="40" y="28" width="6" height="20" rx="1" fill="#0F9D58" />
            <circle cx="20" cy="54" r="4" fill="#1B5E20" />
            <circle cx="44" cy="54" r="4" fill="#1B5E20" />
            <path d="M12 54H52" stroke="#1B5E20" strokeWidth="3" strokeLinecap="round" />
          </svg>
        </div>
        <h2 className="text-2xl font-black tracking-tight text-white">{title}</h2>
        <p className="text-xs text-emerald-100 mt-1 max-w-xs mx-auto leading-relaxed">
          {subtitle}
        </p>
      </div>

      <div className="p-6 space-y-5">
        {/* Real Error Message Display */}
        {error && (
          <div className="p-3.5 bg-rose-50 border border-rose-200 text-rose-800 rounded-xl text-xs flex items-start space-x-2 leading-relaxed">
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
            <div className="flex-1 font-medium">{error}</div>
          </div>
        )}

        {statusMessage && !error && (
          <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl text-xs flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-[#0F9D58] shrink-0" />
            <span>{statusMessage}</span>
          </div>
        )}

        {step === 'phone' ? (
          <form onSubmit={handleSendOtp} autoComplete="off" className="space-y-4">
            {/* 2. Disable Browser Auto-fill: autoComplete="off" */}
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Full Name <span className="text-slate-400 font-normal">(for new customers)</span>
              </label>
              <div className="relative flex items-center">
                <User className="absolute left-3.5 w-4 h-4 text-slate-400" />
                <input
                  type="text"
                  autoComplete="off"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Ramesh Kumar"
                  className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-semibold text-slate-800 outline-none focus:border-[#0F9D58] focus:bg-white transition"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Mobile Number
              </label>
              <div className="relative flex items-center">
                <div className="absolute left-3.5 flex items-center space-x-1 text-xs font-bold text-slate-700 border-r border-slate-200 pr-2 select-none">
                  <span>🇮🇳</span>
                  <span className="font-mono text-[#0F9D58] font-extrabold">+91</span>
                </div>
                <input
                  type="tel"
                  maxLength={10}
                  autoComplete="off"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value.replace(/\D/g, ''))}
                  placeholder="Enter 10-digit mobile number"
                  required
                  className="w-full pl-20 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-mono font-semibold text-slate-800 outline-none focus:border-[#0F9D58] focus:bg-white transition"
                />
              </div>
              <p className="text-[10px] text-slate-400 mt-1">
                Free Firebase SMS OTP delivered to your phone
              </p>
            </div>

            {/* Send OTP Button with Visual Loading State */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3.5 bg-[#0F9D58] hover:bg-[#0D874C] disabled:opacity-60 disabled:cursor-not-allowed text-white font-bold rounded-xl shadow-md transition flex items-center justify-center space-x-2 text-sm cursor-pointer active:scale-98"
            >
              {isLoading ? (
                <>
                  <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                  <span>Sending Free OTP...</span>
                </>
              ) : (
                <>
                  <span>Send OTP</span>
                  <Send className="w-4 h-4" />
                </>
              )}
            </button>
          </form>
        ) : (
          <form onSubmit={handleVerifyOtp} autoComplete="off" className="space-y-4">
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-600">
                Code sent to: <strong className="text-slate-900">+91 {phone}</strong>
              </span>
              <button
                type="button"
                onClick={() => setStep('phone')}
                className="text-[#0F9D58] font-bold hover:underline"
              >
                Change
              </button>
            </div>

            <div>
              <label className="block text-center text-xs font-semibold text-slate-600 mb-2">
                Enter 6-Digit SMS Verification Code
              </label>
              <div className="flex justify-center items-center gap-2">
                {otp.map((digit, idx) => (
                  <input
                    key={idx}
                    id={`react-otp-${idx}`}
                    type="tel"
                    maxLength={1}
                    autoComplete="off"
                    value={digit}
                    onChange={(e) => handleOtpChange(idx, e.target.value)}
                    onKeyDown={(e) => handleOtpKeyDown(idx, e)}
                    className="w-11 h-12 text-center text-lg font-bold font-mono bg-slate-50 border border-slate-200 rounded-xl focus:border-[#0F9D58] focus:bg-white outline-none transition"
                  />
                ))}
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading || otp.join('').length !== 6}
              className="w-full py-3.5 bg-[#0F9D58] hover:bg-[#0D874C] disabled:opacity-60 disabled:cursor-not-allowed text-white font-bold rounded-xl shadow-md transition flex items-center justify-center space-x-2 text-sm cursor-pointer active:scale-98"
            >
              {isLoading ? (
                <>
                  <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                  <span>Verifying...</span>
                </>
              ) : (
                <>
                  <span>Verify & Proceed</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>

            <div className="text-center pt-1">
              <button
                type="button"
                onClick={() => handleSendOtp()}
                disabled={isLoading}
                className="text-xs text-slate-500 hover:text-[#0F9D58] font-semibold underline"
              >
                Resend OTP
              </button>
            </div>
          </form>
        )}

        <div className="pt-2 text-center text-[11px] text-slate-400 flex items-center justify-center space-x-1">
          <ShieldCheck className="w-3.5 h-3.5 text-[#0F9D58]" />
          <span>Apna GaonBazaar Secure Zero-Data-Leak Authentication</span>
        </div>
      </div>
    </div>
  );
}

export default MobileLogin;
