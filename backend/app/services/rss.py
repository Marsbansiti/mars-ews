from datetime import datetime, timezone
from email.utils import format_datetime
from sqlalchemy.orm import Session
from app.models.articles import Article

def generate_public_rss_feed(db: Session, base_url: str = "https://marsnews.in") -> str:
    articles = db.query(Article).filter(Article.status == "PUBLISHED").order_by(Article.published_at.desc()).limit(50).all()

    now_rfc822 = format_datetime(datetime.now(timezone.utc))

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
        '  <channel>',
        '    <title>MARS NEWS — Automated Indian Digital Newspaper</title>',
        f'    <link>{base_url}</link>',
        '    <description>Verified, multi-source digital journalism covering National, Business, Tech, Sports, and Regional India.</description>',
        '    <language>en-in</language>',
        f'    <lastBuildDate>{now_rfc822}</lastBuildDate>',
        f'    <atom:link href="{base_url}/rss.xml" rel="self" type="application/rss+xml" />',
    ]

    for a in articles:
        pub_date = format_datetime(a.published_at) if a.published_at else now_rfc822
        clean_headline = a.headline.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        clean_summary = a.summary.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        cat_name = a.category_rel.name if a.category_rel else "General"

        lines.extend([
            '    <item>',
            f'      <title>{clean_headline}</title>',
            f'      <link>{base_url}/article/{a.slug}</link>',
            f'      <guid isPermaLink="true">{base_url}/article/{a.slug}</guid>',
            f'      <description>{clean_summary}</description>',
            f'      <category>{cat_name}</category>',
            f'      <pubDate>{pub_date}</pubDate>',
            '    </item>'
        ])

    lines.extend([
        '  </channel>',
        '</rss>'
    ])
    return "\n".join(lines)
