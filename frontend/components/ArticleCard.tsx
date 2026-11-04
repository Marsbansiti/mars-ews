"use client";

import React from "react";
import Link from "next/link";
import { Clock } from "lucide-react";
import { formatDate } from "@/lib/utils";

interface ArticleItem {
  id: string;
  slug: string;
  headline: string;
  summary: string;
  category: string;
  category_slug?: string;
  published_at?: string;
  hero_image_url?: string;
  hero_image_alt?: string;
  hero_image_caption?: string;
  reading_time_minutes?: number;
  readability_score?: number;
  sources_count?: number;
  claims_count?: number;
  is_breaking?: boolean;
  is_featured?: boolean;
  is_regional?: boolean;
  regional_state?: string;
}

export default function ArticleCard({
  article,
  variant = "standard",
}: {
  article: ArticleItem;
  variant?: "hero" | "standard" | "compact" | "horizontal";
}) {
  const imageUrl = article.hero_image_url || "/images/news-default.svg";

  const handleImageError = (e: React.SyntheticEvent<HTMLImageElement, Event>) => {
    const target = e.currentTarget;
    if (!target.src.includes("news-default.svg")) {
      target.src = "/images/news-default.svg";
    }
  };

  const cleanHeadline = (article.headline || "").replace(/^Report:\s*/i, "");
  let rawSummary = (article.summary || "")
    .replace(/^Key developments regarding\s+/i, "")
    .replace(/\.\s*Cross-verified across.*$/i, ".");
  if (rawSummary.includes("Verified reporting published by")) {
    rawSummary = cleanHeadline;
  }
  const cleanSummary = rawSummary;

  if (variant === "hero") {
    return (
      <article className="group bg-white border border-zinc-200 rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-0">
          <div className="lg:col-span-7 relative h-72 lg:h-[420px] overflow-hidden bg-zinc-900">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={imageUrl}
              alt={article.hero_image_alt || cleanHeadline}
              onError={handleImageError}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            />
            <div className="absolute top-3 left-3 flex flex-wrap gap-1.5">
              <span className="bg-rose-700 text-white font-bold text-[10px] tracking-wider uppercase px-2 py-0.5 rounded shadow">
                Featured Lead
              </span>
              {article.is_regional && (
                <span className="bg-amber-600 text-white font-bold text-[10px] tracking-wider uppercase px-2 py-0.5 rounded shadow">
                  {article.regional_state || "Regional"}
                </span>
              )}
            </div>
          </div>

          <div className="lg:col-span-5 p-6 md:p-8 flex flex-col justify-between">
            <div>
              <div className="flex items-center space-x-2 text-xs font-semibold text-rose-700 uppercase tracking-wider mb-2">
                <span>{article.category}</span>
                <span>·</span>
                <span suppressHydrationWarning className="text-zinc-500 font-normal">{formatDate(article.published_at)}</span>
              </div>

              <Link href={`/article/${article.slug}`}>
                <h2 className="font-serif text-2xl md:text-3xl font-extrabold text-zinc-950 group-hover:text-rose-700 leading-tight transition-colors mb-3">
                  {cleanHeadline}
                </h2>
              </Link>

              <p className="text-zinc-600 text-sm leading-relaxed line-clamp-3 mb-6">
                {cleanSummary}
              </p>
            </div>

            <div className="border-t border-zinc-100 pt-4 flex flex-wrap items-center justify-between gap-2 text-xs text-zinc-500">
              <span className="font-semibold text-rose-700 uppercase tracking-wider text-[11px]">
                {article.category} Special Report
              </span>

              <span className="flex items-center space-x-1 text-zinc-500">
                <Clock className="w-3.5 h-3.5" />
                <span>{article.reading_time_minutes || 2} min read</span>
              </span>
            </div>
          </div>
        </div>
      </article>
    );
  }

  if (variant === "compact") {
    return (
      <article className="group py-3 border-b border-zinc-100 last:border-0">
        <div className="flex items-center space-x-2 text-[11px] font-semibold text-rose-700 uppercase tracking-wider mb-1">
          <span>{article.category}</span>
          <span className="text-zinc-400">·</span>
          <span suppressHydrationWarning className="text-zinc-500 font-normal">{formatDate(article.published_at)}</span>
        </div>
        <Link href={`/article/${article.slug}`}>
          <h4 className="font-serif text-sm font-bold text-zinc-900 group-hover:text-rose-700 leading-snug transition-colors line-clamp-2">
            {cleanHeadline}
          </h4>
        </Link>
      </article>
    );
  }

  return (
    <article className="group bg-white border border-zinc-200 rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between">
      <div>
        <div className="relative h-44 overflow-hidden bg-zinc-900">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={imageUrl}
            alt={article.hero_image_alt || cleanHeadline}
            onError={handleImageError}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
          <div className="absolute top-2 left-2">
            <span className="bg-zinc-900/80 backdrop-blur-sm text-white text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded">
              {article.category}
            </span>
          </div>
        </div>

        <div className="p-4">
          <div className="flex items-center space-x-2 text-[11px] text-zinc-500 mb-1.5">
            <span suppressHydrationWarning>{formatDate(article.published_at)}</span>
            <span>·</span>
            <span>{article.reading_time_minutes || 2} min read</span>
          </div>

          <Link href={`/article/${article.slug}`}>
            <h3 className="font-serif text-base font-bold text-zinc-950 group-hover:text-rose-700 leading-snug line-clamp-2 mb-2 transition-colors">
              {cleanHeadline}
            </h3>
          </Link>

          <p className="text-zinc-600 text-xs leading-relaxed line-clamp-2 mb-4">
            {cleanSummary}
          </p>
        </div>
      </div>

      <div className="px-4 py-2.5 bg-zinc-50 border-t border-zinc-100 flex items-center justify-between text-[11px] text-zinc-500">
        <span className="font-semibold text-rose-700 uppercase tracking-wider text-[10px]">
          {article.category}
        </span>
        <span className="text-zinc-500 group-hover:text-zinc-900 font-medium transition-colors">
          Read Story →
        </span>
      </div>
    </article>
  );
}
