import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ShieldCheck, Lock, User, Building, AlertCircle, 
  CheckCircle, ArrowRight, Key, Sparkles, Eye, EyeOff
} from 'lucide-react';
import client from '../api/client';

const DEMO_PRESETS = [
  { role: 'ADMIN', username: 'admin', password: 'admin123', label: 'Command Admin', desc: 'Full pipeline governance & policy' },
  { role: 'AUDITOR', username: 'auditor', password: 'auditor123', label: 'Security Auditor', desc: 'Audit trail inspection & reports' },
  { role: 'MODEL_TRAINER', username: 'trainer', password: 'trainer123', label: 'Model Trainer', desc: 'Fingerprinting & substitution check' },
  { role: 'DATA_CONTRIBUTOR', username: 'contributor', password: 'contrib123', label: 'Data Contributor', desc: 'Recon dataset ingress & validation' },
];

export default function Login() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('login'); // 'login' | 'register'
  
  // Login State
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  
  // Register State
  const [regName, setRegName] = useState('');
  const [regOrg, setRegOrg] = useState('Indian Army DGIS');
  const [regUsername, setRegUsername] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regRole, setRegRole] = useState('AUDITOR');
  
  // UI State
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const handleLogin = async (e) => {
    if (e) e.preventDefault();
    setError('');
    setSuccessMsg('');
    if (!username.trim() || !password.trim()) {
      setError('Please enter both username and password.');
      return;
    }

    setLoading(true);
    try {
      const res = await client.post('/api/auth/login', {
        username: username.trim(),
        password: password.trim()
      });

      const data = res.data;
      localStorage.setItem('tl_token', data.access_token);
      localStorage.setItem('tl_user', JSON.stringify({
        username: data.username,
        role: data.role
      }));
      window.dispatchEvent(new Event('auth-changed'));
      setSuccessMsg(`Welcome, ${data.username.toUpperCase()}! Redirecting to Tactical Dashboard...`);
      setTimeout(() => navigate('/dashboard'), 800);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Authentication failed. Please check credentials or use demo presets.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMsg('');
    if (!regUsername.trim() || !regPassword.trim()) {
      setError('Please provide a username and password.');
      return;
    }

    setLoading(true);
    try {
      const res = await client.post('/api/auth/register', {
        username: regUsername.trim(),
        password: regPassword.trim(),
        role: regRole,
        organization: regOrg,
        name: regName.trim() || regUsername.trim()
      });

      const data = res.data;
      localStorage.setItem('tl_token', data.access_token);
      localStorage.setItem('tl_user', JSON.stringify({
        username: data.username,
        role: data.role
      }));
      window.dispatchEvent(new Event('auth-changed'));
      setSuccessMsg(`Operator ${data.username} registered with role ${data.role}! Redirecting...`);
      setTimeout(() => navigate('/dashboard'), 800);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Registration failed. Please try a different username.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const selectPreset = (preset) => {
    setUsername(preset.username);
    setPassword(preset.password);
    setError('');
    setSuccessMsg(`Selected ${preset.label} (${preset.username}). Click "Authorize Session" or press Enter.`);
  };

  const continueAsGuest = () => {
    localStorage.setItem('tl_token', 'demo-guest-token-airgapped');
    localStorage.setItem('tl_user', JSON.stringify({
      username: 'auditor_demo',
      role: 'AUDITOR'
    }));
    window.dispatchEvent(new Event('auth-changed'));
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-center items-center p-4 relative overflow-hidden">
      {/* Background ambient military grid */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_50%,#000_70%,transparent_100%)] opacity-20 pointer-events-none" />

      {/* Main card */}
      <div className="relative z-10 w-full max-w-xl bg-slate-900/90 border border-slate-800 backdrop-blur-xl rounded-2xl shadow-2xl overflow-hidden">
        
        {/* Top Header Banner */}
        <div className="bg-slate-950/80 px-8 pt-8 pb-6 border-b border-slate-800/80 text-center relative">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 mb-3 shadow-[0_0_20px_rgba(16,185,129,0.15)]">
            <ShieldCheck size={32} />
          </div>
          <h1 className="text-2xl font-bold tracking-wider text-slate-100 uppercase">
            TrustLens <span className="text-emerald-400 text-sm font-semibold ml-1.5 px-2 py-0.5 rounded border border-emerald-500/30 bg-emerald-500/10">v1.0</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
            VisionTrust AI — SIH26228 | Ministry of Defence & Indian Army DGIS
          </p>
          <div className="flex items-center justify-center gap-2 mt-3 text-[11px] text-emerald-400/90 bg-emerald-950/40 border border-emerald-800/50 py-1 px-3 rounded-full w-fit mx-auto">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            Air-Gapped Local Authentication · Zero Cloud Telemetry
          </div>
        </div>

        {/* Tab Toggle */}
        <div className="flex border-b border-slate-800 bg-slate-950/40 p-1">
          <button
            type="button"
            onClick={() => { setActiveTab('login'); setError(''); setSuccessMsg(''); }}
            className={`flex-1 py-2.5 text-xs font-semibold rounded-lg transition-all ${
              activeTab === 'login'
                ? 'bg-slate-800 text-emerald-400 shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Operator Sign In
          </button>
          <button
            type="button"
            onClick={() => { setActiveTab('register'); setError(''); setSuccessMsg(''); }}
            className={`flex-1 py-2.5 text-xs font-semibold rounded-lg transition-all ${
              activeTab === 'register'
                ? 'bg-slate-800 text-emerald-400 shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Register Operator
          </button>
        </div>

        <div className="p-8">
          {/* Status Message Alerts */}
          {error && (
            <div className="mb-5 p-3.5 rounded-xl bg-red-950/40 border border-red-500/30 text-red-300 text-xs flex items-start gap-2.5">
              <AlertCircle size={16} className="text-red-400 mt-0.5 flex-shrink-0" />
              <div>{error}</div>
            </div>
          )}

          {successMsg && (
            <div className="mb-5 p-3.5 rounded-xl bg-emerald-950/40 border border-emerald-500/30 text-emerald-300 text-xs flex items-start gap-2.5">
              <CheckCircle size={16} className="text-emerald-400 mt-0.5 flex-shrink-0" />
              <div>{successMsg}</div>
            </div>
          )}

          {/* TAB 1: LOGIN */}
          {activeTab === 'login' && (
            <div>
              {/* Fast Demo Preset Buttons for Jury/Hackathon */}
              <div className="mb-6">
                <div className="flex items-center justify-between mb-2.5">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                    <Sparkles size={12} className="text-emerald-400" />
                    1-Click Evaluation Presets (Live Demo)
                  </span>
                  <span className="text-[10px] text-slate-500">Seeded offline</span>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  {DEMO_PRESETS.map((p) => (
                    <button
                      key={p.role}
                      type="button"
                      onClick={() => selectPreset(p)}
                      className="p-2.5 text-left rounded-xl bg-slate-950/60 border border-slate-800 hover:border-emerald-500/50 hover:bg-emerald-950/10 transition-all group"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-medium text-slate-200 group-hover:text-emerald-300">{p.label}</span>
                        <span className="text-[9px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">{p.username}</span>
                      </div>
                      <div className="text-[10px] text-slate-500 mt-0.5 truncate">{p.desc}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Login Form */}
              <form onSubmit={handleLogin} className="space-y-4">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1.5">Operator ID / Username</label>
                  <div className="relative">
                    <User size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
                    <input
                      type="text"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      placeholder="e.g. admin, auditor, trainer"
                      className="w-full bg-slate-950 border border-slate-800 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 outline-none transition-all"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1.5">Access Key / Password</label>
                  <div className="relative">
                    <Lock size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••"
                      className="w-full bg-slate-950 border border-slate-800 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 rounded-xl pl-10 pr-10 py-2.5 text-sm text-slate-100 placeholder-slate-600 outline-none transition-all"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
                    >
                      {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
                    </button>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full mt-2 py-3 px-4 bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 disabled:opacity-50 text-white text-xs font-bold uppercase tracking-wider rounded-xl transition-all shadow-[0_0_20px_rgba(16,185,129,0.25)] flex items-center justify-center gap-2 cursor-pointer"
                >
                  {loading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Verifying Cryptographic Credentials...
                    </>
                  ) : (
                    <>
                      <Key size={14} />
                      Authorize Session
                      <ArrowRight size={14} />
                    </>
                  )}
                </button>
              </form>
            </div>
          )}

          {/* TAB 2: REGISTER */}
          {activeTab === 'register' && (
            <form onSubmit={handleRegister} className="space-y-3.5">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Full Name / Callsign</label>
                <input
                  type="text"
                  value={regName}
                  onChange={(e) => setRegName(e.target.value)}
                  placeholder="e.g. Major R. Sharma"
                  className="w-full bg-slate-950 border border-slate-800 focus:border-emerald-500 rounded-xl px-3.5 py-2 text-sm text-slate-100 placeholder-slate-600 outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Assigned Role</label>
                  <select
                    value={regRole}
                    onChange={(e) => setRegRole(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 focus:border-emerald-500 rounded-xl px-3 py-2 text-xs text-slate-100 outline-none"
                  >
                    <option value="AUDITOR">AUDITOR (Security Audit)</option>
                    <option value="ADMIN">ADMIN (Command Oversight)</option>
                    <option value="MODEL_TRAINER">MODEL_TRAINER (Weights)</option>
                    <option value="DATA_CONTRIBUTOR">DATA_CONTRIBUTOR (Ingress)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Organization / Unit</label>
                  <input
                    type="text"
                    value={regOrg}
                    onChange={(e) => setRegOrg(e.target.value)}
                    placeholder="e.g. Indian Army DGIS"
                    className="w-full bg-slate-950 border border-slate-800 focus:border-emerald-500 rounded-xl px-3 py-2 text-xs text-slate-100 placeholder-slate-600 outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Desired Operator Username</label>
                <input
                  type="text"
                  value={regUsername}
                  onChange={(e) => setRegUsername(e.target.value)}
                  placeholder="e.g. army_auditor_02"
                  className="w-full bg-slate-950 border border-slate-800 focus:border-emerald-500 rounded-xl px-3.5 py-2 text-sm text-slate-100 placeholder-slate-600 outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Password</label>
                <input
                  type="password"
                  value={regPassword}
                  onChange={(e) => setRegPassword(e.target.value)}
                  placeholder="At least 4 characters"
                  className="w-full bg-slate-950 border border-slate-800 focus:border-emerald-500 rounded-xl px-3.5 py-2 text-sm text-slate-100 placeholder-slate-600 outline-none"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full mt-2 py-3 px-4 bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 disabled:opacity-50 text-white text-xs font-bold uppercase tracking-wider rounded-xl transition-all shadow-[0_0_20px_rgba(16,185,129,0.25)] flex items-center justify-center gap-2 cursor-pointer"
              >
                {loading ? (
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <>
                    <User size={14} />
                    Create Account & Commit to Ledger
                  </>
                )}
              </button>
            </form>
          )}

          {/* Guest / Instant Demo Bypass */}
          <div className="mt-6 pt-4 border-t border-slate-800/80 text-center">
            <button
              type="button"
              onClick={continueAsGuest}
              className="text-xs text-slate-400 hover:text-emerald-400 transition-colors font-medium"
            >
              Explore Live Demo Dashboard as Guest Auditor &rarr;
            </button>
          </div>
        </div>
      </div>

      {/* Footer System Specs */}
      <div className="mt-6 text-center text-slate-500 text-[11px]">
        Defense Security Enclave · PBKDF2-HMAC-SHA256 · Local SQLite Session Store
      </div>
    </div>
  );
}
