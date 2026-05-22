"use client";
import { useState } from "react";
import { apiPost } from "@/lib/api";

export default function QueryPage() {
  const [question, setQuestion] = useState("Is MRI lumbar spine covered after 6 weeks of conservative treatment?");
  const [result, setResult] = useState<unknown>(null);

  async function ask() {
    setResult(await apiPost("/api/query", { question, top_k: 5 }));
  }

  return (
    <div>
      <h1>Policy Q&A</h1>
      <div className="card">
        <textarea rows={4} value={question} onChange={(e) => setQuestion(e.target.value)} />
        <button onClick={ask}>Ask</button>
      </div>
      {result ? <pre>{JSON.stringify(result, null, 2)}</pre> : null}
    </div>
  );
}
