import { Card, CardHeader, CardBody } from '../components/ui/Card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const MOCK_SHIFT = {
  reference_dataset: 'DS-2026-REF',
  current_dataset:   'DS-2026-001',
  shift_score: 0.34,
  interpretation: 'MODERATE SHIFT',
  components: {
    brightness:   { ref_mean: 127.4, cur_mean: 114.2, diff: -13.2, shift: 0.28 },
    contrast:     { ref_mean: 48.1,  cur_mean: 51.7,  diff: 3.6,   shift: 0.07 },
    blur_score:   { ref_mean: 122.3, cur_mean: 98.5,  diff: -23.8, shift: 0.42 },
    file_size_kb: { ref_mean: 32.1,  cur_mean: 29.8,  diff: -2.3,  shift: 0.09 },
  },
  embedding_distance: {
    cosine: 0.21,
    interpretation: 'Moderate distributional separation',
  },
  limitation: 'This analysis uses statistical and embedding-level distance metrics only. It cannot identify the cause of distribution shift or determine whether any shift is adversarial.',
};

const shiftChartData = Object.entries(MOCK_SHIFT.components).map(([k, v]) => ({
  name: k,
  reference: parseFloat(v.ref_mean.toFixed(1)),
  current:   parseFloat(v.cur_mean.toFixed(1)),
}));

export default function DistributionShift() {
  return (
    <div className="space-y-5">
      {/* Shift score banner */}
      <div className={`rounded-xl border p-5 ${MOCK_SHIFT.shift_score > 0.5 ? 'border-red-500/40 bg-red-500/5' : MOCK_SHIFT.shift_score > 0.3 ? 'border-amber-500/40 bg-amber-500/5' : 'border-emerald-500/40 bg-emerald-500/5'}`}>
        <div className="flex items-center gap-4">
          <div>
            <p className="text-gray-500 text-xs">SHIFT SCORE</p>
            <p className="text-4xl font-bold text-amber-400">{MOCK_SHIFT.shift_score.toFixed(2)}</p>
          </div>
          <div>
            <p className="text-gray-500 text-xs">INTERPRETATION</p>
            <p className="text-amber-400 font-bold">{MOCK_SHIFT.interpretation}</p>
            <p className="text-gray-500 text-xs mt-1">{MOCK_SHIFT.reference_dataset} → {MOCK_SHIFT.current_dataset}</p>
          </div>
        </div>
        <p className="text-gray-500 text-xs mt-4 italic">{MOCK_SHIFT.limitation}</p>
      </div>

      {/* Component comparison */}
      <Card>
        <CardHeader title="Reference vs Current — Feature Statistics" />
        <CardBody>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={shiftChartData} barCategoryGap="30%">
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
              <XAxis dataKey="name" tick={{ fill: '#6b7280', fontSize: 11 }} />
              <YAxis tick={{ fill: '#6b7280', fontSize: 11 }} />
              <Tooltip contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: 6, fontSize: 12 }} />
              <Bar dataKey="reference" fill="#3b82f6" radius={[3,3,0,0]} name="Reference" />
              <Bar dataKey="current"   fill="#f97316" radius={[3,3,0,0]} name="Current" />
            </BarChart>
          </ResponsiveContainer>
        </CardBody>
      </Card>

      {/* Per-component table */}
      <Card>
        <CardHeader title="Per-Component Shift Breakdown" />
        <CardBody className="p-0">
          <table className="w-full text-xs">
            <thead className="border-b border-gray-800">
              <tr className="text-gray-500">
                <th className="text-left px-4 py-2">Feature</th>
                <th className="text-right px-4 py-2">Reference</th>
                <th className="text-right px-4 py-2">Current</th>
                <th className="text-right px-4 py-2">Δ</th>
                <th className="text-right px-4 py-2">Shift Score</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(MOCK_SHIFT.components).map(([k, v]) => (
                <tr key={k} className="border-b border-gray-800 hover:bg-gray-800/50">
                  <td className="px-4 py-2 font-mono text-gray-300">{k}</td>
                  <td className="px-4 py-2 text-right text-gray-400">{v.ref_mean}</td>
                  <td className="px-4 py-2 text-right text-gray-400">{v.cur_mean}</td>
                  <td className={`px-4 py-2 text-right font-mono ${v.diff < 0 ? 'text-red-400' : 'text-emerald-400'}`}>{v.diff > 0 ? '+' : ''}{v.diff}</td>
                  <td className="px-4 py-2 text-right text-amber-400 font-bold">{v.shift.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardBody>
      </Card>

      {/* Embedding distance */}
      <Card>
        <CardHeader title="Embedding Space Distance" subtitle="ResNet-18 penultimate layer" />
        <CardBody>
          <div className="flex gap-6">
            <div>
              <p className="text-gray-500 text-xs">Cosine Distance</p>
              <p className="text-2xl font-bold text-purple-400">{MOCK_SHIFT.embedding_distance.cosine.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-gray-500 text-xs">Interpretation</p>
              <p className="text-gray-300 text-sm mt-1">{MOCK_SHIFT.embedding_distance.interpretation}</p>
            </div>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
