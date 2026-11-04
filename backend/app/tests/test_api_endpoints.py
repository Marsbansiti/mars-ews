import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["service"] == "MARS NEWS"

def test_public_categories():
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_public_sources():
    response = client.get("/api/v1/sources")
    assert response.status_code == 200
    sources = response.json()
    assert len(sources) > 0
    names = [s["publisher_name"] for s in sources]
    assert "The Hindu" in names
    assert "The Times of India" in names

def test_rss_feed():
    response = client.get("/api/v1/rss.xml")
    assert response.status_code == 200
    assert "application/rss+xml" in response.headers["content-type"]
    assert "<rss version=\"2.0\"" in response.text
    assert "<title>MARS NEWS" in response.text

def test_sitemap_xml():
    response = client.get("/api/v1/sitemap.xml")
    assert response.status_code == 200
    assert "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\"" in response.text

def test_admin_dashboard_unauthorized():
    response = client.get("/api/v1/admin/dashboard")
    assert response.status_code in [401, 403]
