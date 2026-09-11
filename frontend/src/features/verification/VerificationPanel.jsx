// Verification Panel — section 28
// Drag-and-drop file upload, client-side SHA-256, compare against backend registered hash
import { useState, useRef, useCallback } from 'react';
import { Upload, CheckCircle, XCircle, Loader2, FileText } from 'lucide-react';
import HashDisplay from '../../components/ui/HashDisplay';

async function sha256File(file) {
  const buf = await file.arrayBuffer();
  const hashBuf = await crypto.subtle.digest('SHA-256', buf);
  const arr = Array.from(new Uint8Array(hashBuf));
  return 'sha256:' + arr.map(b => b.toString(16).padStart(2, '0')).join('');
}

// Mock registered hashes (M1's real endpoint would supply these)
const MOCK_REGISTRY = {
  'demo_dataset.zip': {
    expected_hash: 'sha256:a3f2c1d8b9e5f4a2c7d3e8b1f9a4c2d7e3b8f5a1c9d4e2b7f3a8c1d9e5b4f2a7',
    contributor: 'team-alpha',
    asset_id: 'DS-2026-001',
    timestamp: '2026-09-09T13:00:00Z',
    parent_artifact: null,
    audit_records: ['AUD-001', 'AUD-002'],
  },
  'model.pt': {
    expected_hash: 'sha256:c9d1a0f3b7e2c5d8a4f1b9e3c6d2a8f5b1e4c7d3a9f2b6e1c4d8a5f3b7e0c2d9',
    contributor: 'team-beta',
    asset_id: 'MDL-2026-001',
    timestamp: '2026-09-09T16:10:00Z',
    parent_artifact: 'DS-2026-001',
    audit_records: ['AUD-003', 'AUD-004'],
  },
};

function DropZone({ onFile }) {
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef();

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) onFile(file);
  }, [onFile]);

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current.click()}
      className={`border-2 border-dashed rounded-xl p-10 flex flex-col items-center gap-3 cursor-pointer transition-colors
        ${dragging ? 'border-emerald-500 bg-emerald-500/5' : 'border-gray-700 hover:border-gray-600 bg-gray-900/50'}`}
    >
      <Upload size={28} className={dragging ? 'text-emerald-400' : 'text-gray-500'} />
      <p className="text-gray-400 text-sm">Drag & drop a file here, or click to browse</p>
      <p className="text-gray-600 text-xs">Supports: image, dataset ZIP, model .pt/.onnx, inference JSON</p>
      <input ref={inputRef} type="file" className="hidden" onChange={(e) => e.target.files[0] && onFile(e.target.files[0])} />
    </div>
  );
}

function VerificationResult({ result, file }) {
  const ok = result.status === 'VERIFIED';
  return (
    <div className={`rounded-xl border p-5 space-y-4 ${ok ? 'border-emerald-500/40 bg-emerald-500/5' : 'border-red-500/40 bg-red-500/5'}`}>
      {/* Header */}
      <div className="flex items-center gap-3">
        {ok
          ? <CheckCircle size={22} className="text-emerald-400" />
          : <XCircle size={22} className="text-red-400" />}
        <div>
          <p className={`font-bold text-base ${ok ? 'text-emerald-400' : 'text-red-400'}`}>
            {ok ? '✓ VERIFIED' : '✗ INTEGRITY VIOLATION'}
          </p>
          <p className="text-gray-500 text-xs">{file.name}</p>
        </div>
      </div>

      {/* Hash comparison */}
      <div className="grid grid-cols-1 gap-2">
        <div className="bg-gray-900 rounded p-3">
          <p className="text-gray-500 text-xs mb-1">EXPECTED HASH (registered)</p>
          <HashDisplay hash={result.expected_hash} maxLen={64} />
        </div>
        <div className={`rounded p-3 ${ok ? 'bg-gray-900' : 'bg-red-950/30'}`}>
          <p className="text-gray-500 text-xs mb-1">CURRENT HASH (computed now)</p>
          <HashDisplay hash={result.current_hash} maxLen={64} />
        </div>
      </div>

      {/* Metadata */}
      {result.meta && (
        <div className="grid grid-cols-2 gap-2 text-xs">
          {[
            ['Asset ID',       result.meta.asset_id],
            ['Contributor',    result.meta.contributor],
            ['Registered At',  result.meta.timestamp ? new Date(result.meta.timestamp).toLocaleString() : '—'],
            ['Parent Artifact',result.meta.parent_artifact || '—'],
          ].map(([k, v]) => (
            <div key={k} className="bg-gray-900 rounded p-2">
              <p className="text-gray-500">{k}</p>
              <p className="text-gray-200 font-mono mt-0.5 break-all">{v}</p>
            </div>
          ))}
        </div>
      )}

      {result.meta?.audit_records && (
        <div>
          <p className="text-gray-500 text-xs mb-1">LINKED AUDIT RECORDS</p>
          <div className="flex gap-2 flex-wrap">
            {result.meta.audit_records.map((id) => (
              <span key={id} className="bg-gray-800 border border-gray-700 rounded px-2 py-0.5 text-xs font-mono text-gray-300">{id}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function VerificationPanel() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const verify = async (f) => {
    setFile(f);
    setResult(null);
    setLoading(true);
    try {
      const current_hash = await sha256File(f);
      await new Promise(r => setTimeout(r, 800)); // simulate API call
      const reg = MOCK_REGISTRY[f.name];
      if (reg) {
        setResult({
          status: reg.expected_hash === current_hash ? 'VERIFIED' : 'INTEGRITY_VIOLATION',
          expected_hash: reg.expected_hash,
          current_hash,
          meta: reg,
        });
      } else {
        // Not in registry — show computed hash, no expected
        setResult({
          status: 'INTEGRITY_VIOLATION',
          expected_hash: null,
          current_hash,
          meta: null,
          note: 'File not found in artifact registry. Hash computed but no reference registered.',
        });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-5">
      <DropZone onFile={verify} />

      {loading && (
        <div className="flex items-center gap-3 text-gray-400 text-sm p-4 bg-gray-900 rounded-xl border border-gray-800">
          <Loader2 size={18} className="animate-spin text-emerald-400" />
          Computing SHA-256 and querying registry…
        </div>
      )}

      {result && file && !loading && (
        <VerificationResult result={result} file={file} />
      )}
    </div>
  );
}
