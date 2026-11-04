import { AlertTriangle, History } from "lucide-react";

export default function CorrectionsPage() {
  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div className="border-b-2 border-zinc-950 pb-4">
        <h1 className="font-serif text-3xl md:text-5xl font-black text-zinc-950 uppercase tracking-tight">
          Corrections & Editorial Standards Policy
        </h1>
        <p className="text-zinc-600 text-sm mt-1">
          Our commitment to transparent fact-checking, rapid error rectification, and version traceability.
        </p>
      </div>

      <div className="prose prose-zinc max-w-none text-zinc-800 space-y-6 text-sm md:text-base leading-relaxed">
        <p>
          At <strong>MARS NEWS</strong>, accuracy is our primary editorial priority. When errors occur in ingested metadata, source reporting, or our synthesized articles, we correct them swiftly and transparently.
        </p>

        <h3 className="font-serif text-xl font-bold text-zinc-950">1. Version Tracking</h3>
        <p>
          Every published article maintains an immutable revision history stored in our PostgreSQL database (<code>article_revisions</code> table). Any update to headlines, numbers, or facts increments the article version number and records the editor responsible and timestamp.
        </p>

        <h3 className="font-serif text-xl font-bold text-zinc-950">2. Transparent Correction Notices</h3>
        <p>
          Substantive corrections are displayed prominently at the bottom of the affected article with the date, time, and specific fields updated.
        </p>

        <h3 className="font-serif text-xl font-bold text-zinc-950">3. Reporting an Inaccuracy</h3>
        <p>
          If you identify a factual error, misattributed quote, or unverified number in any of our reports, please email our newsroom at:
          <br />
          <a href="mailto:corrections@marsnews.in" className="text-rose-700 font-bold underline">corrections@marsnews.in</a>
        </p>
      </div>
    </div>
  );
}
