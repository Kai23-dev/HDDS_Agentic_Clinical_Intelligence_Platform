#!/usr/bin/env python3
"""
HDDS Agentic Clinical Intelligence Platform — Dashboard Generator
=================================================================
Reads the combined AI medical insights JSON produced by the six clinical
intelligence agents and generates a stunning, self-contained static HTML
dashboard with inline CSS & JS (no external packages required).

Usage (from the hdds_clinical_intelligence directory):
    python dashboard/generate_dashboard.py

Output:
    dashboard/clinical_dashboard.html

Author : HDDS Clinical Intelligence Team
Version: 1.0.0
"""

import json
import os
import sys
from datetime import datetime
from html import escape

# ---------------------------------------------------------------------------
# Paths – all relative to the *hdds_clinical_intelligence* project root
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
INPUT_JSON = os.path.join(PROJECT_ROOT, "outputs", "ai_medical_insights.json")
OUTPUT_HTML = os.path.join(PROJECT_ROOT, "dashboard", "clinical_dashboard.html")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _esc(text) -> str:
    """HTML-escape any value, converting non-strings first."""
    return escape(str(text))


def _risk_color(level: str) -> str:
    m = {"high": "#ef4444", "medium": "#f59e0b", "low": "#22c55e"}
    return m.get(level.lower(), "#94a3b8")


def _severity_color(severity: str) -> str:
    m = {"high": "#ef4444", "moderate": "#f59e0b", "low": "#22c55e"}
    return m.get(severity.lower(), "#94a3b8")


def _priority_color(priority: str) -> str:
    m = {"urgent": "#ef4444", "high": "#f97316", "medium": "#f59e0b", "standard": "#14b8a6", "low": "#22c55e"}
    return m.get(priority.lower(), "#94a3b8")


def _priority_order(priority: str) -> int:
    m = {"urgent": 0, "high": 1, "medium": 2, "standard": 3, "low": 4}
    return m.get(priority.lower(), 5)


def _validation_color(status: str) -> str:
    return "#22c55e" if status.upper() == "PASS" else "#f59e0b"


def _fmt_datetime(raw: str) -> str:
    """Pretty-format an ISO datetime string."""
    try:
        dt = datetime.fromisoformat(raw)
        return dt.strftime("%B %d, %Y at %I:%M %p")
    except Exception:
        return raw


# ---------------------------------------------------------------------------
# Section builders — each returns an HTML string
# ---------------------------------------------------------------------------

def _build_kpi_cards(data: dict) -> str:
    risk = data["agent_results"]["risk_assessment"]
    early = data["agent_results"]["early_detection"]
    recs = data["agent_results"]["recommendations"]
    followup = data["agent_results"]["followup_actions"]
    evidence = data["agent_results"]["evidence_validation"]

    risk_level = risk["risk_level"]
    risk_score = risk["risk_score"]
    abnormal_count = early.get("total_flags", len(early.get("flagged_abnormal_results", [])))
    rec_count = recs.get("total_recommendations", len(recs.get("recommendations", [])))
    action_count = followup.get("total_actions", len(followup.get("follow_up_actions", [])))
    val_status = evidence.get("validation_status", "N/A")

    cards = []

    # 1 – Risk Level
    cards.append(f"""
    <div class="kpi-card" style="--accent:{_risk_color(risk_level)}">
        <div class="kpi-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="{_risk_color(risk_level)}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
        </div>
        <div class="kpi-label">Risk Level</div>
        <div class="kpi-value" style="color:{_risk_color(risk_level)}">{_esc(risk_level)}</div>
        <div class="kpi-sub">Score: {risk_score}/20</div>
    </div>""")

    # 2 – Abnormal Flags
    cards.append(f"""
    <div class="kpi-card" style="--accent:#f59e0b">
        <div class="kpi-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="18" x2="12" y2="12"/><line x1="9" y1="15" x2="15" y2="15"/></svg>
        </div>
        <div class="kpi-label">Abnormal Flags</div>
        <div class="kpi-value" style="color:#f59e0b">{abnormal_count}</div>
        <div class="kpi-sub">Lab results flagged</div>
    </div>""")

    # 3 – Recommendations
    cards.append(f"""
    <div class="kpi-card" style="--accent:#14b8a6">
        <div class="kpi-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#14b8a6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>
        </div>
        <div class="kpi-label">Recommendations</div>
        <div class="kpi-value" style="color:#14b8a6">{rec_count}</div>
        <div class="kpi-sub">Clinical actions drafted</div>
    </div>""")

    # 4 – Follow-up Actions
    cards.append(f"""
    <div class="kpi-card" style="--accent:#8b5cf6">
        <div class="kpi-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
        </div>
        <div class="kpi-label">Follow-up Actions</div>
        <div class="kpi-value" style="color:#8b5cf6">{action_count}</div>
        <div class="kpi-sub">Pending clinician review</div>
    </div>""")

    # 5 – Validation Status
    cards.append(f"""
    <div class="kpi-card" style="--accent:{_validation_color(val_status)}">
        <div class="kpi-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="{_validation_color(val_status)}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        </div>
        <div class="kpi-label">Validation</div>
        <div class="kpi-value" style="color:{_validation_color(val_status)}">{_esc(val_status)}</div>
        <div class="kpi-sub">{evidence.get('total_assertions_checked',0)} assertions checked</div>
    </div>""")

    return '<div class="kpi-grid">' + "\n".join(cards) + "</div>"


