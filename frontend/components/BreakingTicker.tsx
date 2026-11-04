import Link from "next/link";
import { Zap } from "lucide-react";

interface BreakingItem {
  id: string;
  slug: string;
  headline: string;
}

export default function BreakingTicker({ items = [] }: { items?: BreakingItem[] }) {
  if (!items || items.length === 0) {
    return null;
  }

  return (
    <div className="bg-zinc-950 text-white flex items-center overflow-hidden border-b border-zinc-800">
      <div className="bg-rose-600 px-3 py-1.5 flex items-center space-x-1.5 shrink-0 z-10 font-bold text-xs uppercase tracking-wider">
        <Zap className="w-3.5 h-3.5 fill-current animate-pulse" />
        <span>Breaking News</span>
      </div>

      <div className="overflow-hidden whitespace-nowrap py-1.5 text-xs">
        <div className="animate-ticker space-x-8">
          {items.map((item, idx) => (
            <Link
              key={`${item.id}-${idx}`}
              href={`/article/${item.slug}`}
              className="inline-block text-zinc-200 hover:text-white transition-colors"
            >
              <span className="text-rose-400 font-semibold mr-1">●</span>
              {item.headline}
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
