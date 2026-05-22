"use client";
import { useState } from "react";
import { apiPost } from "@/lib/api";

export default function ValidatePage() {
  const [procedure, setProcedure] = useState("MRI lumbar spine");
  const [diagnosis, setDiagnosis] = useState("lower back pain");
  const [weeks, setWeeks] = useState(6);
  const [symptoms, setSymptoms] = useState(true);
  const [result, setResult] = useState<unknown>(null);

  async function validate() {
    setResult(await apiPost("/api/validate-case", {
      procedure,
      diagnosis,
      conservative_treatment_weeks: weeks,
      symptoms_persist: symptoms
    }));
  }

  return (
    <div>
      <h1>Case Validation</h1>
      <div className="card">
        <label>Procedure</label><input value={procedure} onChange={(e) => setProcedure(e.target.value)} />
        <label>Diagnosis</label><input value={diagnosis} onChange={(e) => setDiagnosis(e.target.value)} />
        <label>Conservative treatment weeks</label><input type="number" value={weeks} onChange={(e) => setWeeks(Number(e.target.value))} />
        <label><input type="checkbox" checked={symptoms} onChange={(e) => setSymptoms(e.target.checked)} /> Symptoms persist</label>
        <button onClick={validate}>Validate</button>
      </div>
      {result ? <pre>{JSON.stringify(result, null, 2)}</pre> : null}
    </div>
  );
}