def _build_clinical_summary(cs: dict) -> str:
    enc = cs.get("latest_encounter", {})
    conditions_html = "".join(
        f'<span class="tag tag-condition">{_esc(c)}</span>' for c in cs.get("active_conditions", [])
    )
    medications_html = "".join(
        f'<span class="tag tag-med">{_esc(m)}</span>' for m in cs.get("current_medications", [])
    )

    labs_rows = ""
    for lab in cs.get("abnormal_labs", []):
        status_class = "badge-elevated" if "elevated" in lab["status"].lower() or "high" in lab["status"].lower() else "badge-low" if "low" in lab["status"].lower() else "badge-borderline"
        labs_rows += f"""
        <tr>
            <td>{_esc(lab['test'])}</td>
            <td class="mono">{_esc(lab['value'])} {_esc(lab['unit'])}</td>
            <td class="mono dim">{_esc(lab.get('reference_range',''))}</td>
            <td><span class="status-badge {status_class}">{_esc(lab['status'])}</span></td>
        </tr>"""

    return f"""
    <div class="section-card animate-in" id="sec-summary">
        <div class="section-header" onclick="toggleSection('summary-body')">
            <div class="section-title-group">
                <div class="section-icon" style="background:linear-gradient(135deg,#14b8a6,#0d9488)">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/></svg>
                </div>
                <div>
                    <h2 class="section-title">Clinical Summary</h2>
                    <span class="section-subtitle">Agent v{_esc(cs.get('version',''))}</span>
                </div>
            </div>
            <span class="chevron" id="chevron-summary-body">&#9660;</span>
        </div>
        <div class="section-body" id="summary-body">
            <p class="summary-text">{_esc(cs.get('summary_text',''))}</p>

            <div class="detail-grid">
                <div class="detail-box">
                    <h4>Active Conditions</h4>
                    <div class="tag-wrap">{conditions_html}</div>
                </div>
                <div class="detail-box">
                    <h4>Current Medications</h4>
                    <div class="tag-wrap">{medications_html}</div>
                </div>
            </div>

            <h3 class="sub-heading">Abnormal Lab Results</h3>
            <div class="table-wrap">
                <table>
                    <thead>
                        <tr><th>Test</th><th>Value</th><th>Ref Range</th><th>Status</th></tr>
                    </thead>
                    <tbody>{labs_rows}</tbody>
                </table>
            </div>

            <div class="encounter-box">
                <h4>Latest Encounter — {_esc(enc.get('date',''))}</h4>
                <p><strong>Reason:</strong> {_esc(enc.get('reason',''))}</p>
                <p><strong>Provider:</strong> {_esc(enc.get('provider',''))}</p>
                <p class="encounter-notes">{_esc(enc.get('notes',''))}</p>
            </div>
        </div>
    </div>"""


def _build_risk_assessment(ra: dict) -> str:
    level = ra["risk_level"]
    score = ra["risk_score"]
    bd = ra.get("score_breakdown", {})

    # Build mini donut chart using SVG
    pct = min(score / 20 * 100, 100)
    circumference = 2 * 3.14159 * 54
    dash = circumference * pct / 100
    gap = circumference - dash

    breakdown_items = f"""
        <div class="breakdown-item"><span class="bd-label">Conditions ({bd.get('conditions_count',0)})</span><span class="bd-pts">+{bd.get('conditions_points',0)} pts</span></div>
        <div class="breakdown-item"><span class="bd-label">Medications ({bd.get('medications_count',0)})</span><span class="bd-pts">+{bd.get('medications_points',0)} pts</span></div>
        <div class="breakdown-item"><span class="bd-label">Abnormal Labs ({bd.get('abnormal_labs_count',0)})</span><span class="bd-pts">+{bd.get('abnormal_labs_points',0)} pts</span></div>
    """

    return f"""
    <div class="section-card animate-in" id="sec-risk">
        <div class="section-header" onclick="toggleSection('risk-body')">
            <div class="section-title-group">
                <div class="section-icon" style="background:linear-gradient(135deg,{_risk_color(level)},#dc2626)">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
                </div>
                <div>
                    <h2 class="section-title">Risk Assessment</h2>
                    <span class="section-subtitle">Agent v{_esc(ra.get('version',''))}</span>
                </div>
            </div>
            <span class="chevron" id="chevron-risk-body">&#9660;</span>
        </div>
        <div class="section-body" id="risk-body">
            <div class="risk-hero">
                <div class="risk-donut-wrap">
                    <svg viewBox="0 0 120 120" class="risk-donut">
                        <circle cx="60" cy="60" r="54" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="10"/>
                        <circle cx="60" cy="60" r="54" fill="none" stroke="{_risk_color(level)}" stroke-width="10"
                            stroke-dasharray="{dash:.1f} {gap:.1f}" stroke-dashoffset="0"
                            stroke-linecap="round" transform="rotate(-90 60 60)" class="donut-progress"/>
                    </svg>
                    <div class="risk-donut-label">
                        <span class="risk-donut-score" style="color:{_risk_color(level)}">{score}</span>
                        <span class="risk-donut-max">/20</span>
                    </div>
                </div>
                <div class="risk-meta">
                    <div class="risk-badge" style="background:{_risk_color(level)}20;border:1px solid {_risk_color(level)}60;color:{_risk_color(level)}">
                        {_esc(level)} Risk
                    </div>
                    <div class="risk-breakdown">{breakdown_items}</div>
                </div>
            </div>
            <div class="rationale-box">
                <h4>Rationale</h4>
                <p>{_esc(ra.get('rationale',''))}</p>
            </div>
        </div>
    </div>"""


