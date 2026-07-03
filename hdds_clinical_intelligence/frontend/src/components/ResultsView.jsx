/*
  ResultsView - Displays the final AI-generated insights.
  Shows patient selector, KPIs, and detailed agent outputs.
*/
import { useState } from 'react';
import {
  ArrowLeft, User, ShieldAlert, AlertTriangle,
  CheckCircle, Clock, FileText, TrendingUp, ChevronDown, ChevronUp,
  MessageSquare, X, Send, Loader2
} from 'lucide-react';

// helper: risk level badge color
function riskStyles(level) {
  const l = (level || '').toLowerCase();
  if (l === 'high') return 'bg-red-100 text-red-700 border-red-200';
  if (l === 'medium') return 'bg-amber-100 text-amber-700 border-amber-200';
  return 'bg-green-100 text-green-700 border-green-200';
}

function severityColor(sev) {
  const s = (sev || '').toLowerCase();
  if (s === 'high') return 'text-red-600';
  if (s === 'moderate') return 'text-amber-600';
  return 'text-green-600';
}

// Collapsible section wrapper
function Section({ title, icon, children, defaultOpen = true }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="bg-white rounded-lg border border-gray-200 result-card">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-5 py-4 text-left hover:bg-gray-50 rounded-t-lg"
      >
        <div className="flex items-center gap-2">
          {icon}
          <h3 className="font-semibold text-[#2e2e38]">{title}</h3>
        </div>
        {open ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
      </button>
      {open && <div className="px-5 pb-5 border-t border-gray-100 pt-4">{children}</div>}
    </div>
  );
}

