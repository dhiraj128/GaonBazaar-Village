import React, { useState } from 'react';
import {
  HelpCircle,
  Package,
  Layers,
  AlertCircle,
  CalendarCheck,
  CreditCard,
  ChevronDown,
  Sparkles,
} from 'lucide-react';

interface VendorFaqProps {
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

const vendorFaqs: FaqItem[] = [
  {
    id: 1,
    icon: Layers,
    qEn: 'How do I update shop inventory & daily stocks?',
    qHi: 'दुकान इन्वेंटरी और दैनिक स्टॉक को कैसे अपडेट करें?',
    aEn: 'Regularly update your item availability and quantities in the "Inventory" tab. When fresh dairy, produce, or packaged groceries arrive each morning, toggle them "IN STOCK" so village customers can place instant orders.',
    aHi: 'अपनी "इन्वेंटरी" टैब में वस्तुओं की उपलब्धता और मात्रा को नियमित रूप से अपडेट करें। जब हर सुबह ताजा डेयरी, सब्जियां या किराने का सामान आए, तो उन्हें "IN STOCK" चालू करें ताकि ग्रामीण ग्राहक तुरंत ऑर्डर दे सकें।',
  },
  {
    id: 2,
    icon: Package,
    qEn: 'What are the packaging guidelines for safe rural transit?',
    qHi: 'ग्रामीण रास्तों पर सुरक्षित डिलीवरी के लिए पैकेजिंग निर्देश क्या हैं?',
    aEn: 'Always double-bag liquid items like milk pouches, mustard oil bottles, and ghee jars. Use sturdy paper or cloth bags for heavy grains, pulses, and flours to avoid tearing or spillage over unpaved village roads.',
    aHi: 'दूध के पैकेट, सरसों के तेल की बोतलें और घी के डिब्बे जैसी तरल वस्तुओं को हमेशा डबल बैग में पैक करें। पक्की/कच्ची ग्रामीण सड़कों पर फटने या गिरने से बचाने के लिए भारी दालों और आटे के लिए मजबूत बैग का उपयोग करें।',
  },
  {
    id: 3,
    icon: AlertCircle,
    qEn: 'How should I manage out-of-stock items during rush hours?',
    qHi: 'पीक आवर्स में आउट-ऑफ-स्टॉक सामान को कैसे प्रबंधित करें?',
    aEn: 'If any product sells out in your physical shop, immediately toggle its switch to "OUT OF STOCK" in the Dukaan app. This prevents unfulfillable customer orders, avoids cancellation penalties, and protects your merchant rating.',
    aHi: 'यदि आपकी भौतिक दुकान में कोई उत्पाद समाप्त हो जाता है, तो तुरंत दुकान ऐप में उसका स्विच "OUT OF STOCK" कर दें। इससे ग्राहक ऑर्डर रद्द होने से बचते हैं और आपकी विक्रेता रेटिंग सुरक्षित रहती है।',
  },
  {
    id: 4,
    icon: CalendarCheck,
    qEn: 'What is the weekly bank settlement schedule?',
    qHi: 'साप्ताहिक बैंक सेटलमेंट की समय सारिणी क्या है?',
    aEn: 'All completed order earnings are automatically processed and transferred directly to your Penny Drop verified bank account every Tuesday and Friday night through automated NEFT/IMPS clearinghouse with zero platform commission.',
    aHi: 'सभी पूर्ण किए गए ऑर्डरों की कमाई प्रत्येक मंगलवार और शुक्रवार की रात स्वचालित एनईएफटी/आईएमपीएस के माध्यम से सीधे आपके पेनी ड्रॉप सत्यापित बैंक खाते में बिना किसी प्लेटफ़ॉर्म कमीशन के स्थानांतरित की जाती है।',
  },
  {
    id: 5,
    icon: CreditCard,
    qEn: 'Why is my earning slightly less on online orders?',
    qHi: 'ऑनलाइन ऑर्डर पर मेरी कमाई थोड़ी कम क्यों है?',
    aEn: 'For online payments, backend processors like Razorpay deduct a standard percentage fee to process and transfer the money to your bank account. Cash on Delivery (COD) orders do not have this online fee, so you get the full amount.',
    aHi: 'ऑनलाइन भुगतान के लिए, रेज़रपे (Razorpay) जैसे बैकएंड प्रोसेसर आपके बैंक खाते में पैसे को प्रोसेस और ट्रांसफर करने के लिए एक मानक प्रतिशत शुल्क काटते हैं। कैश ऑन डिलीवरी (COD) ऑर्डरों पर यह ऑनलाइन शुल्क नहीं होता है, इसलिए आपको पूरी राशि मिलती है।',
    highlight: true,
  },
];

export const VendorFaq: React.FC<VendorFaqProps> = ({ lang = 'en' }) => {
  const [openId, setOpenId] = useState<number | null>(5); // Open point 5 by default for clarity

  const toggle = (id: number) => {
    setOpenId((prev) => (prev === id ? null : id));
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
      {/* Header */}
      <div className="p-4 sm:p-5 border-b border-slate-100 bg-gradient-to-r from-emerald-50 via-teal-50/50 to-white flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-emerald-600 text-white flex items-center justify-center shadow-xs">
            <HelpCircle className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-extrabold text-slate-900 flex items-center space-x-2">
              <span>{lang === 'hi' ? 'दुकानदार सहायता एवं अक्सर पूछे जाने वाले प्रश्न' : 'Merchant Operations & FAQ'}</span>
              <span className="text-[10px] font-bold text-emerald-700 bg-emerald-100/70 px-2 py-0.5 rounded-full flex items-center gap-1">
                <Sparkles className="w-3 h-3" />
                5 Points
              </span>
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              {lang === 'hi'
                ? 'स्टॉक प्रबंधन, सुरक्षित पैकेजिंग और साप्ताहिक भुगतान से जुड़े महत्वपूर्ण नियम'
                : 'Key guidelines on inventory, rural packaging, and payment settlements'}
            </p>
          </div>
        </div>
      </div>

      {/* Accordion List */}
      <div className="divide-y divide-slate-100">
        {vendorFaqs.map((faq) => {
          const isOpen = openId === faq.id;
          const IconComponent = faq.icon;
          return (
            <div
              key={faq.id}
              className={`transition-colors ${faq.highlight ? 'bg-emerald-50/40' : 'hover:bg-slate-50/60'}`}
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
                        ? 'bg-emerald-600 text-white shadow-xs'
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
                      <span className="inline-block mt-1 text-[10px] font-extrabold text-emerald-800 bg-emerald-100 px-2 py-0.2 rounded">
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

export default VendorFaq;