def _build_early_detection(ed: dict) -> str:
    # Flagged results table
    rows = ""
    for r in ed.get("flagged_abnormal_results", []):
        sev_color = _severity_color(r.get("severity", ""))
        rows += f"""
        <tr>
            <td>{_esc(r['test_name'])}</td>
            <td class="mono">{_esc(r['value'])} {_esc(r['unit'])}</td>
            <td class="mono dim">{_esc(r.get('reference_range',''))}</td>
            <td><span class="status-badge" style="background:{sev_color}18;color:{sev_color};border:1px solid {sev_color}40">{_esc(r['status'])}</span></td>
            <td><span class="severity-dot" style="background:{sev_color}"></span> {_esc(r.get('severity',''))}</td>
        </tr>"""

    # Chronic monitoring
    mon_items = ""
    for m in ed.get("chronic_monitoring_needs", []):
        icon = "✅" if m.get("recently_completed") else "⚠️"
        bar_class = "mon-done" if m.get("recently_completed") else "mon-gap"
        mon_items += f"""
        <div class="mon-item {bar_class}">
            <span class="mon-icon">{icon}</span>
            <div class="mon-detail">
                <span class="mon-test">{_esc(m['recommended_test'])}</span>
                <span class="mon-cond">{_esc(m['condition'])}</span>
            </div>
            <span class="mon-freq">{_esc(m['frequency'])}</span>
        </div>"""

    # Alerts
    alerts_html = ""
    for a in ed.get("alerts", []):
        alerts_html += f'<div class="alert-banner">{_esc(a)}</div>'

    return f"""
    <div class="section-card animate-in" id="sec-detection">
        <div class="section-header" onclick="toggleSection('detection-body')">
            <div class="section-title-group">
                <div class="section-icon" style="background:linear-gradient(135deg,#f59e0b,#d97706)">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                </div>
                <div>
                    <h2 class="section-title">Early Detection</h2>
                    <span class="section-subtitle">Agent v{_esc(ed.get('version',''))}</span>
                </div>
            </div>
            <span class="chevron" id="chevron-detection-body">&#9660;</span>
        </div>
        <div class="section-body" id="detection-body">
            {alerts_html}
            <h3 class="sub-heading">Flagged Abnormal Results</h3>
            <div class="table-wrap">
                <table>
                    <thead><tr><th>Test</th><th>Value</th><th>Ref Range</th><th>Status</th><th>Severity</th></tr></thead>
                    <tbody>{rows}</tbody>
                </table>
            </div>

            <h3 class="sub-heading">Chronic Monitoring Needs</h3>
            <div class="mon-list">{mon_items}</div>
        </div>
    </div>"""


def _build_recommendations(rec: dict) -> str:
    items = sorted(rec.get("recommendations", []), key=lambda x: _priority_order(x.get("priority", "")))
    cards = ""
    for r in items:
        pc = _priority_color(r.get("priority", ""))
        cards += f"""
        <div class="rec-card" style="--pri-color:{pc}">
            <div class="rec-top">
                <span class="rec-priority" style="background:{pc}20;color:{pc};border:1px solid {pc}40">{_esc(r.get('priority',''))}</span>
                <span class="rec-category">{_esc(r.get('category',''))}</span>
            </div>
            <p class="rec-text">{_esc(r.get('recommendation',''))}</p>
            <span class="rec-status">{_esc(r.get('status',''))}</span>
        </div>"""

    return f"""
    <div class="section-card animate-in" id="sec-recs">
        <div class="section-header" onclick="toggleSection('recs-body')">
            <div class="section-title-group">
                <div class="section-icon" style="background:linear-gradient(135deg,#14b8a6,#0d9488)">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>
                </div>
                <div>
                    <h2 class="section-title">Clinical Recommendations</h2>
                    <span class="section-subtitle">Agent v{_esc(rec.get('version',''))} · {len(items)} items</span>
                </div>
            </div>
            <span class="chevron" id="chevron-recs-body">&#9660;</span>
        </div>
        <div class="section-body" id="recs-body">
            <div class="rec-grid">{cards}</div>
            <p class="disclaimer-inline">{_esc(rec.get('disclaimer',''))}</p>
        </div>
    </div>"""


