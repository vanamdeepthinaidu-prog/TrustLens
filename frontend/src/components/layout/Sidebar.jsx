import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, Database, Brain, Activity, BarChart2,
  FlaskConical, Search, ScrollText, FileBarChart, Info,
  ShieldCheck,
} from 'lucide-react';

const NAV_ITEMS = [
  { to: '/dashboard',              label: 'Dashboard',              icon: LayoutDashboard },
  { to: '/dataset-integrity',      label: 'Dataset Integrity',      icon: Database        },
  { to: '/model-integrity',        label: 'Model Integrity',        icon: Brain           },
  { to: '/inference-verification', label: 'Inference Verification', icon: Activity        },
  { to: '/distribution-shift',     label: 'Distribution Shift',     icon: BarChart2       },
  { to: '/security-lab',           label: 'Security Lab',           icon: FlaskConical    },
  { to: '/evidence-explorer',      label: 'Evidence Explorer',      icon: Search          },
  { to: '/audit-trail',            label: 'Audit Trail',            icon: ScrollText      },
  { to: '/assurance-reports',      label: 'Assurance Reports',      icon: FileBarChart    },
  { to: '/system-information',     label: 'System Information',     icon: Info            },
];

export default function Sidebar() {
  return (
    <aside className="w-64 flex-shrink-0 bg-gray-900 border-r border-gray-800 flex flex-col h-screen sticky top-0">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-gray-800">
        <div className="flex items-center gap-2">
          <ShieldCheck className="text-emerald-400" size={22} />
          <span className="text-white font-bold tracking-wider text-sm">TRUST<span className="text-emerald-400">LENS</span></span>
        </div>
        <p className="text-gray-500 text-xs mt-1">AI Assurance Platform · SIH26228</p>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-3 px-2">
        {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-md mb-0.5 text-sm transition-colors ${
                isActive
                  ? 'bg-emerald-500/10 text-emerald-400 font-medium'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800'
              }`
            }
          >
            <Icon size={15} />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-gray-800">
        <p className="text-gray-600 text-xs">Offline-capable · No cloud AI</p>
      </div>
    </aside>
  );
}
