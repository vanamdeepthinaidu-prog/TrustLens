import { useState } from 'react';
import { Card, CardHeader, CardBody } from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import { mockAttackTypes, mockSimulations } from '../mock/mockData';
import { Play, Loader2, CheckCircle } from 'lucide-react';

function AttackCard({ attack, onRun }) {
  const [params, setParams] = useState({ random_seed: '42' });
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 space-y-3">
      <div>
        <p className="text-gray-200 font-semibold text-sm">{attack.label}</p>
        <p className="text-gray-500 text-xs mt-0.5">{attack.desc}</p>
      </div>
      <div className="space-y-2">
        {attack.params.map((p) => (
          <div key={p} className="flex items-center gap-2">
            <label className="text-gray-500 text-xs w-36 flex-shrink-0 font-mono">{p}</label>
            <input
              type="text"
              defaultValue={p === 'random_seed' ? '42' : ''}
              placeholder={p}
              className="flex-1 bg-gray-800 border border-gray-700 rounded px-2 py-1 text-xs text-gray-200 focus:outline-none focus:border-emerald-500"
              onChange={(e) => setParams(prev => ({ ...prev, [p]: e.target.value }))}
            />
          </div>
        ))}
      </div>
      <button
        onClick={() => onRun(attack.id, params)}
        className="flex items-center gap-1.5 px-3 py-1.5 bg-red-500/20 border border-red-500/30 text-red-400 hover:bg-red-500/30 rounded text-xs font-medium transition-colors"
      >
        <Play size={12} /> Run Simulation
      </button>
    </div>
  );
}

export default function SecurityLab() {
  const [sims, setSims] = useState(mockSimulations);
  const [running, setRunning] = useState(null);

  const handleRun = async (attackId, params) => {
    setRunning(attackId);
    await new Promise(r => setTimeout(r, 1500 + Math.random() * 1000));
    const newSim = {
      sim_id: `SIM-2026-${String(sims.length + 46).padStart(5, '0')}`,
      attack_type: attackId,
      status: 'COMPLETE',
      severity: ['LOW','MEDIUM','HIGH','CRITICAL'][Math.floor(Math.random()*4)],
      ts: new Date().toISOString(),
      detected: Math.random() > 0.1,
    };
    setSims(prev => [newSim, ...prev]);
    setRunning(null);
  };

  return (
    <div className="space-y-6">
      <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 text-xs text-red-400">
        ⚠ Security Lab operates on <strong>copies of demo data only</strong>. No original data is modified. Each simulation generates a unique SIM-XXXX ID with recorded seed for reproducibility.
      </div>

      {/* Attack type grid */}
      <div>
        <h3 className="text-gray-400 text-xs font-mono uppercase tracking-wider mb-3">ATTACK SIMULATIONS (9 TYPES)</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {mockAttackTypes.map((a) => (
            <div key={a.id} className="relative">
              {running === a.id && (
                <div className="absolute inset-0 bg-gray-900/80 rounded-xl z-10 flex items-center justify-center gap-2 text-emerald-400 text-sm">
                  <Loader2 size={16} className="animate-spin" /> Simulating…
                </div>
              )}
              <AttackCard attack={a} onRun={handleRun} />
            </div>
          ))}
        </div>
      </div>

      {/* Simulation results */}
      <Card>
        <CardHeader title="Simulation Results" subtitle={`${sims.length} runs recorded`} />
        <CardBody className="p-0">
          <table className="w-full text-xs">
            <thead className="border-b border-gray-800">
              <tr className="text-gray-500">
                <th className="text-left px-4 py-2">SIM ID</th>
                <th className="text-left px-4 py-2">Attack Type</th>
                <th className="text-left px-4 py-2">Timestamp</th>
                <th className="text-center px-4 py-2">Severity</th>
                <th className="text-center px-4 py-2">Status</th>
                <th className="text-center px-4 py-2">Detected</th>
              </tr>
            </thead>
            <tbody>
              {sims.map((s) => (
                <tr key={s.sim_id} className="border-b border-gray-800 hover:bg-gray-800/50">
                  <td className="px-4 py-2 font-mono text-emerald-400">{s.sim_id}</td>
                  <td className="px-4 py-2 text-gray-300">{s.attack_type.replace(/_/g,' ')}</td>
                  <td className="px-4 py-2 text-gray-500">{new Date(s.ts).toLocaleString()}</td>
                  <td className="px-4 py-2 text-center"><Badge label={s.severity} /></td>
                  <td className="px-4 py-2 text-center"><Badge label={s.status} /></td>
                  <td className="px-4 py-2 text-center">
                    {s.detected
                      ? <CheckCircle size={14} className="text-emerald-400 mx-auto" />
                      : <span className="text-red-400 font-mono">✗</span>}
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
