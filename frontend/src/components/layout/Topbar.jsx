import { Wifi, WifiOff, Bell, User, LogOut, KeyRound, ChevronDown } from 'lucide-react';
import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

const ROLE_BADGE_COLORS = {
  ADMIN: 'text-purple-400 bg-purple-500/10 border-purple-500/30',
  AUDITOR: 'text-blue-400 bg-blue-500/10 border-blue-500/30',
  MODEL_TRAINER: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
  DATA_CONTRIBUTOR: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
};

export default function Topbar({ title }) {
  const navigate = useNavigate();
  const [online, setOnline] = useState(navigator.onLine);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const menuRef = useRef(null);

  const getStoredUser = () => {
    try {
      const stored = localStorage.getItem('tl_user');
      if (stored) return JSON.parse(stored);
    } catch {
      // fallback
    }
    return { username: 'auditor', role: 'AUDITOR' };
  };

  const [currentUser, setCurrentUser] = useState(getStoredUser);

  useEffect(() => {
    const up = () => setOnline(true);
    const dn = () => setOnline(false);
    window.addEventListener('online',  up);
    window.addEventListener('offline', dn);

    const updateAuth = () => setCurrentUser(getStoredUser());
    window.addEventListener('auth-changed', updateAuth);

    const handleClickOutside = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setUserMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);

    return () => { 
      window.removeEventListener('online', up); 
      window.removeEventListener('offline', dn);
      window.removeEventListener('auth-changed', updateAuth);
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('tl_token');
    localStorage.removeItem('tl_user');
    window.dispatchEvent(new Event('auth-changed'));
    setUserMenuOpen(false);
    navigate('/login');
  };

  const roleStyle = ROLE_BADGE_COLORS[currentUser.role] || 'text-gray-300 bg-gray-800 border-gray-700';

  return (
    <header className="h-12 border-b border-gray-800 bg-gray-950 flex items-center px-5 gap-4 flex-shrink-0 relative">
      <h1 className="text-gray-100 text-sm font-semibold flex-1 tracking-wide">{title}</h1>

      {/* Air-gapped / offline indicator */}
      <div className={`flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full border ${online ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' : 'text-amber-400 bg-amber-400/10 border-amber-400/20'}`}>
        {online ? <Wifi size={12} /> : <WifiOff size={12} />}
        <span className="font-mono text-[11px]">{online ? 'Enclave Connected' : 'Air-Gapped Local'}</span>
      </div>

      <div className="flex items-center gap-3 text-gray-500 relative" ref={menuRef}>
        <button className="hover:text-gray-300 transition-colors p-1"><Bell size={15} /></button>
        
        {/* User Badge Button */}
        <button 
          onClick={() => setUserMenuOpen(!userMenuOpen)}
          className="flex items-center gap-2 hover:bg-gray-900 border border-gray-800 px-2.5 py-1 rounded-lg transition-colors cursor-pointer"
        >
          <div className="w-5 h-5 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300">
            <User size={12} />
          </div>
          <span className="text-xs text-gray-200 font-medium">{currentUser.username}</span>
          <span className={`text-[10px] px-1.5 py-0.5 rounded border font-mono font-semibold uppercase ${roleStyle}`}>
            {currentUser.role}
          </span>
          <ChevronDown size={12} className="text-gray-500" />
        </button>

        {/* User Dropdown Menu */}
        {userMenuOpen && (
          <div className="absolute right-0 top-11 w-64 bg-slate-900 border border-slate-700 rounded-xl shadow-2xl z-50 p-3 text-xs">
            <div className="pb-2 mb-2 border-b border-slate-800">
              <div className="text-slate-200 font-bold">{currentUser.username}</div>
              <div className="text-[10px] text-slate-400">Authenticated Operator</div>
              <div className="mt-1.5 flex items-center gap-1.5">
                <span className={`text-[9px] px-2 py-0.5 rounded border font-mono font-semibold uppercase ${roleStyle}`}>
                  {currentUser.role}
                </span>
                <span className="text-[10px] text-slate-500">Security Enclave</span>
              </div>
            </div>

            <div className="space-y-1">
              <button
                onClick={() => { setUserMenuOpen(false); navigate('/login'); }}
                className="w-full flex items-center gap-2 px-2.5 py-2 rounded-lg hover:bg-slate-800 text-slate-300 hover:text-emerald-400 transition-colors text-left"
              >
                <KeyRound size={14} />
                <span>Switch Operator / Re-Authenticate</span>
              </button>

              <button
                onClick={handleLogout}
                className="w-full flex items-center gap-2 px-2.5 py-2 rounded-lg hover:bg-red-950/30 text-red-400 transition-colors text-left"
              >
                <LogOut size={14} />
                <span>Sign Out Session</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
