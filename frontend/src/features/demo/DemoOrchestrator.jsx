// Demo Orchestrator — section 34
// 18-step sequential demo with live progress bars and checkmarks
import { useState, useEffect, useRef } from 'react';
import { X, CheckCircle, Loader2, Clock } from 'lucide-react';
import { DEMO_STEPS } from '../../mock/mockData';

const PHASE_COLORS = {
  SETUP:     'text-gray-400',
  DATASET:   'text-blue-400',
  MODEL:     'text-purple-400',
  INFERENCE: 'text-amber-400',
  ATTACK:    'text-red-400',
  RISK:      'text-orange-400',
  REPORT:    'text-emerald-400',
};

const PHASE_BG = {
  SETUP:     'bg-gray-400',
  DATASET:   'bg-blue-500',
  MODEL:     'bg-purple-500',
  INFERENCE: 'bg-amber-500',
  ATTACK:    'bg-red-500',
  RISK:      'bg-orange-500',
  REPORT:    'bg-emerald-500',
};

export default function DemoOrchestrator({ onClose }) {
  const [running, setRunning] = useState(false);
  const [stepStatus, setStepStatus] = useState({}); // step -> 'running'|'done'
  const [currentStep, setCurrentStep] = useState(null);
  const [elapsed, setElapsed] = useState(0);
  const [done, setDone] = useState(false);
  const timerRef = useRef(null);
  const startRef = useRef(null);

  const completedCount = Object.values(stepStatus).filter(s => s === 'done').length;
  const overallPct = Math.round((completedCount / DEMO_STEPS.length) * 100);

  // Elapsed timer
  useEffect(() => {
    if (running) {
      startRef.current = Date.now() - elapsed * 1000;
      timerRef.current = setInterval(() => {
        setElapsed(Math.floor((Date.now() - startRef.current) / 1000));
      }, 500);
    } else {
      clearInterval(timerRef.current);
    }
    return () => clearInterval(timerRef.current);
  }, [running]);

  const runDemo = async () => {
    setRunning(true);
    setDone(false);
    setStepStatus({});
    setElapsed(0);

    for (const { step } of DEMO_STEPS) {
      setCurrentStep(step);
      setStepStatus(prev => ({ ...prev, [step]: 'running' }));
      // Simulate step duration: 600–1200ms each
      await new Promise(r => setTimeout(r, 600 + Math.random() * 600));
      setStepStatus(prev => ({ ...prev, [step]: 'done' }));
    }

    setRunning(false);
    setCurrentStep(null);
    setDone(true);
  };

  const fmt = (s) => `${Math.floor(s/60).toString().padStart(2,'0')}:${(s%60).toString().padStart(2,'0')}`;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="bg-gray-900 border border-gray-700 rounded-2xl w-full max-w-2xl max-h-[90vh] flex flex-col shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-800">
          <div>
            <h2 className="text-gray-100 font-bold text-base">COMPLETE SECURITY DEMO</h2>
            <p className="text-gray-500 text-xs mt-0.5">SIH26228 — TrustLens End-to-End Attack Detection Chain</p>
          </div>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-200 transition-colors">
            <X size={20} />
          </button>
        </div>

        {/* Overall progress bar */}
        <div className="px-6 py-3 border-b border-gray-800">
          <div className="flex items-center justify-between text-xs text-gray-400 mb-1.5">
            <span>{completedCount} / {DEMO_STEPS.length} steps complete</span>
            <div className="flex items-center gap-1.5">
              <Clock size={11} />
              {fmt(elapsed)}
            </div>
          </div>
          <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-emerald-500 rounded-full transition-all duration-300"
              style={{ width: `${overallPct}%` }}
            />
          </div>
        </div>

        {/* Steps list */}
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-2">
          {DEMO_STEPS.map(({ step, label, phase }) => {
            const status = stepStatus[step];
            const isRunning = status === 'running';
            const isDone    = status === 'done';
            const isPending = !status;

            return (
              <div
                key={step}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${
                  isRunning ? 'bg-emerald-500/10 border border-emerald-500/30' :
                  isDone    ? 'bg-gray-800/50' :
                  'opacity-50'
                }`}
              >
                {/* Step status icon */}
                <div className="w-5 flex-shrink-0 flex items-center justify-center">
                  {isDone    && <CheckCircle size={16} className="text-emerald-400" />}
                  {isRunning && <Loader2 size={16} className="text-emerald-400 animate-spin" />}
                  {isPending && <span className="w-4 h-4 rounded-full border border-gray-600 flex items-center justify-center text-gray-600 text-xs">{step}</span>}
                </div>

                {/* Step label */}
                <div className="flex-1 min-w-0">
                  <p className={`text-sm ${isDone ? 'text-gray-300' : isRunning ? 'text-gray-100 font-medium' : 'text-gray-500'}`}>
                    {label}
                  </p>
                </div>

                {/* Phase tag */}
                <span className={`text-xs font-mono flex-shrink-0 ${PHASE_COLORS[phase]}`}>{phase}</span>

                {/* Step progress bar */}
                {isRunning && (
                  <div className="w-16 h-1 bg-gray-700 rounded-full overflow-hidden flex-shrink-0">
                    <div className="h-full bg-emerald-500 rounded-full animate-pulse w-3/4" />
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-800 flex items-center gap-3">
          {done ? (
            <div className="flex-1 flex items-center gap-2 text-emerald-400 text-sm font-semibold">
              <CheckCircle size={16} /> All 18 steps complete — demo finished in {fmt(elapsed)}
            </div>
          ) : (
            <div className="flex-1 text-gray-500 text-xs">
              {running ? `Running step ${currentStep}/${DEMO_STEPS.length}…` : 'Ready to run. Press Start to begin.'}
            </div>
          )}

          <button
            onClick={onClose}
            className="px-4 py-2 text-xs text-gray-400 hover:text-gray-200 border border-gray-700 rounded-lg transition-colors"
          >
            Close
          </button>

          {!done && (
            <button
              onClick={runDemo}
              disabled={running}
              className="px-5 py-2 bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 text-black font-semibold text-sm rounded-lg transition-colors"
            >
              {running ? 'Running…' : 'Start Demo'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
