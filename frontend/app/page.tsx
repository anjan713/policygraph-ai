export default function Home() {
  return (
    <div>
      <h1>PolicyGraph AI</h1>
      <p>Healthcare policy document intelligence using PDF ingestion, real retrieval, rule extraction, and Graph-RAG style evidence expansion.</p>
      <div className="grid">
        <div className="card"><h3>1. Upload</h3><p>Upload healthcare policy PDFs.</p></div>
        <div className="card"><h3>2. Process</h3><p>Extract text, chunks, rules, and graph relationships.</p></div>
        <div className="card"><h3>3. Query</h3><p>Ask policy questions with source citations.</p></div>
        <div className="card"><h3>4. Validate</h3><p>Check case facts against extracted policy rules.</p></div>
      </div>
    </div>
  );
}
