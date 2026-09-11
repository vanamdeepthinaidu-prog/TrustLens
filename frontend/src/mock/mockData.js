// ─── Mock data matching TrustLens spec schemas ───────────────────────────────
// Used when backend stubs are unavailable (offline demo / early dev)

export const mockTrustScore = {
  overall_score: 78.4,
  score_band: 'LOW',
  components: {
    dataset_integrity: { score: 82.1, weight: 0.30, weighted: 24.63 },
    model_integrity:   { score: 91.0, weight: 0.30, weighted: 27.30 },
    inference_integrity: { score: 68.5, weight: 0.25, weighted: 17.13 },
    distribution_stability: { score: 62.6, weight: 0.15, weighted: 9.39 },
  },
  calculation_detail: '(82.1×0.30) + (91.0×0.30) + (68.5×0.25) + (62.6×0.15) = 78.45',
  last_updated: '2026-09-10T07:00:00Z',
};

export const mockTrustHistory = [
  { ts: '2026-09-04', score: 91.2 },
  { ts: '2026-09-05', score: 88.7 },
  { ts: '2026-09-06', score: 74.3 },
  { ts: '2026-09-07', score: 70.1 },
  { ts: '2026-09-08', score: 72.9 },
  { ts: '2026-09-09', score: 76.0 },
  { ts: '2026-09-10', score: 78.4 },
];

export const mockSeverityDist = [
  { name: 'CRITICAL', value: 2,  color: '#ef4444' },
  { name: 'HIGH',     value: 5,  color: '#f97316' },
  { name: 'MEDIUM',   value: 11, color: '#eab308' },
  { name: 'LOW',      value: 8,  color: '#3b82f6' },
  { name: 'INFO',     value: 4,  color: '#6b7280' },
];

export const mockAnomalyDist = [
  { name: 'Exact Duplicate', value: 120 },
  { name: 'Near Duplicate',  value: 47  },
  { name: 'OOD Sample',      value: 23  },
  { name: 'Label Inconsistency', value: 15 },
  { name: 'Corrupted File', value: 6   },
];

export const mockProvenanceResults = [
  { name: 'Verified', value: 312, color: '#22c55e' },
  { name: 'Tampered', value: 4,   color: '#ef4444' },
  { name: 'Unverified', value: 18, color: '#6b7280' },
];

export const mockPipelineNodes = [
  {
    id: 'dataset',
    label: 'DATASET',
    status: 'VERIFIED',
    asset_id: 'DS-2026-001',
    hash: 'sha256:a3f2c1...e8d4b7',
    contributor: 'team-alpha',
    timestamp: '2026-09-09T14:22:00Z',
    findings: ['Near-duplicate cluster detected (47 images)', 'OOD samples flagged (23)'],
  },
  {
    id: 'model',
    label: 'MODEL',
    status: 'VERIFIED',
    asset_id: 'MDL-2026-001',
    hash: 'sha256:c9d1a0...f3e2b5',
    contributor: 'team-beta',
    timestamp: '2026-09-09T16:10:00Z',
    findings: ['Reference hash match confirmed'],
  },
  {
    id: 'inference',
    label: 'INFERENCE',
    status: 'TAMPERED',
    asset_id: 'INF-2026-042',
    hash: 'sha256:00b3f7...a1c9d2',
    contributor: 'operator-01',
    timestamp: '2026-09-10T06:55:00Z',
    findings: ['Record hash mismatch — tamper detected', 'Sequence anomaly in nonce reuse'],
  },
  {
    id: 'output',
    label: 'OUTPUT',
    status: 'UNVERIFIED',
    asset_id: 'OUT-2026-042',
    hash: null,
    contributor: null,
    timestamp: null,
    findings: ['Pending verification — upstream inference integrity compromised'],
  },
];

