import { Mail, MapPin, Phone } from "lucide-react";

export default function ContactPage() {
  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div className="border-b-2 border-zinc-950 pb-4">
        <h1 className="font-serif text-3xl md:text-5xl font-black text-zinc-950 uppercase tracking-tight">
          Newsroom Contact
        </h1>
        <p className="text-zinc-600 text-sm mt-1">
          Reach our editorial desk, technology team, or syndication licensing bureau.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 my-6">
        <div className="p-5 bg-white border border-zinc-200 rounded-lg text-center shadow-sm">
          <Mail className="w-6 h-6 text-rose-700 mx-auto mb-2" />
          <h3 className="font-bold text-sm text-zinc-900 mb-1">Editorial Desk</h3>
          <p className="text-xs text-zinc-600">editor@marsnews.in</p>
        </div>

        <div className="p-5 bg-white border border-zinc-200 rounded-lg text-center shadow-sm">
          <MapPin className="w-6 h-6 text-rose-700 mx-auto mb-2" />
          <h3 className="font-bold text-sm text-zinc-900 mb-1">Offices</h3>
          <p className="text-xs text-zinc-600">New Delhi &amp; Bhubaneswar, India</p>
        </div>

        <div className="p-5 bg-white border border-zinc-200 rounded-lg text-center shadow-sm">
          <Phone className="w-6 h-6 text-rose-700 mx-auto mb-2" />
          <h3 className="font-bold text-sm text-zinc-900 mb-1">Syndication</h3>
          <p className="text-xs text-zinc-600">syndication@marsnews.in</p>
        </div>
      </div>
    </div>
  );
}