export default function ResultsView({ data, onBack, token, role }) {
  const [selectedIdx, setSelectedIdx] = useState(0);
  const [riskFilter, setRiskFilter] = useState('All');
  
  // Chat state
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState([
    { role: 'assistant', content: 'Hello doctor. I have analyzed this patient. What would you like to know?' }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [isChatLoading, setIsChatLoading] = useState(false);

  const handleSendChat = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userMessage = chatInput;
    setChatMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setChatInput('');
    setIsChatLoading(true);

    try {
      const pid = data.patients[selectedIdx].patient_id;
      // Depending on how Axios is configured globally in App, we use native fetch here for simplicity
      const response = await fetch('http://127.0.0.1:8000/api/chat', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ patient_id: pid, question: userMessage })
      });
      const result = await response.json();
      setChatMessages(prev => [...prev, { role: 'assistant', content: result.answer || 'Error getting response.' }]);
    } catch (err) {
      setChatMessages(prev => [...prev, { role: 'assistant', content: 'Network error communicating with Chat Agent.' }]);
    } finally {
      setIsChatLoading(false);
    }
  };

  if (!data || !data.patients || data.patients.length === 0) return null;

  const patient = data.patients[selectedIdx];
  const ar = patient.agent_results;
  const meta = data.metadata;

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      {/* Top bar */}
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={onBack}
          className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-[#2e2e38]"
        >
          <ArrowLeft className="w-4 h-4" /> Upload new document
        </button>
        <div className="flex items-center gap-4">
          {role === 'admin' && (
            <button className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 bg-red-50 hover:bg-red-100 text-red-700 border border-red-200 rounded transition-colors">
              <ShieldAlert className="w-3.5 h-3.5" /> Admin Settings
            </button>
          )}
          <button 
            onClick={() => window.print()}
            className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded transition-colors"
          >
            <FileText className="w-3.5 h-3.5" /> Export to PDF
          </button>
          <div className="text-xs text-gray-400">
            Generated: {new Date(meta.generated_at).toLocaleString()}
          </div>
        </div>
      </div>

      <div className="flex flex-col md:flex-row gap-6">
        
        {/* Sidebar Patient List */}
        {data.patients.length > 1 && (
          <div className="w-full md:w-64 flex-shrink-0">
            <div className="bg-white rounded-lg border border-gray-200 p-4 sticky top-6">
              <h3 className="font-semibold text-gray-700 mb-4 flex items-center gap-2">
                <User className="w-4 h-4" /> Patient List
              </h3>
              
              <div className="mb-4">
                <label className="text-xs font-medium text-gray-500 mb-1 block">Filter by Risk:</label>
                <select 
                  value={riskFilter}
                  onChange={(e) => setRiskFilter(e.target.value)}
                  className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:border-[#ffe600]"
                >
                  <option value="All">All Patients</option>
                  <option value="High">High Risk</option>
                  <option value="Medium">Medium Risk</option>
                  <option value="Low">Low Risk</option>
                </select>
              </div>

              <div className="space-y-2 max-h-[60vh] overflow-y-auto pr-1">
                {data.patients.map((p, i) => {
                  const pRisk = p.agent_results.risk_assessment.risk_level;
                  if (riskFilter !== 'All' && pRisk !== riskFilter) return null;
                  
                  return (
                    <button
                      key={p.patient_id}
                      onClick={() => setSelectedIdx(i)}
                      className={`w-full text-left px-3 py-2 rounded border transition-all ${
                        i === selectedIdx
                          ? 'bg-[#ffe600] border-[#e6cf00] text-[#2e2e38] shadow-sm'
                          : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100'
                      }`}
                    >
                      <div className="font-medium text-sm truncate">{p.patient_name}</div>
                      <div className={`text-[10px] font-bold mt-1 uppercase ${severityColor(pRisk === 'High' ? 'High' : pRisk === 'Medium' ? 'Moderate' : 'Low')}`}>
                        {pRisk} Risk
                      </div>
                    </button>
                  )
                })}
              </div>
            </div>
          </div>
        )}

        {/* Main Content Area */}
        <div className="flex-1 min-w-0">
          
          {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-lg border border-gray-200 p-4 result-card">
          <p className="text-xs text-gray-400 uppercase font-medium mb-1">Risk Level</p>
          <span className={`inline-block px-3 py-1 rounded-full text-sm font-bold border ${riskStyles(ar.risk_assessment.risk_level)}`}>
            {ar.risk_assessment.risk_level}
          </span>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4 result-card">
          <p className="text-xs text-gray-400 uppercase font-medium mb-1">Abnormal Flags</p>
          <p className="text-2xl font-bold text-[#2e2e38]">{ar.early_detection.total_flags || 0}</p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4 result-card">
          <p className="text-xs text-gray-400 uppercase font-medium mb-1">Recommendations</p>
          <p className="text-2xl font-bold text-[#2e2e38]">{ar.recommendations.total_recommendations || 0}</p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4 result-card">
          <p className="text-xs text-gray-400 uppercase font-medium mb-1">Validation</p>
          <span className={`inline-block px-3 py-1 rounded-full text-sm font-bold border ${
            ar.evidence_validation.validation_status === 'PASS'
              ? 'bg-green-100 text-green-700 border-green-200'
              : 'bg-amber-100 text-amber-700 border-amber-200'
          }`}>
            {ar.evidence_validation.validation_status}
          </span>
        </div>
      </div>

      {/* Agent Result Sections */}
      <div className="space-y-4">

        {/* Clinical Summary */}
        <Section title="Clinical Summary" icon={<FileText className="w-4 h-4 text-blue-500" />}>
          <p className="text-sm text-gray-600 leading-relaxed mb-4">{ar.clinical_summary.summary_text}</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-gray-400 font-medium uppercase mb-2">Active Conditions</p>
              <div className="space-y-2">
                {ar.clinical_summary.active_conditions.map((c, i) => (
                  <div key={i} className="text-xs bg-gray-50 border border-gray-100 p-2 rounded flex justify-between items-center group">
                    <div>
                      <span className="text-gray-700 font-medium">{c}</span>
                      <span className="ml-2 text-[9px] text-gray-400 uppercase bg-gray-200 px-1 rounded">Source: conditions.csv</span>
                    </div>
                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button className="px-1.5 py-0.5 bg-green-100 text-green-700 rounded border border-green-200 hover:bg-green-200">✓</button>
                      <button className="px-1.5 py-0.5 bg-red-100 text-red-700 rounded border border-red-200 hover:bg-red-200">✕</button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <div className="flex justify-between items-end mb-2">
                <p className="text-xs text-gray-400 font-medium uppercase">Current Medications</p>
                {ar.clinical_summary.medication_complexity && (
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${
                    ar.clinical_summary.medication_complexity.includes('High') 
                      ? 'bg-red-100 text-red-700' 
                      : ar.clinical_summary.medication_complexity === 'Moderate'
                      ? 'bg-amber-100 text-amber-700'
                      : 'bg-green-100 text-green-700'
                  }`}>
                    Complexity: {ar.clinical_summary.medication_complexity}
                  </span>
                )}
              </div>
              <div className="space-y-2">
                {ar.clinical_summary.current_medications.map((m, i) => (
                  <div key={i} className="text-xs bg-blue-50 border border-blue-100 p-2 rounded flex justify-between items-center group">
                    <div>
                      <span className="text-blue-800 font-medium">{m}</span>
                      <span className="ml-2 text-[9px] text-blue-400 uppercase bg-blue-100 px-1 rounded">Source: medications.csv</span>
                    </div>
                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button className="px-1.5 py-0.5 bg-green-100 text-green-700 rounded border border-green-200 hover:bg-green-200">✓</button>
                      <button className="px-1.5 py-0.5 bg-red-100 text-red-700 rounded border border-red-200 hover:bg-red-200">✕</button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </Section>

        {/* Risk Assessment */}
        <Section title="Risk Assessment" icon={<ShieldAlert className="w-4 h-4 text-red-500" />}>
          <div className="flex items-center gap-4 mb-4">
            <div className={`text-3xl font-extrabold px-5 py-2 rounded-lg border ${riskStyles(ar.risk_assessment.risk_level)}`}>
              {ar.risk_assessment.risk_level}
            </div>
            <div>
              <p className="text-sm text-gray-500">Score: <strong>{ar.risk_assessment.risk_score}</strong></p>
            </div>
          </div>
          {ar.risk_assessment.rationale && (
            <p className="text-sm text-gray-600 bg-gray-50 rounded p-3">{ar.risk_assessment.rationale}</p>
          )}
        </Section>

        {/* Early Detection */}
        <Section title="Early Detection Flags" icon={<AlertTriangle className="w-4 h-4 text-amber-500" />}>
          {ar.early_detection.flagged_abnormal_results && ar.early_detection.flagged_abnormal_results.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-xs text-gray-400 uppercase border-b border-gray-100">
                    <th className="pb-2 pr-4">Test</th>
                    <th className="pb-2 pr-4">Value</th>
                    <th className="pb-2 pr-4">Status</th>
                    <th className="pb-2">Severity</th>
                  </tr>
                </thead>
                <tbody>
                  {ar.early_detection.flagged_abnormal_results.map((lab, i) => (
                    <tr key={i} className="border-b border-gray-50 last:border-0">
                      <td className="py-2.5 pr-4 font-medium text-gray-700">{lab.test_name}</td>
                      <td className="py-2.5 pr-4 text-gray-600">
                        {lab.value} <span className="text-gray-400">{lab.unit}</span>
                      </td>
                      <td className="py-2.5 pr-4 text-gray-600">{lab.status}</td>
                      <td className={`py-2.5 font-semibold ${severityColor(lab.severity)}`}>{lab.severity}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-sm text-gray-400">No abnormal results flagged.</p>
          )}
        </Section>

        {/* Recommendations */}
        <Section title="Treatment Recommendations" icon={<CheckCircle className="w-4 h-4 text-green-500" />} defaultOpen={true}>
          <div className="space-y-3">
            {ar.recommendations.recommendations && ar.recommendations.recommendations.map((rec, i) => (
              <div key={i} className="border border-gray-100 rounded-lg p-3 flex justify-between items-start">
                <div className="flex gap-3">
                  <div className="flex-shrink-0 mt-0.5">
                    <TrendingUp className="w-4 h-4 text-green-500" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-700">{rec.recommendation}</p>
                    <div className="flex gap-3 mt-1.5 items-center">
                      <span className="text-[10px] text-gray-400 uppercase">{rec.category}</span>
                      <span className="text-[10px] text-[#b8a800] font-semibold uppercase">{rec.priority}</span>
                      {rec.source && (
                        <span className="text-[10px] bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded">
                          Source: {rec.source}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex flex-col gap-1.5 ml-4">
                  <button className="text-xs px-3 py-1 bg-green-50 text-green-600 hover:bg-green-100 rounded font-medium border border-green-200 whitespace-nowrap">
                    Accept
                  </button>
                  <button className="text-xs px-3 py-1 bg-red-50 text-red-600 hover:bg-red-100 rounded font-medium border border-red-200 whitespace-nowrap">
                    Reject
                  </button>
                </div>
              </div>
            ))}
          </div>
          <p className="text-xs text-gray-400 mt-3 italic">
            Draft -- Requires Clinician Review
          </p>
        </Section>

        {/* Follow-up Actions */}
        <Section title="Follow-up Actions" icon={<Clock className="w-4 h-4 text-purple-500" />} defaultOpen={false}>
          <div className="space-y-2">
            {ar.followup_actions.follow_up_actions && ar.followup_actions.follow_up_actions.map((act, i) => (
              <div key={i} className="flex items-start gap-3 py-2 border-b border-gray-50 last:border-0">
                <input type="checkbox" className="mt-1 accent-[#ffe600]" readOnly />
                <div>
                  <p className="text-sm text-gray-700 font-medium">{act.action}</p>
                  <p className="text-xs text-gray-400 mt-0.5">{act.rationale}</p>
                </div>
              </div>
            ))}
          </div>
        </Section>

      </div>

      {/* Footer disclaimer */}
      <div className="mt-8 bg-amber-50 border border-amber-200 rounded-lg p-4 text-center">
        <p className="text-xs text-amber-700">
          <strong>Responsible AI Notice:</strong> {meta.responsible_ai_note}
        </p>
      </div>
      
      </div> {/* Close Main Content Area */}
      
      </div> {/* Close Layout wrapper */}

      {/* Floating Chatbot UI */}
      {isChatOpen ? (
        <div className="fixed bottom-6 right-6 w-80 sm:w-96 bg-white rounded-xl shadow-2xl border border-gray-200 flex flex-col overflow-hidden z-50">
          <div className="bg-[#2e2e38] px-4 py-3 flex justify-between items-center">
            <div className="flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-[#ffe600]" />
              <h3 className="font-semibold text-white">Clinical Assistant</h3>
            </div>
            <button onClick={() => setIsChatOpen(false)} className="text-gray-400 hover:text-white">
              <X className="w-5 h-5" />
            </button>
          </div>
          
          <div className="flex-1 p-4 overflow-y-auto bg-gray-50 h-80 flex flex-col gap-3">
            {chatMessages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] p-3 rounded-lg text-sm ${
                  msg.role === 'user' 
                    ? 'bg-[#ffe600] text-[#2e2e38] rounded-br-none' 
                    : 'bg-white border border-gray-200 text-gray-700 rounded-bl-none shadow-sm'
                }`}>
                  {msg.content}
                </div>
              </div>
            ))}
            {isChatLoading && (
              <div className="flex justify-start">
                <div className="bg-white border border-gray-200 text-gray-500 rounded-lg rounded-bl-none p-3 shadow-sm">
                  <Loader2 className="w-4 h-4 animate-spin" />
                </div>
              </div>
            )}
          </div>
          
          <div className="p-3 border-t border-gray-200 bg-white">
            <form onSubmit={handleSendChat} className="flex items-center gap-2">
              <input
                type="text"
                value={chatInput}
                onChange={e => setChatInput(e.target.value)}
                placeholder="Ask about this patient..."
                className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#ffe600]"
              />
              <button 
                type="submit" 
                disabled={!chatInput.trim() || isChatLoading}
                className="bg-[#2e2e38] text-white p-2 rounded-lg hover:bg-black disabled:opacity-50"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        </div>
      ) : (
        <button
          onClick={() => setIsChatOpen(true)}
          className="fixed bottom-6 right-6 bg-[#2e2e38] text-white p-4 rounded-full shadow-xl hover:bg-black transition-transform hover:scale-105 z-50 flex items-center justify-center"
        >
          <MessageSquare className="w-6 h-6 text-[#ffe600]" />
        </button>
      )}

    </div>
  );
}
