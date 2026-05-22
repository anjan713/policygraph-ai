"use client";
import { useState } from "react";
import { apiPost, QueryResult } from "@/lib/api";

const SAMPLES = [
  "Is MRI lumbar spine covered after 6 weeks of conservative treatment?",
  "When is prior authorization required?",
  "What are the HbA1c testing requirements for diabetes care?",
  "Which services are excluded from coverage?",
];

export default function QueryPage() {
  const [question, setQuestion] = useState(SAMPLES[0]);
  const [result, setResult] = useState<QueryResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function ask() {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      setResult(await apiPost<QueryResult>("/api/query", { question, top_k: 5 }));
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  const confidencePct = result ? Math.round(result.confidence * 100) : 0;
  const confColor =
    confidencePct >= 70 ? "var(--success-deep)" : confidencePct >= 45 ? "var(--accent-purple)" : "var(--error)";

  return (
    <div>
      <h1>Policy Q&amp;A</h1>
      <p className="subtitle">
        Ask a coverage question. Answers are grounded in retrieved policy chunks with
        page-level citations and Graph-RAG context.
      </p>

      <div className="card">
        <label htmlFor="q">Question</label>
        <textarea id="q" rows={3} value={question} onChange={(e) => setQuestion(e.target.value)} />
        <div className="row" style={{ marginBottom: 16 }}>
          {SAMPLES.map((s) => (
            <button key={s} className="chip" onClick={() => setQuestion(s)}>
              {s.length > 40 ? s.slice(0, 40) + "…" : s}
            </button>
          ))}
        </div>
        <button onClick={ask} disabled={loading || question.trim().length < 3}>
          {loading ? <><span className="spinner" /> Asking…</> : "Ask"}
        </button>
      </div>

      {error && <div className="error-box">{error}</div>}

      {result && (
        <>
          <div className="card">
            <div className="row">
              <h3 style={{ margin: 0 }}>Answer</h3>
              {result.answer_mode === "vertex_gemini" ? (
                <span className="badge purple">✦ Gemini · {result.model}</span>
              ) : result.answer_mode === "rule_based" ? (
                <span className="badge neutral">Rule-based fallback</span>
              ) : null}
            </div>
            <p style={{ fontSize: 16, color: "var(--body)", marginTop: 12 }}>{result.answer}</p>
            <div className="confidence">
              <div className="meta">
                <span>CONFIDENCE</span>
                <span>{confidencePct}%</span>
              </div>
              <div className="track">
                <div className="fill" style={{ width: `${confidencePct}%`, background: confColor }} />
              </div>
            </div>
          </div>

          <div className="card">
            <h3>Citations ({result.citations.length})</h3>
            {result.citations.length === 0 && <p className="empty">No supporting citations.</p>}
            <div style={{ marginTop: 12 }}>
              {result.citations.map((c, i) => (
                <div className="evidence" key={c.chunk_id}>
                  <div className="head">
                    <span className="badge info">#{i + 1}</span>
                    <span className="badge neutral">Page {c.page_number}</span>
                    {c.score != null && (
                      <span className="badge success">score {c.score.toFixed(3)}</span>
                    )}
                  </div>
                  <div className="excerpt">{c.excerpt}</div>
                </div>
              ))}
            </div>
          </div>

          {result.graph_context.length > 0 && (
            <div className="card">
              <h3>Graph context ({result.graph_context.length})</h3>
              <div style={{ marginTop: 12 }}>
                {result.graph_context.map((g, i) => (
                  <div className="evidence" key={i}>
                    <div className="excerpt">
                      {String(g.procedure ?? "")} <strong>{String(g.relationship ?? "")}</strong>{" "}
                      {String(g.label ?? g.text ?? "")}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
