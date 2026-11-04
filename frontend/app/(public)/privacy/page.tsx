export default function PrivacyPage() {
  return (
    <div className="max-w-3xl mx-auto space-y-6 text-sm text-zinc-800">
      <div className="border-b-2 border-zinc-950 pb-4">
        <h1 className="font-serif text-3xl md:text-5xl font-black text-zinc-950 uppercase tracking-tight">
          Privacy Policy
        </h1>
        <p className="text-zinc-600 text-xs mt-1">Last Updated: November 2026</p>
      </div>

      <p>
        MARS NEWS respects your privacy. We do not sell or rent personal information to third parties. We collect standard aggregate telemetry (page views, search queries, referral sources) solely to optimize newsroom delivery and improve factual indexing.
      </p>

      <h3 className="font-serif text-lg font-bold text-zinc-950">Cookies &amp; Local Storage</h3>
      <p>
        We use essential cookies strictly for newsroom dashboard authentication and user session management.
      </p>
    </div>
  );
}
