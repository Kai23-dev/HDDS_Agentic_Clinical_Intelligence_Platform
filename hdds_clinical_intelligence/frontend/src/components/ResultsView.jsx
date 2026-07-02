/*
  ResultsView - Displays the final AI-generated insights.
  Shows patient selector, KPIs, and detailed agent outputs.
*/
import { useState } from 'react';
import {
  ArrowLeft, User, ShieldAlert, AlertTriangle,
  CheckCircle, Clock, FileText, TrendingUp, ChevronDown, ChevronUp
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

export default function ResultsView({ data, onBack }) {
  const [selectedIdx, setSelectedIdx] = useState(0);

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
        <div className="text-xs text-gray-400">
          Generated: {new Date(meta.generated_at).toLocaleString()}
        </div>
      </div>

      {/* Patient selector tabs */}
      {data.patients.length > 1 && (
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          {data.patients.map((p, i) => (
            <button
              key={p.patient_id}
              onClick={() => setSelectedIdx(i)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium border transition-all whitespace-nowrap ${
                i === selectedIdx
                  ? 'bg-[#ffe600] border-[#e6cf00] text-[#2e2e38] shadow-sm'
                  : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
              }`}
            >
              <User className="w-3.5 h-3.5" />
              {p.patient_name}
            </button>
          ))}
        </div>
      )}

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
              <div className="flex flex-wrap gap-1.5">
                {ar.clinical_summary.active_conditions.map((c, i) => (
                  <span key={i} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">{c}</span>
                ))}
              </div>
            </div>
            <div>
              <p className="text-xs text-gray-400 font-medium uppercase mb-2">Current Medications</p>
              <div className="flex flex-wrap gap-1.5">
                {ar.clinical_summary.current_medications.map((m, i) => (
                  <span key={i} className="text-xs bg-blue-50 text-blue-600 px-2 py-1 rounded">{m}</span>
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
              <div key={i} className="border border-gray-100 rounded-lg p-3 flex gap-3">
                <div className="flex-shrink-0 mt-0.5">
                  <TrendingUp className="w-4 h-4 text-green-500" />
                </div>
                <div>
                  <p className="text-sm text-gray-700">{rec.recommendation}</p>
                  <div className="flex gap-3 mt-1.5">
                    <span className="text-[10px] text-gray-400 uppercase">{rec.category}</span>
                    <span className="text-[10px] text-[#b8a800] font-semibold uppercase">{rec.priority}</span>
                  </div>
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
    </div>
  );
}
