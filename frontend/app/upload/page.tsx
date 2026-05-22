"use client";
import { useCallback, useEffect, useState } from "react";
import { API_BASE, apiGet, apiPost, DocumentItem, statusColor, prettyLabel } from "@/lib/api";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [docs, setDocs] = useState<DocumentItem[]>([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState(false);
  const [busyId, setBusyId] = useState<string | null>(null);

  const loadDocs = useCallback(async () => {
    try {
      setDocs(await apiGet<DocumentItem[]>("/api/documents"));
    } catch (e) {
      setError(String(e));
    }
  }, []);

  useEffect(() => {
    loadDocs();
    const id = setInterval(loadDocs, 4000);
    return () => clearInterval(id);
  }, [loadDocs]);

  async function upload() {
    if (!file) return;
    setUploading(true);
    setError("");
    setMessage("");
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(`${API_BASE}/api/documents/upload`, { method: "POST", body: form });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setMessage(`Uploaded "${data.file_name}". Click "Process" to run OCR and Graph-RAG.`);
      setFile(null);
      await loadDocs();
    } catch (e) {
      setError(String(e));
    } finally {
      setUploading(false);
    }
  }

  async function processDoc(id: string) {
    setBusyId(id);
    setError("");
    try {
      await apiPost(`/api/documents/${id}/process`);
      setMessage("Processing job queued. Status updates automatically below.");
      await loadDocs();
    } catch (e) {
      setError(String(e));
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div>
      <h1>Upload policy PDF</h1>
      <p className="subtitle">
        Upload a healthcare policy PDF, then process it in the background — PaddleOCR parsing,
        chunking, embeddings, rule extraction, and graph construction.
      </p>

      <div className="card">
        <label htmlFor="pdf">Policy PDF</label>
        <input
          id="pdf"
          type="file"
          accept="application/pdf"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
        />
        <button onClick={upload} disabled={!file || uploading}>
          {uploading ? <><span className="spinner" /> Uploading…</> : "Upload"}
        </button>
      </div>

      {message && <div className="info-box">{message}</div>}
      {error && <div className="error-box">{error}</div>}

      <h2>Documents ({docs.length})</h2>
      {docs.length === 0 && <p className="empty">No documents uploaded yet.</p>}
      <div className="stack">
        {docs.map((doc) => {
          const inFlight = ["queued", "processing"].includes(doc.status);
          return (
            <div className="card" key={doc.id} style={{ marginBottom: 0 }}>
              <div className="row">
                <h3 style={{ margin: 0 }}>{doc.file_name}</h3>
                <span className={`badge ${statusColor(doc.status)}`}>{prettyLabel(doc.status)}</span>
                {doc.job_id && <span className="badge neutral">job {doc.job_id.slice(0, 8)}</span>}
                <span className="spacer" />
                <button
                  className={inFlight ? "secondary" : ""}
                  onClick={() => processDoc(doc.id)}
                  disabled={inFlight || busyId === doc.id}
                >
                  {busyId === doc.id ? (
                    <><span className="spinner" /> Queuing…</>
                  ) : inFlight ? "Processing…" : "Process"}
                </button>
              </div>
              <p className="caption" style={{ margin: "8px 0 0", wordBreak: "break-all" }}>
                {doc.storage_uri}
              </p>
              {doc.error_message && <div className="error-box" style={{ marginTop: 12, marginBottom: 0 }}>{doc.error_message}</div>}
            </div>
          );
        })}
      </div>
    </div>
  );
}
