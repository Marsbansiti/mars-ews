export default function NewsArticleStructuredData({ article }: { article: any }) {
  if (!article) return null;

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "NewsArticle",
    "headline": article.headline,
    "description": article.summary,
    "image": [
      article.hero_image_url || "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?auto=format&fit=crop&w=1200&q=80"
    ],
    "datePublished": article.published_at,
    "dateModified": article.updated_at || article.published_at,
    "author": [{
      "@type": "Organization",
      "name": "MARS NEWS AI Editorial Bureau",
      "url": "https://marsnews.in/about"
    }],
    "publisher": {
      "@type": "Organization",
      "name": "MARS NEWS",
      "url": "https://marsnews.in",
      "logo": {
        "@type": "ImageObject",
        "url": "https://marsnews.in/logo.png"
      }
    },
    "mainEntityOfPage": {
      "@type": "WebPage",
      "@id": `https://marsnews.in/article/${article.slug}`
    },
    "articleSection": article.category,
    "inLanguage": "en-IN"
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
    />
  );
}
