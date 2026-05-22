"use client";
import { useState } from "react";
import { apiPost, ValidationResult, decisionColor, prettyLabel } from "@/lib/api";

export default function ValidatePage() {
  const [procedure, setProcedure] = useState("MRI lumbar spine");
  const [diagnosis, setDiagnosis] = useState("lower back pain");
  const [weeks, setWeeks] = useState(6);
  const [symptoms, setSymptoms] = useState(true);
  const [priorAuth, setPriorAuth] = useState(false);
  const [result, setResult] = useState<ValidationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function validate() {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      setResult(
        await apiPost<ValidationResult>("/api/validate-case", {
          procedure,
          diagnosis,
          conservative_treatment_weeks: weeks,
          symptoms_persist: symptoms,
          prior_authorization: priorAuth,
        }),
      );
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h1>Case validation</h1>
      <p className="subtitle">
        Check a patient case against extracted policy rules to get a coverage decision
        with the rules that matched.
      </p>

      <div className="card">
        <label htmlFor="proc">Procedure</label>
        <input id="proc" value={procedure} onChange={(e) => setProcedure(e.target.value)} />
        <label htmlFor="diag">Diagnosis</label>
        <input id="diag" value={diagnosis} onChange={(e) => setDiagnosis(e.target.value)} />
        <label htmlFor="weeks">Conservative treatment (weeks)</label>
        <input id="weeks" type="number" min={0} value={weeks} onChange={(e) => setWeeks(Number(e.target.value))} />
        <div className="checkbox-row">
          <input id="symptoms" type="checkbox" checked={symptoms} onChange={(e) => setSymptoms(e.target.checked)} />
          <label htmlFor="symptoms">Symptoms persist</label>
        </div>
        <div className="checkbox-row">
          <input id="priorAuth" type="checkbox" checked={priorAuth} onChange={(e) => setPriorAuth(e.target.checked)} />
          <label htmlFor="priorAuth">Prior authorization obtained</label>
        </div>
        <button onClick={validate} disabled={loading || !procedure.trim()}>
          {loading ? <><span className="spinner" /> Validating…</> : "Validate case"}
        </button>
      </div>

      {error && <div className="error-box">{error}</div>}

      {result && (
        <>
          <div className="card">
            <div className="row">
              <h3 style={{ margin: 0 }}>Decision</h3>
              <span className={`badge ${decisionColor(result.decision)}`}>
                {prettyLabel(result.decision)}
              </span>
            </div>
            <p style={{ margin: "12px 0 0", color: "var(--body)" }}>{result.reasoning}</p>
            {result.missing_fields.length > 0 && (
              <div className="info-box" style={{ marginTop: 16, marginBottom: 0 }}>
                Missing case details: {result.missing_fields.map(prettyLabel).join(", ")}
              </div>
            )}
          </div>

          <div className="card">
            <h3>Matched rules ({result.matched_rules.length})</h3>
            {result.matched_rules.length === 0 && <p className="empty">No matching policy rules found.</p>}
            <div style={{ marginTop: 12 }}>
              {result.matched_rules.map((r) => (
                <div className="evidence" key={r.rule_id}>
                  <div className="head">
                    <span className={`badge ${decisionColor(r.decision)}`}>{prettyLabel(r.decision)}</span>
                    {r.procedure && <span className="badge info">{r.procedure}</span>}
                    {r.page_number != null && <span className="badge neutral">Page {r.page_number}</span>}
                    <span className="badge neutral">conf {r.confidence.toFixed(2)}</span>
                  </div>
                  {r.requirement_text && (
                    <div className="excerpt"><strong>Requirement:</strong> {r.requirement_text}</div>
                  )}
                  {r.condition_text && (
                    <div className="excerpt mute" style={{ marginTop: 4 }}>{r.condition_text}</div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
