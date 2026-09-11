// Pipeline Visualizer — section 27
// DATASET → MODEL → INFERENCE → OUTPUT node graph with status per node
import { useState } from 'react';
import { X, Hash, User, Clock, AlertTriangle, CheckCircle, HelpCircle } from 'lucide-react';
import Badge from '../../components/ui/Badge';
import HashDisplay from '../../components/ui/HashDisplay';
import { mockPipelineNodes } from '../../mock/mockData';

const STATUS_ICON = {
  VERIFIED:   <CheckCircle size={16} className="text-emerald-400" />,
  TAMPERED:   <AlertTriangle size={16} className="text-red-400" />,
  UNVERIFIED: <HelpCircle size={16} className="text-gray-500" />,
};

const STATUS_RING = {
  VERIFIED:   'border-emerald-500/50 shadow-emerald-500/20',
  TAMPERED:   'border-red-500/50    shadow-red-500/20',
  UNVERIFIED: 'border-gray-700      shadow-transparent',
};

const CONNECTOR_COLOR = {
  VERIFIED:   'bg-emerald-500',
  TAMPERED:   'bg-red-500',
  UNVERIFIED: 'bg-gray-700',
};

function PipelineNodeCard({ node, onClick, isSelected }) {
  return (
    <button
      onClick={() => onClick(node)}
      className={`relative flex flex-col items-center gap-2 bg-gray-900 border-2 rounded-xl px-5 py-4 min-w-[130px] transition-all shadow-lg
        ${STATUS_RING[node.status]}
        ${isSelected ? 'ring-2 ring-white/20' : ''}
        hover:scale-105`}
    >
      <div className="flex items-center gap-1.5 text-gray-300 text-xs font-mono font-bold tracking-wider">
        {STATUS_ICON[node.status]}
        {node.label}
      </div>
      <Badge label={node.status} />
      <p className="text-gray-600 text-xs">{node.asset_id || '—'}</p>
    </button>
  );
}

function Connector({ fromStatus }) {
  const color = CONNECTOR_COLOR[fromStatus] || 'bg-gray-700';
  return (
    <div className="flex items-center mx-1">
      <div className={`w-10 h-0.5 ${color} transition-colors`} />
      <div className={`w-0 h-0 border-t-4 border-b-4 border-l-6 border-transparent ${fromStatus === 'VERIFIED' ? 'border-l-emerald-500' : fromStatus === 'TAMPERED' ? 'border-l-red-500' : 'border-l-gray-700'}`}
        style={{ borderLeftWidth: 8, borderTopWidth: 5, borderBottomWidth: 5 }}
      />
    </div>
  );
}

function EvidencePanel({ node, onClose }) {
  return (
    <div className="bg-gray-900 border border-gray-700 rounded-xl p-5 w-80 flex-shrink-0 animate-in slide-in-from-right">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-gray-100 font-semibold text-sm">{node.label} — Evidence Detail</h3>
          <p className="text-gray-500 text-xs">{node.asset_id}</p>
        </div>
        <button onClick={onClose} className="text-gray-500 hover:text-gray-200"><X size={16} /></button>
      </div>

      <div className="space-y-3">
        <div>
          <p className="text-gray-500 text-xs mb-1">STATUS</p>
          <Badge label={node.status} />
        </div>

        <div>
          <p className="text-gray-500 text-xs mb-1 flex items-center gap-1"><Hash size={10} /> HASH</p>
          <HashDisplay hash={node.hash} />
        </div>

        {node.contributor && (
          <div>
            <p className="text-gray-500 text-xs mb-1 flex items-center gap-1"><User size={10} /> CONTRIBUTOR</p>
            <p className="text-gray-300 text-xs font-mono">{node.contributor}</p>
          </div>
        )}

        {node.timestamp && (
          <div>
            <p className="text-gray-500 text-xs mb-1 flex items-center gap-1"><Clock size={10} /> TIMESTAMP</p>
            <p className="text-gray-300 text-xs">{new Date(node.timestamp).toLocaleString()}</p>
          </div>
        )}

        <div>
          <p className="text-gray-500 text-xs mb-2">FINDINGS</p>
          <div className="space-y-1">
            {node.findings.map((f, i) => (
              <div key={i} className="flex items-start gap-1.5">
                <span className="text-amber-400 text-xs mt-0.5">•</span>
                <p className="text-gray-300 text-xs">{f}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function PipelineVisualizer() {
  const [selectedNode, setSelectedNode] = useState(null);
  const nodes = mockPipelineNodes;

  return (
    <div className="space-y-4">
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h3 className="text-gray-400 text-xs font-mono uppercase tracking-wider mb-6">AI PIPELINE INTEGRITY MAP</h3>

        {/* Node graph */}
        <div className="flex items-center justify-center overflow-x-auto pb-2">
          {nodes.map((node, i) => (
            <div key={node.id} className="flex items-center">
              <PipelineNodeCard
                node={node}
                onClick={setSelectedNode}
                isSelected={selectedNode?.id === node.id}
              />
              {i < nodes.length - 1 && <Connector fromStatus={nodes[i].status} />}
            </div>
          ))}
        </div>

        {/* Legend */}
        <div className="flex items-center gap-5 justify-center mt-6 text-xs text-gray-500">
          {[
            { label: 'VERIFIED',   color: 'bg-emerald-500' },
            { label: 'TAMPERED',   color: 'bg-red-500'     },
            { label: 'UNVERIFIED', color: 'bg-gray-600'    },
          ].map(({ label, color }) => (
            <div key={label} className="flex items-center gap-1.5">
              <span className={`w-2 h-2 rounded-full ${color}`} />
              {label}
            </div>
          ))}
        </div>
      </div>

      {/* Evidence panel */}
      {selectedNode && (
        <div className="flex justify-end">
          <EvidencePanel node={selectedNode} onClose={() => setSelectedNode(null)} />
        </div>
      )}
    </div>
  );
}
