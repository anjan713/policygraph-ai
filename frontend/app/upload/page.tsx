"use client";
import { useEffect, useState } from "react";
import { API_BASE, apiGet, apiPost } from "@/lib/api";

type DocumentItem = { id: string; file_name: string; status: string; storage_uri: string; job_id?: string | null; error_message?: string | null; created_at: string; processed_at?: string | null };

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [docs, setDocs] = useState<DocumentItem[]>([]);
  const [message, setMessage] = useState("");

  async function loadDocs() {
    setDocs(await apiGet<DocumentItem[]>("/api/documents"));
  }

  useEffect(() => {
    loadDocs();
    const id = setInterval(loadDocs, 4000);
    return () => clearInterval(id);
  }, []);

  async function upload() {
    if (!file) return;
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(`${API_BASE}/api/documents/upload`, { method: "POST", body: form });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    setMessage(`Uploaded ${data.file_name}. Now click Process to enqueue OCR/Graph-RAG processing.`);
    await loadDocs();
  }

  async function processDoc(id: string) {
    const data = await apiPost(`/api/documents/${id}/process`);
    setMessage(JSON.stringify(data, null, 2));
    await loadDocs();
  }

  return (
    <div>
      <h1>Upload Policy PDF</h1>
      <div className="card">
        <input type="file" accept="application/pdf" onChange={(e) => setFile(e.target.files?.[0] || null)} />
        <button onClick={upload} disabled={!file}>Upload</button>
      </div>
      {message && <pre>{message}</pre>}
      <h2>Documents</h2>
      {docs.map((doc) => (
        <div className="card" key={doc.id}>
          <h3>{doc.file_name}</h3>
          <p><span className="badge">{doc.status}</span> {doc.job_id && <span className="badge">job: {doc.job_id.slice(0, 8)}</span>}</p>
          <p>{doc.storage_uri}</p>
          {doc.error_message && <pre>{doc.error_message}</pre>}
          <button onClick={() => processDoc(doc.id)} disabled={["queued", "processing"].includes(doc.status)}>Process in Background</button>
        </div>
      ))}
    </div>
  );
}
