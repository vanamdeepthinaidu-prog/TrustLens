import { useState, useMemo } from 'react';
import { Card, CardBody } from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import { mockEvidenceItems } from '../mock/mockData';
import { X, Filter, ChevronRight } from 'lucide-react';

const SEVERITIES = ['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO'];
const DISPOSITIONS = ['ALL', 'PENDING', 'REVIEW', 'QUARANTINE', 'ACCEPT'];

function EvidenceDetailDrawer({ item, onClose, onDispose }) {
  return (
    <div className="fixed inset-y-0 right-0 z-50 w-[420px] bg-gray-900 border-l border-gray-700 flex flex-col shadow-2xl">
      <div className="flex items-start justify-between px-5 py-4 border-b border-gray-800">
        <div>
          <p className="text-gray-200 font-semibold text-sm">{item.id}</p>
          <p className="text-gray-500 text-xs font-mono">{item.finding_type}</p>
        </div>
        <button onClick={onClose} className="text-gray-500 hover:text-gray-200"><X size={18} /></button>
      </div>

      <div className="flex-1 overflow-y-auto p-5 space-y-4 text-xs">
        {[
          { label: 'WHAT HAPPENED',      value: item.what_happened },
          { label: 'WHY FLAGGED',        value: item.why_flagged },
          { label: 'AFFECTED ASSET',     value: item.affected_asset },
          { label: 'CONTRIBUTOR',        value: item.contributor },
          { label: 'CONFIDENCE',         value: `${(item.confidence * 100).toFixed(0)}%` },
          { label: 'RECOMMENDED ACTION', value: item.recommended_action },
          { label: 'LIMITATIONS',        value: item.limitations },
        ].map(({ label, value }) => (
          <div key={label}>
            <p className="text-gray-500 font-mono mb-0.5">{label}</p>
            <p className="text-gray-300">{value}</p>
          </div>
        ))}

        <div>
          <p className="text-gray-500 font-mono mb-1">EVIDENCE</p>
          <div className="space-y-1">
            {item.evidence.map((e) => (
              <div key={e} className="bg-gray-800 rounded px-2 py-1 font-mono text-emerald-400">{e}</div>
            ))}
          </div>
        </div>

        <div className="flex gap-2 flex-wrap">
          <Badge label={item.severity} />
          {item.attack_type && <Badge label="ATTACK" />}
          <Badge label={item.disposition} />
        </div>
      </div>

      {/* Disposition buttons */}
      <div className="border-t border-gray-800 p-4">
        <p className="text-gray-500 text-xs mb-2">SET DISPOSITION</p>
        <div className="flex gap-2">
          {['ACCEPT','REVIEW','QUARANTINE'].map((d) => (
            <button
              key={d}
              onClick={() => onDispose(item.id, d)}
              className={`flex-1 py-2 rounded text-xs font-semibold transition-colors ${
                d === 'ACCEPT'     ? 'bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30 border border-emerald-500/30' :
                d === 'REVIEW'     ? 'bg-amber-500/20   text-amber-400   hover:bg-amber-500/30   border border-amber-500/30'   :
                                     'bg-red-500/20     text-red-400     hover:bg-red-500/30     border border-red-500/30'
              }`}
            >
              {d}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function EvidenceExplorer() {
  const [items, setItems] = useState(mockEvidenceItems);
  const [selected, setSelected] = useState(null);
  const [filterSev, setFilterSev] = useState('ALL');
  const [filterDisp, setFilterDisp] = useState('ALL');
  const [filterText, setFilterText] = useState('');

  const filtered = useMemo(() => items.filter((i) => {
    if (filterSev  !== 'ALL' && i.severity    !== filterSev)  return false;
    if (filterDisp !== 'ALL' && i.disposition !== filterDisp) return false;
    if (filterText && !JSON.stringify(i).toLowerCase().includes(filterText.toLowerCase())) return false;
    return true;
  }), [items, filterSev, filterDisp, filterText]);

  const handleDispose = (id, disposition) => {
    setItems(prev => prev.map(i => i.id === id ? { ...i, disposition } : i));
    setSelected(prev => prev?.id === id ? { ...prev, disposition } : prev);
  };

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-wrap gap-3 items-center">
        <div className="flex items-center gap-1.5 text-gray-500 text-xs">
          <Filter size={13} /> Severity:
        </div>
        <div className="flex gap-1">
          {SEVERITIES.map(s => (
            <button key={s} onClick={() => setFilterSev(s)}
              className={`px-2 py-0.5 rounded text-xs transition-colors ${filterSev === s ? 'bg-gray-700 text-gray-100' : 'text-gray-500 hover:text-gray-300'}`}>
              {s}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-1.5 text-gray-500 text-xs ml-4">Disposition:</div>
        <div className="flex gap-1">
          {DISPOSITIONS.map(d => (
            <button key={d} onClick={() => setFilterDisp(d)}
              className={`px-2 py-0.5 rounded text-xs transition-colors ${filterDisp === d ? 'bg-gray-700 text-gray-100' : 'text-gray-500 hover:text-gray-300'}`}>
              {d}
            </button>
          ))}
        </div>
        <input
          type="text" placeholder="Search…"
          value={filterText} onChange={(e) => setFilterText(e.target.value)}
          className="ml-auto bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-xs text-gray-200 focus:outline-none focus:border-emerald-500 w-40"
        />
      </div>

      <p className="text-gray-500 text-xs">{filtered.length} evidence items</p>

      {/* Evidence list */}
      <div className="space-y-2">
        {filtered.map((item) => (
          <button
            key={item.id}
            onClick={() => setSelected(item)}
            className={`w-full text-left bg-gray-900 border rounded-xl px-4 py-3 flex items-center gap-4 hover:bg-gray-800 transition-colors ${
              selected?.id === item.id ? 'border-emerald-500/40' : 'border-gray-800'
            }`}
          >
            <Badge label={item.severity} />
            <div className="flex-1 min-w-0">
              <p className="text-gray-200 text-sm font-medium truncate">{item.what_happened}</p>
              <div className="flex gap-3 mt-0.5 text-xs text-gray-500">
                <span className="font-mono">{item.id}</span>
                <span>{item.affected_asset}</span>
                {item.contributor && <span>{item.contributor}</span>}
                <span>{new Date(item.date).toLocaleDateString()}</span>
              </div>
            </div>
            <div className="flex items-center gap-2 flex-shrink-0">
              <Badge label={item.disposition} />
              <ChevronRight size={14} className="text-gray-600" />
            </div>
          </button>
        ))}
      </div>

      {/* Detail drawer */}
      {selected && (
        <>
          <div className="fixed inset-0 z-40 bg-black/30" onClick={() => setSelected(null)} />
          <EvidenceDetailDrawer item={selected} onClose={() => setSelected(null)} onDispose={handleDispose} />
        </>
      )}
    </div>
  );
}
