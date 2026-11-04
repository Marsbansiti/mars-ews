import Link from "next/link";
import { ArrowLeft, Newspaper } from "lucide-react";

export default function NotFound() {
  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center text-center px-4 py-16">
      <div className="w-16 h-16 bg-rose-50 text-rose-600 rounded-full flex items-center justify-center mb-6">
        <Newspaper className="w-8 h-8" />
      </div>
      <h1 className="font-serif text-3xl md:text-4xl font-black text-zinc-950 mb-3">
        Article Not Found
      </h1>
      <p className="text-zinc-600 text-sm max-w-md mb-8">
        The story you are looking for may have been archived, updated, or is no longer available.
      </p>
      <Link
        href="/"
        className="inline-flex items-center space-x-2 bg-zinc-950 hover:bg-zinc-800 text-white font-bold text-xs uppercase tracking-wider px-5 py-2.5 rounded transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Return to Front Page</span>
      </Link>
    </div>
  );
}
