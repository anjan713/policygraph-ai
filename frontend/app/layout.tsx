import "./globals.css";
import Link from "next/link";

export const metadata = { title: "PolicyGraph AI", description: "Healthcare policy Graph-RAG demo" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <main className="container">
          <nav className="nav">
            <Link href="/">Dashboard</Link>
            <Link href="/upload">Upload</Link>
            <Link href="/query">Query</Link>
            <Link href="/validate">Validate</Link>
            <Link href="/graph">Graph</Link>
          </nav>
          {children}
        </main>
      </body>
    </html>
  );
}
