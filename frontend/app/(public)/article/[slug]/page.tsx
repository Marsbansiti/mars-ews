import { notFound } from "next/navigation";
import Link from "next/link";
import { fetchArticleBySlug, fetchPublicNews } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import NewsArticleStructuredData from "@/components/NewsArticleStructuredData";
import ArticleCard from "@/components/ArticleCard";
import ArticleHeroImage from "@/components/ArticleHeroImage";
import {
  Clock,
  AlertTriangle,
} from "lucide-react";

export async function generateMetadata({ params }: { params: { slug: string } }) {
  const article = await fetchArticleBySlug(params.slug);
  if (!article) return { title: "Article Not Found | MARS NEWS" };

  const cleanHeadline = (article.headline || "").replace(/^Report:\s*/i, "");
  let rawSummary = (article.summary || "")
    .replace(/^Key developments regarding\s+/i, "")
    .replace(/\.\s*Cross-verified across.*$/i, ".");
  if (rawSummary.includes("Verified reporting published by")) {
    rawSummary = cleanHeadline;
  }
  const cleanSummary = rawSummary;

  return {
    title: `${article.seo_title || cleanHeadline} | MARS NEWS`,
    description: article.seo_description || cleanSummary,
    openGraph: {
      title: cleanHeadline,
      description: cleanSummary,
      images: [article.hero_image_url || ""],
      type: "article",
      publishedTime: article.published_at,
    },
  };
}

export default async function ArticleDetailPage({ params }: { params: { slug: string } }) {
  const article = await fetchArticleBySlug(params.slug);
  if (!article) {
    notFound();
  }

  const cleanHeadline = (article.headline || "").replace(/^Report:\s*/i, "");
  let rawSummary = (article.summary || "")
    .replace(/^Key developments regarding\s+/i, "")
    .replace(/\.\s*Cross-verified across.*$/i, ".");
  if (rawSummary.includes("Verified reporting published by")) {
    rawSummary = cleanHeadline;
  }
  const cleanSummary = rawSummary;

  const related = await fetchPublicNews({ category: article.category_slug, limit: 3 });
  const contentBody = article.content_body || "";

  return (
    <>
      <NewsArticleStructuredData article={{ ...article, headline: cleanHeadline, summary: cleanSummary }} />

      <article className="max-w-4xl mx-auto space-y-8">
        {/* Header Section */}
        <header className="space-y-4 border-b border-zinc-200 pb-6">
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <Link
              href={`/${article.category_slug || "india"}`}
              className="bg-rose-900 text-white font-bold uppercase tracking-wider px-2.5 py-0.5 rounded text-[11px]"
            >
              {article.category}
            </Link>
            {article.is_regional && (
              <span className="bg-amber-600 text-white font-bold uppercase tracking-wider px-2.5 py-0.5 rounded text-[11px]">
                {article.regional_state || "Regional"} Bureau
              </span>
            )}
            <span className="text-zinc-400">·</span>
            <span suppressHydrationWarning className="text-zinc-600">Published: {formatDate(article.published_at)}</span>
            <span className="text-zinc-400">·</span>
            <span className="flex items-center space-x-1 text-zinc-600">
              <Clock className="w-3.5 h-3.5" />
              <span>{article.reading_time_minutes || 2} min read</span>
            </span>
          </div>

          <h1 className="font-serif text-3xl md:text-5xl font-black text-zinc-950 leading-[1.15] tracking-tight">
            {cleanHeadline}
          </h1>

          {cleanSummary && (
            <p className="text-zinc-700 text-base md:text-lg font-serif italic leading-relaxed border-l-4 border-rose-600 pl-4 bg-zinc-50 py-2">
              {cleanSummary}
            </p>
          )}
        </header>

        {/* Hero Image */}
        <figure className="space-y-2">
          <div className="relative h-80 md:h-[450px] w-full rounded-lg overflow-hidden bg-zinc-900 border border-zinc-800 shadow-sm">
            <ArticleHeroImage
              src={article.hero_image_url}
              alt={article.hero_image_alt || cleanHeadline}
            />
          </div>
          <figcaption className="text-xs text-zinc-500 flex flex-wrap justify-between items-center px-1">
            <span>{article.hero_image_caption || cleanHeadline}</span>
            <span className="font-medium text-zinc-700">License: {article.hero_image_license || "Editorial Use"}</span>
          </figcaption>
        </figure>

        {/* Article Body */}
        <div className="prose prose-zinc max-w-none font-serif text-zinc-900 leading-relaxed text-base md:text-lg space-y-6">
          {contentBody
            .split("\n\n")
            .filter((p: string) => {
              const text = p.trim();
              if (!text) return false;
              if (text.includes("Verified reporting published by")) return false;
              if (text.includes("Cross-source verification indicates")) return false;
              if (text.includes("Mars News editorial intelligence")) return false;
              if (text.includes("Editorial review indicates consensus")) return false;
              return true;
            })
            .map((para: string, idx: number) => {
              const cleanedPara = para
                .replace(/\.\s*According to reports cross-verified across [^,.]+, the development represents an active news update in national and regional coverage\./gi, ".")
                .replace(/\.\s*According to reports compiled from verified publications including [^,.]+, the development represents a significant update in national coverage\./gi, ".")
                .replace(/\.\s*Reporting compiled across verified Indian news desks confirms key developments in this developing story\./gi, ".")
                .trim();
              return (
                <p key={idx} className="whitespace-pre-line">
                  {cleanedPara}
                </p>
              );
            })}
        </div>

        {/* Corrections Log if any */}
        {article.corrections && article.corrections.length > 0 && (
          <section className="bg-amber-50 border border-amber-200 rounded-xl p-5 space-y-2 text-xs">
            <div className="flex items-center space-x-1.5 font-bold text-amber-950">
              <AlertTriangle className="w-4 h-4 text-amber-600" />
              <span>Editorial Correction Notice</span>
            </div>
            {article.corrections.map((c: any, idx: number) => (
              <p key={idx} className="text-amber-900">
                <strong>{formatDate(c.corrected_at)}:</strong> {c.correction_notice} (Signed by {c.editor_name})
              </p>
            ))}
          </section>
        )}

        {/* Related Coverage */}
        {related && related.length > 0 && (
          <section className="pt-8 border-t border-zinc-200">
            <h3 className="font-serif text-2xl font-black text-zinc-950 mb-6 uppercase tracking-tight">
              Related Coverage
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
              {related.map((r: any) => (
                <ArticleCard key={r.id} article={r} variant="standard" />
              ))}
            </div>
          </section>
        )}
      </article>
    </>
  );
}
