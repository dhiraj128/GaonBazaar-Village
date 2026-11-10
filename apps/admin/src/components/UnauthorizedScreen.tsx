import React from 'react';
import { ShieldAlert, ArrowLeft, Ban, AlertTriangle } from 'lucide-react';
import type { Language } from '../i18n';
import { translations } from '../i18n';

interface UnauthorizedScreenProps {
  lang: Language;
  onReturnToLogin: () => void;
  detectedRole?: string;
  userPhone?: string;
}

export const UnauthorizedScreen: React.FC<UnauthorizedScreenProps> = ({
  lang,
  onReturnToLogin,
  detectedRole = 'customer',
  userPhone,
}) => {
  const t = translations[lang];

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4 font-sans text-slate-100">
      <div className="max-w-md w-full bg-slate-900 rounded-3xl shadow-2xl border border-rose-900/40 p-8 text-center space-y-6">
        <div className="w-16 h-16 mx-auto rounded-2xl bg-rose-950/80 border border-rose-500/30 text-rose-400 flex items-center justify-center shadow-lg shadow-rose-950/50">
          <ShieldAlert className="w-9 h-9" />
        </div>

        <div className="space-y-2">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-black uppercase tracking-wider bg-rose-900/40 text-rose-300 border border-rose-800/40">
            <Ban className="w-3.5 h-3.5" />
            403 Forbidden
          </span>
          <h1 className="text-xl font-black text-white tracking-tight">
            {t.unauthorizedTitle}
          </h1>
          <p className="text-xs text-slate-400 leading-relaxed">
            {t.unauthorizedDesc}
          </p>
        </div>

        <div className="bg-slate-950 p-4 rounded-2xl border border-slate-800 text-left space-y-2 text-xs">
          <div className="flex items-center justify-between text-slate-400">
            <span>Detected Account:</span>
            <span className="font-mono font-bold text-slate-200">
              {userPhone ? `+91 ${userPhone}` : 'Non-Admin User'}
            </span>
          </div>
          <div className="flex items-center justify-between text-slate-400">
            <span>Assigned Role:</span>
            <span className="px-2 py-0.5 rounded text-[10px] font-extrabold uppercase bg-rose-500/20 text-rose-400">
              {detectedRole}
            </span>
          </div>
          <div className="flex items-center justify-between text-slate-400">
            <span>Access Gate:</span>
            <span className="font-bold text-rose-400">
              REVOKED & LOGGED
            </span>
          </div>
        </div>

        <div className="p-3 bg-amber-950/30 border border-amber-800/30 rounded-xl text-left flex items-start space-x-2 text-[11px] text-amber-300">
          <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
          <span>
            {lang === 'hi'
              ? 'प्रशासनिक विशेषाधिकारों का उल्लंघन सुरक्षा ऑडिट लॉग में दर्ज किया गया है।'
              : 'Security Protocol: Customer, Vendor, and Runner credentials cannot access Super Admin command controls.'}
          </span>
        </div>

        <button
          onClick={onReturnToLogin}
          className="w-full py-3 bg-rose-600 hover:bg-rose-500 text-white font-extrabold rounded-xl shadow-lg shadow-rose-950 transition flex items-center justify-center space-x-2 text-xs"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>{t.returnToLogin}</span>
        </button>
      </div>
    </div>
  );
};
