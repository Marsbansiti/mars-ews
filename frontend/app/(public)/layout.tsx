import Masthead from "@/components/Masthead";
import Navbar from "@/components/Navbar";
import BreakingTicker from "@/components/BreakingTicker";
import Footer from "@/components/Footer";
import { fetchBreakingNews } from "@/lib/api";

export default async function PublicLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  let breakingItems = [];
  try {
    breakingItems = await fetchBreakingNews();
  } catch (e) {
    breakingItems = [];
  }

  return (
    <>
      <Masthead />
      <Navbar />
      <BreakingTicker items={breakingItems} />
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-8">
        {children}
      </main>
      <Footer />
    </>
  );
}
