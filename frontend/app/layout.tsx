import type { Metadata } from "next";
import "./globals.css";
import Masthead from "@/components/Masthead";
import Navbar from "@/components/Navbar";
import BreakingTicker from "@/components/BreakingTicker";
import Footer from "@/components/Footer";

export const metadata: Metadata = {
  title: "MARS NEWS — Automated Indian Digital Newspaper & News Intelligence",
  description: "India's premier AI-powered digital newspaper. Multi-source verified coverage spanning National, Politics, Business, Tech, Odisha, and Science.",
  keywords: ["India News", "Digital Newspaper", "AI Journalism", "Odisha News", "Verified News", "ISRO", "Business News India"],
  openGraph: {
    title: "MARS NEWS — The Digital Voice of India",
    description: "Multi-source verified coverage with automated fact validation.",
    url: "https://marsnews.in",
    siteName: "MARS NEWS",
    locale: "en_IN",
    type: "website",
  },
  alternates: {
    types: {
      "application/rss+xml": "https://marsnews.in/api/v1/rss.xml",
    },
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col bg-[#fbfbfb]">
        {children}
      </body>
    </html>
  );
}
