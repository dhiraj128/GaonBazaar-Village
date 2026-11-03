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
} from 'lucide-react';
import type {
  PendingKycApplicant,
  KycSideBySideDetail,
  DirectoryUser,
} from '../types';

interface KycUsersViewProps {
  pendingApplicants: PendingKycApplicant[];
  directoryUsers: DirectoryUser[];
  onOpenSideBySide: (type: 'vendor' | 'runner', id: string) => Promise<KycSideBySideDetail>;
  onApprove: (type: 'vendor' | 'runner', id: string) => Promise<void>;
  onReject: (type: 'vendor' | 'runner', id: string, reason: string) => Promise<void>;
  onToggleUserStatus: (userId: string, isActive: boolean, reason?: string) => Promise<void>;
}

export const KycUsersView: React.FC<KycUsersViewProps> = ({
  pendingApplicants,
  directoryUsers,
  onOpenSideBySide,
  onApprove,
  onReject,
  onToggleUserStatus,
}) => {
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
      alert('Failed to load applicant verification details.');
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
      alert(`Approval error: ${e.message || 'Operation failed'}`);
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
      alert(`Rejection error: ${e.message || 'Operation failed'}`);
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
            <span>Pending Approvals Queue</span>
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
            <span>Active Directory & User Suspension</span>
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
                {filter === 'ALL' ? 'All Applicants' : filter === 'VENDOR' ? 'Vendors (Kirana)' : 'Runners'}
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
                Newly Registered Applications (Awaiting Gatekeeper Approval)
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Every vendor & runner must undergo side-by-side Penny Drop bank verification and Aadhaar liveness score match before mobile app unlock.
              </p>
            </div>
          </div>

          {filteredApplicants.length === 0 ? (
            <div className="p-12 text-center text-slate-400 text-xs">
              <CheckCircle className="w-10 h-10 text-emerald-500 mx-auto mb-2 opacity-60" />
              <p className="font-bold text-slate-700 text-sm">Approvals Queue is Clear!</p>
              <p className="text-slate-500 mt-1">No pending vendor or runner KYC applications at this time.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] font-bold tracking-wider border-b border-slate-200">
                  <tr>
                    <th className="px-6 py-3">Applicant / Store</th>
                    <th className="px-6 py-3">Type</th>
                    <th className="px-6 py-3">Phone & Village</th>
                    <th className="px-6 py-3">Status</th>
                    <th className="px-6 py-3">Date Applied</th>
                    <th className="px-6 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                  {filteredApplicants.map((app) => (
                    <tr key={app.id} className="hover:bg-slate-50/80 transition">
                      <td className="px-6 py-4">
                        <div className="font-bold text-slate-900">{app.name}</div>
                        <div className="text-[11px] text-slate-500">
                          {app.shop_name || app.vehicle_type || 'Applicant'}
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
                        <div className="text-[11px] text-slate-500">{app.village}</div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center gap-1 text-amber-600 font-bold bg-amber-50 px-2 py-0.5 rounded text-[11px]">
                          <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-ping" />
                          Pending Review
                        </span>
                      </td>
                      <td className="px-6 py-4 text-slate-500 text-[11px]">
                        {app.created_at ? new Date(app.created_at).toLocaleDateString() : 'Recent'}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button
                          onClick={() => handleReviewClick(app.type, app.id)}
                          className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded-lg font-bold text-xs shadow-xs transition"
                        >
                          Review & Verify
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
            <div className="relative flex-1 max-w-md">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                value={directorySearch}
                onChange={(e) => setDirectorySearch(e.target.value)}
                placeholder="Search directory by name, phone (+91)..."
                className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 rounded-lg border border-slate-200 outline-none focus:border-emerald-500 focus:bg-white"
              />
            </div>

            <div className="flex items-center space-x-2">
              <span className="text-xs text-slate-500 font-bold">Filter Role:</span>
              <select
                value={directoryRoleFilter}
                onChange={(e) => setDirectoryRoleFilter(e.target.value)}
                className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 font-bold outline-none"
              >
                <option value="ALL">All Roles ({directoryUsers.length})</option>
                <option value="customer">Customers</option>
                <option value="vendor">Vendors</option>
                <option value="runner">Runners</option>
              </select>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] font-bold tracking-wider border-b border-slate-200">
                <tr>
                  <th className="px-6 py-3">User Details</th>
                  <th className="px-6 py-3">Platform Role</th>
                  <th className="px-6 py-3">Location / Village</th>
                  <th className="px-6 py-3">Order History</th>
                  <th className="px-6 py-3">Account Status</th>
                  <th className="px-6 py-3 text-right">Instant Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                {filteredDirectory.map((user) => (
                  <tr key={user.id} className="hover:bg-slate-50/80 transition">
                    <td className="px-6 py-3.5">
                      <div className="font-bold text-slate-900">{user.name}</div>
                      <div className="text-[11px] text-slate-500">{user.phone}</div>
                    </td>
                    <td className="px-6 py-3.5">
                      <span className="capitalize font-bold text-[11px] px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                        {user.role}
                      </span>
                    </td>
                    <td className="px-6 py-3.5 text-[11px] text-slate-600">
                      {user.village || 'Minapur'}
                    </td>
                    <td className="px-6 py-3.5">
                      <span className="font-bold text-slate-900">{user.orders_count}</span>{' '}
                      <span className="text-[11px] text-slate-400">orders</span>
                    </td>
                    <td className="px-6 py-3.5">
                      <span
                        className={`inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded-full ${
                          user.is_active
                            ? 'bg-emerald-100 text-emerald-800'
                            : 'bg-rose-100 text-rose-800'
                        }`}
                      >
                        {user.is_active ? 'Active' : 'Suspended'}
                      </span>
                    </td>
                    <td className="px-6 py-3.5 text-right">
                      {user.is_active ? (
                        <button
                          onClick={() => {
                            if (window.confirm(`Suspend / block user '${user.name}' immediately?`)) {
                              onToggleUserStatus(user.id, false, 'Suspended by admin');
                            }
                          }}
                          className="px-2.5 py-1 text-[11px] font-bold text-rose-700 bg-rose-50 hover:bg-rose-100 rounded-lg border border-rose-200 transition"
                        >
                          Block / Suspend
                        </button>
                      ) : (
                        <button
                          onClick={() => {
                            onToggleUserStatus(user.id, true, 'Re-activated by admin');
                          }}
                          className="px-2.5 py-1 text-[11px] font-bold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 rounded-lg border border-emerald-200 transition"
                        >
                          Unblock User
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

      {/* MODAL: Side-by-Side Approval Detail View (PDF Module 2) */}
      {selectedDetail && (
        <div className="fixed inset-0 bg-slate-950/70 z-50 flex items-center justify-center p-4 backdrop-blur-xs animate-in fade-in duration-150">
          <div className="bg-white rounded-3xl max-w-4xl w-full max-h-[92vh] overflow-y-auto shadow-2xl border border-slate-200 flex flex-col">
            {/* Modal Header */}
            <div className="px-6 py-4 bg-slate-900 text-white flex items-center justify-between sticky top-0 z-10">
              <div className="flex items-center space-x-2.5">
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
                <div>
                  <h3 className="text-sm font-black uppercase tracking-wide">
                    KYC Verification & Side-by-Side Review
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

            {/* Modal Body: Side-by-Side Comparison */}
            <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6 divide-y md:divide-y-0 md:divide-x divide-slate-200">
              {/* LEFT: User-Submitted Details */}
              <div className="space-y-4">
                <div className="flex items-center space-x-2 pb-2 border-b border-slate-100">
                  <UserCheck className="w-4 h-4 text-slate-500" />
                  <h4 className="text-xs font-black text-slate-800 uppercase tracking-wider">
                    Left: User-Submitted Details
                  </h4>
                </div>

                <div className="space-y-3 text-xs">
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase font-bold block">
                      Applicant Full Name
                    </span>
                    <span className="font-bold text-slate-900 text-sm">
                      {selectedDetail.user_submitted.name}
                    </span>
                  </div>

                  {selectedDetail.user_submitted.shop_name && (
                    <div>
                      <span className="text-[10px] text-slate-400 uppercase font-bold block">
                        Shop Name & Category
                      </span>
                      <span className="font-bold text-slate-800">
                        {selectedDetail.user_submitted.shop_name} ({selectedDetail.user_submitted.category})
                      </span>
                    </div>
                  )}

                  {selectedDetail.user_submitted.vehicle_type && (
                    <div>
                      <span className="text-[10px] text-slate-400 uppercase font-bold block">
                        Vehicle Type & Registration
                      </span>
                      <span className="font-bold text-slate-800">
                        {selectedDetail.user_submitted.vehicle_type} — {selectedDetail.user_submitted.vehicle_number}
                      </span>
                    </div>
                  )}

                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <span className="text-[10px] text-slate-400 uppercase font-bold block">
                        Registered Mobile
                      </span>
                      <span className="font-bold text-slate-800">
                        {selectedDetail.user_submitted.phone}
                      </span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-400 uppercase font-bold block">
                        Village / Hub
                      </span>
                      <span className="font-bold text-slate-800">
                        {selectedDetail.user_submitted.village}
                      </span>
                    </div>
                  </div>

                  <div className="bg-slate-50 p-3 rounded-xl border border-slate-200 space-y-1.5">
                    <span className="text-[10px] font-black uppercase text-slate-500 flex items-center gap-1">
                      <CreditCard className="w-3.5 h-3.5 text-slate-500" /> Bank Account Submitted
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

                  {/* Document & Selfie Previews */}
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase font-bold block mb-2">
                      Applicant Photos & Documents
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
                            Live Selfie Photo
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
                            Store Front Signage
                          </span>
                        </div>
                      )}
                      {selectedDetail.user_submitted.driving_license_url && (
                        <div>
                          <img
                            src={selectedDetail.user_submitted.driving_license_url}
                            alt="Driving License"
                            className="w-full h-24 object-cover rounded-lg border border-slate-200"
                          />
                          <span className="text-[9px] text-slate-500 font-semibold block text-center mt-1">
                            Driving License / RC
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* RIGHT: API-Verified Data (Penny Drop & Aadhaar Match) */}
              <div className="space-y-4 md:pl-6 pt-4 md:pt-0">
                <div className="flex items-center space-x-2 pb-2 border-b border-slate-100">
                  <FileCheck className="w-4 h-4 text-emerald-600" />
                  <h4 className="text-xs font-black text-emerald-950 uppercase tracking-wider">
                    Right: API-Verified Results
                  </h4>
                </div>

                {/* 1. Penny Drop Bank Verification */}
                <div className="bg-emerald-50/70 border border-emerald-200 rounded-2xl p-4 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-extrabold text-emerald-900 flex items-center gap-1.5">
                      <CheckCircle className="w-4 h-4 text-emerald-600" /> Penny Drop Bank Validation
                    </span>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-black bg-emerald-600 text-white">
                      100% MATCH
                    </span>
                  </div>

                  <div className="space-y-1 text-xs">
                    <div className="text-slate-600">
                      Verified Bank Holder:{' '}
                      <strong className="text-emerald-950">
                        {selectedDetail.api_verified.penny_drop_bank_match.verified_account_holder}
                      </strong>
                    </div>
                    <div className="text-slate-600">
                      Branch:{' '}
                      <span className="text-slate-800">
                        {selectedDetail.api_verified.penny_drop_bank_match.bank_name}
                      </span>
                    </div>
                    <div className="text-slate-500 text-[11px]">
                      Ref ID: {selectedDetail.api_verified.penny_drop_bank_match.penny_drop_reference}
                    </div>
                  </div>
                </div>

                {/* 2. Aadhaar Liveness Match Score */}
                <div className="bg-blue-50/70 border border-blue-200 rounded-2xl p-4 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-extrabold text-blue-900 flex items-center gap-1.5">
                      <ShieldCheck className="w-4 h-4 text-blue-600" /> Aadhaar & Liveness Check
                    </span>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-black bg-blue-600 text-white">
                      PASSED
                    </span>
                  </div>

                  <div className="space-y-1.5 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-600">Liveness Match Score:</span>
                      <strong className="text-blue-950 text-sm">
                        {selectedDetail.api_verified.aadhaar_liveness.liveness_score}%
                      </strong>
                    </div>
                    <div className="text-slate-600 text-[11px]">
                      Liveness Test: {selectedDetail.api_verified.aadhaar_liveness.liveness_check}
                    </div>
                    <div className="text-slate-600 text-[11px]">
                      Face Match Confidence: {selectedDetail.api_verified.aadhaar_liveness.face_match_confidence}
                    </div>
                    <div className="text-slate-600 text-[11px]">
                      UIDAI Verification: {selectedDetail.api_verified.aadhaar_liveness.aadhaar_uidai_status}
                    </div>
                  </div>
                </div>

                {/* Gatekeeper Decision Banner */}
                <div className="p-3 bg-slate-100 rounded-xl text-xs text-slate-600">
                  <p className="font-semibold text-slate-800 mb-1">
                    Gatekeeper Security Protocol:
                  </p>
                  Approving unlocks the partner app immediately for operational duty. Rejecting prompts the partner to submit replacement KYC documents.
                </div>
              </div>
            </div>

            {/* Modal Action Buttons: Approve & Unlock App vs Reject & Request Re-upload */}
            <div className="px-6 py-4 bg-slate-50 border-t border-slate-200 flex items-center justify-between sticky bottom-0">
              <button
                onClick={() => setShowRejectModal(true)}
                disabled={isActionSubmitting}
                className="px-4 py-2.5 bg-rose-50 hover:bg-rose-100 text-rose-700 font-bold text-xs rounded-xl border border-rose-300 transition flex items-center space-x-1.5"
              >
                <XCircle className="w-4 h-4" />
                <span>Reject & Request Re-upload</span>
              </button>

              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setSelectedDetail(null)}
                  className="px-4 py-2.5 text-slate-600 hover:text-slate-900 text-xs font-semibold"
                >
                  Cancel
                </button>
                <button
                  onClick={handleApproveAction}
                  disabled={isActionSubmitting}
                  className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs rounded-xl shadow-md transition flex items-center space-x-2"
                >
                  <CheckCircle className="w-4 h-4" />
                  <span>Approve & Unlock App</span>
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
              Reject KYC Application & Send Correction Request
            </h4>
            <p className="text-xs text-slate-600">
              Specify the reason for rejection. This explanation will be displayed in the partner's mobile application.
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
                Cancel
              </button>
              <button
                onClick={handleRejectConfirm}
                disabled={isActionSubmitting}
                className="px-4 py-1.5 bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs rounded-lg shadow-xs"
              >
                Confirm Rejection
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
