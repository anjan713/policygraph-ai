"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { apiGet, DocumentItem, statusColor, prettyLabel } from "@/lib/api";

type Health = { status: string } & Record<string, string>;

export default function Home() {
  const [docs, setDocs] = useState<DocumentItem[] | null>(null);
  const [health, setHealth] = useState<Health | null>(null);
  const [apiError, setApiError] = useState("");

  useEffect(() => {
    apiGet<Health>("/health").then(setHealth).catch(() => setHealth(null));
    apiGet<DocumentItem[]>("/api/documents")
      .then(setDocs)
      .catch((e) => setApiError(String(e)));
  }, []);

  const counts = (docs || []).reduce<Record<string, number>>((acc, d) => {
    acc[d.status] = (acc[d.status] || 0) + 1;
    return acc;
  }, {});

  return (
    <div>
      <h1>Healthcare policy intelligence</h1>
      <p className="subtitle">
        Upload policy PDFs, parse them with PaddleOCR, and ask coverage questions
        answered with vector retrieval, Graph-RAG evidence expansion, and page-level citations.
      </p>

      {apiError && (
        <div className="error-box">
          Backend not reachable. Start the stack with <strong>docker compose up</strong>. ({apiError})
        </div>
      )}

      <div className="grid" style={{ marginBottom: 24 }}>
        <div className="stat">
          <div className="num">{docs ? docs.length : "—"}</div>
          <div className="lbl">Documents</div>
        </div>
        <div className="stat">
          <div className="num" style={{ color: "var(--success-deep)" }}>{counts["processed"] || 0}</div>
          <div className="lbl">Processed</div>
        </div>
        <div className="stat">
          <div className="num" style={{ color: "var(--accent-purple-deep)" }}>
            {(counts["queued"] || 0) + (counts["processing"] || 0)}
          </div>
          <div className="lbl">In Progress</div>
        </div>
        <div className="stat">
          <div className="num" style={{ color: "var(--error)" }}>{counts["failed"] || 0}</div>
          <div className="lbl">Failed</div>
        </div>
      </div>

      <div className="card">
        <h3>Service health</h3>
        {health ? (
          <div className="row" style={{ marginTop: 12 }}>
            <span className="badge success">api: {health.status}</span>
            {Object.entries(health)
              .filter(([k]) => k !== "status")
              .map(([k, v]) => (
                <span key={k} className="badge neutral">{k}: {v}</span>
              ))}
          </div>
        ) : (
          <p className="mute" style={{ marginTop: 8 }}>Backend health endpoint unavailable.</p>
        )}
      </div>

      <div className="card">
        <div className="row">
          <h3 style={{ margin: 0 }}>Recent documents</h3>
          <span className="spacer" />
          <Link href="/upload" className="caption" style={{ color: "var(--primary)", fontWeight: 700 }}>
            Manage documents →
          </Link>
        </div>
        {!docs && !apiError && <p className="mute" style={{ marginTop: 8 }}>Loading…</p>}
        {docs && docs.length === 0 && (
          <p className="empty">
            No documents yet. <Link href="/upload" style={{ color: "var(--primary)", fontWeight: 700 }}>Upload a policy PDF →</Link>
          </p>
        )}
        {docs &&
          docs.slice(0, 6).map((d) => (
            <div className="row" key={d.id} style={{ padding: "12px 0", borderBottom: "1px solid var(--hairline)" }}>
              <span className="body-strong">{d.file_name}</span>
              <span className={`badge ${statusColor(d.status)}`}>{prettyLabel(d.status)}</span>
              <span className="spacer" />
              <span className="caption">{new Date(d.created_at).toLocaleString()}</span>
            </div>
          ))}
      </div>

      <h2>Workflow</h2>
      <div className="grid">
        <Link className="card" href="/upload">
          <h3>1 · Upload &amp; Process</h3>
          <p className="mute">Upload policy PDFs and run background OCR and Graph-RAG processing.</p>
        </Link>
        <Link className="card" href="/query">
          <h3>2 · Query</h3>
          <p className="mute">Ask coverage questions and get answers with page-level citations.</p>
        </Link>
        <Link className="card" href="/validate">
          <h3>3 · Validate</h3>
          <p className="mute">Check patient case facts against extracted policy rules.</p>
        </Link>
        <Link className="card" href="/graph">
          <h3>4 · Knowledge Graph</h3>
          <p className="mute">Explore procedures, requirements, and coverage decisions.</p>
        </Link>
      </div>
    </div>
  );
}