export const mockEvidenceItems = [
  {
    id: 'EVD-001',
    finding_type: 'NEAR_DUPLICATE_DETECTED',
    what_happened: 'Near-duplicate image cluster identified with 94% perceptual similarity.',
    why_flagged: 'Perceptual hash distance below threshold; cluster of 12 images with identical composition.',
    evidence: ['phash_cluster_12.json', 'similarity_matrix.csv'],
    severity: 'MEDIUM',
    confidence: 0.89,
    affected_asset: 'DS-2026-001',
    contributor: 'team-alpha',
    attack_type: 'duplicate_flooding',
    disposition: 'REVIEW',
    recommended_action: 'Investigate cluster origin; remove duplicates if unintentional.',
    limitations: 'Cannot determine intent — may be legitimate augmentation.',
    date: '2026-09-09T14:22:00Z',
  },
  {
    id: 'EVD-002',
    finding_type: 'OOD_SAMPLE_DETECTED',
    what_happened: 'Out-of-distribution samples detected in training batch.',
    why_flagged: 'Isolation Forest anomaly score 0.83 — well above 0.65 threshold.',
    evidence: ['ood_scores.json', 'embedding_viz.png'],
    severity: 'HIGH',
    confidence: 0.83,
    affected_asset: 'DS-2026-001',
    contributor: 'team-alpha',
    attack_type: 'ood_injection',
    disposition: 'REVIEW',
    recommended_action: 'Quarantine flagged samples pending manual review.',
    limitations: 'Detection method based on statistical distance, not semantic understanding.',
    date: '2026-09-09T14:30:00Z',
  },
  {
    id: 'EVD-003',
    finding_type: 'INFERENCE_TAMPER_DETECTED',
    what_happened: 'Inference record hash mismatch — record content may have been modified.',
    why_flagged: 'Recomputed hash 00b3f7... does not match stored hash a9f1c2...',
    evidence: ['tamper_report_INF-042.json'],
    severity: 'CRITICAL',
    confidence: 1.0,
    affected_asset: 'INF-2026-042',
    contributor: 'operator-01',
    attack_type: 'inference_tampering',
    disposition: 'QUARANTINE',
    recommended_action: 'Invalidate inference record and re-run under audited conditions.',
    limitations: 'Cannot determine what field was modified without prior snapshot.',
    date: '2026-09-10T06:55:00Z',
  },
  {
    id: 'EVD-004',
    finding_type: 'LABEL_INCONSISTENCY',
    what_happened: 'Potential label inconsistency detected via feature-cluster disagreement.',
    why_flagged: 'Nearest-neighbor cluster agreement below 60% for 15 samples.',
    evidence: ['label_check_report.json'],
    severity: 'LOW',
    confidence: 0.61,
    affected_asset: 'DS-2026-001',
    contributor: 'team-alpha',
    attack_type: null,
    disposition: 'PENDING',
    recommended_action: 'Manual label review recommended for flagged samples.',
    limitations: 'Detection uses feature similarity only — no semantic understanding.',
    date: '2026-09-09T15:00:00Z',
  },
  {
    id: 'EVD-005',
    finding_type: 'TRIGGER_SENSITIVITY',
    what_happened: 'Potential trigger-sensitive behavior observed on demo image with synthetic patch.',
    why_flagged: 'Model output changed from class 3 (confidence 0.91) to class 7 (confidence 0.94) after 20×20 patch applied.',
    evidence: ['trigger_sensitivity_demo.json'],
    severity: 'HIGH',
    confidence: 0.77,
    affected_asset: 'MDL-2026-001',
    contributor: 'team-beta',
    attack_type: 'trigger_injection',
    disposition: 'REVIEW',
    recommended_action: 'Conduct additional trigger sensitivity analysis across patch types.',
    limitations: 'Potential trigger-sensitive behavior — cannot confirm adversarial intent without broader investigation.',
    date: '2026-09-09T17:10:00Z',
  },
];

export const mockAuditLog = [
  { id: 'AUD-001', action: 'DATASET_UPLOADED',   actor: 'team-alpha',   asset: 'DS-2026-001', ts: '2026-09-09T13:00:00Z', hash: 'sha256:a3f2c1...e8d4b7', role: 'DATA_CONTRIBUTOR' },
  { id: 'AUD-002', action: 'DATASET_ANALYZED',   actor: 'system',       asset: 'DS-2026-001', ts: '2026-09-09T14:22:00Z', hash: 'sha256:b9d1f2...c3a4e5', role: 'SYSTEM' },
  { id: 'AUD-003', action: 'MODEL_UPLOADED',      actor: 'team-beta',    asset: 'MDL-2026-001', ts: '2026-09-09T16:10:00Z', hash: 'sha256:c9d1a0...f3e2b5', role: 'MODEL_TRAINER' },
  { id: 'AUD-004', action: 'FINGERPRINT_COMPUTED',actor: 'system',       asset: 'MDL-2026-001', ts: '2026-09-09T16:11:00Z', hash: 'sha256:d0e3b1...a2c9f6', role: 'SYSTEM' },
  { id: 'AUD-005', action: 'INFERENCE_RUN',        actor: 'operator-01',  asset: 'INF-2026-042', ts: '2026-09-10T06:54:00Z', hash: 'sha256:a9f1c2...d4b3e7', role: 'AUDITOR' },
  { id: 'AUD-006', action: 'TAMPER_DETECTED',      actor: 'system',       asset: 'INF-2026-042', ts: '2026-09-10T06:55:00Z', hash: 'sha256:00b3f7...a1c9d2', role: 'SYSTEM' },
  { id: 'AUD-007', action: 'EVIDENCE_QUARANTINED', actor: 'auditor-02',   asset: 'EVD-003',      ts: '2026-09-10T07:10:00Z', hash: 'sha256:f1a9c3...e2b4d6', role: 'AUDITOR' },
];

