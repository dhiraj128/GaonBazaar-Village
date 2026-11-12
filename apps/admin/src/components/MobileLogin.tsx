import React, { useState, useEffect } from 'react';
import { Send, ArrowRight, CheckCircle2, AlertCircle } from 'lucide-react';
import {
  sendFast2SmsOtp,
  verifyFast2SmsOtp,
  sendFirebaseTestPhoneOtp,
  type ConfirmationResult
} from '../utils/firebase';
import { PullToRefresh } from './PullToRefresh';

interface MobileLoginProps {
  onSuccess?: (user: { phone: string; name?: string; token?: string; uid?: string; role?: string }) => void;
  onCancel?: () => void;
  lang?: 'en' | 'hi';
  title?: string;
  subtitle?: string;
}

export function MobileLogin({
  onSuccess,
  onCancel,
  lang: propLang,
  title: propTitle,
  subtitle: propSubtitle,
}: MobileLoginProps) {
  // Strict Language Detection (No mixing of Hindi & English)
  const [lang, setLang] = useState<'en' | 'hi'>(() => {
    if (propLang === 'en' || propLang === 'hi') return propLang;
    try {
      const stored = localStorage.getItem('gb_customer_lang');
      return stored === 'hi' ? 'hi' : 'en';
    } catch {
      return 'en';
    }
  });

  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [step, setStep] = useState<'phone' | 'otp'>('phone');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [confirmationResult, setConfirmationResult] = useState<ConfirmationResult | null>(null);

  // Guarantee strictly empty inputs on mount
  useEffect(() => {
    setName('');
    setPhone('');
  }, []);

  // Sync prop changes if language is updated from parent
  useEffect(() => {
    if (propLang && (propLang === 'en' || propLang === 'hi')) {
      setLang(propLang);
    }
  }, [propLang]);

  // Strict localized copy dictionary
  const isHindi = lang === 'hi';
  const t = {
    title: propTitle || (isHindi ? "मोबाइल लॉगिन" : "Mobile Login"),
    subtitle: propSubtitle || (isHindi
      ? "सुरक्षित 6-अंकीय OTP प्राप्त करने के लिए अपना मोबाइल नंबर दर्ज करें।"
      : "Enter your mobile number to receive a secure 6-digit OTP."),
    nameLabel: isHindi ? "पूरा नाम" : "Full Name",
    nameSublabel: isHindi ? "(नए ग्राहकों के लिए)" : "(for new customers)",
    namePlaceholder: isHindi ? "उदा. रमेश कुमार" : "e.g. Ramesh Kumar",
    phoneLabel: isHindi ? "मोबाइल नंबर" : "Mobile Number",
    phonePlaceholder: isHindi ? "10 अंकों का मोबाइल नंबर दर्ज करें" : "Enter 10-digit mobile number",
    phoneHelper: isHindi ? "आपके फोन पर तुरंत SMS OTP भेजा जाएगा।" : "Instant SMS OTP delivered to your phone.",
    sendBtn: isHindi ? "OTP भेजें" : "Send OTP",
    sendingBtn: isHindi ? "भेजा जा रहा है..." : "Sending...",
    codeSentTo: isHindi ? "कोड भेजा गया:" : "Code sent to:",
    changeBtn: isHindi ? "बदलें" : "Change",
    otpTitle: isHindi ? "6-अंकीय SMS सत्यापन कोड दर्ज करें" : "Enter 6-Digit SMS Verification Code",
    verifyBtn: isHindi ? "सत्यापित करें और आगे बढ़ें" : "Verify & Proceed",
    verifyingBtn: isHindi ? "सत्यापित हो रहा है..." : "Verifying...",
    resendBtn: isHindi ? "OTP पुनः भेजें" : "Resend OTP",
    trustBadge: isHindi ? "🔒 100% सुरक्षित और एन्क्रिप्टेड लॉगिन" : "🔒 256-bit Encrypted & Secure Authentication",
    invalidPhone: isHindi ? "कृपया 10 अंकों का वैध भारतीय मोबाइल नंबर दर्ज करें" : "Please enter a valid 10-digit Indian mobile number",
    invalidOtp: isHindi ? "कृपया पूरा 6-अंकीय OTP कोड दर्ज करें" : "Please enter complete 6-digit OTP",
  };

  const handleSendOtp = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setError(null);
    setStatusMessage(null);

    const clean = phone.replace(/\D/g, '').slice(-10);
    if (!/^[6-9]\d{9}$/.test(clean) && clean !== '9999999999') {
      setError(t.invalidPhone);
      return;
    }

    const formattedPhoneNumber = `+91${clean}`;
    setIsLoading(true);

    try {
      // 1. Whitelisted Razorpay Compliance Numbers: Bypass external SMS (Fast2SMS)
      const isComplianceTestNumber = (clean === '9905361711' || clean === '9999999999');
      if (isComplianceTestNumber) {
        console.log('[Auth] Compliance test number whitelisted for static review:', clean);

        // Route into Firebase Phone Auth test flow (recognizes test numbers with static 123456)
        try {
          const conf = await sendFirebaseTestPhoneOtp(clean);
          if (conf) {
            setConfirmationResult(conf);
          }
        } catch (testFlowErr) {
          console.warn('[Auth] Test flow verifier notice:', testFlowErr);
        }

        setStep('otp');
        setOtp(['1', '2', '3', '4', '5', '6']);
        setStatusMessage(
          isHindi
            ? "रेज़रपे समीक्षा मोड: स्थिर कोड 123456 सक्रिय है"
            : "Razorpay Review Mode: Static code 123456 active"
        );
        return;
      }

      // 2. Standard Public Number: Trigger Fast2SMS Smart OTP flow
      console.log('[Auth] Initiating Fast2SMS OTP dispatch for:', formattedPhoneNumber);
      await sendFast2SmsOtp(clean);
      setStep('otp');
      setStatusMessage(
        isHindi
          ? `सत्यापन कोड ${formattedPhoneNumber} पर भेजा गया`
          : `Verification code sent to ${formattedPhoneNumber}`
      );
    } catch (err: any) {
      console.error("SMS DISPATCH ERROR:", err);
      const msg = err?.message || (isHindi
        ? "OTP भेजने में असमर्थ। कृपया अपना नेटवर्क जांचें और पुनः प्रयास करें।"
        : "Unable to send OTP. Please check your network and try again.");
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyOtp = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setError(null);

    const code = otp.join('');
    if (code.length !== 6) {
      setError(t.invalidOtp);
      return;
    }

    setIsLoading(true);
    try {
      const clean = phone.replace(/\D/g, '').slice(-10);
      const formattedPhoneNumber = `+91${clean}`;

      // 1. Razorpay Compliance Static Verification (9905361711 or 9999999999 with 123456)
      const isComplianceTestNumber = (clean === '9905361711' || clean === '9999999999');
      const isStaticOtpValid = (code === '123456' || code === '1234');

      if (isComplianceTestNumber && isStaticOtpValid) {
        console.log('[Auth] Compliance test OTP verified successfully for:', formattedPhoneNumber);

        let token = 'razorpay-compliance-verified-session-token';
        let authUid = `usr_test_${clean}`;

        // If native Firebase test ConfirmationResult exists, verify with Firebase
        if (confirmationResult) {
          try {
            const cred = await confirmationResult.confirm(code);
            if (cred && cred.user) {
              authUid = cred.user.uid;
              token = await cred.user.getIdToken().catch(() => token);
              console.log('[Auth] Native Firebase test user confirmed, UID:', authUid);
            }
          } catch (confErr) {
            console.warn('[Auth] ConfirmationResult notice:', confErr);
          }
        }

        const complianceUser = {
          phone: formattedPhoneNumber,
          name: name.trim() || (clean === '9905361711' ? 'Dhiraj Kumar' : 'Razorpay Compliance Reviewer'),
          role: 'customer',
          token: token,
          uid: authUid
        };

        // Persist session tokens to grant full access to inner pages
        try {
          localStorage.setItem('gaonbazaar_admin_jwt_token', token);
          localStorage.setItem('gb_customer_token', token);
          localStorage.setItem('gb_customer_phone', formattedPhoneNumber);
          localStorage.setItem('gb_customer_logged_in', 'true');
          localStorage.setItem('gaonbazaar_admin_user_info', JSON.stringify(complianceUser));
        } catch (storageErr) {
          console.warn('[Auth] LocalStorage set notice:', storageErr);
        }

        // Grant full access
        if (onSuccess) {
          onSuccess(complianceUser);
        }
        return;
      }

      // 2. Standard Public Number: Verify OTP via Fast2SMS API & authenticate with Firebase Custom Token
      console.log('[Auth] Verifying OTP and signing in via Firebase Custom Token...');
      const userCred = await verifyFast2SmsOtp(clean, code);
      const authUser = userCred.user;
      console.log('[Auth] OTP successfully verified for UID:', authUser.uid);

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

      // Proceed with verified auth session
      if (onSuccess) {
        const token = await authUser.getIdToken().catch(() => 'auth-verified');
        const sessionUser = {
          phone: formattedPhoneNumber,
          name: name.trim() || undefined,
          token,
          uid: authUser.uid
        };
        try {
          localStorage.setItem('gaonbazaar_admin_jwt_token', token);
          localStorage.setItem('gb_customer_token', token);
          localStorage.setItem('gb_customer_phone', formattedPhoneNumber);
          localStorage.setItem('gb_customer_logged_in', 'true');
        } catch {}
        onSuccess(sessionUser);
      }
    } catch (err: any) {
      console.error("FIREBASE FATAL ERROR:", err?.code, err?.message);
      console.error("FIREBASE FULL ERROR:", err);

      const code = err?.code || '';

      if (code === 'auth/invalid-verification-code') {
        setError(isHindi
          ? "अमान्य OTP कोड। कृपया सही 6-अंकीय कोड दर्ज करें।"
          : "Invalid OTP code. Please enter the correct 6-digit code.");
      } else if (code === 'auth/code-expired') {
        setError(isHindi
          ? "सत्यापन कोड समाप्त हो गया है। कृपया नया OTP अनुरोध करें।"
          : "Verification code has expired. Please request a new OTP.");
      } else {
        setError(err?.message || (isHindi
          ? "OTP सत्यापित करने में असमर्थ। कृपया पुनः प्रयास करें।"
          : "Unable to verify OTP. Please try again."));
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
    <PullToRefresh className="w-full flex items-center justify-center">
      <div className="max-w-md w-full mx-auto bg-white rounded-3xl shadow-2xl border border-slate-100 overflow-hidden font-sans relative select-none">
        {/* Invisible container for Firebase test phone auth reCAPTCHA */}
        <div id="recaptcha-test-container" style={{ position: 'fixed', bottom: 0, opacity: 0, pointerEvents: 'none', zIndex: -1 }} />

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
          <h2 className="text-2xl font-black tracking-tight text-white">{t.title}</h2>
          <p className="text-xs text-emerald-100 mt-1 max-w-xs mx-auto leading-relaxed">
            {t.subtitle}
          </p>
        </div>

        <div className="p-6 space-y-5">
          {/* Human-Readable Error Message Display */}
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
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                {t.phoneLabel}
              </label>
                <div className="relative flex items-center">
                  <div className="absolute left-3.5 flex items-center space-x-1 text-xs font-bold text-slate-700 border-r border-slate-200 pr-2 select-none">
                    <span>🇮🇳</span>
                    <span className="font-mono text-[#0F9D58] font-extrabold">+91</span>
                  </div>
                  <input
                    type="tel"
                    name="gb_usr_reg_phone"
                    id="customer-phone-field"
                    maxLength={10}
                    value={phone}
                    onChange={(e) => setPhone(e.target.value.replace(/\D/g, ''))}
                    autoComplete="off"
                    autoCorrect="off"
                    autoCapitalize="off"
                    spellCheck={false}
                    data-lpignore="true"
                    data-form-type="other"
                    placeholder={t.phonePlaceholder}
                    required
                    className="w-full pl-20 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-mono font-semibold text-slate-800 outline-none focus:border-[#0F9D58] focus:bg-white transition"
                  />
                </div>
              <p className="text-[10px] text-slate-400 mt-1">
                {t.phoneHelper}
              </p>
            </div>

            {/* Send OTP Button with Visual Loading State */}
            <button
              id="send-otp-btn"
              type="submit"
              disabled={isLoading}
              className="w-full py-3.5 bg-[#0F9D58] hover:bg-[#0D874C] disabled:opacity-60 disabled:cursor-not-allowed text-white font-bold rounded-xl shadow-md transition flex items-center justify-center space-x-2 text-sm cursor-pointer active:scale-98"
            >
              {isLoading ? (
                <>
                  <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                  <span>{t.sendingBtn}</span>
                </>
              ) : (
                <>
                  <span>{t.sendBtn}</span>
                  <Send className="w-4 h-4" />
                </>
              )}
            </button>
          </form>
        ) : (
          <form onSubmit={handleVerifyOtp} autoComplete="off" className="space-y-4">
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-600">
                {t.codeSentTo} <strong className="text-slate-900">+91 {phone}</strong>
              </span>
              <button
                type="button"
                onClick={() => setStep('phone')}
                className="text-[#0F9D58] font-bold hover:underline"
              >
                {t.changeBtn}
              </button>
            </div>

            <div>
              <label className="block text-center text-xs font-semibold text-slate-600 mb-2">
                {t.otpTitle}
              </label>
              <div className="flex justify-center items-center gap-2">
                {otp.map((digit, idx) => (
                  <input
                    key={idx}
                    id={`react-otp-${idx}`}
                    type="tel"
                    maxLength={1}
                    autoComplete="off"
                    autoCorrect="off"
                    autoCapitalize="off"
                    spellCheck={false}
                    data-lpignore="true"
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
                  <span>{t.verifyingBtn}</span>
                </>
              ) : (
                <>
                  <span>{t.verifyBtn}</span>
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
                {t.resendBtn}
              </button>
            </div>
          </form>
        )}

        {/* Upgraded Trust Badge: Strict i18n & Tailwind Typography */}
        <div className="text-xs font-medium text-gray-500 tracking-wide mt-4 flex items-center justify-center gap-1 select-none">
          <span>{t.trustBadge}</span>
        </div>
      </div>
      </div>
    </PullToRefresh>
  );
}

export default MobileLogin;
