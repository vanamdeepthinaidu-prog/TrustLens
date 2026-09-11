import { useState } from 'react';
import { Card, CardHeader, CardBody } from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import HashDisplay from '../components/ui/HashDisplay';
import PipelineVisualizer from '../features/pipeline/PipelineVisualizer';
import VerificationPanel from '../features/verification/VerificationPanel';

const MOCK_DATASET = {
  dataset_id: 'DS-2026-001',
  name: 'CIFAR-10 Demo Subset',
  total_images: 1024,
  analyzed: 1024,
  corrupted: 6,
  exact_duplicates: 120,
  near_duplicates: 47,
  ood_samples: 23,
  label_inconsistencies: 15,
  dataset_hash: 'sha256:a3f2c1d8b9e5f4a2c7d3e8b1f9a4c2d7',
  analyzed_at: '2026-09-09T14:22:00Z',
};

const MOCK_DUPLICATES = [
  { cluster_id: 'CLU-001', count: 12, similarity: '94%', indicator: 'Potential duplicate flooding indicator', severity: 'MEDIUM' },
  { cluster_id: 'CLU-002', count: 7,  similarity: '89%', indicator: 'Potential duplicate flooding indicator', severity: 'LOW'    },
  { cluster_id: 'CLU-003', count: 4,  similarity: '97%', indicator: 'Potential duplicate flooding indicator', severity: 'MEDIUM' },
];

const MOCK_OOD = [
  { sample_id: 'IMG-0042', ood_score: 0.91, severity: 'HIGH',   method: 'Isolation Forest' },
  { sample_id: 'IMG-0118', ood_score: 0.83, severity: 'HIGH',   method: 'Distance-based' },
  { sample_id: 'IMG-0271', ood_score: 0.74, severity: 'MEDIUM', method: 'Isolation Forest' },
];

export default function DatasetIntegrity() {
  const [activeTab, setActiveTab] = useState('overview');
  const tabs = ['overview', 'duplicates', 'ood', 'verify', 'pipeline'];

  return (
    <div className="space-y-5">
      {/* Tabs */}
      <div className="flex gap-1 bg-gray-900 border border-gray-800 rounded-lg p-1 w-fit">
        {tabs.map(t => (
          <button
            key={t}
            onClick={() => setActiveTab(t)}
            className={`px-3 py-1.5 rounded text-xs font-medium capitalize transition-colors ${
              activeTab === t ? 'bg-gray-700 text-gray-100' : 'text-gray-500 hover:text-gray-300'
            }`}
          >
            {t === 'ood' ? 'OOD / Anomaly' : t}
          </button>
        ))}
      </div>

      {activeTab === 'overview' && (
        <div className="space-y-4">
          {/* Summary cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {[
              { label: 'Total Images',          value: MOCK_DATASET.total_images },
              { label: 'Exact Duplicates',      value: MOCK_DATASET.exact_duplicates, color: 'text-amber-400' },
              { label: 'Near Duplicates',       value: MOCK_DATASET.near_duplicates,  color: 'text-amber-400' },
              { label: 'OOD Samples',           value: MOCK_DATASET.ood_samples,      color: 'text-orange-400' },
            ].map(({ label, value, color }) => (
              <div key={label} className="bg-gray-900 border border-gray-800 rounded-lg p-4">
                <p className="text-gray-500 text-xs">{label}</p>
                <p className={`text-2xl font-bold mt-1 ${color || 'text-gray-100'}`}>{value}</p>
              </div>
            ))}
          </div>
          <Card>
            <CardHeader title="Dataset Fingerprint" />
            <CardBody>
              <div className="grid grid-cols-2 gap-3 text-xs">
                {[
                  ['Dataset ID',   MOCK_DATASET.dataset_id],
                  ['Name',         MOCK_DATASET.name],
                  ['Analyzed At',  new Date(MOCK_DATASET.analyzed_at).toLocaleString()],
                  ['Corrupted Files', MOCK_DATASET.corrupted],
                  ['Label Inconsistencies', MOCK_DATASET.label_inconsistencies],
                ].map(([k, v]) => (
                  <div key={k} className="bg-gray-800 rounded p-2">
                    <p className="text-gray-500">{k}</p>
                    <p className="text-gray-200 font-mono mt-0.5">{v}</p>
                  </div>
                ))}
                <div className="bg-gray-800 rounded p-2 col-span-2">
                  <p className="text-gray-500 mb-1">Dataset Hash (SHA-256)</p>
                  <HashDisplay hash={MOCK_DATASET.dataset_hash} maxLen={80} />
                </div>
              </div>
            </CardBody>
          </Card>
        </div>
      )}

      {activeTab === 'duplicates' && (
        <Card>
          <CardHeader title="Duplicate Clusters" subtitle="Exact (SHA-256) and near-duplicate (perceptual hash) clusters" />
          <CardBody>
            <p className="text-gray-500 text-xs mb-4 italic">
              ⚠ &quot;Potential duplicate flooding indicator&quot; — cannot determine intent. May be legitimate augmentation.
            </p>
            <div className="space-y-3">
              {MOCK_DUPLICATES.map((c) => (
                <div key={c.cluster_id} className="bg-gray-800 rounded-lg p-4 flex items-center gap-4">
                  <div className="flex-1">
                    <p className="text-gray-300 text-sm font-mono">{c.cluster_id}</p>
                    <p className="text-gray-500 text-xs mt-0.5">{c.indicator}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-gray-200 text-sm font-bold">{c.count}</p>
                    <p className="text-gray-500 text-xs">images</p>
                  </div>
                  <div className="text-center">
                    <p className="text-emerald-400 text-sm font-mono">{c.similarity}</p>
                    <p className="text-gray-500 text-xs">similarity</p>
                  </div>
                  <Badge label={c.severity} />
                </div>
              ))}
            </div>
          </CardBody>
        </Card>
      )}

      {activeTab === 'ood' && (
        <Card>
          <CardHeader title="OOD / Anomaly Detection" subtitle="Isolation Forest + distance-based scoring" />
          <CardBody>
            <p className="text-gray-500 text-xs mb-4 italic">
              ⚠ Detection based on statistical distance only — not semantic understanding. Scores are indicative.
            </p>
            <div className="space-y-2">
              {MOCK_OOD.map((s) => (
                <div key={s.sample_id} className="bg-gray-800 rounded-lg p-3 flex items-center gap-4">
                  <p className="text-gray-300 font-mono text-sm flex-1">{s.sample_id}</p>
                  <div>
                    <p className="text-xs text-gray-500">OOD Score</p>
                    <p className="text-orange-400 font-bold">{s.ood_score.toFixed(2)}</p>
                  </div>
                  <p className="text-gray-500 text-xs">{s.method}</p>
                  <Badge label={s.severity} />
                </div>
              ))}
            </div>
          </CardBody>
        </Card>
      )}

      {activeTab === 'verify' && (
        <Card>
          <CardHeader title="Artifact Verification" subtitle="Drag-and-drop a dataset file to verify integrity" />
          <CardBody><VerificationPanel /></CardBody>
        </Card>
      )}

      {activeTab === 'pipeline' && <PipelineVisualizer />}
    </div>
  );
}
