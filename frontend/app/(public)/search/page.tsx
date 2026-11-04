"use client";

import { useState } from "react";
import ArticleCard from "@/components/ArticleCard";
import { searchNews } from "@/lib/api";
import { Search, Loader2 } from "lucide-react";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setSearched(true);
    try {
      const data = await searchNews(query, category || undefined);
      setResults(data.articles || []);
    } catch (err) {
      setResults([]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="border-b-2 border-zinc-950 pb-4">
        <h1 className="font-serif text-3xl md:text-4xl font-black text-zinc-950 uppercase tracking-tight">
          Search Mars News
        </h1>
        <p className="text-zinc-600 text-sm mt-1">
          Search verified reports, archives, and multi-source coverage across India.
        </p>
      </div>

      <form onSubmit={handleSearch} className="space-y-4">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-zinc-400 absolute left-3 top-3" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search by keywords, people, institutions (e.g. ISRO, RBI, Odisha, Semiconductors)..."
              className="w-full pl-9 pr-4 py-2.5 text-sm border border-zinc-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-zinc-950"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="bg-zinc-950 hover:bg-zinc-800 text-white font-bold text-xs px-6 py-2.5 rounded-lg uppercase tracking-wider transition-colors flex items-center space-x-1.5 disabled:opacity-50"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <span>Search</span>}
          </button>
        </div>

        <div className="flex flex-wrap items-center gap-2 text-xs">
          <span className="text-zinc-500 font-medium">Filter Category:</span>
          {["All", "India", "Business", "Technology", "Science", "Odisha", "Sports"].map((cat) => {
            const isSelected = (cat === "All" && !category) || category === cat;
            return (
              <button
                key={cat}
                type="button"
                onClick={() => setCategory(cat === "All" ? "" : cat)}
                className={`px-2.5 py-1 rounded-full text-xs transition-colors ${
                  isSelected ? "bg-zinc-900 text-white font-bold" : "bg-zinc-100 text-zinc-700 hover:bg-zinc-200"
                }`}
              >
                {cat}
              </button>
            );
          })}
        </div>
      </form>

      {/* Results */}
      <div>
        {searched && (
          <p className="text-xs text-zinc-500 mb-4">
            Found {results.length} verified {results.length === 1 ? "article" : "articles"} for &ldquo;{query}&rdquo;
          </p>
        )}

        {results.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {results.map((art) => (
              <ArticleCard key={art.id} article={art} variant="standard" />
            ))}
          </div>
        ) : searched && !loading ? (
          <div className="p-12 text-center border rounded-lg bg-zinc-50 text-zinc-500 text-sm">
            No matching articles found. Try different search terms or clear category filters.
          </div>
        ) : null}
      </div>
    </div>
  );
}