export const mockAttackTypes = [
  { id: 'label_flip',           label: 'Label Flip',           desc: 'Randomly reassign labels to n% of dataset samples.',    params: ['flip_percentage', 'random_seed'] },
  { id: 'duplicate_flooding',   label: 'Duplicate Flooding',   desc: 'Inject n copies of a selected image into the dataset.', params: ['copies', 'target_image', 'random_seed'] },
  { id: 'ood_injection',        label: 'OOD Injection',        desc: 'Inject out-of-distribution noise samples.',             params: ['count', 'noise_type', 'random_seed'] },
  { id: 'image_corruption',     label: 'Image Corruption',     desc: 'Apply blurring, compression artifacts, or truncation.', params: ['corruption_type', 'severity', 'random_seed'] },
  { id: 'metadata_manipulation',label: 'Metadata Manipulation',desc: 'Alter EXIF or annotation metadata fields.',             params: ['field', 'value', 'random_seed'] },
  { id: 'model_substitution',   label: 'Model Substitution',   desc: 'Swap registered model binary with a modified version.', params: ['model_id', 'random_seed'] },
  { id: 'trigger_injection',    label: 'Trigger Injection',    desc: 'Apply synthetic visual patch to demo images.',          params: ['patch_type', 'patch_size', 'random_seed'] },
  { id: 'inference_tampering',  label: 'Inference Tampering',  desc: 'Modify a field in a demo inference record.',            params: ['record_id', 'field', 'new_value'] },
  { id: 'replay_attack',        label: 'Replay Attack',        desc: 'Replay a previous inference record with reused nonce.', params: ['record_id', 'random_seed'] },
];

export const mockSimulations = [
  { sim_id: 'SIM-2026-00041', attack_type: 'label_flip',         status: 'COMPLETE', severity: 'HIGH',   ts: '2026-09-09T10:00:00Z', detected: true  },
  { sim_id: 'SIM-2026-00042', attack_type: 'duplicate_flooding', status: 'COMPLETE', severity: 'MEDIUM', ts: '2026-09-09T11:30:00Z', detected: true  },
  { sim_id: 'SIM-2026-00043', attack_type: 'model_substitution', status: 'COMPLETE', severity: 'HIGH',   ts: '2026-09-09T13:00:00Z', detected: true  },
  { sim_id: 'SIM-2026-00044', attack_type: 'inference_tampering',status: 'COMPLETE', severity: 'CRITICAL',ts:'2026-09-10T06:50:00Z', detected: true  },
  { sim_id: 'SIM-2026-00045', attack_type: 'replay_attack',      status: 'COMPLETE', severity: 'HIGH',   ts: '2026-09-10T07:00:00Z', detected: true  },
];

export const DEMO_STEPS = [
  { step: 1,  label: 'Initialize demo environment',           phase: 'SETUP'     },
  { step: 2,  label: 'Load demo dataset (CIFAR-10 subset)',   phase: 'DATASET'   },
  { step: 3,  label: 'Compute per-image SHA-256 hashes',      phase: 'DATASET'   },
  { step: 4,  label: 'Run duplicate detection analysis',      phase: 'DATASET'   },
  { step: 5,  label: 'Run OOD / anomaly detection',           phase: 'DATASET'   },
  { step: 6,  label: 'Run label consistency check',           phase: 'DATASET'   },
  { step: 7,  label: 'Load demo model (ResNet-18)',           phase: 'MODEL'     },
  { step: 8,  label: 'Compute model fingerprint',             phase: 'MODEL'     },
  { step: 9,  label: 'Verify model against reference hash',   phase: 'MODEL'     },
  { step: 10, label: 'Run baseline inference',                phase: 'INFERENCE' },
  { step: 11, label: 'Create provenance record chain',        phase: 'INFERENCE' },
  { step: 12, label: 'Simulate inference tampering attack',   phase: 'ATTACK'    },
  { step: 13, label: 'Detect tamper via hash verification',   phase: 'ATTACK'    },
  { step: 14, label: 'Simulate replay attack',                phase: 'ATTACK'    },
  { step: 15, label: 'Detect replay via nonce/sequence check',phase: 'ATTACK'    },
  { step: 16, label: 'Compute distribution shift score',      phase: 'RISK'      },
  { step: 17, label: 'Calculate composite trust score',       phase: 'RISK'      },
  { step: 18, label: 'Generate assurance report',             phase: 'REPORT'    },
];

export const mockSystemInfo = {
  version: '1.0.0-demo',
  build: 'SIH26228',
  backend_url: import.meta?.env?.VITE_API_BASE_URL || 'http://localhost:8000',
  ledger_type: 'SQLite tamper-evident chain',
  model: 'ResNet-18 (TorchVision)',
  hash_algorithm: 'SHA-256',
  offline_capable: true,
  detection_coverage: {
    supported: [
      'Exact duplicate detection (SHA-256)',
      'Near-duplicate detection (perceptual hash)',
      'Model hash verification',
      'Inference record tamper detection',
      'Replay attack detection (nonce/sequence)',
      'Audit chain integrity',
    ],
    partial: [
      'OOD / anomaly detection (statistical, not semantic)',
      'Trigger sensitivity (synthetic patches only)',
      'Distribution shift (brightness/quality/embedding distance)',
    ],
    unsupported: [
      'Real-time network traffic analysis',
      'Federated learning attack detection',
      'Hardware-level supply chain verification',
    ],
  },
};
