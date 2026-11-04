import { ShieldCheck, Compass, Layers, CheckCircle2 } from "lucide-react";

export default function AboutPage() {
  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div className="border-b-2 border-zinc-950 pb-4">
        <h1 className="font-serif text-3xl md:text-5xl font-black text-zinc-950 uppercase tracking-tight">
          About MARS NEWS
        </h1>
        <p className="text-zinc-600 text-sm mt-1">
          India&apos;s Next-Generation Automated Digital Newspaper & Content Intelligence System.
        </p>
      </div>

      <div className="prose prose-zinc max-w-none text-zinc-800 space-y-6 text-sm md:text-base leading-relaxed">
        <p>
          <strong>MARS NEWS</strong> is a production-grade digital newspaper platform built to provide impartial, verified, and multi-source journalistic intelligence for India.
        </p>

        <h3 className="font-serif text-xl font-bold text-zinc-950">Our Editorial Mission</h3>
        <p>
          In an era of hyper-partisan news and fragmented digital information, MARS NEWS operates an automated newsroom pipeline that collects permitted headlines and descriptions from 10+ established Indian newspapers, regional publications, and official government releases.
        </p>

        <h3 className="font-serif text-xl font-bold text-zinc-950">How Our Pipeline Works</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 not-prose my-6">
          <div className="p-4 bg-white border border-zinc-200 rounded-lg shadow-sm">
            <Layers className="w-5 h-5 text-rose-600 mb-2" />
            <h4 className="font-bold text-sm text-zinc-900 mb-1">1. Multi-Source Ingestion</h4>
            <p className="text-xs text-zinc-600">
              Continuously monitors authorized RSS feeds and public APIs of The Hindu, Times of India, PIB, and regional dailies.
            </p>
          </div>

          <div className="p-4 bg-white border border-zinc-200 rounded-lg shadow-sm">
            <Compass className="w-5 h-5 text-rose-600 mb-2" />
            <h4 className="font-bold text-sm text-zinc-900 mb-1">2. Deduplication & Clustering</h4>
            <p className="text-xs text-zinc-600">
              Identifies duplicate stories and groups multiple reports on the same event into unified clusters using semantic similarity.
            </p>
          </div>

          <div className="p-4 bg-white border border-zinc-200 rounded-lg shadow-sm">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 mb-2" />
            <h4 className="font-bold text-sm text-zinc-900 mb-1">3. AI Synthesis with Zero Hallucination</h4>
            <p className="text-xs text-zinc-600">
              Drafts original news summaries strictly bound to authorized source facts without inventing quotes, statistics, or events.
            </p>
          </div>

          <div className="p-4 bg-white border border-zinc-200 rounded-lg shadow-sm">
            <ShieldCheck className="w-5 h-5 text-rose-600 mb-2" />
            <h4 className="font-bold text-sm text-zinc-900 mb-1">4. Fact-Validation & Risk Gate</h4>
            <p className="text-xs text-zinc-600">
              Every factual assertion is mapped to source citations. High-risk topics are automatically placed on editorial hold.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
