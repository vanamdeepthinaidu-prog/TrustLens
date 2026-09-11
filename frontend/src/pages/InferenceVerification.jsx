import { useState } from 'react';
import { Card, CardHeader, CardBody } from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import HashDisplay from '../components/ui/HashDisplay';

const MOCK_RECORD = {
  inference_id: 'INF-2026-042',
  model_id: 'MDL-2026-001',
  operator_id: 'operator-01',
  input_hash: 'sha256:f4a2c7d3e8b1f9a4c2d7e3b8f5a1c9d4',
  model_hash: 'sha256:c9d1a0f3b7e2c5d8a4f1b9e3c6d2a8f5',
  preprocessing_hash: 'sha256:b7e2c5d8a4f1b9e3c6d2a8f5b1e4c7d3',
  result_hash: 'sha256:a9f1c2d4b3e7f0a5c8d2b6e1c4d8a5f3',
  record_hash: 'sha256:a9f1c2d4b3e7f0a5c8d2b6e1c4d8a5f3',
  timestamp: '2026-09-10T06:54:00Z',
  sequence_number: 42,
  nonce: 'n0nc3-ab12cd',
  previous_record_hash: 'sha256:d0e3b1a2c9f6d4e7b0a3c8f1e5d2b7a4',
  prediction: 'class_3',
  confidence: 0.91,
  tamper_status: 'TAMPERED',
};

const MOCK_TAMPER = {
  original_hash: 'sha256:a9f1c2d4b3e7f0a5c8d2b6e1c4d8a5f3',
  current_hash:  'sha256:00b3f7a1c9d2e4b6f3a0c8d5e1b9f2a4',
  modified_field: 'result',
  original_value: 'class_3',
  tampered_value: 'class_7',
  detection_method: 'Record hash recomputation',
};

const MOCK_REPLAY = [
  { issue: 'DUPLICATE_SEQUENCE',   detail: 'Sequence number 42 appears in records INF-042 and INF-039', severity: 'HIGH'   },
  { issue: 'REUSED_NONCE',         detail: 'Nonce n0nc3-ab12cd was used in INF-038 (2026-09-09T22:00Z)', severity: 'CRITICAL' },
  { issue: 'STALE_TIMESTAMP',      detail: 'Record timestamp predates previous record by -3 seconds', severity: 'MEDIUM' },
];

export default function InferenceVerification() {
  const [tab, setTab] = useState('provenance');

  return (
    <div className="space-y-5">
      <div className="flex gap-1 bg-gray-900 border border-gray-800 rounded-lg p-1 w-fit">
        {['provenance','tamper','replay'].map(t => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-3 py-1.5 rounded text-xs font-medium capitalize transition-colors ${tab === t ? 'bg-gray-700 text-gray-100' : 'text-gray-500 hover:text-gray-300'}`}>
            {t === 'tamper' ? 'Tamper Test' : t === 'replay' ? 'Replay Detection' : 'Provenance Record'}
          </button>
        ))}
      </div>

      {tab === 'provenance' && (
        <Card>
          <CardHeader title={`Inference Provenance — ${MOCK_RECORD.inference_id}`} />
          <CardBody>
            <div className="grid grid-cols-2 gap-3 text-xs">
              {[
                ['Inference ID',     MOCK_RECORD.inference_id],
                ['Model ID',         MOCK_RECORD.model_id],
                ['Operator',         MOCK_RECORD.operator_id],
                ['Prediction',       `${MOCK_RECORD.prediction} (${(MOCK_RECORD.confidence*100).toFixed(0)}%)`],
                ['Sequence Number',  MOCK_RECORD.sequence_number],
                ['Nonce',            MOCK_RECORD.nonce],
                ['Timestamp',        new Date(MOCK_RECORD.timestamp).toLocaleString()],
              ].map(([k, v]) => (
                <div key={k} className="bg-gray-800 rounded p-2">
                  <p className="text-gray-500">{k}</p>
                  <p className="text-gray-200 font-mono mt-0.5 break-all">{v}</p>
                </div>
              ))}
              <div className="col-span-2 bg-gray-800 rounded p-2">
                <p className="text-gray-500 mb-1">Input Hash</p>
                <HashDisplay hash={MOCK_RECORD.input_hash} maxLen={80} />
              </div>
              <div className="col-span-2 bg-gray-800 rounded p-2">
                <p className="text-gray-500 mb-1">Record Hash</p>
                <HashDisplay hash={MOCK_RECORD.record_hash} maxLen={80} />
              </div>
              <div className="col-span-2 bg-gray-800 rounded p-2">
                <p className="text-gray-500 mb-1">Previous Record Hash</p>
                <HashDisplay hash={MOCK_RECORD.previous_record_hash} maxLen={80} />
              </div>
            </div>
            <div className="mt-4 flex items-center gap-3">
              <p className="text-gray-500 text-xs">Tamper Status</p>
              <Badge label={MOCK_RECORD.tamper_status} />
            </div>
          </CardBody>
        </Card>
      )}

      {tab === 'tamper' && (
        <div className="space-y-4">
          <Card>
            <CardHeader title="Tamper Detection — Demo Record" subtitle="Operates on demo/test records only" />
            <CardBody>
              <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 mb-4">
                <p className="text-red-400 font-bold font-mono text-sm">✗ TAMPER DETECTED</p>
                <p className="text-gray-400 text-xs mt-1">Field &quot;{MOCK_TAMPER.modified_field}&quot; modified: {MOCK_TAMPER.original_value} → {MOCK_TAMPER.tampered_value}</p>
                <p className="text-gray-500 text-xs mt-0.5">Detection method: {MOCK_TAMPER.detection_method}</p>
              </div>
              <div className="grid grid-cols-1 gap-2">
                <div className="bg-gray-800 rounded p-3">
                  <p className="text-gray-500 text-xs mb-1">ORIGINAL HASH</p>
                  <HashDisplay hash={MOCK_TAMPER.original_hash} maxLen={80} />
                </div>
                <div className="bg-red-900/30 rounded p-3 border border-red-500/20">
                  <p className="text-gray-500 text-xs mb-1">CURRENT HASH (post-modification)</p>
                  <HashDisplay hash={MOCK_TAMPER.current_hash} maxLen={80} />
                </div>
              </div>
            </CardBody>
          </Card>
        </div>
      )}

      {tab === 'replay' && (
        <Card>
          <CardHeader title="Replay Attack Detection" subtitle="Nonce, sequence, timestamp, chain order checks" />
          <CardBody>
            <div className="space-y-3">
              {MOCK_REPLAY.map((r) => (
                <div key={r.issue} className="bg-gray-800 rounded-lg p-4 flex items-start gap-3">
                  <Badge label={r.severity} />
                  <div>
                    <p className="text-gray-300 text-sm font-mono">{r.issue}</p>
                    <p className="text-gray-500 text-xs mt-0.5">{r.detail}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>
      )}
    </div>
  );
}
