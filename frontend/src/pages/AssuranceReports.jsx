import { useState } from 'react';
import { Card, CardHeader, CardBody } from '../components/ui/Card';
import { FileBarChart, Download, Loader2, CheckCircle } from 'lucide-react';

const REPORT_SECTIONS = [
  'Executive Summary',
  'System Configuration',
  'Dataset Integrity Assessment',
  'Duplicate & Near-Duplicate Analysis',
  'OOD / Anomaly Detection Results',
  'Model Integrity Assessment',
  'Inference Provenance Verification',
  'Tamper & Replay Detection Summary',
  'Distribution Shift Analysis',
  'Trust Score Calculation (with per-component breakdown)',
  'Security Lab — Attack Simulation Results',
  'Detection Coverage (supported / partially supported / unsupported)',
  'Recommended Actions & Remediation Steps',
];

const MOCK_REPORTS = [
  { id: 'RPT-2026-001', type: 'JSON', ts: '2026-09-09T18:00:00Z', size: '42 KB', trust_score: 91.2 },
  { id: 'RPT-2026-002', type: 'PDF',  ts: '2026-09-09T18:01:00Z', size: '210 KB', trust_score: 91.2 },
  { id: 'RPT-2026-003', type: 'JSON', ts: '2026-09-10T07:15:00Z', size: '47 KB', trust_score: 78.4 },
  { id: 'RPT-2026-004', type: 'PDF',  ts: '2026-09-10T07:16:00Z', size: '220 KB', trust_score: 78.4 },
];

export default function AssuranceReports() {
  const [generating, setGenerating] = useState(null);
  const [done, setDone] = useState({});

  const generate = async (type) => {
    setGenerating(type);
    await new Promise(r => setTimeout(r, 2000));
    setDone(prev => ({ ...prev, [type]: true }));
    setGenerating(null);
  };

  return (
    <div className="space-y-6">
      {/* Generate */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {['JSON', 'PDF'].map((type) => (
          <Card key={type}>
            <CardHeader
              title={`${type} Assurance Report`}
              subtitle={type === 'JSON' ? 'Machine-readable — all 13 sections' : 'Human-readable — formatted for judges/auditors'}
            />
            <CardBody>
              <button
                onClick={() => generate(type)}
                disabled={!!generating}
                className="flex items-center gap-2 px-4 py-2 bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/30 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
              >
                {generating === type
                  ? <><Loader2 size={15} className="animate-spin" /> Generating…</>
                  : done[type]
                  ? <><CheckCircle size={15} /> Generated</>
                  : <><FileBarChart size={15} /> Generate {type} Report</>
                }
              </button>
            </CardBody>
          </Card>
        ))}
      </div>

      {/* Sections list */}
      <Card>
        <CardHeader title="Report Contents — All 13 Sections" />
        <CardBody>
          <div className="space-y-1.5">
            {REPORT_SECTIONS.map((s, i) => (
              <div key={s} className="flex items-center gap-3 text-xs py-1 border-b border-gray-800 last:border-0">
                <span className="text-gray-600 w-6 text-right flex-shrink-0">{i + 1}.</span>
                <span className="text-gray-300">{s}</span>
              </div>
            ))}
          </div>
        </CardBody>
      </Card>

      {/* Previous reports */}
      <Card>
        <CardHeader title="Report History" />
        <CardBody className="p-0">
          <table className="w-full text-xs">
            <thead className="border-b border-gray-800">
              <tr className="text-gray-500">
                <th className="text-left px-4 py-2">Report ID</th>
                <th className="text-left px-4 py-2">Type</th>
                <th className="text-left px-4 py-2">Generated</th>
                <th className="text-right px-4 py-2">Trust Score</th>
                <th className="text-right px-4 py-2">Size</th>
                <th className="text-center px-4 py-2">Action</th>
              </tr>
            </thead>
            <tbody>
              {MOCK_REPORTS.map((r) => (
                <tr key={r.id} className="border-b border-gray-800 hover:bg-gray-800/50">
                  <td className="px-4 py-2 font-mono text-gray-300">{r.id}</td>
                  <td className="px-4 py-2">
                    <span className={`px-1.5 py-0.5 rounded text-xs font-mono ${r.type === 'PDF' ? 'bg-red-500/20 text-red-400' : 'bg-blue-500/20 text-blue-400'}`}>{r.type}</span>
                  </td>
                  <td className="px-4 py-2 text-gray-500">{new Date(r.ts).toLocaleString()}</td>
                  <td className="px-4 py-2 text-right text-gray-200 font-semibold">{r.trust_score}</td>
                  <td className="px-4 py-2 text-right text-gray-500">{r.size}</td>
                  <td className="px-4 py-2 text-center">
                    <button className="text-gray-500 hover:text-emerald-400 transition-colors">
                      <Download size={13} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardBody>
      </Card>
    </div>
  );
}
