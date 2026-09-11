import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import Topbar from './Topbar';

const ROUTE_TITLES = {
  '/dashboard':               'Dashboard',
  '/dataset-integrity':       'Dataset Integrity',
  '/model-integrity':         'Model Integrity',
  '/inference-verification':  'Inference Verification',
  '/distribution-shift':      'Distribution Shift Analysis',
  '/security-lab':            'Security Lab — Attack Simulator',
  '/evidence-explorer':       'Evidence Explorer',
  '/audit-trail':             'Audit Trail',
  '/assurance-reports':       'Assurance Reports',
  '/system-information':      'System Information',
};

export default function Layout() {
  const { pathname } = useLocation();
  const title = ROUTE_TITLES[pathname] || 'TrustLens';
  return (
    <div className="flex bg-gray-950 min-h-screen text-gray-200">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Topbar title={title} />
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
