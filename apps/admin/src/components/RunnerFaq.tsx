import React, { useState } from 'react';
import {
  HelpCircle,
  Compass,
  PhoneCall,
  Banknote,
  CalendarCheck,
  CreditCard,
  ChevronDown,
  Sparkles,
} from 'lucide-react';

interface RunnerFaqProps {
  lang?: 'en' | 'hi';
}

interface FaqItem {
  id: number;
  icon: React.ComponentType<{ className?: string }>;
  qEn: string;
  qHi: string;
  aEn: string;
  aHi: string;
  highlight?: boolean;
}

const runnerFaqs: FaqItem[] = [
  {
    id: 1,
    icon: Compass,
    qEn: 'What is the delivery radius & cluster geofencing rules?',
    qHi: 'डिलीवरी दायरा और क्लस्टर जियोफेंसिंग नियम क्या हैं?',
    aEn: 'Gaon Mitra riders operate within an 8km geofenced rural cluster. Missions are assigned close to your base village to ensure 15–30 minute doorsteps while keeping bike fuel expenditure low.',
    aHi: 'गाँव मित्र राइडर्स 8 किमी के जियोफेंस्ड ग्रामीण क्लस्टर के भीतर काम करते हैं। 15-30 मिनट में डिलीवरी सुनिश्चित करने और बाइक पेट्रोल खर्च को कम रखने के लिए आपके आधार गाँव के करीब के मिशन सौंपे जाते हैं।',
  },
  {
    id: 2,
    icon: PhoneCall,
    qEn: 'How should I handle unreachable customers at the doorstep?',
    qHi: 'ग्राहक के न मिलने पर क्या प्रक्रिया अपनानी चाहिए?',
    aEn: 'If a customer is unreachable, attempt at least 3 phone calls within 5 minutes. If still unavailable, inform your Hub Manager in the app. Never mark any delivery complete without inputting the customer’s secure 4-digit handover OTP.',
    aHi: 'यदि ग्राहक फोन नहीं उठाता है, तो 5 मिनट के भीतर कम से कम 3 बार कॉल करने का प्रयास करें। यदि फिर भी संपर्क न हो, तो ऐप में हब मैनेजर को सूचित करें। ग्राहक के सुरक्षित 4-अंकीय ओटीपी (OTP) के बिना डिलीवरी को कभी पूर्ण न करें।',
  },
  {
    id: 3,
    icon: Banknote,
    qEn: 'How and when do I deposit daily COD cash at the rural hub?',
    qHi: 'दैनिक सीओडी (COD) नकद ग्रामीण हब पर कब और कैसे जमा करना है?',
    aEn: 'All cash collected from Cash on Delivery (COD) orders must be deposited at the Muzaffarpur rural operations hub at the end of your shift every evening. The Hub Manager will reconcile your cash collection immediately.',
    aHi: 'कैश ऑन डिलीवरी (COD) ऑर्डरों से एकत्र की गई पूरी नकद राशि हर शाम आपकी शिफ्ट खत्म होने पर मुजफ्फरपुर ग्रामीण हब पर जमा की जानी चाहिए। हब मैनेजर तुरंत आपके नकद संग्रह का समाधान दर्ज करेंगे।',
  },
  {
    id: 4,
    icon: CalendarCheck,
    qEn: 'What is the weekly delivery payout schedule?',
    qHi: 'साप्ताहिक डिलीवरी भुगतान अनुसूची क्या है?',
    aEn: 'Delivery fees and completed order bonuses are settled directly to your verified bank account or UPI ID every Friday night. You can review all completed trip earnings in real-time in your Earnings tab.',
    aHi: 'डिलीवरी शुल्क और पूर्ण ऑर्डर प्रोत्साहन राशि हर शुक्रवार की रात सीधे आपके सत्यापित बैंक खाते या यूपीआई आईडी में स्थानांतरित की जाती है। आप अपनी कमाई टैब में सभी पूरी की गई यात्राओं को देख सकते हैं।',
  },
  {
    id: 5,
    icon: CreditCard,
    qEn: 'Why is my delivery payout slightly less on online orders?',
    qHi: 'ऑनलाइन ऑर्डर पर मेरा डिलीवरी भुगतान थोड़ा कम क्यों होता है?',
    aEn: 'For online payments, backend processors like Razorpay charge a standard fee to process the electronic transfer. Cash on Delivery (COD) deliveries do not have this online fee.',
    aHi: 'ऑनलाइन भुगतान के लिए, रेज़रपे (Razorpay) जैसे बैकएंड प्रोसेसर इलेक्ट्रॉनिक ट्रांसफर को प्रोसेस करने के लिए एक मानक शुल्क लेते हैं। कैश ऑन डिलीवरी (COD) डिलीवरी में यह ऑनलाइन शुल्क नहीं होता है।',
    highlight: true,
  },
];

