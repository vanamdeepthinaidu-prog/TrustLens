import { Card, CardHeader, CardBody } from '../components/ui/Card';
import { mockSystemInfo } from '../mock/mockData';
import { CheckCircle, XCircle, AlertCircle, Wifi, WifiOff } from 'lucide-react';

export default function SystemInformation() {
  const info = mockSystemInfo;
  const dc = info.detection_coverage;

  return (
    <div className="space-y-5">
      {/* System config */}
      <Card>
        <CardHeader title="System Configuration" />
        <CardBody>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
            {[
              ['Version',         info.version],
              ['Build',           info.build],
              ['Ledger Type',     info.ledger_type],
              ['Inference Model', info.model],
              ['Hash Algorithm',  info.hash_algorithm],
              ['Backend URL',     info.backend_url],
            ].map(([k, v]) => (
              <div key={k} className="bg-gray-800 rounded p-3">
                <p className="text-gray-500">{k}</p>
                <p className="text-gray-200 font-mono mt-1 break-all">{v}</p>
              </div>
            ))}
          </div>
          <div className={`mt-4 flex items-center gap-2 text-sm ${info.offline_capable ? 'text-emerald-400' : 'text-gray-400'}`}>
            {info.offline_capable ? <Wifi size={16} /> : <WifiOff size={16} />}
            {info.offline_capable ? 'Offline-capable — zero external internet dependency' : 'Requires internet'}
          </div>
        </CardBody>
      </Card>

      {/* Detection coverage */}
      <Card>
        <CardHeader title="Detection Coverage" subtitle="Honest capability assessment — per spec section 32" />
        <CardBody>
          <div className="space-y-5">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle size={15} className="text-emerald-400" />
                <h4 className="text-emerald-400 text-sm font-semibold">SUPPORTED</h4>
              </div>
              <div className="space-y-1.5">
                {dc.supported.map((s) => (
                  <div key={s} className="flex items-start gap-2 text-xs">
                    <span className="text-emerald-500 mt-0.5 flex-shrink-0">✓</span>
                    <span className="text-gray-300">{s}</span>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <div className="flex items-center gap-2 mb-2">
                <AlertCircle size={15} className="text-amber-400" />
                <h4 className="text-amber-400 text-sm font-semibold">PARTIALLY SUPPORTED</h4>
              </div>
              <div className="space-y-1.5">
                {dc.partial.map((s) => (
                  <div key={s} className="flex items-start gap-2 text-xs">
                    <span className="text-amber-500 mt-0.5 flex-shrink-0">~</span>
                    <span className="text-gray-300">{s}</span>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <div className="flex items-center gap-2 mb-2">
                <XCircle size={15} className="text-gray-500" />
                <h4 className="text-gray-500 text-sm font-semibold">NOT SUPPORTED</h4>
              </div>
              <div className="space-y-1.5">
                {dc.unsupported.map((s) => (
                  <div key={s} className="flex items-start gap-2 text-xs">
                    <span className="text-gray-600 mt-0.5 flex-shrink-0">✗</span>
                    <span className="text-gray-500">{s}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Roles */}
      <Card>
        <CardHeader title="Access Roles" />
        <CardBody>
          <div className="grid grid-cols-2 gap-3 text-xs">
            {[
              { role: 'DATA_CONTRIBUTOR', desc: 'Upload datasets, view own submissions', color: 'text-blue-400' },
              { role: 'MODEL_TRAINER',    desc: 'Upload models, view fingerprints', color: 'text-purple-400' },
              { role: 'AUDITOR',          desc: 'View all evidence, set dispositions, export reports', color: 'text-amber-400' },
              { role: 'ADMIN',            desc: 'Full access including ledger management', color: 'text-red-400' },
            ].map(({ role, desc, color }) => (
              <div key={role} className="bg-gray-800 rounded p-3">
                <p className={`font-mono font-semibold ${color}`}>{role}</p>
                <p className="text-gray-400 mt-1">{desc}</p>
              </div>
            ))}
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
