/*
  ProcessingView - Shows agent pipeline progress while the backend runs.
  Displays each of the 6 agents with a step indicator.
*/
import { useState, useEffect } from 'react';
import { CheckCircle, Loader2 } from 'lucide-react';

const AGENT_STEPS = [
  { name: 'Clinical Summary', desc: 'Extracting patient demographics, conditions, and medications' },
  { name: 'Risk Assessment', desc: 'Calculating overall risk level from clinical data' },
  { name: 'Early Detection', desc: 'Flagging abnormal lab values and monitoring gaps' },
  { name: 'Recommendations', desc: 'Generating treatment recommendation drafts' },
  { name: 'Evidence Validation', desc: 'Mapping assertions back to source data fields' },
  { name: 'Follow-up Actions', desc: 'Creating prioritized follow-up action items' },
];

export default function ProcessingView() {
  const [currentStep, setCurrentStep] = useState(0);

  // Simulate step progression while waiting for API
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev < AGENT_STEPS.length - 1) return prev + 1;
        return prev;
      });
    }, 800);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="max-w-2xl mx-auto px-6 py-16 text-center">
      <div className="relative w-16 h-16 mx-auto mb-6">
        <div className="absolute inset-0 rounded-full bg-[#ffe600]/30 pulse-ring"></div>
        <div className="relative w-16 h-16 bg-[#ffe600] rounded-full flex items-center justify-center">
          <Loader2 className="w-7 h-7 text-[#2e2e38] animate-spin" />
        </div>
      </div>

      <h2 className="text-2xl font-bold text-[#2e2e38] mb-2">Processing Patient Data</h2>
      <p className="text-gray-500 mb-10">Running AI agent pipeline...</p>

      <div className="text-left bg-white rounded-lg border border-gray-200 overflow-hidden">
        {AGENT_STEPS.map((step, i) => {
          const status = i < currentStep ? 'completed' : i === currentStep ? 'active' : 'pending';
          return (
            <div
              key={i}
              className={`flex items-center gap-4 px-5 py-4 border-b border-gray-100 last:border-0 ${
                status === 'active' ? 'bg-[#fffde6]' : ''
              }`}
            >
              <div className={`step-dot ${status}`}>
                {status === 'completed' ? (
                  <CheckCircle className="w-5 h-5" />
                ) : status === 'active' ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <span>{i + 1}</span>
                )}
              </div>
              <div>
                <p className={`text-sm font-semibold ${status === 'pending' ? 'text-gray-400' : 'text-[#2e2e38]'}`}>
                  {step.name}
                </p>
                <p className="text-xs text-gray-400">{step.desc}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