export const RunnerFaq: React.FC<RunnerFaqProps> = ({ lang = 'en' }) => {
  const [openId, setOpenId] = useState<number | null>(5); // Open point 5 by default

  const toggle = (id: number) => {
    setOpenId((prev) => (prev === id ? null : id));
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
      {/* Header */}
      <div className="p-4 sm:p-5 border-b border-slate-100 bg-gradient-to-r from-blue-50 via-indigo-50/50 to-white flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-blue-600 text-white flex items-center justify-center shadow-xs">
            <HelpCircle className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-extrabold text-slate-900 flex items-center space-x-2">
              <span>{lang === 'hi' ? 'रनर सहायता एवं अक्सर पूछे जाने वाले प्रश्न' : 'Runner Operations & FAQ'}</span>
              <span className="text-[10px] font-bold text-blue-700 bg-blue-100/70 px-2 py-0.5 rounded-full flex items-center gap-1">
                <Sparkles className="w-3 h-3" />
                5 Points
              </span>
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              {lang === 'hi'
                ? 'जियोफेंसिंग, सीओडी नकद समाधान और शुक्रवार भुगतान से जुड़े नियम'
                : 'Key guidelines on cluster delivery, COD deposits, and weekly payouts'}
            </p>
          </div>
        </div>
      </div>

      {/* Accordion List */}
      <div className="divide-y divide-slate-100">
        {runnerFaqs.map((faq) => {
          const isOpen = openId === faq.id;
          const IconComponent = faq.icon;
          return (
            <div
              key={faq.id}
              className={`transition-colors ${faq.highlight ? 'bg-blue-50/40' : 'hover:bg-slate-50/60'}`}
            >
              <button
                type="button"
                onClick={() => toggle(faq.id)}
                className="w-full p-4 sm:p-4.5 text-left flex items-start justify-between gap-3 focus:outline-none"
              >
                <div className="flex items-start space-x-3">
                  <div
                    className={`w-7 h-7 rounded-lg shrink-0 flex items-center justify-center mt-0.5 ${
                      faq.highlight
                        ? 'bg-blue-600 text-white shadow-xs'
                        : 'bg-slate-100 text-slate-600'
                    }`}
                  >
                    <IconComponent className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="text-[11px] font-mono font-bold text-slate-400">#{faq.id}</span>
                      <h4 className="text-xs sm:text-sm font-bold text-slate-900">
                        {lang === 'hi' ? faq.qHi : faq.qEn}
                      </h4>
                    </div>
                    {faq.highlight && (
                      <span className="inline-block mt-1 text-[10px] font-extrabold text-blue-800 bg-blue-100 px-2 py-0.2 rounded">
                        {lang === 'hi' ? 'ऑनलाइन भुगतान स्पष्टीकरण' : 'Online Payout Explanation'}
                      </span>
                    )}
                  </div>
                </div>

                <div
                  className={`w-6 h-6 rounded-full flex items-center justify-center shrink-0 transition-transform duration-200 ${
                    isOpen ? 'rotate-180 bg-slate-200/80' : 'bg-slate-100'
                  }`}
                >
                  <ChevronDown className="w-3.5 h-3.5 text-slate-600" />
                </div>
              </button>

              {isOpen && (
                <div className="px-4 pb-4 sm:px-14 sm:pb-4.5 text-xs text-slate-700 leading-relaxed animate-in fade-in duration-150">
                  <div className="p-3 rounded-xl bg-white border border-slate-200 shadow-2xs">
                    <p>{lang === 'hi' ? faq.aHi : faq.aEn}</p>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default RunnerFaq;
