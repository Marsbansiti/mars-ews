import Link from "next/link";
import { Rss, ShieldCheck } from "lucide-react";

export default function Footer() {
  return (
    <footer className="bg-zinc-950 text-zinc-400 text-xs border-t-4 border-zinc-900 mt-16 pt-12 pb-16">
      <div className="max-w-7xl mx-auto px-4 grid grid-cols-1 md:grid-cols-4 gap-8 mb-10">
        <div className="md:col-span-2">
          <h2 className="font-serif text-2xl font-black text-white tracking-wider mb-2">MARS NEWS</h2>
          <p className="text-zinc-400 text-xs leading-relaxed max-w-lg mb-4">
            India’s automated digital newspaper and content intelligence platform. We monitor authorized public feeds
            across national dailies, regional media, and official government releases, applying algorithmic deduplication,
            multi-source synthesis, and automated fact validation to deliver original, verified reporting.
          </p>
          <div className="flex items-center space-x-3 text-emerald-400 text-[11px] font-medium">
            <ShieldCheck className="w-4 h-4" />
            <span>Fact-Validation Engine Active · Editorial Claim Attribution Verified</span>
          </div>
        </div>

        <div>
          <h3 className="text-zinc-200 font-semibold uppercase tracking-wider text-xs mb-3">Sections & Desks</h3>
          <ul className="space-y-1.5 text-xs">
            <li><Link href="/india" className="hover:text-white transition-colors">National India</Link></li>
            <li><Link href="/politics" className="hover:text-white transition-colors">Politics & Parliament</Link></li>
            <li><Link href="/business" className="hover:text-white transition-colors">Business & Economy</Link></li>
            <li><Link href="/technology" className="hover:text-white transition-colors">Technology & AI</Link></li>
            <li><Link href="/science" className="hover:text-white transition-colors">Science & ISRO</Link></li>
            <li><Link href="/odisha" className="text-rose-400 hover:text-rose-300 font-medium">Odisha Regional Desk</Link></li>
            <li><Link href="/sports" className="hover:text-white transition-colors">Sports & Cricket</Link></li>
          </ul>
        </div>

        <div>
          <h3 className="text-zinc-200 font-semibold uppercase tracking-wider text-xs mb-3">Standards & Policies</h3>
          <ul className="space-y-1.5 text-xs">
            <li><Link href="/about" className="hover:text-white transition-colors">About Mars News</Link></li>
            <li><Link href="/corrections" className="hover:text-white transition-colors">Corrections Policy</Link></li>
            <li><Link href="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link></li>
            <li><Link href="/terms" className="hover:text-white transition-colors">Terms of Service</Link></li>
            <li><Link href="/contact" className="hover:text-white transition-colors">Newsroom Contact</Link></li>
            <li>
              <a href="/api/v1/rss.xml" target="_blank" rel="noreferrer" className="flex items-center space-x-1 text-amber-400 hover:text-amber-300">
                <Rss className="w-3.5 h-3.5" />
                <span>RSS Feed (XML)</span>
              </a>
            </li>
            <li>
              <a href="/api/v1/sitemap.xml" target="_blank" rel="noreferrer" className="hover:text-white transition-colors">
                XML Sitemap
              </a>
            </li>
          </ul>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 pt-8 border-t border-zinc-800 text-center text-zinc-400 text-[11px] flex flex-col sm:flex-row justify-between items-center">
        <p>© 2026 MARS NEWS. All rights reserved. Content synthesized with AI-assisted editorial attribution.</p>
        <p className="mt-2 sm:mt-0">Powered by FastAPI, PostgreSQL, Redis, and Next.js</p>
      </div>
    </footer>
  );
}
