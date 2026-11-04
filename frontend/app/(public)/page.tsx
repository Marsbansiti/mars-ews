import Link from "next/link";
import ArticleCard from "@/components/ArticleCard";
import { fetchPublicNews, fetchTrendingNews } from "@/lib/api";
import { ShieldCheck, Sparkles, TrendingUp, Compass, ArrowRight, Award, Flame, Landmark, Briefcase, Cpu, Trophy, Film, MapPin } from "lucide-react";

export default async function HomePage() {
  const [
    allNews,
    trending,
    politicsNews,
    businessNews,
    sportsNews,
    entNews,
    techNews,
    odishaNews,
  ] = await Promise.all([
    fetchPublicNews({ limit: 8 }),
    fetchTrendingNews(),
    fetchPublicNews({ category: "politics", limit: 3 }),
    fetchPublicNews({ category: "business", limit: 3 }),
    fetchPublicNews({ category: "sports", limit: 3 }),
    fetchPublicNews({ category: "entertainment", limit: 3 }),
    fetchPublicNews({ category: "technology", limit: 3 }),
    fetchPublicNews({ category: "odisha", limit: 3 }),
  ]);

  const heroArticle = allNews[0];
  const secondaryStories = allNews.slice(1, 4);

  return (
    <div className="space-y-12">
      {/* Editorial Edition Banner */}
      <div className="bg-zinc-950 text-white rounded-lg p-3 px-4 flex flex-wrap items-center justify-between text-xs shadow-sm border border-zinc-800">
        <div className="flex items-center space-x-2">
          <span className="inline-block w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span className="font-medium text-zinc-200">
            <strong>Mars News Live Wire:</strong> Continuous national &amp; regional newsroom coverage from 60+ verified publications.
          </span>
        </div>
        <div className="text-zinc-400 text-[11px] mt-1 sm:mt-0">
          Updated continuously 24/7 · National &amp; Regional Editions
        </div>
      </div>

      {/* Top News Grid (Hero + Sidebar) */}
      <section>
        <div className="flex items-center justify-between mb-4 pb-2 border-b-2 border-zinc-950">
          <div className="flex items-center space-x-2">
            <Flame className="w-4 h-4 text-rose-600" />
            <h2 className="font-serif text-xl md:text-2xl font-black text-zinc-950 uppercase tracking-tight">
              Lead Stories &amp; Front Page
            </h2>
          </div>
          <span className="text-xs font-semibold uppercase tracking-wider text-rose-700">Live Edition</span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Main Hero Story */}
          <div className="lg:col-span-8">
            {heroArticle ? (
              <ArticleCard article={heroArticle} variant="hero" />
            ) : (
              <div className="p-12 text-center border rounded-lg bg-zinc-50">
                <p className="text-zinc-500 text-sm">No articles published yet. The automated newsroom is ingesting feeds.</p>
              </div>
            )}

            {/* 3 Secondary Lead Stories */}
            {secondaryStories.length > 0 && (
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mt-6">
                {secondaryStories.map((art) => (
                  <ArticleCard key={art.id} article={art} variant="standard" />
                ))}
              </div>
            )}
          </div>

          {/* Trending & Editorial Radar Sidebar */}
          <div className="lg:col-span-4 space-y-6">
            <div className="bg-white border border-zinc-200 rounded-lg p-5 shadow-sm">
              <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-zinc-950 pb-3 border-b border-zinc-200 mb-2">
                <TrendingUp className="w-4 h-4 text-rose-600" />
                <span>Trending Intelligence</span>
              </div>
              <div>
                {(trending.length > 0 ? trending.slice(0, 5) : allNews.slice(0, 5)).map((art) => (
                  <ArticleCard key={art.id} article={art} variant="compact" />
                ))}
              </div>
            </div>

            {/* Quick Briefs Card */}
            <div className="bg-rose-50 border border-rose-200 rounded-lg p-5">
              <h3 className="font-serif text-base font-bold text-rose-950 mb-2">
                MARS NEWS Editorial Charter
              </h3>
              <p className="text-xs text-rose-900 leading-relaxed mb-3">
                All articles published on MARS NEWS are synthesized from permitted source metadata and authorized public feeds. Every factual assertion maps to source citations. High-risk coverage carries transparent disclaimers.
              </p>
              <Link href="/about" className="inline-flex items-center space-x-1 text-xs font-bold text-rose-700 hover:text-rose-900">
                <span>Read our verification charter</span>
                <ArrowRight className="w-3 h-3" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* CATEGORY SECTION 1: POLITICS DESK */}
      {politicsNews.length > 0 && (
        <section className="space-y-4">
          <div className="flex items-center justify-between pb-2 border-b-2 border-zinc-950">
            <div className="flex items-center space-x-2">
              <Landmark className="w-4 h-4 text-blue-700" />
              <h2 className="font-serif text-xl md:text-2xl font-black text-zinc-950 uppercase tracking-tight">
                Politics &amp; National Affairs
              </h2>
            </div>
            <Link href="/politics" className="text-xs font-semibold text-rose-700 hover:underline inline-flex items-center space-x-1">
              <span>View All Politics Desk</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {politicsNews.map((art) => (
              <ArticleCard key={art.id} article={art} variant="standard" />
            ))}
          </div>
        </section>
      )}

      {/* CATEGORY SECTION 2: BUSINESS & FINANCIAL MARKETS */}
      {businessNews.length > 0 && (
        <section className="space-y-4">
          <div className="flex items-center justify-between pb-2 border-b-2 border-zinc-950">
            <div className="flex items-center space-x-2">
              <Briefcase className="w-4 h-4 text-emerald-700" />
              <h2 className="font-serif text-xl md:text-2xl font-black text-zinc-950 uppercase tracking-tight">
                Business &amp; Economy Desk
              </h2>
            </div>
            <Link href="/business" className="text-xs font-semibold text-rose-700 hover:underline inline-flex items-center space-x-1">
              <span>View All Business</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {businessNews.map((art) => (
              <ArticleCard key={art.id} article={art} variant="standard" />
            ))}
          </div>
        </section>
      )}

      {/* CATEGORY SECTION 3: ODISHA & REGIONAL SPOTLIGHT */}
      <section className="bg-zinc-900 text-white rounded-xl p-6 md:p-8">
        <div className="flex flex-wrap items-center justify-between mb-6 pb-4 border-b border-zinc-800">
          <div>
            <div className="flex items-center space-x-2">
              <MapPin className="w-4 h-4 text-amber-400" />
              <span className="text-[10px] uppercase font-bold tracking-widest text-amber-400 bg-amber-950/60 px-2 py-0.5 rounded border border-amber-800/40">
                Regional Bureau
              </span>
            </div>
            <h2 className="font-serif text-2xl md:text-3xl font-black text-white mt-2">
              Odisha &amp; Eastern India Spotlight
            </h2>
          </div>
          <Link
            href="/odisha"
            className="text-xs text-amber-400 hover:text-amber-300 font-semibold inline-flex items-center space-x-1 mt-2 sm:mt-0"
          >
            <span>View Full Odisha Desk</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {(odishaNews.length > 0 ? odishaNews : allNews.slice(0, 3)).map((art) => (
            <div key={art.id} className="bg-zinc-800/70 border border-zinc-700/60 rounded-lg p-4 hover:border-zinc-500 transition-colors">
              <span className="text-[10px] text-amber-400 uppercase font-bold tracking-wider">{art.category}</span>
              <Link href={`/article/${art.slug}`}>
                <h3 className="font-serif text-base font-bold text-white hover:text-amber-300 transition-colors mt-1 mb-2 line-clamp-2">
                  {(art.headline || "").replace(/^Report:\s*/i, "")}
                </h3>
              </Link>
              <p className="text-zinc-400 text-xs line-clamp-2 mb-3">
                {(art.summary || "").replace(/^Key developments regarding\s+/i, "").replace(/\.\s*Cross-verified across.*$/i, ".")}
              </p>
              <span className="text-[11px] text-zinc-400">Regional Desk Reporting</span>
            </div>
          ))}
        </div>
      </section>

      {/* CATEGORY SECTION 4: SPORTS ARENA */}
      {sportsNews.length > 0 && (
        <section className="space-y-4">
          <div className="flex items-center justify-between pb-2 border-b-2 border-zinc-950">
            <div className="flex items-center space-x-2">
              <Trophy className="w-4 h-4 text-amber-600" />
              <h2 className="font-serif text-xl md:text-2xl font-black text-zinc-950 uppercase tracking-tight">
                Sports Arena Desk
              </h2>
            </div>
            <Link href="/sports" className="text-xs font-semibold text-rose-700 hover:underline inline-flex items-center space-x-1">
              <span>View All Sports</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {sportsNews.map((art) => (
              <ArticleCard key={art.id} article={art} variant="standard" />
            ))}
          </div>
        </section>
      )}

      {/* CATEGORY SECTION 5: ARTS & ENTERTAINMENT */}
      {entNews.length > 0 && (
        <section className="space-y-4">
          <div className="flex items-center justify-between pb-2 border-b-2 border-zinc-950">
            <div className="flex items-center space-x-2">
              <Film className="w-4 h-4 text-purple-700" />
              <h2 className="font-serif text-xl md:text-2xl font-black text-zinc-950 uppercase tracking-tight">
                Cinema, OTT &amp; Entertainment Desk
              </h2>
            </div>
            <Link href="/entertainment" className="text-xs font-semibold text-rose-700 hover:underline inline-flex items-center space-x-1">
              <span>View All Entertainment</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {entNews.map((art) => (
              <ArticleCard key={art.id} article={art} variant="standard" />
            ))}
          </div>
        </section>
      )}

      {/* CATEGORY SECTION 6: TECHNOLOGY & AI */}
      {techNews.length > 0 && (
        <section className="space-y-4">
          <div className="flex items-center justify-between pb-2 border-b-2 border-zinc-950">
            <div className="flex items-center space-x-2">
              <Cpu className="w-4 h-4 text-cyan-700" />
              <h2 className="font-serif text-xl md:text-2xl font-black text-zinc-950 uppercase tracking-tight">
                Technology &amp; AI Desk
              </h2>
            </div>
            <Link href="/technology" className="text-xs font-semibold text-rose-700 hover:underline inline-flex items-center space-x-1">
              <span>View All Technology</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {techNews.map((art) => (
              <ArticleCard key={art.id} article={art} variant="standard" />
            ))}
          </div>
        </section>
      )}

      {/* Newsletter Subscription Banner */}
      <section className="bg-white border-2 border-zinc-950 rounded-xl p-8 text-center max-w-2xl mx-auto shadow-sm">
        <h3 className="font-serif text-2xl font-black text-zinc-950 mb-2">
          Subscribe to the Morning Briefing
        </h3>
        <p className="text-xs text-zinc-600 mb-6 max-w-md mx-auto">
          Get the top multi-source verified Indian news briefing delivered to your inbox every morning at 7:00 AM IST. Zero noise, 100% verified claims.
        </p>
        <form className="flex flex-col sm:flex-row gap-2 max-w-md mx-auto" action="#">
          <input
            type="email"
            placeholder="Enter your email address"
            className="flex-1 px-4 py-2 text-xs border border-zinc-300 rounded focus:outline-none focus:ring-2 focus:ring-zinc-950"
          />
          <button
            type="submit"
            className="bg-zinc-950 hover:bg-zinc-800 text-white font-bold text-xs px-5 py-2 rounded uppercase tracking-wider transition-colors"
          >
            Subscribe
          </button>
        </form>
      </section>
    </div>
  );
}