def _build_evidence_validation(ev: dict) -> str:
    total = ev.get("total_assertions_checked", 0)
    issues = ev.get("total_issues_found", 0)
    mapped = total - issues
    status = ev.get("validation_status", "N/A")

    rows = ""
    for e in ev.get("evidence_mappings", []):
        icon = "✅" if e.get("source_match_found") else "❌"
        match_class = "match-pass" if e.get("source_match_found") else "match-fail"
        detail = e.get("source_detail", "")
        if isinstance(detail, dict):
            detail = ", ".join(f"{k}: {v}" for k, v in detail.items())
        rows += f"""
        <tr class="{match_class}">
            <td>{icon}</td>
            <td>{_esc(e.get('assertion',''))}</td>
            <td class="dim">{_esc(e.get('source_field',''))}</td>
            <td class="dim small">{_esc(str(detail)[:120])}</td>
        </tr>"""

    issues_html = ""
    for iss in ev.get("validation_issues", []):
        issues_html += f'<div class="alert-banner alert-warning">{_esc(iss)}</div>'

    return f"""
    <div class="section-card animate-in" id="sec-evidence">
        <div class="section-header" onclick="toggleSection('evidence-body')">
            <div class="section-title-group">
                <div class="section-icon" style="background:linear-gradient(135deg,{_validation_color(status)},#15803d)">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                </div>
                <div>
                    <h2 class="section-title">Evidence Validation</h2>
                    <span class="section-subtitle">Agent v{_esc(ev.get('version',''))}</span>
                </div>
            </div>
            <span class="chevron" id="chevron-evidence-body">&#9660;</span>
        </div>
        <div class="section-body" id="evidence-body">
            <div class="evidence-stats">
                <div class="ev-stat"><span class="ev-num" style="color:#22c55e">{mapped}</span><span class="ev-lbl">Mapped</span></div>
                <div class="ev-stat"><span class="ev-num" style="color:#ef4444">{issues}</span><span class="ev-lbl">Issues</span></div>
                <div class="ev-stat"><span class="ev-num" style="color:#14b8a6">{total}</span><span class="ev-lbl">Total Checked</span></div>
                <div class="ev-stat">
                    <span class="ev-badge" style="background:{_validation_color(status)}20;color:{_validation_color(status)};border:1px solid {_validation_color(status)}40">{_esc(status)}</span>
                    <span class="ev-lbl">Status</span>
                </div>
            </div>
            {issues_html}
            <h3 class="sub-heading">Assertion → Source Mapping</h3>
            <div class="table-wrap">
                <table class="ev-table">
                    <thead><tr><th></th><th>Assertion</th><th>Source</th><th>Detail</th></tr></thead>
                    <tbody>{rows}</tbody>
                </table>
            </div>
        </div>
    </div>"""


def _build_followup_actions(fu: dict) -> str:
    actions = sorted(fu.get("follow_up_actions", []), key=lambda x: _priority_order(x.get("priority", "")))

    items_html = ""
    for i, a in enumerate(actions):
        pc = _priority_color(a.get("priority", ""))
        items_html += f"""
        <div class="fu-item" style="--fu-color:{pc}">
            <div class="fu-check">
                <input type="checkbox" id="fu-{i}" class="fu-checkbox">
                <label for="fu-{i}"></label>
            </div>
            <div class="fu-content">
                <div class="fu-top">
                    <span class="fu-priority" style="background:{pc}20;color:{pc};border:1px solid {pc}40">{_esc(a.get('priority',''))}</span>
                    <span class="fu-category">{_esc(a.get('category',''))}</span>
                </div>
                <p class="fu-action">{_esc(a.get('action',''))}</p>
                <p class="fu-rationale">{_esc(a.get('rationale',''))}</p>
                <span class="fu-status">{_esc(a.get('status',''))}</span>
            </div>
        </div>"""

    return f"""
    <div class="section-card animate-in" id="sec-followup">
        <div class="section-header" onclick="toggleSection('followup-body')">
            <div class="section-title-group">
                <div class="section-icon" style="background:linear-gradient(135deg,#8b5cf6,#7c3aed)">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                </div>
                <div>
                    <h2 class="section-title">Follow-up Actions</h2>
                    <span class="section-subtitle">Agent v{_esc(fu.get('version',''))} · {len(actions)} actions</span>
                </div>
            </div>
            <span class="chevron" id="chevron-followup-body">&#9660;</span>
        </div>
        <div class="section-body" id="followup-body">
            <div class="fu-list">{items_html}</div>
            <p class="disclaimer-inline">{_esc(fu.get('disclaimer',''))}</p>
        </div>
    </div>"""


# ---------------------------------------------------------------------------
# Master HTML template
# ---------------------------------------------------------------------------
def _full_html(data: dict) -> str:
    meta = data.get("metadata", {})
    project_name = meta.get("project", "Clinical Intelligence Dashboard")
    generated_at = _fmt_datetime(meta.get("generated_at", ""))
    ai_note = meta.get("responsible_ai_note", "")
    data_source = meta.get("data_source", "")
    version = meta.get("version", "")
    now = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    agent_results = data.get("agent_results", {})

    kpi_html = _build_kpi_cards(data)
    summary_html = _build_clinical_summary(agent_results.get("clinical_summary", {}))
    risk_html = _build_risk_assessment(agent_results.get("risk_assessment", {}))
    detection_html = _build_early_detection(agent_results.get("early_detection", {}))
    recs_html = _build_recommendations(agent_results.get("recommendations", {}))
    evidence_html = _build_evidence_validation(agent_results.get("evidence_validation", {}))
    followup_html = _build_followup_actions(agent_results.get("followup_actions", {}))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_esc(project_name)} — Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
/* ===== RESET & BASE ===== */
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth}}
body{{
    font-family:'Inter',system-ui,-apple-system,sans-serif;
    background:#0f172a;
    color:#e2e8f0;
    line-height:1.6;
    min-height:100vh;
    -webkit-font-smoothing:antialiased;
}}

