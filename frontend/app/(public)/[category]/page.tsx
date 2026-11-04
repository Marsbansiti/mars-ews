import { notFound } from "next/navigation";
import ArticleCard from "@/components/ArticleCard";
import { fetchPublicNews } from "@/lib/api";
import { Compass, Sparkles } from "lucide-react";

const CATEGORY_TITLES: Record<string, { title: string; subtitle: string }> = {
  latest: { title: "Latest News", subtitle: "Continuous updates synthesized across Indian digital publications." },
  breaking: { title: "Breaking News", subtitle: "Developing alerts and rapid reports verified by our intelligence desk." },
  india: { title: "National India", subtitle: "Governance, public policy, parliament, and key national developments." },
  politics: { title: "Politics & Policy", subtitle: "Electoral developments, parliamentary debates, and policy decisions." },
  business: { title: "Business & Economy", subtitle: "Markets, central bank decisions, startups, trade, and financial policy." },
  technology: { title: "Technology & AI", subtitle: "Digital public infrastructure, artificial intelligence, and semiconductors." },
  sports: { title: "Sports Desk", subtitle: "Cricket, Olympics, athletics, badminton, and domestic competitions." },
  entertainment: { title: "Arts & Entertainment", subtitle: "Cinema, culture, literature, OTT releases, and festivals." },
  education: { title: "Education & Skills", subtitle: "Higher education, universities, competitive examinations, and EdTech." },
  science: { title: "Science & Space", subtitle: "ISRO space missions, biotechnology, climate research, and green tech." },
  lifestyle: { title: "Lifestyle & Heritage", subtitle: "Public health, wellness, tourism, cultural heritage, and architecture." },
  regional: { title: "Regional India", subtitle: "Grassroots reporting and state administration across the Indian federation." },
  odisha: { title: "Odisha Regional Bureau", subtitle: "Dedicated governance, semiconductor investments, culture, and coastal reporting from Bhubaneswar and across Odisha." },
};

export default async function CategoryPage({ params }: { params: { category: string } }) {
  const catSlug = params.category.toLowerCase();
  const info = CATEGORY_TITLES[catSlug];

  if (!info) {
    notFound();
  }

  const isOdisha = catSlug === "odisha";
  const isRegional = catSlug === "regional" || isOdisha;
  const isBreaking = catSlug === "breaking";

  let articles = [];
  if (isOdisha) {
    articles = await fetchPublicNews({ category: "odisha", limit: 30 });
    if (articles.length === 0) {
      articles = await fetchPublicNews({ state: "Odisha", limit: 30 });
    }
  } else if (catSlug === "latest" || catSlug === "breaking") {
    articles = await fetchPublicNews({ limit: 30 });
  } else {
    articles = await fetchPublicNews({ category: catSlug, limit: 30 });
  }

  return (
    <div className="space-y-8">
      {/* Category Header */}
      <div className="border-b-2 border-zinc-950 pb-4">
        <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-rose-700 mb-1">
          <Compass className="w-3.5 h-3.5" />
          <span>MARS NEWS Section Desk</span>
        </div>
        <h1 className="font-serif text-3xl md:text-5xl font-black text-zinc-950 uppercase tracking-tight">
          {info.title}
        </h1>
        <p className="text-zinc-600 text-sm mt-1 max-w-2xl">{info.subtitle}</p>
      </div>

      {/* Grid of Articles */}
      {articles.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {articles.map((art) => (
            <ArticleCard key={art.id} article={art} variant="standard" />
          ))}
        </div>
      ) : (
        <div className="p-16 text-center border rounded-lg bg-zinc-50">
          <p className="text-zinc-500 text-sm">No stories currently published in this section.</p>
        </div>
      )}
    </div>
  );
}
