import Link from "next/link";
import { Search, ShieldAlert, Sparkles, SlidersHorizontal } from "lucide-react";

export default function Masthead() {
  const today = new Date().toLocaleDateString("en-IN", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  return (
    <header className="border-b border-zinc-200 bg-white">
      {/* Top Utility Bar */}
      <div className="max-w-7xl mx-auto px-4 py-1.5 text-xs text-zinc-600 flex flex-wrap justify-between items-center border-b border-zinc-100">
        <div className="flex items-center space-x-4">
          <span suppressHydrationWarning className="font-medium text-zinc-800">{today}</span>
          <span className="hidden sm:inline text-zinc-400">|</span>
          <span className="hidden sm:inline text-zinc-700">New Delhi 26°C · Bhubaneswar 29°C</span>
          <span className="hidden md:inline text-zinc-400">|</span>
          <span className="hidden md:inline text-emerald-700 font-medium">BSE Sensex: 84,210 ▲ 0.4%</span>
        </div>
        <div className="flex items-center space-x-4 mt-1 sm:mt-0">
          <span className="bg-zinc-900 text-white px-2 py-0.5 rounded text-[10px] tracking-wider font-semibold uppercase">
            National & Odisha Edition
          </span>
          <Link
            href="/admin"
            className="flex items-center space-x-1 text-zinc-700 hover:text-rose-600 font-medium transition-colors"
          >
            <SlidersHorizontal className="w-3.5 h-3.5" />
            <span>Newsroom Desk</span>
          </Link>
        </div>
      </div>

      {/* Main Classical Masthead */}
      <div className="max-w-7xl mx-auto px-4 py-6 text-center">
        <div className="flex items-center justify-between">
          <div className="hidden lg:block w-36 text-left">
            <p className="text-[11px] uppercase tracking-wider text-zinc-500 font-medium">Verified Multi-Source</p>
            <p className="text-xs font-semibold text-zinc-800">10+ Top Indian Dailies</p>
          </div>

          <div className="flex-1">
            <Link href="/" className="inline-block">
              <h1 className="font-serif text-5xl md:text-7xl font-black tracking-tight text-zinc-950 uppercase hover:opacity-95 transition-opacity">
                Mars News
              </h1>
            </Link>
            <p className="text-[11px] md:text-xs uppercase tracking-[0.25em] text-zinc-600 mt-1 font-medium">
              The AI-Powered Digital Newspaper of India · Automated Editorial Intelligence
            </p>
          </div>

          <div className="hidden lg:block w-36 text-right">
            <Link
              href="/search"
              className="inline-flex items-center space-x-1 text-xs border border-zinc-300 px-2.5 py-1 rounded-full text-zinc-700 hover:border-zinc-900 transition-colors"
            >
              <Search className="w-3.5 h-3.5" />
              <span>Search News</span>
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}
