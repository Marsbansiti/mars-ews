"use client";

import React, { useEffect } from "react";
import Link from "next/link";
import { AlertCircle, RotateCcw, Home } from "lucide-react";

export default function ErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Client boundary caught error:", error);
  }, [error]);

  return (
    <div className="min-h-[50vh] flex flex-col items-center justify-center text-center px-4 py-12">
      <div className="w-14 h-14 bg-amber-50 text-amber-600 rounded-full flex items-center justify-center mb-4">
        <AlertCircle className="w-7 h-7" />
      </div>
      <h2 className="font-serif text-2xl md:text-3xl font-black text-zinc-950 mb-2">
        Newsroom Notice
      </h2>
      <p className="text-zinc-600 text-sm max-w-md mb-6">
        An error occurred while loading this section. Our newsroom intelligence engine is updating the feeds.
      </p>
      <div className="flex items-center space-x-3">
        <button
          onClick={() => reset()}
          className="inline-flex items-center space-x-2 bg-rose-700 hover:bg-rose-800 text-white font-bold text-xs uppercase tracking-wider px-4 py-2 rounded transition-colors"
        >
          <RotateCcw className="w-4 h-4" />
          <span>Retry</span>
        </button>
        <Link
          href="/"
          className="inline-flex items-center space-x-2 bg-zinc-100 hover:bg-zinc-200 text-zinc-800 font-bold text-xs uppercase tracking-wider px-4 py-2 rounded transition-colors"
        >
          <Home className="w-4 h-4" />
          <span>Front Page</span>
        </Link>
      </div>
    </div>
  );
}
