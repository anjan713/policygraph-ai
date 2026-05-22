"use client";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { apiGet, GraphData, GraphNode } from "@/lib/api";

const W = 1100;
const H = 680;

// Node colors from the design.md palette. Brand red is intentionally NOT used
// here — it stays reserved for primary CTAs and the active-node selection ring.
const TYPE_COLOR: Record<string, string> = {
  Document: "#262622", // charcoal
  Procedure: "#7e238b", // accent-purple
  Requirement: "#617bff", // accent-blue
  CoverageDecision: "#103c25", // success-deep
  Chunk: "#91918c", // ash
};
const colorFor = (t: string) => TYPE_COLOR[t] || "#91918c";
const radiusFor = (t: string) => (t === "Document" || t === "Procedure" ? 14 : 9);

type Placed = GraphNode & { x: number; y: number };

/** Deterministic force-directed layout — no external dependency. */
function computeLayout(data: GraphData): Placed[] {
  const n = data.nodes.length;
  if (n === 0) return [];

  const pos = data.nodes.map((node, i) => ({
    node,
    x: W / 2 + Math.cos((i / n) * 2 * Math.PI) * 250,
    y: H / 2 + Math.sin((i / n) * 2 * Math.PI) * 250,
    vx: 0,
    vy: 0,
  }));
  const idx = new Map(pos.map((p, i) => [p.node.id, i]));
  const edges = data.edges
    .map((e) => [idx.get(e.source_id), idx.get(e.target_id)] as const)
    .filter(([a, b]) => a != null && b != null) as [number, number][];

  const iters = n > 120 ? 90 : 240;
  const ideal = 120;
  for (let step = 0; step < iters; step++) {
    const cool = 1 - step / iters;
    for (let i = 0; i < n; i++) {
      for (let j = i + 1; j < n; j++) {
        let dx = pos[i].x - pos[j].x;
        let dy = pos[i].y - pos[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 0.01;
        const rep = 9000 / (dist * dist);
        dx /= dist;
        dy /= dist;
        pos[i].vx += dx * rep;
        pos[i].vy += dy * rep;
        pos[j].vx -= dx * rep;
        pos[j].vy -= dy * rep;
      }
    }
    for (const [a, b] of edges) {
      let dx = pos[b].x - pos[a].x;
      let dy = pos[b].y - pos[a].y;
      const dist = Math.sqrt(dx * dx + dy * dy) || 0.01;
      const f = (dist - ideal) * 0.05;
      dx = (dx / dist) * f;
      dy = (dy / dist) * f;
      pos[a].vx += dx;
      pos[a].vy += dy;
      pos[b].vx -= dx;
      pos[b].vy -= dy;
    }
    for (const p of pos) {
      p.vx += (W / 2 - p.x) * 0.013;
      p.vy += (H / 2 - p.y) * 0.013;
      p.x += Math.max(-32, Math.min(32, p.vx)) * cool;
      p.y += Math.max(-32, Math.min(32, p.vy)) * cool;
      p.vx *= 0.82;
      p.vy *= 0.82;
    }
  }

  const xs = pos.map((p) => p.x);
  const ys = pos.map((p) => p.y);
  const pad = 70;
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  const s = Math.min((W - 2 * pad) / Math.max(maxX - minX, 1), (H - 2 * pad) / Math.max(maxY - minY, 1));
  return pos.map((p) => ({ ...p.node, x: pad + (p.x - minX) * s, y: pad + (p.y - minY) * s }));
}

type Drag = { kind: "node" | "pan"; id?: string; vx: number; vy: number; ox: number; oy: number; moved: boolean };

export default function GraphPage() {
  const [data, setData] = useState<GraphData | null>(null);
  const [error, setError] = useState("");
  const [nodes, setNodes] = useState<Placed[]>([]);
  const [view, setView] = useState({ x: 0, y: 0, k: 1 });
  const [selected, setSelected] = useState<string | null>(null);
  const [hover, setHover] = useState<string | null>(null);
  const [panning, setPanning] = useState(false);

  const svgRef = useRef<SVGSVGElement>(null);
  const drag = useRef<Drag | null>(null);

  useEffect(() => {
    apiGet<GraphData>("/api/graph")
      .then((d) => {
        setData(d);
        setNodes(computeLayout(d));
      })
      .catch((e) => setError(String(e)));
  }, []);

  const posById = useMemo(() => new Map(nodes.map((p) => [p.id, p])), [nodes]);
  const types = useMemo(() => [...new Set(nodes.map((p) => p.type))], [nodes]);

  // Node ids directly connected to the focused (selected or hovered) node.
  const focusId = selected || hover;
  const connected = useMemo(() => {
    const set = new Set<string>();
    if (!focusId || !data) return set;
    for (const e of data.edges) {
      if (e.source_id === focusId) set.add(e.target_id);
      if (e.target_id === focusId) set.add(e.source_id);
    }
    return set;
  }, [focusId, data]);

  const toVB = useCallback((clientX: number, clientY: number) => {
    const r = svgRef.current!.getBoundingClientRect();
    return { x: ((clientX - r.left) / r.width) * W, y: ((clientY - r.top) / r.height) * H };
  }, []);

  // Wheel zoom toward the cursor — attached natively so preventDefault works.
  useEffect(() => {
    const svg = svgRef.current;
    if (!svg) return;
    const onWheel = (e: WheelEvent) => {
      e.preventDefault();
      const r = svg.getBoundingClientRect();
      const vx = ((e.clientX - r.left) / r.width) * W;
      const vy = ((e.clientY - r.top) / r.height) * H;
      const factor = e.deltaY < 0 ? 1.15 : 1 / 1.15;
      setView((v) => {
        const k = Math.min(3.5, Math.max(0.35, v.k * factor));
        const rf = k / v.k;
        return { k, x: vx - (vx - v.x) * rf, y: vy - (vy - v.y) * rf };
      });
    };
    svg.addEventListener("wheel", onWheel, { passive: false });
    return () => svg.removeEventListener("wheel", onWheel);
  }, [data]);

  function zoomBy(factor: number) {
    setView((v) => {
      const k = Math.min(3.5, Math.max(0.35, v.k * factor));
      const rf = k / v.k;
      return { k, x: W / 2 - (W / 2 - v.x) * rf, y: H / 2 - (H / 2 - v.y) * rf };
    });
  }

  function onNodeDown(e: React.PointerEvent, id: string) {
    e.stopPropagation();
    const node = posById.get(id);
    if (!node) return;
    const vb = toVB(e.clientX, e.clientY);
    drag.current = { kind: "node", id, vx: vb.x, vy: vb.y, ox: node.x, oy: node.y, moved: false };
    svgRef.current?.setPointerCapture(e.pointerId);
  }

  function onBgDown(e: React.PointerEvent) {
    const vb = toVB(e.clientX, e.clientY);
    drag.current = { kind: "pan", vx: vb.x, vy: vb.y, ox: view.x, oy: view.y, moved: false };
    setPanning(true);
    svgRef.current?.setPointerCapture(e.pointerId);
  }

  function onMove(e: React.PointerEvent) {
    const d = drag.current;
    if (!d) return;
    const vb = toVB(e.clientX, e.clientY);
    const dx = vb.x - d.vx;
    const dy = vb.y - d.vy;
    if (Math.abs(dx) > 3 || Math.abs(dy) > 3) d.moved = true;
    if (d.kind === "pan") {
      setView((v) => ({ ...v, x: d.ox + dx, y: d.oy + dy }));
    } else {
      setNodes((ns) => ns.map((n) => (n.id === d.id ? { ...n, x: d.ox + dx / view.k, y: d.oy + dy / view.k } : n)));
    }
  }

  function onUp() {
    const d = drag.current;
    if (d && !d.moved) {
      if (d.kind === "node" && d.id) setSelected((s) => (s === d.id ? null : d.id!));
      else if (d.kind === "pan") setSelected(null);
    }
    drag.current = null;
    setPanning(false);
  }

  const selectedNode = selected ? posById.get(selected) : null;

  return (
    <div>
      <h1>Knowledge graph</h1>
      <p className="subtitle">
        Procedures, requirements, and coverage decisions extracted from processed policies,
        connected through document chunks.
      </p>

      {error && <div className="error-box">{error}</div>}
      {data && data.nodes.length === 0 && (
        <p className="empty">The graph is empty. Upload and process a policy PDF, then come back here.</p>
      )}

      {data && data.nodes.length > 0 && (
        <>
          <div className="graph-toolbar">
            <span className="badge info">{data.nodes.length} nodes</span>
            <span className="badge neutral">{data.edges.length} edges</span>
            <span className="spacer" />
            <button className="icon-circular" onClick={() => zoomBy(1.25)} aria-label="Zoom in">+</button>
            <button className="icon-circular" onClick={() => zoomBy(1 / 1.25)} aria-label="Zoom out">−</button>
            <button className="secondary small" onClick={() => { setView({ x: 0, y: 0, k: 1 }); setSelected(null); }}>
              Reset view
            </button>
          </div>

          <div className="graph-legend">
            {types.map((t) => (
              <div className="item" key={t}>
                <span className="dot" style={{ background: colorFor(t) }} />
                {t}
              </div>
            ))}
          </div>

          <div className="graph-canvas">
            <svg
              ref={svgRef}
              viewBox={`0 0 ${W} ${H}`}
              width="100%"
              className={panning ? "panning" : ""}
              onPointerDown={onBgDown}
              onPointerMove={onMove}
              onPointerUp={onUp}
              onPointerLeave={onUp}
            >
              <g transform={`translate(${view.x} ${view.y}) scale(${view.k})`}>
                {data.edges.map((e) => {
                  const a = posById.get(e.source_id);
                  const b = posById.get(e.target_id);
                  if (!a || !b) return null;
                  const lit = focusId === e.source_id || focusId === e.target_id;
                  return (
                    <g key={e.id} opacity={focusId && !lit ? 0.25 : 1}>
                      <line
                        x1={a.x} y1={a.y} x2={b.x} y2={b.y}
                        stroke={lit ? "#e60023" : "#dadad3"}
                        strokeWidth={lit ? 2.2 : 1.3}
                      />
                      <text className="graph-edge-label" x={(a.x + b.x) / 2} y={(a.y + b.y) / 2 - 3} textAnchor="middle">
                        {e.relationship}
                      </text>
                    </g>
                  );
                })}
                {nodes.map((p) => {
                  const r = radiusFor(p.type);
                  const isSel = selected === p.id;
                  const isHov = hover === p.id;
                  const dim = focusId != null && !isSel && !isHov && !connected.has(p.id) && focusId !== p.id;
                  return (
                    <g
                      key={p.id}
                      opacity={dim ? 0.3 : 1}
                      style={{ cursor: "pointer" }}
                      onPointerDown={(e) => onNodeDown(e, p.id)}
                      onPointerEnter={() => setHover(p.id)}
                      onPointerLeave={() => setHover((h) => (h === p.id ? null : h))}
                    >
                      {/* Enlarged transparent hit target for easy clicking/dragging. */}
                      <circle cx={p.x} cy={p.y} r={r + 12} fill="transparent" />
                      <circle
                        cx={p.x} cy={p.y} r={r}
                        fill={colorFor(p.type)}
                        stroke={isSel ? "#e60023" : isHov ? "#000000" : "#ffffff"}
                        strokeWidth={isSel ? 3.5 : isHov ? 2.5 : 1.8}
                      />
                      <text className="graph-node-label" x={p.x} y={p.y - r - 5} textAnchor="middle">
                        {(p.label || p.type).slice(0, 24)}
                      </text>
                    </g>
                  );
                })}
              </g>
            </svg>
          </div>
          <p className="graph-hint">
            Scroll to zoom · drag the background to pan · drag a node to move it · click a node to inspect it.
          </p>

          {selectedNode && (
            <div className="card" style={{ marginTop: 16 }}>
              <div className="row">
                <span className="dot" style={{ width: 12, height: 12, borderRadius: 9999, background: colorFor(selectedNode.type) }} />
                <h3 style={{ margin: 0 }}>{selectedNode.label || selectedNode.type}</h3>
                <span className="badge info">{selectedNode.type}</span>
                <span className="spacer" />
                <button className="tertiary small" onClick={() => setSelected(null)}>Close</button>
              </div>
              <pre style={{ marginTop: 12 }}>{JSON.stringify(selectedNode.properties, null, 2)}</pre>
            </div>
          )}
        </>
      )}
    </div>
  );
}
