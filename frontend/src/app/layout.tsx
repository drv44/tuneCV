// src/app/layout.tsx
import "./globals.css";
import { Inter } from "next/font/google";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "TuneCV - AI Resume Analyzer",
  description: "Upload your resume, get instant AI-powered feedback and upskilling suggestions.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={inter.className + " bg-gradient-to-br from-gray-50 to-blue-50 min-h-screen"}>
        <header className="w-full border-b bg-white/80 backdrop-blur sticky top-0 z-50">
          <div className="container mx-auto flex items-center justify-between py-4 px-4">
            <div className="flex items-center gap-2">
              <span className="font-bold text-xl text-blue-600">TuneCV</span>
              <span className="ml-2 text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded">AI Resume Analyzer</span>
            </div>
            <a
              href="https://github.com/your-repo" // <-- update with your repo if public
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-500 hover:text-blue-600 transition"
            >
              GitHub
            </a>
          </div>
        </header>
        {children}
        <footer className="w-full border-t bg-white/80 backdrop-blur py-4 mt-8 text-center text-gray-500 text-sm">
        &copy; {new Date().getFullYear()} TuneCV. All rights reserved.
        </footer>
      </body>
    </html>
  );
}