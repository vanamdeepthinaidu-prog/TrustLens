// Displays a hash string in a monospace chip with copy-to-clipboard
import { useState } from 'react';
import { Copy, Check } from 'lucide-react';

export default function HashDisplay({ hash, maxLen = 32 }) {
  const [copied, setCopied] = useState(false);
  if (!hash) return <span className="text-gray-600 text-xs font-mono">—</span>;
  const display = hash.length > maxLen ? hash.slice(0, maxLen) + '…' : hash;
  const copy = () => {
    navigator.clipboard.writeText(hash).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    });
  };
  return (
    <span className="inline-flex items-center gap-1.5 bg-gray-800 border border-gray-700 rounded px-2 py-0.5">
      <code className="text-emerald-400 text-xs font-mono">{display}</code>
      <button onClick={copy} className="text-gray-500 hover:text-gray-300 transition-colors">
        {copied ? <Check size={11} className="text-emerald-400" /> : <Copy size={11} />}
      </button>
    </span>
  );
}
