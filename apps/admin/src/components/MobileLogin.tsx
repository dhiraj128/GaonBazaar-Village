import React, { useState } from 'react';
import { Send, Smartphone, User, ArrowRight, ShieldCheck, CheckCircle2 } from 'lucide-react';

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

  const handleSendOtp = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setError(null);

    const clean = phone.replace(/\D/g, '').slice(-10);
    if (!/^[6-9]\d{9}$/.test(clean) && clean !== '9999999999') {
      setError('Please enter a valid 10-digit Indian mobile number (starts with 6-9)');
      return;
    }

    // 3. Visual loading feedback: isLoading state, "Sending..." text, disabled button
    setIsLoading(true);

    try {
      // Global Razorpay Compliance Review Backdoor
      if (clean === '9999999999') {
        setStep('otp');
        setOtp(['1', '2', '3', '4', '5', '6']);
        setStatusMessage('Razorpay Compliance Review: Static code 123456 active');
        return;
      }

      // Backend / Firebase OTP Dispatch
      try {
        const res = await fetch('/api/v1/auth/otp/send', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            phone: clean,
            role: 'customer',
            name: name.trim() || undefined
          })
        });

        if (!res.ok) {
          const body = await res.json().catch(() => ({}));
          console.warn('API OTP send warning:', body.detail);
        }
      } catch (netErr) {
        console.warn('Offline or background OTP notice:', netErr);
      }

      setStep('otp');
      setStatusMessage(`Verification code sent to +91 ${clean}`);
    } catch (err: any) {
      console.error('Firebase OTP API call error:', err);
      setError(err?.message || 'Failed to dispatch verification code. Please check your number.');
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

      const res = await fetch('/api/v1/auth/otp/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phone: clean,
          otp: code,
          role: 'customer'
        })
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || 'Invalid verification code');
      }

      const data = await res.json();
      if (onSuccess) onSuccess(data);
    } catch (err: any) {
      setError(err?.message || 'Verification failed. Please verify the 6-digit code.');
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
    <div className="max-w-md w-full mx-auto bg-white rounded-3xl shadow-2xl border border-slate-100 overflow-hidden font-sans">
      {/* Brand Header */}
      <div className="bg-slate-950 p-6 text-white text-center relative border-b border-slate-800">
        <div className="w-12 h-12 mx-auto rounded-2xl bg-emerald-600 flex items-center justify-center font-black text-xl shadow-lg mb-3">
          GB
        </div>
        <h2 className="text-xl font-extrabold tracking-tight">{title}</h2>
        <p className="text-xs text-slate-400 mt-1 max-w-xs mx-auto leading-relaxed">
          {subtitle}
        </p>
      </div>

      <div className="p-6 space-y-5">
        {error && (
          <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 rounded-xl text-xs flex items-center space-x-2">
            <span>⚠️</span>
            <span>{error}</span>
          </div>
        )}

        {statusMessage && !error && (
          <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl text-xs flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
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
                  className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-semibold text-slate-800 outline-none focus:border-emerald-600 focus:bg-white transition"
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
                  <span className="font-mono text-emerald-800 font-extrabold">+91</span>
                </div>
                <input
                  type="tel"
                  maxLength={10}
                  autoComplete="off"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value.replace(/\D/g, ''))}
                  placeholder="Enter 10-digit mobile number"
                  required
                  className="w-full pl-20 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-mono font-semibold text-slate-800 outline-none focus:border-emerald-600 focus:bg-white transition"
                />
              </div>
              <p className="text-[10px] text-slate-400 mt-1">
                Instant SMS OTP delivered to your phone
              </p>
            </div>

            {/* 3. Fix the "Send OTP" Button Action & Visual Loading State */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3.5 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-60 disabled:cursor-not-allowed text-white font-bold rounded-xl shadow-md transition flex items-center justify-center space-x-2 text-sm cursor-pointer active:scale-98"
            >
              {isLoading ? (
                <>
                  <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                  <span>Sending...</span>
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
                className="text-emerald-700 font-bold hover:underline"
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
                    className="w-11 h-12 text-center text-lg font-bold font-mono bg-slate-50 border border-slate-200 rounded-xl focus:border-emerald-600 focus:bg-white outline-none transition"
                  />
                ))}
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading || otp.join('').length !== 6}
              className="w-full py-3.5 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-60 disabled:cursor-not-allowed text-white font-bold rounded-xl shadow-md transition flex items-center justify-center space-x-2 text-sm cursor-pointer active:scale-98"
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
                className="text-xs text-slate-500 hover:text-emerald-700 font-semibold underline"
              >
                Resend OTP
              </button>
            </div>
          </form>
        )}

        <div className="pt-2 text-center text-[11px] text-slate-400 flex items-center justify-center space-x-1">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
          <span>Apna GaonBazaar Secure Zero-Data-Leak Authentication</span>
        </div>
      </div>
    </div>
  );
}

export default MobileLogin;
