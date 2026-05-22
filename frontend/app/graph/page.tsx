"use client";
import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api";

export default function GraphPage() {
  const [graph, setGraph] = useState<any>(null);
  useEffect(() => { apiGet("/api/graph").then(setGraph).catch((e) => setGraph({ error: String(e) })); }, []);
  return (
    <div>
      <h1>Knowledge Graph</h1>
      <p>This MVP displays graph nodes and edges as JSON. Upgrade with React Flow or Cytoscape.js for visual graph rendering.</p>
      <pre>{JSON.stringify(graph, null, 2)}</pre>
    </div>
  );
}
