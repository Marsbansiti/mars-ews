from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.articles import Article

def generate_xml_sitemap(db: Session, base_url: str = "https://marsnews.in") -> str:
    articles = db.query(Article).filter(Article.status == "PUBLISHED").order_by(Article.published_at.desc()).limit(500).all()

    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        f'  <url><loc>{base_url}/</loc><changefreq>always</changefreq><priority>1.0</priority></url>',
        f'  <url><loc>{base_url}/latest</loc><changefreq>always</changefreq><priority>0.9</priority></url>',
        f'  <url><loc>{base_url}/breaking</loc><changefreq>always</changefreq><priority>0.9</priority></url>',
        f'  <url><loc>{base_url}/india</loc><changefreq>hourly</changefreq><priority>0.8</priority></url>',
        f'  <url><loc>{base_url}/politics</loc><changefreq>hourly</changefreq><priority>0.8</priority></url>',
        f'  <url><loc>{base_url}/business</loc><changefreq>hourly</changefreq><priority>0.8</priority></url>',
        f'  <url><loc>{base_url}/technology</loc><changefreq>hourly</changefreq><priority>0.8</priority></url>',
        f'  <url><loc>{base_url}/sports</loc><changefreq>hourly</changefreq><priority>0.8</priority></url>',
        f'  <url><loc>{base_url}/entertainment</loc><changefreq>hourly</changefreq><priority>0.7</priority></url>',
        f'  <url><loc>{base_url}/education</loc><changefreq>daily</changefreq><priority>0.7</priority></url>',
        f'  <url><loc>{base_url}/science</loc><changefreq>daily</changefreq><priority>0.8</priority></url>',
        f'  <url><loc>{base_url}/lifestyle</loc><changefreq>daily</changefreq><priority>0.7</priority></url>',
        f'  <url><loc>{base_url}/regional</loc><changefreq>hourly</changefreq><priority>0.8</priority></url>',
        f'  <url><loc>{base_url}/odisha</loc><changefreq>hourly</changefreq><priority>0.8</priority></url>',
    ]

    for a in articles:
        lastmod = a.updated_at.strftime("%Y-%m-%d") if a.updated_at else datetime.now(timezone.utc).strftime("%Y-%m-%d")
        xml_lines.append(f'  <url><loc>{base_url}/article/{a.slug}</loc><lastmod>{lastmod}</lastmod><priority>0.7</priority></url>')

    xml_lines.append('</urlset>')
    return "\n".join(xml_lines)

def generate_google_news_sitemap(db: Session, base_url: str = "https://marsnews.in") -> str:
    """Generates Google News sitemap containing published articles from the last 48 hours."""
    articles = db.query(Article).filter(Article.status == "PUBLISHED").order_by(Article.published_at.desc()).limit(100).all()

    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">',
    ]

    for a in articles:
        pub_iso = a.published_at.isoformat() if a.published_at else datetime.now(timezone.utc).isoformat()
        clean_headline = a.headline.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
        xml_lines.extend([
            '  <url>',
            f'    <loc>{base_url}/article/{a.slug}</loc>',
            '    <news:news>',
            '      <news:publication>',
            '        <news:name>MARS NEWS</news:name>',
            '        <news:language>en</news:language>',
            '      </news:publication>',
            f'      <news:publication_date>{pub_iso}</news:publication_date>',
            f'      <news:title>{clean_headline}</news:title>',
            '    </news:news>',
            '  </url>'
        ])

    xml_lines.append('</urlset>')
    return "\n".join(xml_lines)
