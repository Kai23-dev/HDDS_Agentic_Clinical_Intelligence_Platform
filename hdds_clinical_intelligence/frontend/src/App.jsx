import { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Activity, AlertTriangle, CheckCircle, Clock, 
  FileText, ShieldAlert, HeartPulse, User
} from 'lucide-react';

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedPatientIndex, setSelectedPatientIndex] = useState(0);

  useEffect(() => {
    // Fetch insights from FastAPI backend
    axios.get('http://127.0.0.1:8000/api/insights')
      .then(response => {
        setData(response.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setError("Failed to load data. Ensure the FastAPI server is running.");
        setLoading(false);
      });
  }, []);

  if (loading) return (
    <div className="flex h-screen items-center justify-center">
      <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-teal-500"></div>
    </div>
  );

  if (error) return (
    <div className="flex h-screen items-center justify-center p-4 text-center">
      <div className="glass-card p-8 border-red-500/50">
        <AlertTriangle className="w-16 h-16 text-red-500 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-slate-100 mb-2">Connection Error</h2>
        <p className="text-slate-400">{error}</p>
        <p className="mt-4 text-sm">Did you run: <code>uvicorn api:app --reload</code> ?</p>
      </div>
    </div>
  );

  if (!data || !data.patients) return null;

  const currentPatient = data.patients[selectedPatientIndex];
  const { metadata } = data;
  const agentResults = currentPatient.agent_results;

  // Helper colors
  const riskColor = (level) => {
    const l = (level || '').toLowerCase();
    if (l === 'high') return 'text-red-500 bg-red-500/10 border-red-500/20';
    if (l === 'medium') return 'text-amber-500 bg-amber-500/10 border-amber-500/20';
    return 'text-green-500 bg-green-500/10 border-green-500/20';
  };

  return (
    <div className="min-h-screen p-4 md:p-8 max-w-7xl mx-auto space-y-8">
      {/* Header Banner */}
      <header className="glass-card p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-t-4 border-t-teal-500">
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-teal-400 to-blue-500">
            {metadata.project}
          </h1>
          <p className="text-slate-400 mt-1 flex items-center gap-2">
            <span className="badge bg-slate-700 text-slate-300">v{metadata.version}</span>
            Generated: {new Date(metadata.generated_at).toLocaleString()}
          </p>
        </div>
        <div className="bg-amber-500/10 border border-amber-500/30 p-3 rounded-lg max-w-sm text-sm text-amber-200/90">
          <strong>⚠️ Responsible AI:</strong> {metadata.responsible_ai_note}
        </div>
      </header>

      {/* Patient Selector */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {data.patients.map((p, idx) => (
          <button 
            key={p.patient_id}
            onClick={() => setSelectedPatientIndex(idx)}
            className={`flex items-center gap-2 px-4 py-3 rounded-xl border transition-all ${
              idx === selectedPatientIndex 
                ? 'bg-teal-500/20 border-teal-500/50 text-teal-300 shadow-[0_0_15px_rgba(20,184,166,0.2)]'
                : 'bg-slate-800/50 border-slate-700 hover:bg-slate-700/50 text-slate-400'
            }`}
          >
            <User className="w-4 h-4" />
            <span className="font-medium whitespace-nowrap">{p.patient_name}</span>
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left Column: Summary & KPIs */}
        <div className="space-y-6 md:col-span-1">
          {/* Main Risk KPI */}
          <div className={`glass-card p-6 text-center ${riskColor(agentResults.risk_assessment.risk_level)} border-t-4`}>
            <h3 className="text-sm uppercase tracking-wider opacity-80 mb-2">Overall Risk Level</h3>
            <div className="text-5xl font-extrabold my-4">{agentResults.risk_assessment.risk_level}</div>
            <div className="inline-flex items-center gap-2 bg-slate-900/50 rounded-full px-4 py-1 text-sm">
              <ShieldAlert className="w-4 h-4" /> Score: {agentResults.risk_assessment.risk_score}
            </div>
          </div>

          {/* Clinical Summary */}
          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold text-slate-200 mb-4 flex items-center gap-2">
              <FileText className="w-5 h-5 text-teal-400" /> Clinical Summary
            </h3>
            <p className="text-slate-300 text-sm leading-relaxed mb-4">
              {agentResults.clinical_summary.summary_text}
            </p>
            <div className="space-y-3">
              <div>
                <h4 className="text-xs uppercase text-slate-500 font-semibold mb-2">Conditions</h4>
                <div className="flex flex-wrap gap-2">
                  {agentResults.clinical_summary.active_conditions.map(c => (
                    <span key={c} className="badge bg-slate-700/50 border border-slate-600 text-slate-300">{c}</span>
                  ))}
                </div>
              </div>
              <div>
                <h4 className="text-xs uppercase text-slate-500 font-semibold mb-2 mt-4">Medications</h4>
                <div className="flex flex-wrap gap-2">
                  {agentResults.clinical_summary.current_medications.map(m => (
                    <span key={m} className="badge bg-blue-500/10 border border-blue-500/20 text-blue-300">{m}</span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Details */}
        <div className="space-y-6 md:col-span-2">
          
          {/* Flags & Detection */}
          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold text-slate-200 mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-red-400" /> Early Detection & Flags
            </h3>
            {agentResults.early_detection.total_flags > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                  <thead className="text-xs text-slate-400 bg-slate-800/50 uppercase">
                    <tr>
                      <th className="px-4 py-3 rounded-tl-lg">Test</th>
                      <th className="px-4 py-3">Value</th>
                      <th className="px-4 py-3 rounded-tr-lg">Severity</th>
                    </tr>
                  </thead>
                  <tbody>
                    {agentResults.early_detection.flagged_abnormal_results.map((lab, i) => (
                      <tr key={i} className="border-b border-slate-700/50 last:border-0">
                        <td className="px-4 py-3 font-medium text-slate-200">{lab.test_name}</td>
                        <td className="px-4 py-3 text-slate-300">{lab.value} <span className="text-slate-500">{lab.unit}</span></td>
                        <td className="px-4 py-3">
                          <span className={`badge ${riskColor(lab.severity)}`}>{lab.severity}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-slate-400 text-sm">No abnormal flags detected.</p>
            )}
          </div>

          {/* Recommendations & Follow-ups */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="glass-card p-6">
              <h3 className="text-lg font-semibold text-slate-200 mb-4 flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-400" /> Recommendations
              </h3>
              <ul className="space-y-3">
                {agentResults.recommendations.recommendations.map((rec, i) => (
                  <li key={i} className="p-3 bg-slate-800/40 rounded-lg border-l-2 border-l-green-500">
                    <div className="text-sm text-slate-200">{rec.recommendation}</div>
                    <div className="text-xs text-slate-500 mt-1 flex justify-between">
                      <span>{rec.category}</span>
                      <span className="uppercase text-green-400">{rec.priority}</span>
                    </div>
                  </li>
                ))}
              </ul>
            </div>

            <div className="glass-card p-6">
              <h3 className="text-lg font-semibold text-slate-200 mb-4 flex items-center gap-2">
                <Clock className="w-5 h-5 text-purple-400" /> Follow-up Actions
              </h3>
              <ul className="space-y-3">
                {agentResults.followup_actions.follow_up_actions.map((act, i) => (
                  <li key={i} className="flex gap-3 p-3 bg-slate-800/40 rounded-lg border border-slate-700/50">
                    <div className="w-4 h-4 mt-0.5 border border-slate-500 rounded flex-shrink-0"></div>
                    <div>
                      <div className="text-sm text-slate-200 font-medium">{act.action}</div>
                      <div className="text-xs text-slate-400 mt-1">{act.rationale}</div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>

        </div>
      </div>
      
    </div>
  );
}

export default App;
