import React, { useState } from 'react';
import { ShieldCheck, Lock, UserCheck, KeyRound, ArrowRight } from 'lucide-react';
import { adminApi } from '../api';
import type { AdminRole, AdminUser } from '../types';

interface LoginViewProps {
  onLoginSuccess: (user: AdminUser) => void;
}

export function LoginView({ onLoginSuccess }: LoginViewProps) {
  const [phone, setPhone] = useState('9800000099');
  const [secretOrOtp, setSecretOrOtp] = useState('123456');
  const [selectedRole, setSelectedRole] = useState<AdminRole>('super_admin');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const result = await adminApi.login(phone, secretOrOtp, selectedRole);
      onLoginSuccess(result.user);
    } catch (err: any) {
      setError(err?.message || 'Authentication failed. Please verify admin credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  const setTierQuick = (role: AdminRole) => {
    setSelectedRole(role);
    if (role === 'hub_manager') {
      setPhone('9800000098');
      setSecretOrOtp('123456');
    } else {
      setPhone('9800000099');
      setSecretOrOtp('123456');
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4 font-sans">
      <div className="max-w-md w-full bg-white rounded-3xl shadow-2xl border border-slate-800 overflow-hidden">
        {/* Brand Header */}
        <div className="bg-slate-950 p-6 text-center text-white border-b border-slate-800">
          <div className="w-12 h-12 mx-auto rounded-2xl bg-emerald-600 text-white flex items-center justify-center font-black text-xl shadow-lg mb-3">
            GB
          </div>
          <h1 className="text-xl font-extrabold tracking-tight">गांवबाज़ार Super Admin</h1>
          <p className="text-xs text-emerald-400 font-semibold mt-1">
            Rural Hyperlocal Operations & Command Center
          </p>
        </div>

        {/* Form Body */}
        <div className="p-6 space-y-5">
          {/* Quick Role Selection Tabs */}
          <div>
            <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-2">
              Select Operational Tier (RBAC)
            </label>
            <div className="grid grid-cols-2 gap-2 bg-slate-100 p-1 rounded-xl text-xs font-bold">
              <button
                type="button"
                onClick={() => setTierQuick('super_admin')}
                className={`py-2 px-3 rounded-lg transition ${
                  selectedRole !== 'hub_manager'
                    ? 'bg-emerald-600 text-white shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Super Admin
              </button>
              <button
                type="button"
                onClick={() => setTierQuick('hub_manager')}
                className={`py-2 px-3 rounded-lg transition ${
                  selectedRole === 'hub_manager'
                    ? 'bg-amber-600 text-white shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Hub Manager
              </button>
            </div>
          </div>

          {error && (
            <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 rounded-xl text-xs">
              <strong>त्रुटि / Error:</strong> {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4 text-xs">
            <div>
              <label className="font-bold text-slate-700 block mb-1">
                Authorized Admin Phone (+91):
              </label>
              <div className="relative">
                <span className="absolute left-3 top-2.5 text-slate-400 font-bold">+91</span>
                <input
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="9800000099"
                  required
                  className="w-full pl-11 pr-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl outline-none focus:border-emerald-500 font-semibold"
                />
              </div>
            </div>

            <div>
              <label className="font-bold text-slate-700 block mb-1">
                Admin Passcode or Master Key:
              </label>
              <div className="relative">
                <input
                  type="password"
                  value={secretOrOtp}
                  onChange={(e) => setSecretOrOtp(e.target.value)}
                  placeholder="Passcode 123456 or Admin Key"
                  required
                  className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl outline-none focus:border-emerald-500 font-mono"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className={`w-full py-3 text-white font-extrabold rounded-xl shadow-md transition flex items-center justify-center space-x-2 text-xs ${
                selectedRole === 'hub_manager'
                  ? 'bg-amber-600 hover:bg-amber-700'
                  : 'bg-emerald-600 hover:bg-emerald-700'
              }`}
            >
              <span>{isLoading ? 'Verifying Credentials...' : 'Sign In to Operations Panel'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          <div className="pt-2 text-center text-[11px] text-slate-400">
            🔒 Secure JWT Authentication • Minapur Block Pilot Operations
          </div>
        </div>
      </div>
    </div>
  );
}
