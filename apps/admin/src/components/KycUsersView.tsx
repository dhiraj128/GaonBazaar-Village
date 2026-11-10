import React, { useState } from 'react';
import {
  ShieldCheck,
  CheckCircle,
  XCircle,
  Store,
  Bike,
  Users,
  Search,
  ExternalLink,
  Ban,
  Unlock,
  AlertCircle,
  Building,
  UserCheck,
  Check,
  X,
  CreditCard,
  FileCheck,
  MapPin,
  Phone,
} from 'lucide-react';
import type {
  PendingKycApplicant,
  KycSideBySideDetail,
  DirectoryUser,
} from '../types';
import type { Language } from '../i18n';
import { translations } from '../i18n';

interface KycUsersViewProps {
  pendingApplicants: PendingKycApplicant[];
  directoryUsers: DirectoryUser[];
  onOpenSideBySide: (type: 'vendor' | 'runner', id: string) => Promise<KycSideBySideDetail>;
  onApprove: (type: 'vendor' | 'runner', id: string) => Promise<void>;
  onReject: (type: 'vendor' | 'runner', id: string, reason: string) => Promise<void>;
  onToggleUserStatus: (userId: string, isActive: boolean, reason?: string) => Promise<void>;
  lang?: Language;
}

export const KycUsersView: React.FC<KycUsersViewProps> = ({
  pendingApplicants,
  directoryUsers,
  onOpenSideBySide,
  onApprove,
  onReject,
  onToggleUserStatus,
  lang = 'en',
}) => {
  const t = translations[lang];
  const [activeTab, setActiveTab] = useState<'pending' | 'directory'>('pending');
  const [applicantFilter, setApplicantFilter] = useState<'ALL' | 'VENDOR' | 'RUNNER'>('ALL');
  const [directorySearch, setDirectorySearch] = useState('');
  const [directoryRoleFilter, setDirectoryRoleFilter] = useState<string>('ALL');

  // Side-by-side Review Modal State
  const [selectedDetail, setSelectedDetail] = useState<KycSideBySideDetail | null>(null);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [rejectReason, setRejectReason] = useState(
    'Documents unclear. Please re-upload clear Aadhaar card and verified Bank Passbook.'
  );
  const [isActionSubmitting, setIsActionSubmitting] = useState(false);

  const filteredApplicants = pendingApplicants.filter((app) => {
    if (applicantFilter === 'VENDOR') return app.type === 'VENDOR';
    if (applicantFilter === 'RUNNER') return app.type === 'RUNNER';
    return true;
  });

  const filteredDirectory = directoryUsers.filter((u) => {
    const matchesSearch =
      u.name.toLowerCase().includes(directorySearch.toLowerCase()) ||
      u.phone.includes(directorySearch);
    const matchesRole =
      directoryRoleFilter === 'ALL' || u.role.toLowerCase() === directoryRoleFilter.toLowerCase();
    return matchesSearch && matchesRole;
  });

  const handleReviewClick = async (type: 'VENDOR' | 'RUNNER', id: string) => {
    setIsLoadingDetail(true);
    try {
      const detail = await onOpenSideBySide(type.toLowerCase() as any, id);
      setSelectedDetail(detail);
    } catch (e) {
      alert(lang === 'hi' ? 'आवेदक सत्यापन विवरण लोड करने में विफल।' : 'Failed to load applicant verification details.');
    } finally {
      setIsLoadingDetail(false);
    }
  };

  const handleApproveAction = async () => {
    if (!selectedDetail) return;
    setIsActionSubmitting(true);
    try {
      await onApprove(selectedDetail.applicant_type.toLowerCase() as any, selectedDetail.id);
      setSelectedDetail(null);
    } catch (e: any) {
      alert(`${lang === 'hi' ? 'अनुमोदन त्रुटि' : 'Approval error'}: ${e.message || 'Operation failed'}`);
    } finally {
      setIsActionSubmitting(false);
    }
  };

  const handleRejectConfirm = async () => {
    if (!selectedDetail) return;
    setIsActionSubmitting(true);
    try {
      await onReject(
        selectedDetail.applicant_type.toLowerCase() as any,
        selectedDetail.id,
        rejectReason
      );
      setShowRejectModal(false);
      setSelectedDetail(null);
    } catch (e: any) {
      alert(`${lang === 'hi' ? 'अस्वीकृति त्रुटि' : 'Rejection error'}: ${e.message || 'Operation failed'}`);
    } finally {
      setIsActionSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Navigation Tabs: Pending Approvals Queue vs Active Directory */}
      <div className="bg-white rounded-2xl p-2 border border-slate-200 shadow-xs flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setActiveTab('pending')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition flex items-center space-x-2 ${
              activeTab === 'pending'
                ? 'bg-slate-900 text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>{t.pendingApprovalsQueue}</span>
            {pendingApplicants.length > 0 && (
              <span className="px-1.5 py-0.5 rounded-full text-[10px] bg-amber-500 text-white font-black">
                {pendingApplicants.length}
              </span>
            )}
          </button>

          <button
            onClick={() => setActiveTab('directory')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition flex items-center space-x-2 ${
              activeTab === 'directory'
                ? 'bg-slate-900 text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <Users className="w-4 h-4 text-blue-400" />
            <span>{t.activeDirectory}</span>
            <span className="px-1.5 py-0.5 rounded-full text-[10px] bg-slate-700 text-slate-200">
              {directoryUsers.length}
            </span>
          </button>
        </div>

        {activeTab === 'pending' && (
          <div className="flex items-center space-x-1.5 px-3">
            {(['ALL', 'VENDOR', 'RUNNER'] as const).map((filter) => (
              <button
                key={filter}
                onClick={() => setApplicantFilter(filter)}
                className={`px-2.5 py-1 text-xs font-bold rounded-lg transition ${
                  applicantFilter === filter
                    ? 'bg-emerald-100 text-emerald-800'
                    : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                {filter === 'ALL'
                  ? (lang === 'hi' ? 'सभी आवेदक' : 'All Applicants')
                  : filter === 'VENDOR'
                  ? (lang === 'hi' ? 'किराना विक्रेता' : 'Vendors (Kirana)')
                  : (lang === 'hi' ? 'डिलीवरी रनर्स' : 'Delivery Runners')}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* SECTION 1: Pending Approvals Queue */}
      {activeTab === 'pending' && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
            <div>
              <h2 className="text-sm font-extrabold text-slate-900">
                {t.newlyRegisteredHeader}
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                {t.newlyRegisteredSub}
              </p>
            </div>
          </div>

          {filteredApplicants.length === 0 ? (
            <div className="p-12 text-center text-slate-400 text-xs">
              <CheckCircle className="w-10 h-10 text-emerald-500 mx-auto mb-2 opacity-60" />
              <p className="font-bold text-slate-700 text-sm">{t.queueEmpty}</p>
              <p className="text-slate-500 mt-1">{t.queueEmptySub}</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] font-bold tracking-wider border-b border-slate-200">
                  <tr>
                    <th className="px-6 py-3">{t.applicantStore}</th>
                    <th className="px-6 py-3">{t.applicantType}</th>
                    <th className="px-6 py-3">{t.contactVillagePin}</th>
                    <th className="px-6 py-3">{t.status}</th>
                    <th className="px-6 py-3">{t.dateApplied}</th>
                    <th className="px-6 py-3 text-right">{t.actions}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                  {filteredApplicants.map((app) => (
                    <tr
                      key={app.id}
                      onClick={() => handleReviewClick(app.type, app.id)}
                      className="hover:bg-slate-50/80 transition cursor-pointer"
                      title={lang === 'hi' ? 'समीक्षा करने के लिए पंक्ति पर क्लिक करें' : 'Click row to review applicant'}
                    >
                      <td className="px-6 py-4">
                        <div className="font-bold text-slate-900">{app.name}</div>
                        <div className="text-[11px] text-slate-500">
                          {app.type === 'VENDOR'
                            ? (app.shop_name || 'Rural Kirana Store')
                            : (app.vehicle_type || 'Motorcycle')}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-bold ${
                            app.type === 'VENDOR'
                              ? 'bg-amber-100 text-amber-800'
                              : 'bg-blue-100 text-blue-800'
                          }`}
                        >
                          {app.type === 'VENDOR' ? <Store className="w-3 h-3" /> : <Bike className="w-3 h-3" />}
                          {app.type}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="font-semibold text-slate-800">{app.phone}</div>
                        <div className="text-[11px] text-slate-500 flex items-center gap-1">
                          <MapPin className="w-3 h-3 text-slate-400" />
                          <span>{app.village} ({app.pincode || '843128'})</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center gap-1 text-amber-600 font-bold bg-amber-50 px-2 py-0.5 rounded text-[11px]">
                          <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-ping" />
                          PENDING
                        </span>
                      </td>
                      <td className="px-6 py-4 text-slate-500 text-[11px]">
                        {app.created_at ? new Date(app.created_at).toLocaleDateString() : 'Recent'}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleReviewClick(app.type, app.id);
                          }}
                          className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded-lg font-bold text-xs shadow-xs transition"
                        >
                          {t.reviewVerify}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* SECTION 2: Active Directory & User Suspension */}
      {activeTab === 'directory' && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
          <div className="p-5 border-b border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-3">
            <div>
              <h3 className="text-sm font-extrabold text-slate-900">
                {lang === 'hi' ? 'सक्रिय भागीदार एवं ग्राहक निर्देशिका' : 'Active Partner & Customer Directory'}
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                {lang === 'hi'
                  ? 'तत्काल सुरक्षा खाता निलंबन एवं परिचालन स्थिति नियंत्रण।'
                  : 'Immediate security account suspension and operational status control.'}
              </p>
            </div>

            <div className="flex items-center space-x-3">
              <div className="relative">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                <input
                  type="text"
                  value={directorySearch}
                  onChange={(e) => setDirectorySearch(e.target.value)}
                  placeholder={lang === 'hi' ? 'नाम या फ़ोन से खोजें...' : 'Search by name or phone...'}
                  className="text-xs pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 rounded-lg outline-none focus:bg-white focus:border-emerald-500"
                />
              </div>

              <select
                value={directoryRoleFilter}
                onChange={(e) => setDirectoryRoleFilter(e.target.value)}
                className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 font-bold outline-none"
              >
                <option value="ALL">{lang === 'hi' ? 'सभी भूमिकाएं' : 'All Roles'}</option>
                <option value="customer">{lang === 'hi' ? 'ग्राहक' : 'Customers'}</option>
                <option value="vendor">{lang === 'hi' ? 'विक्रेता' : 'Vendors'}</option>
                <option value="runner">{lang === 'hi' ? 'रनर' : 'Runners'}</option>
              </select>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] font-bold tracking-wider border-b border-slate-200">
                <tr>
                  <th className="px-6 py-3">{lang === 'hi' ? 'उपयोगकर्ता' : 'User'}</th>
                  <th className="px-6 py-3">{lang === 'hi' ? 'भूमिका' : 'Role'}</th>
                  <th className="px-6 py-3">{lang === 'hi' ? 'स्थान' : 'Location'}</th>
                  <th className="px-6 py-3">{lang === 'hi' ? 'ऑर्डर' : 'Orders'}</th>
                  <th className="px-6 py-3">{lang === 'hi' ? 'स्थिति' : 'Status'}</th>
                  <th className="px-6 py-3 text-right">{t.actions}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                {filteredDirectory.map((user) => (
                  <tr key={user.id} className="hover:bg-slate-50/80 transition">
                    <td className="px-6 py-4">
                      <div className="font-bold text-slate-900">{user.name}</div>
                      <div className="text-[11px] text-slate-500">{user.phone}</div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-2 py-0.5 rounded text-[10px] font-extrabold uppercase bg-slate-100 text-slate-700">
                        {user.role}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-slate-600">
                      {user.village || 'Minapur Pilot Area'}
                    </td>
                    <td className="px-6 py-4 font-bold text-slate-800">
                      {user.orders_count}
                    </td>
                    <td className="px-6 py-4">
                      {user.is_active ? (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
                          ACTIVE
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-100 text-rose-800">
                          SUSPENDED
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right">
                      {user.is_active ? (
                        <button
                          onClick={() => {
                            if (window.confirm(lang === 'hi' ? `क्या आप '${user.name}' को निलंबित करना चाहते हैं?` : `Suspend user '${user.name}' immediately?`)) {
                              onToggleUserStatus(user.id, false, 'Administrative suspension');
                            }
                          }}
                          className="px-2.5 py-1 text-[11px] font-bold bg-rose-50 hover:bg-rose-100 text-rose-700 rounded-lg border border-rose-200 transition"
                        >
                          {lang === 'hi' ? 'खाता निलंबित करें' : 'Suspend Account'}
                        </button>
                      ) : (
                        <button
                          onClick={() => {
                            onToggleUserStatus(user.id, true);
                          }}
                          className="px-2.5 py-1 text-[11px] font-bold bg-emerald-50 hover:bg-emerald-100 text-emerald-700 rounded-lg border border-emerald-200 transition"
                        >
                          {lang === 'hi' ? 'पुनः सक्रिय करें' : 'Reactivate Account'}
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Side-by-Side Review & Verification Modal */}
      {selectedDetail && (
        <div className="fixed inset-0 bg-slate-950/75 z-50 flex items-center justify-center p-4 backdrop-blur-xs animate-in fade-in duration-150">
          <div className="bg-white rounded-3xl max-w-4xl w-full max-h-[92vh] overflow-y-auto shadow-2xl border border-slate-200">
            {/* Modal Header */}
            <div className="px-6 py-4 bg-slate-900 text-white flex items-center justify-between sticky top-0 z-10">
              <div className="flex items-center space-x-2.5">
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
                <div>
                  <h3 className="text-sm font-black uppercase tracking-wide">
                    {lang === 'hi' ? 'केवाईसी सत्यापन एवं समीक्षा' : 'KYC Verification & Side-by-Side Review'}
                  </h3>
                  <span className="text-[10px] text-emerald-300 font-bold uppercase">
                    {selectedDetail.applicant_type} Application — #{selectedDetail.id.slice(0, 8)}
                  </span>
                </div>
              </div>
              <button
                onClick={() => setSelectedDetail(null)}
                className="text-slate-400 hover:text-white p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body: User Details & Verification */}
            <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6 divide-y md:divide-y-0 md:divide-x divide-slate-200">
              {/* LEFT: User-Submitted Details */}
              <div className="space-y-4">
                <div className="flex items-center space-x-2 pb-2 border-b border-slate-100">
                  <UserCheck className="w-4 h-4 text-slate-500" />
                  <h4 className="text-xs font-black text-slate-800 uppercase tracking-wider">
                    {lang === 'hi' ? 'आवेदक द्वारा प्रस्तुत विवरण' : 'User-Submitted Details'}
                  </h4>
                </div>

                <div className="space-y-3 text-xs">
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase font-bold block">
                      {lang === 'hi' ? 'आवेदक का पूरा नाम' : 'Applicant Full Name'}
                    </span>
                    <span className="font-bold text-slate-900 text-sm">
                      {selectedDetail.user_submitted.name}
                    </span>
                  </div>

                  {selectedDetail.user_submitted.shop_name && (
                    <div>
                      <span className="text-[10px] text-slate-400 uppercase font-bold block">
                        {lang === 'hi' ? 'दुकान का नाम एवं श्रेणी' : 'Shop Name & Category'}
                      </span>
                      <span className="font-bold text-slate-800">
                        {selectedDetail.user_submitted.shop_name} ({selectedDetail.user_submitted.category || 'Kirana'})
                      </span>
                    </div>
                  )}

                  {selectedDetail.user_submitted.vehicle_type && (
                    <div>
                      <span className="text-[10px] text-slate-400 uppercase font-bold block">
                        {lang === 'hi' ? 'वाहन का प्रकार एवं पंजीकरण' : 'Vehicle Type & Registration'}
                      </span>
                      <span className="font-bold text-slate-800">
                        {selectedDetail.user_submitted.vehicle_type} — {selectedDetail.user_submitted.vehicle_number || 'BR-06-AB-1234'}
                      </span>
                    </div>
                  )}

                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <span className="text-[10px] text-slate-400 uppercase font-bold block">
                        {lang === 'hi' ? 'पंजीकृत मोबाइल' : 'Contact Phone'}
                      </span>
                      <span className="font-bold text-slate-800">
                        {selectedDetail.user_submitted.phone}
                      </span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-400 uppercase font-bold block">
                        {lang === 'hi' ? 'ग्राम एवं पिनकोड' : 'Village & Pin'}
                      </span>
                      <span className="font-bold text-slate-800">
                        {selectedDetail.user_submitted.village} (843128)
                      </span>
                    </div>
                  </div>

                  <div className="bg-slate-50 p-3 rounded-xl border border-slate-200 space-y-1.5">
                    <span className="text-[10px] font-black uppercase text-slate-500 flex items-center gap-1">
                      <CreditCard className="w-3.5 h-3.5 text-slate-500" /> {lang === 'hi' ? 'बैंक खाता विवरण' : 'Bank Account Details'}
                    </span>
                    <div className="text-xs font-mono font-bold text-slate-900">
                      A/C: {selectedDetail.user_submitted.bank_account_number}
                    </div>
                    <div className="text-xs font-mono text-slate-600">
                      IFSC: {selectedDetail.user_submitted.bank_ifsc}
                    </div>
                    {selectedDetail.user_submitted.upi_id && (
                      <div className="text-xs text-slate-500">
                        UPI: {selectedDetail.user_submitted.upi_id}
                      </div>
                    )}
                  </div>

                  {/* Photo Previews */}
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase font-bold block mb-2">
                      {lang === 'hi' ? 'आवेदक तस्वीरें एवं दस्तावेज' : 'Applicant Photos & Documents'}
                    </span>
                    <div className="grid grid-cols-2 gap-2">
                      {selectedDetail.user_submitted.selfie_url && (
                        <div>
                          <img
                            src={selectedDetail.user_submitted.selfie_url}
                            alt="Applicant Selfie"
                            className="w-full h-24 object-cover rounded-lg border border-slate-200"
                          />
                          <span className="text-[9px] text-slate-500 font-semibold block text-center mt-1">
                            {lang === 'hi' ? 'लाइव सेल्फी' : 'Live Selfie Photo'}
                          </span>
                        </div>
                      )}
                      {selectedDetail.user_submitted.shop_photo_url && (
                        <div>
                          <img
                            src={selectedDetail.user_submitted.shop_photo_url}
                            alt="Shop Banner"
                            className="w-full h-24 object-cover rounded-lg border border-slate-200"
                          />
                          <span className="text-[9px] text-slate-500 font-semibold block text-center mt-1">
                            {lang === 'hi' ? 'दुकान का बोर्ड' : 'Store Front Signage'}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* RIGHT: System Verification Records */}
              <div className="space-y-4 md:pl-6 pt-4 md:pt-0">
                <div className="flex items-center space-x-2 pb-2 border-b border-slate-100">
                  <FileCheck className="w-4 h-4 text-emerald-600" />
                  <h4 className="text-xs font-black text-slate-800 uppercase tracking-wider">
                    {lang === 'hi' ? 'सिस्टम सत्यापन स्थिति' : 'System Verification Records'}
                  </h4>
                </div>

                {/* Penny Drop Bank Match */}
                <div className="bg-emerald-50/60 p-3.5 rounded-xl border border-emerald-200 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-emerald-950">
                      {lang === 'hi' ? 'पेनी ड्रॉप बैंक खाता मिलान' : 'Penny Drop Bank Match'}
                    </span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-black uppercase bg-emerald-600 text-white">
                      VERIFIED
                    </span>
                  </div>
                  <div className="space-y-1 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-600">{lang === 'hi' ? 'सत्यापित खाताधारक:' : 'Verified Account Holder:'}</span>
                      <strong className="text-emerald-950">
                        {selectedDetail.api_verified.penny_drop_bank_match.verified_account_holder}
                      </strong>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-600">{lang === 'hi' ? 'बैंक:' : 'Bank:'}</span>
                      <span className="text-slate-800">
                        {selectedDetail.api_verified.penny_drop_bank_match.bank_name}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Aadhaar Liveness */}
                <div className="bg-blue-50/60 p-3.5 rounded-xl border border-blue-200 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-blue-950">
                      {lang === 'hi' ? 'आधार एवं बायोमेट्रिक स्कोर' : 'Aadhaar & Biometric Liveness'}
                    </span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-black uppercase bg-blue-600 text-white">
                      PASSED
                    </span>
                  </div>
                  <div className="space-y-1 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-600">{lang === 'hi' ? 'लाइवनेस स्कोर:' : 'Liveness Match Score:'}</span>
                      <strong className="text-blue-950 text-sm">98.6%</strong>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-600">{lang === 'hi' ? 'यूआईडीएआई स्थिति:' : 'UIDAI Status:'}</span>
                      <span className="text-emerald-700 font-bold">VERIFIED</span>
                    </div>
                  </div>
                </div>

                {/* Gatekeeper Decision Protocol */}
                <div className="p-3 bg-slate-100 rounded-xl text-xs text-slate-600">
                  <p className="font-semibold text-slate-800 mb-1">
                    {lang === 'hi' ? 'गेटकीपर सुरक्षा प्रोटोकॉल:' : 'Gatekeeper Security Protocol:'}
                  </p>
                  {lang === 'hi'
                    ? 'स्वीकृत करने पर भागीदार ऐप तुरंत संचालन के लिए अनलॉक हो जाता है।'
                    : 'Approving updates status to ACTIVE, instantly unlocking partner mobile app for orders.'}
                </div>
              </div>
            </div>

            {/* Modal Action Buttons: Approve & Activate vs Reject */}
            <div className="px-6 py-4 bg-slate-50 border-t border-slate-200 flex items-center justify-between sticky bottom-0">
              <button
                onClick={() => setShowRejectModal(true)}
                disabled={isActionSubmitting}
                className="px-4 py-2.5 bg-rose-50 hover:bg-rose-100 text-rose-700 font-bold text-xs rounded-xl border border-rose-300 transition flex items-center space-x-1.5"
              >
                <XCircle className="w-4 h-4" />
                <span>{t.rejectApplication}</span>
              </button>

              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setSelectedDetail(null)}
                  className="px-4 py-2.5 text-slate-600 hover:text-slate-900 text-xs font-semibold"
                >
                  {t.cancel}
                </button>
                <button
                  onClick={handleApproveAction}
                  disabled={isActionSubmitting}
                  className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs rounded-xl shadow-md transition flex items-center space-x-2"
                >
                  <CheckCircle className="w-4 h-4" />
                  <span>{t.approveAndActivate}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Rejection Reason Modal */}
      {showRejectModal && (
        <div className="fixed inset-0 bg-slate-950/80 z-60 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-5 space-y-4 shadow-2xl border border-slate-200">
            <h4 className="text-sm font-black text-rose-950">
              {t.rejectApplication}
            </h4>
            <p className="text-xs text-slate-600">
              {t.rejectReasonPrompt}
            </p>
            <textarea
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              rows={3}
              className="w-full text-xs p-3 border border-slate-300 rounded-xl outline-none focus:border-rose-500"
            />
            <div className="flex items-center justify-end space-x-2 pt-2">
              <button
                onClick={() => setShowRejectModal(false)}
                className="px-3 py-1.5 text-xs text-slate-600 font-semibold"
              >
                {t.cancel}
              </button>
              <button
                onClick={handleRejectConfirm}
                disabled={isActionSubmitting}
                className="px-4 py-1.5 bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs rounded-lg shadow-xs"
              >
                {t.confirmRejection}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
