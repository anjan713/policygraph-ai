"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/", label: "Dashboard" },
  { href: "/query", label: "Query" },
  { href: "/validate", label: "Validate" },
  { href: "/graph", label: "Graph" },
];

export default function Nav() {
  const pathname = usePathname();
  return (
    <nav className="nav">
      <div className="nav-inner">
        <Link href="/" className="brand">⬡ PolicyGraph AI</Link>
        {LINKS.map((l) => {
          const active = l.href === "/" ? pathname === "/" : pathname.startsWith(l.href);
          return (
            <Link key={l.href} href={l.href} className={`nav-link${active ? " active" : ""}`}>
              {l.label}
            </Link>
          );
        })}
        <span className="spacer" />
        <Link href="/upload" className="btn">Upload policy</Link>
      </div>
    </nav>
  );
}
