import Link from "next/link";

const NAV_LINKS = [
  { label: "Home", href: "/" },
  { label: "Latest", href: "/latest" },
  { label: "Breaking", href: "/breaking" },
  { label: "India", href: "/india" },
  { label: "Politics", href: "/politics" },
  { label: "Business", href: "/business" },
  { label: "Technology", href: "/technology" },
  { label: "Sports", href: "/sports" },
  { label: "Entertainment", href: "/entertainment" },
  { label: "Science", href: "/science" },
  { label: "Education", href: "/education" },
  { label: "Lifestyle", href: "/lifestyle" },
  { label: "Regional", href: "/regional" },
  { label: "Odisha Desk", href: "/odisha", highlight: true },
];

export default function Navbar() {
  return (
    <nav className="border-t border-b-2 border-zinc-900 bg-white sticky top-0 z-40 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 overflow-x-auto scrollbar-none">
        <ul className="flex items-center space-x-1 sm:space-x-3 text-xs md:text-sm font-semibold tracking-wide whitespace-nowrap py-2.5">
          {NAV_LINKS.map((link) => (
            <li key={link.href}>
              <Link
                href={link.href}
                className={`px-2 py-1 rounded transition-colors ${
                  link.highlight
                    ? "bg-rose-900 text-white hover:bg-rose-950 font-bold"
                    : "text-zinc-800 hover:text-rose-700 hover:bg-zinc-50"
                }`}
              >
                {link.label}
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
}
