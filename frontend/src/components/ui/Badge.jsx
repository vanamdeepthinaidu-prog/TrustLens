const SEVERITY_STYLES = {
  CRITICAL:   'bg-red-500/20    text-red-400    border-red-500/30',
  HIGH:       'bg-orange-500/20 text-orange-400 border-orange-500/30',
  MEDIUM:     'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  LOW:        'bg-blue-500/20   text-blue-400   border-blue-500/30',
  INFO:       'bg-gray-700/50   text-gray-400   border-gray-600',
  VERIFIED:   'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  TAMPERED:   'bg-red-500/20    text-red-400    border-red-500/30',
  UNVERIFIED: 'bg-gray-700/50   text-gray-400   border-gray-600',
  TRUSTED:    'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  PENDING:    'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  QUARANTINE: 'bg-red-500/20    text-red-400    border-red-500/30',
  REVIEW:     'bg-amber-500/20  text-amber-400  border-amber-500/30',
  ACCEPT:     'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  COMPLETE:   'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  RUNNING:    'bg-blue-500/20   text-blue-400   border-blue-500/30',
};

export default function Badge({ label, className = '' }) {
  const style = SEVERITY_STYLES[label] || SEVERITY_STYLES.INFO;
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-mono border ${style} ${className}`}>
      {label}
    </span>
  );
}
