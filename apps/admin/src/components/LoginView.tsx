import React, { useState } from 'react';
import { ArrowRight, ShieldCheck, Lock } from 'lucide-react';
import { adminApi } from '../api';
import type { AdminUser } from '../types';
import type { Language } from '../i18n';
import { translations } from '../i18n';

interface LoginViewProps {
  onLoginSuccess: (user: AdminUser) => void;
  onUnauthorizedRole: (role: string, phone: string) => void;
  lang: Language;
  onToggleLang: () => void;
}

export function LoginView({
  onLoginSuccess,
  onUnauthorizedRole,
  lang,
  onToggleLang,
}: LoginViewProps) {
  const t = translations[lang];
  const [identifier, setIdentifier] = useState('9800000099');
  const [secretOrOtp, setSecretOrOtp] = useState('123456');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const cleanId = identifier.trim();
      
      // Strict Super Admin RBAC Gate: Only authorized administrative credentials permitted
      const isAllowedAdmin =
        cleanId === '9800000099' ||
        cleanId.toLowerCase().includes('admin') ||
        cleanId.toLowerCase().endsWith('@gaonbazaar.in');

      if (!isAllowedAdmin) {
        adminApi.logout();
        onUnauthorizedRole('customer', cleanId);
        return;
      }

      const result = await adminApi.login(cleanId, secretOrOtp, 'super_admin');

      // Strict RBAC Enforcement: Only 'super_admin' or 'admin' allowed
      const role = result.user?.role;
      if (role !== 'super_admin' && role !== 'admin') {
        adminApi.logout();
        onUnauthorizedRole(role || 'unauthorized', cleanId);
        return;
      }

      onLoginSuccess(result.user);
    } catch (err: any) {
      const msg = err?.message || 'Authentication failed. Please verify admin credentials.';
      if (
        msg.toLowerCase().includes('forbidden') ||
        msg.toLowerCase().includes('access denied') ||
        msg.toLowerCase().includes('customer') ||
        msg.toLowerCase().includes('vendor') ||
        msg.toLowerCase().includes('runner')
      ) {
        onUnauthorizedRole('restricted_user', identifier.trim());
      } else {
        setError(msg);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4 font-sans">
      <div className="max-w-md w-full bg-white rounded-3xl shadow-2xl border border-slate-800 overflow-hidden">
        {/* Brand Header */}
        <div className="bg-slate-950 p-6 text-center text-white border-b border-slate-800 relative">
          {/* Language Switcher pill in header */}
          <button
            type="button"
            onClick={onToggleLang}
            className="absolute top-4 right-4 px-2.5 py-1 rounded-full text-[10px] font-bold bg-slate-800 hover:bg-slate-700 text-emerald-400 border border-slate-700 transition"
          >
            {lang === 'en' ? 'हिंदी' : 'English'}
          </button>

          <div className="w-12 h-12 mx-auto rounded-2xl bg-emerald-600 text-white flex items-center justify-center font-black text-xl shadow-lg mb-3">
            GB
          </div>
          <h1 className="text-xl font-extrabold tracking-tight">{t.loginTitle}</h1>
          <p className="text-xs text-emerald-400 font-semibold mt-1">
            {t.loginSubtitle}
          </p>
        </div>

        {/* Form Body - Single View Super Admin Login */}
        <div className="p-6 space-y-5">
          {error && (
            <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 rounded-xl text-xs">
              <strong>{t.errorTitle}</strong> {error}
            </div>
          )}

          <form onSubmit={handleSubmit} autoComplete="off" className="space-y-4 text-xs">
            <div>
              <label className="font-bold text-slate-700 block mb-1">
                {t.adminPhoneOrEmail}
              </label>
              <div className="relative">
                <input
                  type="text"
                  autoComplete="off"
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  placeholder="9800000099 or admin@gaonbazaar.in"
                  required
                  className="w-full min-h-[48px] h-12 px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl outline-none focus:border-emerald-500 font-semibold text-slate-800 text-sm"
                />
              </div>
            </div>

            <div>
              <label className="font-bold text-slate-700 block mb-1">
                {t.passcodeOrKey}
              </label>
              <div className="relative">
                <input
                  type="password"
                  autoComplete="off"
                  value={secretOrOtp}
                  onChange={(e) => setSecretOrOtp(e.target.value)}
                  placeholder="Passcode 123456 or Master Key"
                  required
                  className="w-full min-h-[48px] h-12 px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl outline-none focus:border-emerald-500 font-mono text-slate-800 text-sm"
                />
              </div>
            </div>

            {/* STRICT RULE: NO SIGN UP BUTTON ALLOWED */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full min-h-[48px] h-12 py-3 text-white font-extrabold rounded-xl shadow-md transition flex items-center justify-center space-x-2 text-sm bg-emerald-600 hover:bg-emerald-700 active:scale-98"
            >
              <span>{isLoading ? t.verifying : t.signInBtn}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          <div className="pt-2 text-center text-[11px] text-slate-400">
            🔒 {t.secureJwtNotice}
          </div>
        </div>
      </div>
    </div>
  );
}
