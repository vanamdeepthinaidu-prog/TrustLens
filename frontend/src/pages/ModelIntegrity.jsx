import { Card, CardHeader, CardBody } from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import HashDisplay from '../components/ui/HashDisplay';
import VerificationPanel from '../features/verification/VerificationPanel';
import { useState } from 'react';

const MOCK_MODEL = {
  model_id: 'MDL-2026-001',
  name: 'ResNet-18 Demo',
  framework: 'PyTorch',
  architecture: 'ResNet-18',
  file_size_mb: 44.7,
  parameter_count: 11689512,
  input_shape: '[1, 3, 224, 224]',
  output_shape: '[1, 1000]',
  sha256: 'sha256:c9d1a0f3b7e2c5d8a4f1b9e3c6d2a8f5b1e4c7d3',
  reference_hash: 'sha256:c9d1a0f3b7e2c5d8a4f1b9e3c6d2a8f5b1e4c7d3',
  match_status: 'REFERENCE MATCH',
  contributor: 'team-beta',
  uploaded_at: '2026-09-09T16:10:00Z',
};

const MOCK_TRIGGER = {
  base_class: 3,
  base_confidence: 0.91,
  patched_class: 7,
  patched_confidence: 0.94,
  patch_type: 'square',
  patch_size: 20,
  finding: 'Potential trigger-sensitive behavior — cannot confirm adversarial intent without broader investigation.',
};

export default function ModelIntegrity() {
  const [tab, setTab] = useState('fingerprint');

  return (
    <div className="space-y-5">
      <div className="flex gap-1 bg-gray-900 border border-gray-800 rounded-lg p-1 w-fit">
        {['fingerprint','substitution','trigger','verify'].map(t => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-3 py-1.5 rounded text-xs font-medium capitalize transition-colors ${tab === t ? 'bg-gray-700 text-gray-100' : 'text-gray-500 hover:text-gray-300'}`}>
            {t === 'substitution' ? 'Hash Verification' : t === 'trigger' ? 'Trigger Sensitivity' : t}
          </button>
        ))}
      </div>

      {tab === 'fingerprint' && (
        <Card>
          <CardHeader title="Model Fingerprint" subtitle={`${MOCK_MODEL.name} — computed on upload`} />
          <CardBody>
            <div className="grid grid-cols-2 gap-3 text-xs">
              {[
                ['Model ID',         MOCK_MODEL.model_id],
                ['Framework',        MOCK_MODEL.framework],
                ['Architecture',     MOCK_MODEL.architecture],
                ['File Size',        `${MOCK_MODEL.file_size_mb} MB`],
                ['Parameter Count',  MOCK_MODEL.parameter_count.toLocaleString()],
                ['Input Shape',      MOCK_MODEL.input_shape],
                ['Output Shape',     MOCK_MODEL.output_shape],
                ['Contributor',      MOCK_MODEL.contributor],
                ['Uploaded At',      new Date(MOCK_MODEL.uploaded_at).toLocaleString()],
              ].map(([k, v]) => (
                <div key={k} className="bg-gray-800 rounded p-2">
                  <p className="text-gray-500">{k}</p>
                  <p className="text-gray-200 font-mono mt-0.5">{v}</p>
                </div>
              ))}
              <div className="col-span-2 bg-gray-800 rounded p-2">
                <p className="text-gray-500 mb-1">SHA-256 Fingerprint</p>
                <HashDisplay hash={MOCK_MODEL.sha256} maxLen={80} />
              </div>
            </div>
          </CardBody>
        </Card>
      )}

      {tab === 'substitution' && (
        <Card>
          <CardHeader title="Model Hash Verification" subtitle="Reference vs current comparison" />
          <CardBody>
            <div className="space-y-4">
              <div className={`rounded-lg p-4 border ${MOCK_MODEL.match_status === 'REFERENCE MATCH' ? 'border-emerald-500/40 bg-emerald-500/5 text-emerald-400' : 'border-red-500/40 bg-red-500/5 text-red-400'}`}>
                <p className="font-bold font-mono">{MOCK_MODEL.match_status}</p>
                <p className="text-xs mt-1 opacity-70">
                  {MOCK_MODEL.match_status === 'REFERENCE MATCH'
                    ? 'Registered reference hash matches current model binary.'
                    : 'MODEL BINARY DIFFERENCE — hashes do not match. This does not automatically indicate malicious substitution.'}
                </p>
              </div>
              <div className="grid grid-cols-1 gap-2">
                <div className="bg-gray-800 rounded p-3">
                  <p className="text-gray-500 text-xs mb-1">REFERENCE HASH</p>
                  <HashDisplay hash={MOCK_MODEL.reference_hash} maxLen={80} />
                </div>
                <div className="bg-gray-800 rounded p-3">
                  <p className="text-gray-500 text-xs mb-1">CURRENT HASH</p>
                  <HashDisplay hash={MOCK_MODEL.sha256} maxLen={80} />
                </div>
              </div>
            </div>
          </CardBody>
        </Card>
      )}

      {tab === 'trigger' && (
        <Card>
          <CardHeader title="Trigger Sensitivity Demo" subtitle="Synthetic patch applied to DEMO IMAGES ONLY" />
          <CardBody>
            <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg p-3 mb-4 text-amber-400 text-xs">
              ⚠ {MOCK_TRIGGER.finding}
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-800 rounded-lg p-4 text-center">
                <p className="text-gray-500 text-xs mb-2">BASELINE (no patch)</p>
                <p className="text-gray-200 text-2xl font-bold">Class {MOCK_TRIGGER.base_class}</p>
                <p className="text-emerald-400 text-sm mt-1">{(MOCK_TRIGGER.base_confidence * 100).toFixed(0)}% confidence</p>
              </div>
              <div className="bg-gray-800 rounded-lg p-4 text-center">
                <p className="text-gray-500 text-xs mb-2">WITH {MOCK_TRIGGER.patch_type.toUpperCase()} PATCH ({MOCK_TRIGGER.patch_size}×{MOCK_TRIGGER.patch_size}px)</p>
                <p className="text-red-400 text-2xl font-bold">Class {MOCK_TRIGGER.patched_class}</p>
                <p className="text-orange-400 text-sm mt-1">{(MOCK_TRIGGER.patched_confidence * 100).toFixed(0)}% confidence</p>
              </div>
            </div>
          </CardBody>
        </Card>
      )}

      {tab === 'verify' && (
        <Card>
          <CardHeader title="Model File Verification" subtitle="Drop a model file to check against registered hash" />
          <CardBody><VerificationPanel /></CardBody>
        </Card>
      )}
    </div>
  );
}