/* Scrollbar */
::-webkit-scrollbar{{width:6px}}
::-webkit-scrollbar-track{{background:#1e293b}}
::-webkit-scrollbar-thumb{{background:#334155;border-radius:3px}}

/* ===== BACKGROUND EFFECTS ===== */
body::before{{
    content:'';position:fixed;top:0;left:0;width:100%;height:100%;
    background:
        radial-gradient(ellipse 80% 50% at 20% 20%, rgba(20,184,166,0.08) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 80%, rgba(139,92,246,0.06) 0%, transparent 60%),
        radial-gradient(ellipse 50% 50% at 50% 50%, rgba(15,23,42,0) 0%, #0f172a 100%);
    pointer-events:none;z-index:0;
}}

/* ===== LAYOUT ===== */
.dashboard-wrapper{{position:relative;z-index:1;max-width:1280px;margin:0 auto;padding:0 24px 60px}}

/* ===== TOP BANNER ===== */
.top-banner{{
    margin-top:24px;padding:32px 40px;
    background:linear-gradient(135deg,rgba(20,184,166,0.12) 0%,rgba(139,92,246,0.08) 100%);
    border:1px solid rgba(255,255,255,0.06);
    border-radius:20px;
    backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
    position:relative;overflow:hidden;
}}
.top-banner::before{{
    content:'';position:absolute;top:0;left:0;right:0;height:1px;
    background:linear-gradient(90deg,transparent,rgba(20,184,166,0.4),rgba(139,92,246,0.3),transparent);
}}
.banner-row{{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:16px}}
.banner-left h1{{
    font-size:1.75rem;font-weight:800;
    background:linear-gradient(135deg,#e2e8f0,#14b8a6);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    background-clip:text;letter-spacing:-0.02em;
}}
.banner-left .version{{font-size:0.75rem;color:#64748b;margin-top:2px;letter-spacing:0.05em;text-transform:uppercase}}
.banner-right{{text-align:right}}
.banner-right .timestamp{{font-size:0.82rem;color:#94a3b8}}
.banner-right .data-source{{font-size:0.72rem;color:#64748b;margin-top:2px}}
.ai-banner{{
    margin-top:16px;padding:12px 18px;
    background:rgba(245,158,11,0.08);
    border:1px solid rgba(245,158,11,0.18);
    border-radius:10px;font-size:0.8rem;color:#fbbf24;
    display:flex;align-items:flex-start;gap:10px;line-height:1.5;
}}
.ai-banner svg{{flex-shrink:0;margin-top:1px}}

/* ===== KPI GRID ===== */
.kpi-grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:16px;margin-top:24px}}
.kpi-card{{
    background:rgba(30,41,59,0.6);
    border:1px solid rgba(255,255,255,0.06);
    border-radius:16px;padding:24px 20px;
    backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);
    text-align:center;transition:all 0.3s ease;position:relative;overflow:hidden;
}}
.kpi-card::before{{
    content:'';position:absolute;top:0;left:0;right:0;height:2px;
    background:linear-gradient(90deg,transparent,var(--accent),transparent);opacity:0.6;
}}
.kpi-card:hover{{transform:translateY(-4px);border-color:rgba(255,255,255,0.12);box-shadow:0 20px 40px rgba(0,0,0,0.3)}}
.kpi-icon{{margin:0 auto 12px;width:48px;height:48px;border-radius:12px;display:flex;align-items:center;justify-content:center;background:rgba(255,255,255,0.04)}}
.kpi-label{{font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;color:#64748b;font-weight:600}}
.kpi-value{{font-size:1.75rem;font-weight:800;margin:4px 0;letter-spacing:-0.02em}}
.kpi-sub{{font-size:0.72rem;color:#475569}}

/* ===== SECTION CARDS ===== */
.section-card{{
    margin-top:20px;
    background:rgba(30,41,59,0.45);
    border:1px solid rgba(255,255,255,0.06);
    border-radius:16px;
    backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
    overflow:hidden;transition:all 0.3s ease;
}}
.section-card:hover{{border-color:rgba(255,255,255,0.1)}}
.section-header{{
    display:flex;align-items:center;justify-content:space-between;
    padding:20px 28px;cursor:pointer;user-select:none;
    transition:background 0.2s;
}}
.section-header:hover{{background:rgba(255,255,255,0.02)}}
.section-title-group{{display:flex;align-items:center;gap:16px}}
.section-icon{{width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center;flex-shrink:0}}
.section-title{{font-size:1.15rem;font-weight:700;color:#f1f5f9;letter-spacing:-0.01em}}
.section-subtitle{{font-size:0.72rem;color:#64748b;letter-spacing:0.02em}}
.chevron{{font-size:0.7rem;color:#64748b;transition:transform 0.3s ease;display:inline-block}}
.chevron.collapsed{{transform:rotate(-90deg)}}
.section-body{{padding:0 28px 28px;}}
.section-body.hidden{{display:none}}

/* ===== COMMON ELEMENTS ===== */
.sub-heading{{font-size:0.85rem;font-weight:600;color:#94a3b8;margin:24px 0 12px;text-transform:uppercase;letter-spacing:0.06em}}
.summary-text{{font-size:0.95rem;color:#cbd5e1;line-height:1.7;padding:12px 0}}
.detail-grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:8px}}
.detail-box{{background:rgba(15,23,42,0.5);border:1px solid rgba(255,255,255,0.04);border-radius:12px;padding:16px 20px}}
.detail-box h4{{font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em;color:#64748b;margin-bottom:10px;font-weight:600}}
.tag-wrap{{display:flex;flex-wrap:wrap;gap:8px}}
.tag{{padding:5px 14px;border-radius:8px;font-size:0.78rem;font-weight:500}}
.tag-condition{{background:rgba(239,68,68,0.12);color:#fca5a5;border:1px solid rgba(239,68,68,0.2)}}
.tag-med{{background:rgba(20,184,166,0.12);color:#5eead4;border:1px solid rgba(20,184,166,0.2)}}

/* ===== TABLES ===== */
.table-wrap{{overflow-x:auto;border-radius:10px;border:1px solid rgba(255,255,255,0.05)}}
table{{width:100%;border-collapse:collapse}}
thead{{background:rgba(15,23,42,0.6)}}
th{{padding:10px 16px;text-align:left;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.08em;color:#64748b;font-weight:600;border-bottom:1px solid rgba(255,255,255,0.06)}}
td{{padding:12px 16px;font-size:0.85rem;border-bottom:1px solid rgba(255,255,255,0.03)}}
tr:hover{{background:rgba(255,255,255,0.02)}}
.mono{{font-family:'SF Mono','Cascadia Code','Consolas',monospace;font-size:0.82rem}}
.dim{{color:#64748b}}
.small{{font-size:0.75rem}}
.status-badge{{
    display:inline-block;padding:3px 10px;border-radius:6px;font-size:0.72rem;font-weight:600;
}}
.badge-elevated{{background:rgba(239,68,68,0.15);color:#fca5a5;border:1px solid rgba(239,68,68,0.25)}}
.badge-borderline{{background:rgba(245,158,11,0.15);color:#fcd34d;border:1px solid rgba(245,158,11,0.25)}}
.badge-low{{background:rgba(59,130,246,0.15);color:#93c5fd;border:1px solid rgba(59,130,246,0.25)}}
.severity-dot{{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:4px;vertical-align:middle}}

/* ===== ENCOUNTER BOX ===== */
.encounter-box{{
    margin-top:20px;padding:18px 22px;
    background:rgba(15,23,42,0.5);border:1px solid rgba(255,255,255,0.04);border-radius:12px;
}}
.encounter-box h4{{font-size:0.85rem;color:#14b8a6;margin-bottom:10px;font-weight:600}}
.encounter-box p{{font-size:0.84rem;color:#94a3b8;margin-bottom:4px}}
.encounter-notes{{font-style:italic;color:#64748b !important;margin-top:8px !important;line-height:1.6}}

/* ===== RISK SECTION ===== */
.risk-hero{{display:flex;align-items:center;gap:48px;padding:20px 0}}
.risk-donut-wrap{{position:relative;width:140px;height:140px;flex-shrink:0}}
.risk-donut{{width:100%;height:100%}}
.donut-progress{{animation:donutFill 1.5s ease-out forwards}}
@keyframes donutFill{{from{{stroke-dasharray:0 340}}}}
.risk-donut-label{{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center}}
.risk-donut-score{{font-size:2rem;font-weight:800;display:block;line-height:1}}
.risk-donut-max{{font-size:0.8rem;color:#475569}}
.risk-meta{{flex:1}}
.risk-badge{{
    display:inline-block;padding:8px 20px;border-radius:10px;
    font-size:0.9rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;
    margin-bottom:20px;
}}
.risk-breakdown{{display:flex;flex-direction:column;gap:8px}}
.breakdown-item{{display:flex;justify-content:space-between;align-items:center;padding:8px 14px;background:rgba(15,23,42,0.5);border-radius:8px;border:1px solid rgba(255,255,255,0.04)}}
.bd-label{{font-size:0.82rem;color:#94a3b8}}
.bd-pts{{font-size:0.82rem;font-weight:600;color:#e2e8f0;font-family:'SF Mono','Cascadia Code','Consolas',monospace}}
.rationale-box{{margin-top:16px;padding:16px 20px;background:rgba(15,23,42,0.5);border-radius:12px;border:1px solid rgba(255,255,255,0.04)}}
.rationale-box h4{{font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em;color:#64748b;margin-bottom:8px}}
.rationale-box p{{font-size:0.84rem;color:#94a3b8;line-height:1.6}}

/* ===== ALERT BANNERS ===== */
.alert-banner{{
    padding:12px 18px;margin-bottom:16px;border-radius:10px;font-size:0.82rem;font-weight:500;
    background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.25);color:#fca5a5;
    display:flex;align-items:center;gap:8px;
}}
.alert-banner::before{{content:'🚨'}}
.alert-warning{{background:rgba(245,158,11,0.1);border-color:rgba(245,158,11,0.25);color:#fcd34d}}
.alert-warning::before{{content:'⚠️'}}

/* ===== MONITORING LIST ===== */
.mon-list{{display:flex;flex-direction:column;gap:6px}}
.mon-item{{
    display:flex;align-items:center;gap:14px;padding:12px 16px;border-radius:10px;
    border:1px solid rgba(255,255,255,0.04);background:rgba(15,23,42,0.3);transition:all 0.2s;
}}
.mon-item:hover{{background:rgba(15,23,42,0.6)}}
.mon-icon{{font-size:1.1rem}}
.mon-detail{{flex:1;display:flex;flex-direction:column}}
.mon-test{{font-size:0.85rem;font-weight:600;color:#e2e8f0}}
.mon-cond{{font-size:0.72rem;color:#64748b}}
.mon-freq{{font-size:0.75rem;color:#475569;text-align:right;max-width:220px}}
.mon-gap{{border-left:3px solid #f59e0b}}
.mon-done{{border-left:3px solid #22c55e}}

/* ===== RECOMMENDATIONS ===== */
.rec-grid{{display:grid;grid-template-columns:1fr;gap:12px}}
.rec-card{{
    padding:18px 22px;border-radius:12px;
    background:rgba(15,23,42,0.5);border:1px solid rgba(255,255,255,0.04);
    border-left:3px solid var(--pri-color);transition:all 0.2s;
}}
.rec-card:hover{{background:rgba(15,23,42,0.7);transform:translateX(4px)}}
.rec-top{{display:flex;align-items:center;gap:10px;margin-bottom:10px}}
.rec-priority{{padding:3px 12px;border-radius:6px;font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.06em}}
.rec-category{{font-size:0.78rem;color:#94a3b8;font-weight:500}}
.rec-text{{font-size:0.85rem;color:#cbd5e1;line-height:1.7}}
.rec-status{{display:inline-block;margin-top:10px;font-size:0.7rem;color:#475569;font-style:italic}}

/* ===== EVIDENCE VALIDATION ===== */
.evidence-stats{{display:flex;gap:20px;flex-wrap:wrap;margin-bottom:24px}}
.ev-stat{{flex:1;min-width:120px;text-align:center;padding:16px;background:rgba(15,23,42,0.5);border-radius:12px;border:1px solid rgba(255,255,255,0.04)}}
.ev-num{{font-size:1.6rem;font-weight:800;display:block}}
.ev-lbl{{font-size:0.7rem;color:#64748b;text-transform:uppercase;letter-spacing:0.08em;margin-top:4px;display:block}}
.ev-badge{{display:inline-block;padding:6px 16px;border-radius:8px;font-size:0.85rem;font-weight:700;text-transform:uppercase;letter-spacing:0.06em}}
.ev-table td:first-child{{text-align:center;width:36px}}
.match-pass td:first-child{{color:#22c55e}}
.match-fail td:first-child{{color:#ef4444}}

/* ===== FOLLOW-UP ACTIONS ===== */
.fu-list{{display:flex;flex-direction:column;gap:10px}}
.fu-item{{
    display:flex;gap:16px;padding:16px 20px;border-radius:12px;
    background:rgba(15,23,42,0.4);border:1px solid rgba(255,255,255,0.04);
    border-left:3px solid var(--fu-color);transition:all 0.2s;
}}
.fu-item:hover{{background:rgba(15,23,42,0.6)}}
.fu-check{{flex-shrink:0;padding-top:4px}}
.fu-checkbox{{display:none}}
.fu-checkbox + label{{
    display:block;width:22px;height:22px;border:2px solid #475569;border-radius:6px;
    cursor:pointer;position:relative;transition:all 0.2s;
}}
.fu-checkbox:checked + label{{background:#14b8a6;border-color:#14b8a6}}
.fu-checkbox:checked + label::after{{
    content:'✓';position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
    color:#fff;font-size:0.7rem;font-weight:800;
}}
.fu-checkbox:checked ~ .fu-content{{opacity:0.45}}
.fu-content{{flex:1;transition:opacity 0.3s}}
.fu-top{{display:flex;align-items:center;gap:10px;margin-bottom:6px}}
.fu-priority{{padding:2px 10px;border-radius:6px;font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.06em}}
.fu-category{{font-size:0.75rem;color:#64748b;font-weight:500}}
.fu-action{{font-size:0.85rem;color:#cbd5e1;line-height:1.6}}
.fu-rationale{{font-size:0.78rem;color:#64748b;margin-top:4px;line-height:1.5}}
.fu-status{{display:inline-block;margin-top:6px;font-size:0.68rem;color:#475569;font-style:italic}}

/* ===== DISCLAIMER ===== */
.disclaimer-inline{{font-size:0.75rem;color:#475569;margin-top:16px;font-style:italic;padding:10px 0;border-top:1px solid rgba(255,255,255,0.04)}}

/* ===== FOOTER ===== */
.footer{{
    margin-top:40px;padding:32px 40px;text-align:center;
    background:rgba(30,41,59,0.3);border:1px solid rgba(255,255,255,0.04);
    border-radius:16px;
}}
.footer-logo{{font-size:0.82rem;font-weight:700;color:#14b8a6;letter-spacing:0.04em;margin-bottom:8px}}
.footer-ai{{font-size:0.78rem;color:#64748b;line-height:1.6;max-width:700px;margin:0 auto}}
.footer-meta{{font-size:0.68rem;color:#334155;margin-top:12px}}

/* ===== ANIMATIONS ===== */
.animate-in{{
    opacity:0;transform:translateY(24px);
    animation:slideIn 0.6s ease forwards;
}}
.animate-in:nth-child(2){{animation-delay:0.08s}}
.animate-in:nth-child(3){{animation-delay:0.16s}}
.animate-in:nth-child(4){{animation-delay:0.24s}}
.animate-in:nth-child(5){{animation-delay:0.32s}}
.animate-in:nth-child(6){{animation-delay:0.40s}}
@keyframes slideIn{{
    to{{opacity:1;transform:translateY(0)}}
}}
@keyframes pulse{{
    0%,100%{{opacity:1}}50%{{opacity:.6}}
}}

/* ===== RESPONSIVE ===== */
@media(max-width:900px){{
    .kpi-grid{{grid-template-columns:repeat(3,1fr)}}
    .detail-grid{{grid-template-columns:1fr}}
    .risk-hero{{flex-direction:column;align-items:flex-start;gap:24px}}
    .banner-row{{flex-direction:column;text-align:center}}
    .banner-right{{text-align:center}}
}}
@media(max-width:600px){{
    .kpi-grid{{grid-template-columns:repeat(2,1fr)}}
    .dashboard-wrapper{{padding:0 12px 40px}}
    .top-banner{{padding:20px 20px}}
    .section-header{{padding:16px 18px}}
    .section-body{{padding:0 18px 20px}}
    .evidence-stats{{flex-direction:column}}
}}
</style>
</head>
<body>
<div class="dashboard-wrapper">

    <!-- ===== TOP BANNER ===== -->
    <div class="top-banner animate-in">
        <div class="banner-row">
            <div class="banner-left">
                <h1>{_esc(project_name)}</h1>
                <div class="version">v{_esc(version)} · Clinical Intelligence Dashboard</div>
            </div>
            <div class="banner-right">
                <div class="timestamp">Generated: {_esc(generated_at)}</div>
                <div class="data-source">{_esc(data_source)}</div>
            </div>
        </div>
        <div class="ai-banner">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            <span><strong>Responsible AI Notice:</strong> {_esc(ai_note)}</span>
        </div>
    </div>

    <!-- ===== KPI CARDS ===== -->
    {kpi_html}

    <!-- ===== AGENT SECTIONS ===== -->
    {summary_html}
    {risk_html}
    {detection_html}
    {recs_html}
    {evidence_html}
    {followup_html}

    <!-- ===== FOOTER ===== -->
    <div class="footer animate-in">
        <div class="footer-logo">HDDS Agentic Clinical Intelligence Platform</div>
        <div class="footer-ai">{_esc(ai_note)}</div>
        <div class="footer-meta">Dashboard rendered on {_esc(now)} · Built with Python standard library · No external dependencies</div>
    </div>

</div>

<!-- ===== INLINE JAVASCRIPT ===== -->
<script>
function toggleSection(id) {{
    const el = document.getElementById(id);
    const chevron = document.getElementById('chevron-' + id);
    if (!el) return;
    el.classList.toggle('hidden');
    if (chevron) chevron.classList.toggle('collapsed');
}}

// Smooth stagger animation on scroll (Intersection Observer)
document.addEventListener('DOMContentLoaded', function() {{
    const observer = new IntersectionObserver(function(entries) {{
        entries.forEach(function(entry) {{
            if (entry.isIntersecting) {{
                entry.target.style.animationPlayState = 'running';
                observer.unobserve(entry.target);
            }}
        }});
    }}, {{ threshold: 0.08 }});

    document.querySelectorAll('.animate-in').forEach(function(el) {{
        el.style.animationPlayState = 'paused';
        observer.observe(el);
    }});

    // Trigger banner immediately
    const banner = document.querySelector('.top-banner');
    if (banner) banner.style.animationPlayState = 'running';
}});
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print()
    print("=" * 64)
    print("  HDDS Clinical Intelligence - Dashboard Generator")
    print("=" * 64)
    print()

    # Resolve input
    if not os.path.isfile(INPUT_JSON):
        print(f"[ERROR] Input file not found: {INPUT_JSON}")
        print("        Run the prototype pipeline first to generate outputs.")
        sys.exit(1)

    print(f"[1/3] Reading  -> {os.path.relpath(INPUT_JSON, PROJECT_ROOT)}")
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    # Convert new multi-patient format back to single-patient for the dashboard
    if "patients" in raw_data and len(raw_data["patients"]) > 0:
        data = raw_data["patients"][0]
        data["metadata"] = raw_data.get("metadata", {})
    else:
        data = raw_data

    print("[2/3] Building -> clinical_dashboard.html")
    html = _full_html(data)

    os.makedirs(os.path.dirname(OUTPUT_HTML), exist_ok=True)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(OUTPUT_HTML) / 1024
    print(f"[3/3] Saved    -> {os.path.relpath(OUTPUT_HTML, PROJECT_ROOT)}  ({size_kb:.1f} KB)")
    print()
    print("-" * 64)
    print(f"  [SUCCESS] Dashboard generated successfully!")
    print(f"  DIR: {os.path.abspath(OUTPUT_HTML)}")
    print()
    print("  Open in your browser:")
    print(f"     start {os.path.abspath(OUTPUT_HTML)}")
    print("-" * 64)
    print()


if __name__ == "__main__":
    main()
