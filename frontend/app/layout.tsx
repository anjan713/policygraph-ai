import "./globals.css";
import Nav from "./Nav";

export const metadata = {
  title: "PolicyGraph AI",
  description: "Healthcare policy Graph-RAG intelligence",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@600;700&display=swap"
        />
      </head>
      <body>
        <Nav />
        <main className="container">{children}</main>
        <footer className="footer">
          <div className="footer-inner">
            <span className="wordmark">⬡ PolicyGraph AI</span>
            <span className="spacer" />
            <span className="copy">© 2026 PolicyGraph AI — healthcare policy intelligence demo</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
