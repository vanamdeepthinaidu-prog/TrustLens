import { useState } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, BarChart, Bar, Legend,
} from 'recharts';
import { Card, CardHeader, CardBody } from '../components/ui/Card';
import ScoreRing from '../components/ui/ScoreRing';
import Badge from '../components/ui/Badge';
import {
  mockTrustScore, mockTrustHistory, mockSeverityDist,
  mockAnomalyDist, mockProvenanceResults,
} from '../mock/mockData';
import DemoOrchestrator from '../features/demo/DemoOrchestrator';

const BAND_COLORS = { CRITICAL:'#ef4444', HIGH:'#f97316', MEDIUM:'#eab308', LOW:'#3b82f6', TRUSTED:'#22c55e' };

const COMPONENT_INFO = [
  { key: 'dataset_integrity',    label: 'Dataset Integrity',       weight: '30%', color: '#22c55e' },
  { key: 'model_integrity',      label: 'Model Integrity',         weight: '30%', color: '#3b82f6' },
  { key: 'inference_integrity',  label: 'Inference Integrity',     weight: '25%', color: '#a855f7' },
  { key: 'distribution_stability',label:'Distribution Stability',  weight: '15%', color: '#f97316' },
];

function ComponentScoreCard({ label, weight, color, score, weighted }) {
  const bar = Math.min(100, score);
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
      <div className="flex items-start justify-between mb-2">
        <div>
          <p className="text-gray-400 text-xs">{label}</p>
          <p className="text-gray-600 text-xs">Weight: {weight}</p>
        </div>
        <div className="text-right">
          <span className="text-xl font-bold" style={{ color }}>{score.toFixed(1)}</span>
          <p className="text-gray-500 text-xs">+{weighted.toFixed(2)} pts</p>
        </div>
      </div>
      <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
        <div className="h-full rounded-full transition-all duration-700" style={{ width: `${bar}%`, backgroundColor: color }} />
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [showDemo, setShowDemo] = useState(false);
  const ts = mockTrustScore;

  return (
    <div className="space-y-6">
      {/* Demo trigger button */}
      <div className="flex justify-end">
        <button
          onClick={() => setShowDemo(true)}
          className="flex items-center gap-2 px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-black font-semibold text-sm rounded-lg transition-colors shadow-lg shadow-emerald-500/20"
        >
          ▶ RUN COMPLETE SECURITY DEMO
        </button>
      </div>

      {/* Trust score hero + components */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
        {/* Hero */}
        <Card className="lg:col-span-2">
          <CardHeader title="Composite Trust Score" subtitle={`Last updated ${new Date(ts.last_updated).toLocaleString()}`} />
          <CardBody className="flex flex-col items-center gap-4">
            <ScoreRing score={ts.overall_score} band={ts.score_band} size={160} />
            <div className="bg-gray-800 rounded px-3 py-2 w-full">
              <p className="text-gray-500 text-xs mb-1 font-mono">CALCULATION</p>
              <p className="text-gray-300 text-xs font-mono break-all">{ts.calculation_detail}</p>
            </div>
          </CardBody>
        </Card>

        {/* Component scores */}
        <div className="lg:col-span-3 grid grid-cols-2 gap-3">
          {COMPONENT_INFO.map(({ key, label, weight, color }) => {
            const comp = ts.components[key];
            return (
              <ComponentScoreCard
                key={key} label={label} weight={weight} color={color}
                score={comp.score} weighted={comp.weighted}
              />
            );
          })}
        </div>
      </div>

      {/* Key metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: 'Total Findings',    value: 30,   sub: 'across all checks' },
          { label: 'Critical Alerts',   value: 2,    sub: 'require immediate action', color: 'text-red-400' },
          { label: 'Simulations Run',   value: 5,    sub: 'attacks detected: 5/5' },
          { label: 'Audited Assets',    value: 334,  sub: 'provenance verified: 312' },
        ].map(({ label, value, sub, color }) => (
          <div key={label} className="bg-gray-900 border border-gray-800 rounded-lg p-4">
            <p className="text-gray-500 text-xs mb-1">{label}</p>
            <p className={`text-2xl font-bold ${color || 'text-gray-100'}`}>{value}</p>
            <p className="text-gray-600 text-xs mt-1">{sub}</p>
          </div>
        ))}
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Trust score over time */}
        <Card>
          <CardHeader title="Trust Score Over Time" subtitle="7-day rolling" />
          <CardBody>
            <ResponsiveContainer width="100%" height={180}>
              <LineChart data={mockTrustHistory}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                <XAxis dataKey="ts" tick={{ fill: '#6b7280', fontSize: 11 }} />
                <YAxis domain={[50, 100]} tick={{ fill: '#6b7280', fontSize: 11 }} />
                <Tooltip contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: 6, fontSize: 12 }} />
                <Line type="monotone" dataKey="score" stroke="#22c55e" strokeWidth={2} dot={{ fill: '#22c55e', r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </CardBody>
        </Card>

        {/* Severity distribution */}
        <Card>
          <CardHeader title="Severity Distribution" subtitle="All active findings" />
          <CardBody className="flex items-center gap-4">
            <ResponsiveContainer width="50%" height={180}>
              <PieChart>
                <Pie data={mockSeverityDist} cx="50%" cy="50%" innerRadius={45} outerRadius={70} dataKey="value" paddingAngle={2}>
                  {mockSeverityDist.map((entry) => <Cell key={entry.name} fill={entry.color} />)}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: 6, fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
            <div className="space-y-1.5">
              {mockSeverityDist.map(({ name, value, color }) => (
                <div key={name} className="flex items-center gap-2 text-xs">
                  <span className="w-2.5 h-2.5 rounded-sm flex-shrink-0" style={{ backgroundColor: color }} />
                  <span className="text-gray-400">{name}</span>
                  <span className="text-gray-200 font-semibold ml-auto pl-4">{value}</span>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>

        {/* Dataset anomaly distribution */}
        <Card>
          <CardHeader title="Dataset Anomaly Distribution" />
          <CardBody>
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={mockAnomalyDist}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                <XAxis dataKey="name" tick={{ fill: '#6b7280', fontSize: 10 }} />
                <YAxis tick={{ fill: '#6b7280', fontSize: 11 }} />
                <Tooltip contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: 6, fontSize: 12 }} />
                <Bar dataKey="value" fill="#3b82f6" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardBody>
        </Card>

        {/* Provenance verification results */}
        <Card>
          <CardHeader title="Provenance Verification Results" />
          <CardBody className="flex items-center gap-4">
            <ResponsiveContainer width="50%" height={180}>
              <PieChart>
                <Pie data={mockProvenanceResults} cx="50%" cy="50%" innerRadius={45} outerRadius={70} dataKey="value" paddingAngle={2}>
                  {mockProvenanceResults.map((entry) => <Cell key={entry.name} fill={entry.color} />)}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: 6, fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
            <div className="space-y-1.5">
              {mockProvenanceResults.map(({ name, value, color }) => (
                <div key={name} className="flex items-center gap-2 text-xs">
                  <span className="w-2.5 h-2.5 rounded-sm flex-shrink-0" style={{ backgroundColor: color }} />
                  <span className="text-gray-400">{name}</span>
                  <span className="text-gray-200 font-semibold ml-auto pl-4">{value}</span>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Demo Orchestrator modal */}
      {showDemo && <DemoOrchestrator onClose={() => setShowDemo(false)} />}
    </div>
  );
}
