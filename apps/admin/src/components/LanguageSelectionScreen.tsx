import React, { useState } from 'react';
import { ArrowRight, Check } from 'lucide-react';

interface LanguageSelectionScreenProps {
  onSelect?: (lang: 'en' | 'hi') => void;
  destination?: string;
}

export function LanguageSelectionScreen({
  onSelect,
  destination = '/login',
}: LanguageSelectionScreenProps) {
  const [selectedLang, setSelectedLang] = useState<'en' | 'hi'>(() => {
    try {
      return (localStorage.getItem('gb_customer_lang') as 'en' | 'hi') || 'en';
    } catch {
      return 'en';
    }
  });

  const handleSelectLang = (lang: 'en' | 'hi') => {
    setSelectedLang(lang);
    try {
      localStorage.setItem('gb_customer_lang', lang);
    } catch {
      // Ignore storage errors
    }
  };

  const handleContinue = () => {
    try {
      localStorage.setItem('gb_customer_lang', selectedLang);
    } catch {
      // Ignore storage errors
    }

    if (onSelect) {
      onSelect(selectedLang);
    } else {
      window.history.pushState({}, '', destination);
      window.dispatchEvent(new PopStateEvent('popstate'));
    }
  };

  return (
    <div className="min-h-[100dvh] w-full bg-gradient-to-b from-slate-100 via-emerald-50/20 to-slate-100 flex flex-col justify-center items-center font-sans select-none p-4 sm:p-6 py-6 sm:py-10 overflow-y-auto">
      <div className="w-full max-w-md my-auto bg-white rounded-3xl shadow-2xl shadow-emerald-950/10 border border-slate-100 overflow-hidden flex flex-col p-6 sm:p-8 landscape:p-5 landscape:max-w-xl transition-all duration-300">
        <div className="space-y-5 landscape:space-y-3">
          {/* Header Brand Badge */}
          <div className="flex items-center space-x-3.5">
            <div className="w-12 h-12 rounded-2xl bg-[#0F9D58] text-white flex items-center justify-center font-black text-2xl shadow-lg shadow-green-600/25">
              GB
            </div>
            <div>
              <h1 className="text-xl font-extrabold text-slate-900 tracking-tight">
                GaonBazaar
              </h1>
              <p className="text-xs font-bold text-[#0F9D58] tracking-wide uppercase">
                Village Hyperlocal
              </p>
            </div>
          </div>

          {/* Title & Subtitle */}
          <div className="space-y-1.5">
            <h2 className="text-2xl font-black text-slate-900 tracking-tight">
              {selectedLang === 'hi' ? 'भाषा चुनें' : 'Choose Language'}
            </h2>
            <p className="text-xs text-slate-500 leading-relaxed">
              {selectedLang === 'hi'
                ? 'किराना खरीदारी और वॉयस सर्च के लिए अपनी पसंदीदा भाषा चुनें।'
                : 'Select your preferred language for grocery shopping and voice search.'}
            </p>
          </div>

          {/* Language Cards */}
          <div className="space-y-3 landscape:grid landscape:grid-cols-2 landscape:gap-3 landscape:space-y-0">
            {/* English Card */}
            <button
              type="button"
              onClick={() => handleSelectLang('en')}
              className={`w-full p-4 rounded-2xl border-2 flex items-center justify-between transition-all duration-200 shadow-xs cursor-pointer active:scale-98 ${
                selectedLang === 'en'
                  ? 'border-[#0F9D58] bg-emerald-50/60 ring-2 ring-emerald-500/20'
                  : 'border-slate-200 bg-white hover:border-slate-300'
              }`}
            >
              <div className="flex items-center space-x-3.5">
                <span className="text-2xl select-none" role="img" aria-label="English">
                  🇬🇧
                </span>
                <div className="text-left">
                  <p className="text-sm font-bold text-slate-900">English</p>
                  <p className="text-[11px] text-slate-500">Default International</p>
                </div>
              </div>
              <div
                className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold transition ${
                  selectedLang === 'en'
                    ? 'bg-[#0F9D58] text-white shadow-xs'
                    : 'border-2 border-slate-300 bg-white text-transparent'
                }`}
              >
                <Check className="w-3.5 h-3.5" />
              </div>
            </button>

            {/* Hindi Card */}
            <button
              type="button"
              onClick={() => handleSelectLang('hi')}
              className={`w-full p-4 rounded-2xl border-2 flex items-center justify-between transition-all duration-200 shadow-xs cursor-pointer active:scale-98 ${
                selectedLang === 'hi'
                  ? 'border-[#0F9D58] bg-emerald-50/60 ring-2 ring-emerald-500/20'
                  : 'border-slate-200 bg-white hover:border-slate-300'
              }`}
            >
              <div className="flex items-center space-x-3.5">
                <span className="text-2xl select-none" role="img" aria-label="Hindi">
                  🇮🇳
                </span>
                <div className="text-left">
                  <p className="text-sm font-bold text-slate-900">हिंदी (Hindi)</p>
                  <p className="text-[11px] text-slate-500">शुद्ध ग्रामीण भाषा</p>
                </div>
              </div>
              <div
                className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold transition ${
                  selectedLang === 'hi'
                    ? 'bg-[#0F9D58] text-white shadow-xs'
                    : 'border-2 border-slate-300 bg-white text-transparent'
                }`}
              >
                <Check className="w-3.5 h-3.5" />
              </div>
            </button>
          </div>
        </div>

        {/* Continue Button */}
        <div className="pt-6 landscape:pt-4">
          <button
            type="button"
            onClick={handleContinue}
            className="w-full py-4 landscape:py-3 bg-[#0F9D58] hover:bg-[#0D874C] text-white font-bold rounded-2xl shadow-lg shadow-emerald-600/30 flex items-center justify-center space-x-2 transition active:scale-98 cursor-pointer"
          >
            <span>{selectedLang === 'hi' ? 'आगे बढ़ें' : 'Continue'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

export default LanguageSelectionScreen;
