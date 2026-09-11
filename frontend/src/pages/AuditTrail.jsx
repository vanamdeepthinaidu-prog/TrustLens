import { Card } from '../components/ui/Card';
import HashDisplay from '../components/ui/HashDisplay';
import { mockAuditLog } from '../mock/mockData';

const ACTION_COLORS = {
  DATASET_UPLOADED:    'bg-blue-500',
  DATASET_ANALYZED:    'bg-blue-400',
  MODEL_UPLOADED:      'bg-purple-500',
  FINGERPRINT_COMPUTED:'bg-purple-400',
  INFERENCE_RUN:       'bg-amber-500',
  TAMPER_DETECTED:     'bg-red-500',
  EVIDENCE_QUARANTINED:'bg-red-400',
};

export default function AuditTrail() {
  return (
    <div className="space-y-4">
      <p className="text-gray-500 text-xs">Chronological tamper-evident audit chain. Each event is hash-linked to the previous.</p>

      <div className="relative">
        {/* Vertical line */}
        <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-800" />

        <div className="space-y-0">
          {mockAuditLog.map((entry, idx) => (
            <div key={entry.id} className="relative pl-10 pb-6">
              {/* Timeline dot */}
              <div className={`absolute left-2.5 top-1.5 w-3 h-3 rounded-full border-2 border-gray-950 ${ACTION_COLORS[entry.action] || 'bg-gray-600'}`} />

              <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
                <div className="flex items-start justify-between gap-3 flex-wrap">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-gray-200 text-sm font-semibold font-mono">{entry.action}</span>
                      <span className="text-gray-600 text-xs">#{entry.id}</span>
                    </div>
                    <div className="flex flex-wrap gap-x-4 gap-y-0.5 text-xs text-gray-500">
                      <span>Actor: <span className="text-gray-300">{entry.actor}</span></span>
                      <span>Asset: <span className="text-gray-300">{entry.asset}</span></span>
                      <span>Role: <span className="text-gray-300">{entry.role}</span></span>
                      <span>{new Date(entry.ts).toLocaleString()}</span>
                    </div>
                  </div>
                </div>

                <div className="mt-3 flex items-center gap-2">
                  <span className="text-gray-600 text-xs">Event Hash</span>
                  <HashDisplay hash={entry.hash} />
                </div>

                {idx > 0 && (
                  <div className="mt-1.5 flex items-center gap-2">
                    <span className="text-gray-700 text-xs">← prev</span>
                    <HashDisplay hash={mockAuditLog[idx - 1].hash} />
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
