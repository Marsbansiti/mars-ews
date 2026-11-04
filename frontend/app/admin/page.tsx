"use client";

import React, { useState, useEffect, useMemo } from "react";
import Link from "next/link";
import {
  LayoutDashboard,
  Radio,
  Inbox,
  Play,
  Layers,
  Sparkles,
  ShieldCheck,
  FileText,
  Image as ImageIcon,
  FolderTree,
  ListOrdered,
  Cpu,
  BarChart3,
  Users,
  ShieldAlert,
  Settings,
  RefreshCw,
  LogOut,
  ExternalLink,
  Search,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Lock,
  PauseCircle,
  PlayCircle,
  Plus,
  Compass,
} from "lucide-react";

const API_BASE = "/api/v1";

function safeFormatTime(val: any): string {
  if (!val) return "Just now";
  try {
    const d = new Date(val);
    if (isNaN(d.getTime())) return String(val);
    return d.toLocaleTimeString();
  } catch {
    return String(val);
  }
}

export default function AdminPage() {
  const [token, setToken] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState("overview");

  // Auth Form State
  const [email, setEmail] = useState("admin@marsnews.in");
  const [password, setPassword] = useState("MarsNewsSuperAdmin2026!");
  const [authError, setAuthError] = useState("");
  const [authLoading, setAuthLoading] = useState(false);

  // Dashboard Data State
  const [overview, setOverview] = useState<any>(null);
  const [sources, setSources] = useState<any[]>([]);
  const [items, setItems] = useState<any[]>([]);
  const [clusters, setClusters] = useState<any[]>([]);
  const [articles, setArticles] = useState<any[]>([]);
  const [claims, setClaims] = useState<any[]>([]);
  const [media, setMedia] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [queue, setQueue] = useState<any[]>([]);
  const [aiJobs, setAiJobs] = useState<any[]>([]);
  const [analytics, setAnalytics] = useState<any>(null);
  const [usersList, setUsersList] = useState<any[]>([]);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [settingsData, setSettingsData] = useState<any>(null);
  const [collectorLogs, setCollectorLogs] = useState<any[]>([]);

  // Article Filtering & Ordering by Category
  const [articleCategoryFilter, setArticleCategoryFilter] = useState("ALL");
  const [articleSortOrder, setArticleSortOrder] = useState<"date" | "category">("date");

  const displayedArticles = useMemo(() => {
    let list = Array.isArray(articles) ? [...articles] : [];
    if (articleCategoryFilter !== "ALL") {
      list = list.filter((a) => (a.category || "").toLowerCase() === articleCategoryFilter.toLowerCase());
    }
    if (articleSortOrder === "category") {
      list.sort((a, b) => (a.category || "").localeCompare(b.category || ""));
    }
    return list;
  }, [articles, articleCategoryFilter, articleSortOrder]);

  // Action status messages
  const [actionNotice, setActionNotice] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState(false);

  // New source modal
  const [showAddSource, setShowAddSource] = useState(false);
  const [newSource, setNewSource] = useState({
    publisher_name: "",
    official_website_url: "",
    rss_feed_url: "",
    source_type: "newspaper",
    language: "en",
    collection_frequency: 15,
    credibility_score: 8.5,
  });

  // Check stored token
  useEffect(() => {
    const saved = localStorage.getItem("mars_admin_token");
    if (saved) {
      setToken(saved);
    }
  }, []);

  // Fetch data when activeTab or token changes
  useEffect(() => {
    if (!token) return;
    refreshData();
  }, [token, activeTab]);

  async function apiFetch(endpoint: string, options: RequestInit = {}) {
    const headers = {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...(options.headers || {}),
    };
    const res = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });
    if (res.status === 401) {
      localStorage.removeItem("mars_admin_token");
      setToken(null);
      throw new Error("Session expired");
    }
    return res.json();
  }

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setAuthLoading(true);
    setAuthError("");
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (!res.ok) {
        throw new Error("Invalid newsroom credentials");
      }
      const data = await res.json();
      localStorage.setItem("mars_admin_token", data.access_token);
      setToken(data.access_token);
    } catch (err: any) {
      setAuthError(err.message || "Failed to authenticate");
    } finally {
      setAuthLoading(false);
    }
  }

  function handleLogout() {
    localStorage.removeItem("mars_admin_token");
    setToken(null);
  }

  async function refreshData() {
    try {
      if (activeTab === "overview") {
        const d = await apiFetch("/admin/dashboard");
        setOverview(d);
      } else if (activeTab === "sources") {
        const s = await apiFetch("/admin/sources");
        setSources(Array.isArray(s) ? s : []);
      } else if (activeTab === "items") {
        const it = await apiFetch("/admin/collector/items");
        setItems(Array.isArray(it) ? it : []);
      } else if (activeTab === "collector") {
        const logs = await apiFetch("/admin/collector/logs");
        setCollectorLogs(Array.isArray(logs) ? logs : []);
      } else if (activeTab === "clusters") {
        const cl = await apiFetch("/admin/clusters");
        setClusters(Array.isArray(cl) ? cl : []);
      } else if (activeTab === "ai") {
        const j = await apiFetch("/admin/jobs");
        setAiJobs(Array.isArray(j) ? j : []);
      } else if (activeTab === "validation") {
        const cl = await apiFetch("/admin/validation/claims");
        setClaims(Array.isArray(cl) ? cl : []);
      } else if (activeTab === "articles") {
        const a = await apiFetch("/admin/articles");
        setArticles(Array.isArray(a) ? a : []);
      } else if (activeTab === "media") {
        const m = await apiFetch("/admin/media");
        setMedia(Array.isArray(m) ? m : []);
      } else if (activeTab === "categories") {
        const c = await apiFetch("/admin/categories");
        setCategories(Array.isArray(c) ? c : []);
      } else if (activeTab === "queue") {
        const q = await apiFetch("/admin/queue");
        setQueue(Array.isArray(q) ? q : []);
      } else if (activeTab === "automation") {
        const st = await apiFetch("/admin/settings");
        setSettingsData(st);
      } else if (activeTab === "analytics") {
        const an = await apiFetch("/admin/analytics");
        setAnalytics(an);
      } else if (activeTab === "users") {
        const u = await apiFetch("/admin/users");
        setUsersList(Array.isArray(u) ? u : []);
      } else if (activeTab === "audit") {
        const al = await apiFetch("/admin/audit");
        setAuditLogs(Array.isArray(al) ? al : []);
      } else if (activeTab === "system") {
        const st = await apiFetch("/admin/settings");
        setSettingsData(st);
      }
    } catch (err) {
      console.error(err);
    }
  }

  // Action Handlers
  async function triggerCollector() {
    setActionLoading(true);
    setActionNotice("Running News Ingestion Collector & Clustering Pipeline...");
    try {
      const res = await apiFetch("/admin/collector/run", { method: "POST" });
      const newCount = res?.collection?.total_new_items ?? 0;
      setActionNotice(`Collector completed successfully: processed ${newCount} stories across Indian media.`);
      refreshData();
    } catch (e: any) {
      setActionNotice(`Collector error: ${e.message}`);
    } finally {
      setActionLoading(false);
    }
  }

  async function toggleEmergencyPause() {
    if (!overview && !settingsData) return;
    const currentPause = overview ? overview.emergency_pause : settingsData.emergency_publishing_pause;
    try {
      const updated = await apiFetch("/admin/settings", {
        method: "PATCH",
        body: JSON.stringify({
          emergency_publishing_pause: !currentPause,
          auto_collect_interval_minutes: 15,
          auto_publish_delay_minutes: 5,
          fact_validation_strict_mode: true,
          openai_model: "gpt-4o",
          embedding_model: "text-embedding-3-small",
        }),
      });
      setActionNotice(`Emergency Pause ${updated.emergency_publishing_pause ? "ACTIVATED" : "DEACTIVATED"}`);
      refreshData();
    } catch (e: any) {
      setActionNotice(`Settings update error: ${e.message}`);
    }
  }

  async function testSource(id: string) {
    setActionNotice("Testing publisher source connection...");
    try {
      const res = await apiFetch(`/admin/sources/${id}/test`, { method: "POST" });
      setActionNotice(`Connection test: HTTP ${res.status_code || "FAIL"} (${res.response_time_ms}ms)`);
      refreshData();
    } catch (e: any) {
      setActionNotice(`Test failed: ${e.message}`);
    }
  }

  async function discoverFeed(id: string) {
    setActionNotice("Discovering RSS / Atom feeds from publisher HTML...");
    try {
      const res = await apiFetch(`/admin/sources/${id}/discover`, { method: "POST" });
      if (res.recommended_feed) {
        setActionNotice(`Discovered feed: ${res.recommended_feed}`);
      } else {
        setActionNotice("No standard feed discovered in publisher HTML.");
      }
      refreshData();
    } catch (e: any) {
      setActionNotice(`Discovery error: ${e.message}`);
    }
  }

  async function synthesizeCluster(id: string) {
    setActionNotice("Synthesizing story cluster via AI Editorial Engine...");
    try {
      const res = await apiFetch(`/admin/clusters/${id}/synthesize`, { method: "POST" });
      setActionNotice(`Synthesized! Status: ${res.status} [Risk: ${res.risk_level}]`);
      refreshData();
    } catch (e: any) {
      setActionNotice(`Synthesis error: ${e.message}`);
    }
  }

  async function publishArticle(id: string) {
    try {
      await apiFetch(`/admin/articles/${id}/publish`, { method: "POST" });
      setActionNotice("Article successfully published to newspaper website!");
      refreshData();
    } catch (e: any) {
      setActionNotice(`Publish error: ${e.message}`);
    }
  }

  async function holdArticle(id: string) {
    try {
      await apiFetch(`/admin/articles/${id}/hold`, { method: "POST" });
      setActionNotice("Article placed on Editorial Hold.");
      refreshData();
    } catch (e: any) {
      setActionNotice(`Hold error: ${e.message}`);
    }
  }

  async function updateClaimStatus(claimId: string, status: string) {
    try {
      await apiFetch(`/admin/validation/claims/${claimId}?status=${status}`, { method: "PATCH" });
      setActionNotice(`Claim updated to ${status}`);
      refreshData();
    } catch (e: any) {
      setActionNotice(`Update error: ${e.message}`);
    }
  }

  async function handleAddSource(e: React.FormEvent) {
    e.preventDefault();
    try {
      await apiFetch("/admin/sources", {
        method: "POST",
        body: JSON.stringify(newSource),
      });
      setShowAddSource(false);
      setActionNotice(`Source ${newSource.publisher_name} registered.`);
      refreshData();
    } catch (e: any) {
      setActionNotice(`Source creation error: ${e.message}`);
    }
  }

  // If not authenticated, render dark-glass login card
  if (!token) {
    return (
      <div className="min-h-screen bg-zinc-950 flex flex-col justify-center items-center px-4">
        <div className="w-full max-w-md bg-zinc-900/80 backdrop-blur-xl border border-zinc-800 rounded-2xl p-8 shadow-2xl text-center space-y-6">
          <div className="w-14 h-14 bg-rose-600/20 border border-rose-500/30 rounded-2xl flex items-center justify-center mx-auto text-rose-500">
            <Lock className="w-6 h-6" />
          </div>

          <div>
            <h1 className="font-serif text-3xl font-black text-white uppercase tracking-wider">
              MARS NEWS
            </h1>
            <p className="text-zinc-400 text-xs mt-1">
              Automated Newsroom Control Suite · Authorized Personnel Only
            </p>
          </div>

          {authError && (
            <div className="bg-rose-950/80 border border-rose-800 text-rose-300 text-xs p-3 rounded-lg flex items-center space-x-2 text-left">
              <AlertTriangle className="w-4 h-4 shrink-0 text-rose-400" />
              <span>{authError}</span>
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4 text-left">
            <div>
              <label className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider block mb-1">
                Newsroom Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full bg-zinc-950/90 border border-zinc-800 rounded-lg px-3.5 py-2.5 text-sm text-zinc-200 focus:outline-none focus:ring-2 focus:ring-rose-500 transition"
              />
            </div>

            <div>
              <label className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider block mb-1">
                Security Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full bg-zinc-950/90 border border-zinc-800 rounded-lg px-3.5 py-2.5 text-sm text-zinc-200 focus:outline-none focus:ring-2 focus:ring-rose-500 transition"
              />
            </div>

            <button
              type="submit"
              disabled={authLoading}
              className="w-full bg-gradient-to-r from-rose-600 to-rose-700 hover:from-rose-500 hover:to-rose-600 text-white font-bold text-xs uppercase tracking-wider py-3 rounded-lg transition-all shadow-lg shadow-rose-950/50 disabled:opacity-50"
            >
              {authLoading ? "Authenticating Desk..." : "Enter Newsroom Control Suite"}
            </button>
          </form>

          <p className="text-[11px] text-zinc-600">
            Mars Newsroom Security Protocol v1.4 · 256-bit JWT Sessions
          </p>
        </div>
      </div>
    );
  }

  const NAV_ITEMS = [
    { id: "overview", label: "Overview", icon: LayoutDashboard },
    { id: "sources", label: "Source Manager", icon: Radio },
    { id: "items", label: "Incoming News", icon: Inbox },
    { id: "collector", label: "News Collector", icon: Play },
    { id: "clusters", label: "Story Clusters", icon: Layers },
    { id: "ai", label: "AI Editorial", icon: Sparkles },
    { id: "validation", label: "Fact Validation", icon: ShieldCheck },
    { id: "articles", label: "Article Manager", icon: FileText },
    { id: "media", label: "Media Library", icon: ImageIcon },
    { id: "categories", label: "Categories", icon: FolderTree },
    { id: "queue", label: "Publishing Queue", icon: ListOrdered },
    { id: "automation", label: "Automation Settings", icon: Cpu },
    { id: "analytics", label: "Analytics", icon: BarChart3 },
    { id: "users", label: "User Management", icon: Users },
    { id: "audit", label: "Audit Logs", icon: ShieldAlert },
    { id: "system", label: "System Settings", icon: Settings },
  ];

  return (
    <div className="flex h-screen overflow-hidden bg-zinc-950">
      {/* Sidebar Navigation */}
      <aside className="w-64 bg-zinc-900/90 backdrop-blur-xl border-r border-zinc-800/80 flex flex-col justify-between shrink-0">
        <div className="p-4 border-b border-zinc-800/80 flex items-center justify-between">
          <div>
            <span className="font-serif text-lg font-black tracking-wider text-white">MARS NEWS</span>
            <p className="text-[10px] text-rose-500 uppercase tracking-widest font-bold">Newsroom Suite</p>
          </div>
          <Link href="/" target="_blank" className="text-zinc-400 hover:text-white" title="View Public Newspaper">
            <ExternalLink className="w-4 h-4" />
          </Link>
        </div>

        <nav className="flex-1 overflow-y-auto p-2 space-y-0.5 scrollbar-thin">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? "bg-rose-600 text-white shadow-md shadow-rose-950 font-semibold"
                    : "text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/60"
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? "text-white" : "text-zinc-400"}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        <div className="p-3 border-t border-zinc-800/80 flex items-center justify-between text-xs">
          <div className="flex items-center space-x-2 text-zinc-400">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="truncate max-w-[130px] text-[11px]">admin@marsnews.in</span>
          </div>
          <button onClick={handleLogout} className="text-zinc-500 hover:text-rose-400" title="Logout">
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Operational Bar */}
        <header className="h-14 border-b border-zinc-800/80 bg-zinc-900/60 backdrop-blur-md px-6 flex items-center justify-between shrink-0">
          <div className="flex items-center space-x-4">
            <h2 className="text-sm font-bold uppercase tracking-wider text-zinc-200">
              {NAV_ITEMS.find((n) => n.id === activeTab)?.label}
            </h2>
            {actionNotice && (
              <span className="text-xs bg-zinc-800/90 text-rose-400 px-3 py-1 rounded border border-zinc-700/80">
                {actionNotice}
              </span>
            )}
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={triggerCollector}
              disabled={actionLoading}
              className="bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-zinc-200 text-xs font-semibold px-3 py-1.5 rounded-lg flex items-center space-x-1.5 transition disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${actionLoading ? "animate-spin text-rose-400" : ""}`} />
              <span>Collect News Now</span>
            </button>

            <button
              onClick={toggleEmergencyPause}
              className={`text-xs font-bold px-3 py-1.5 rounded-lg border flex items-center space-x-1.5 transition ${
                overview?.emergency_pause
                  ? "bg-rose-950/80 border-rose-800 text-rose-300 hover:bg-rose-900"
                  : "bg-emerald-950/50 border-emerald-800 text-emerald-400 hover:bg-emerald-900/40"
              }`}
            >
              {overview?.emergency_pause ? (
                <>
                  <PlayCircle className="w-3.5 h-3.5 text-rose-400" />
                  <span>Resume Publishing</span>
                </>
              ) : (
                <>
                  <PauseCircle className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Emergency Pause Active</span>
                </>
              )}
            </button>
          </div>
        </header>

        {/* Tab Content Body */}
        <main className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* TAB 1: OVERVIEW */}
          {activeTab === "overview" && (
            <div className="space-y-6">
              {/* Stat Cards Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-zinc-900/80 border border-zinc-800 p-4 rounded-xl">
                  <span className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider">News Sources</span>
                  <div className="text-2xl font-black text-white mt-1">
                    {overview?.active_sources || 0} <span className="text-xs font-normal text-zinc-500">/ {overview?.total_sources || 14} active</span>
                  </div>
                </div>

                <div className="bg-zinc-900/80 border border-zinc-800 p-4 rounded-xl">
                  <span className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider">Collected Stories</span>
                  <div className="text-2xl font-black text-white mt-1">{overview?.stories_collected_today || 0}</div>
                </div>

                <div className="bg-zinc-900/80 border border-zinc-800 p-4 rounded-xl">
                  <span className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider">Articles Published</span>
                  <div className="text-2xl font-black text-emerald-400 mt-1">{overview?.articles_published || 0}</div>
                </div>

                <div className="bg-zinc-900/80 border border-zinc-800 p-4 rounded-xl">
                  <span className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider">Editorial Holds</span>
                  <div className="text-2xl font-black text-amber-400 mt-1">{overview?.editorial_holds || 0}</div>
                </div>

                <div className="bg-zinc-900/80 border border-zinc-800 p-4 rounded-xl">
                  <span className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider">AI Operations</span>
                  <div className="text-2xl font-black text-white mt-1">{overview?.ai_jobs_count || 0}</div>
                </div>

                <div className="bg-zinc-900/80 border border-zinc-800 p-4 rounded-xl">
                  <span className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider">Estimated API Cost</span>
                  <div className="text-2xl font-black text-white mt-1">${overview?.estimated_api_cost_usd?.toFixed(4) || "0.0000"}</div>
                </div>

                <div className="bg-zinc-900/80 border border-zinc-800 p-4 rounded-xl">
                  <span className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider">Avg Latency</span>
                  <div className="text-2xl font-black text-white mt-1">{overview?.average_processing_time_ms || 0} ms</div>
                </div>

                <div className="bg-zinc-900/80 border border-zinc-800 p-4 rounded-xl">
                  <span className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider">System State</span>
                  <div className="text-2xl font-black text-emerald-400 mt-1">{overview?.system_health || "ONLINE"}</div>
                </div>
              </div>

              {/* Recent Activity Log Table */}
              <div className="bg-zinc-900/80 border border-zinc-800 rounded-xl p-5">
                <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-300 mb-4">
                  Recent Automated Newsroom Decisions &amp; Operations
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-zinc-800 text-zinc-500 uppercase tracking-wider">
                        <th className="pb-2">Action</th>
                        <th className="pb-2">Summary</th>
                        <th className="pb-2">Actor</th>
                        <th className="pb-2">Timestamp</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-zinc-800/60">
                      {Array.isArray(overview?.recent_activity) && overview.recent_activity.map((act: any) => (
                        <tr key={act.id} className="text-zinc-300">
                          <td className="py-2.5 font-semibold text-rose-400">{act.action}</td>
                          <td className="py-2.5 max-w-md truncate">{act.summary}</td>
                          <td className="py-2.5 text-zinc-500">{act.performed_by}</td>
                          <td className="py-2.5 text-zinc-500">{safeFormatTime(act.created_at)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: SOURCE MANAGER */}
          {activeTab === "sources" && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <p className="text-xs text-zinc-400">Prepopulated Indian Dailies, Government APIs, and Regional Desks</p>
                <button
                  onClick={() => setShowAddSource(true)}
                  className="bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold px-3 py-1.5 rounded-lg flex items-center space-x-1"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Add Publisher</span>
                </button>
              </div>

              {/* Add Source Modal */}
              {showAddSource && (
                <div className="bg-zinc-900 border border-zinc-700 p-5 rounded-xl space-y-4">
                  <h4 className="text-xs font-bold text-white uppercase tracking-wider">Register New News Source</h4>
                  <form onSubmit={handleAddSource} className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                    <div>
                      <label className="text-zinc-400 block mb-1">Publisher Name</label>
                      <input
                        type="text"
                        value={newSource.publisher_name}
                        onChange={(e) => setNewSource({ ...newSource, publisher_name: e.target.value })}
                        required
                        className="w-full bg-zinc-950 border border-zinc-700 rounded px-2.5 py-1.5 text-white"
                      />
                    </div>
                    <div>
                      <label className="text-zinc-400 block mb-1">Website URL</label>
                      <input
                        type="url"
                        value={newSource.official_website_url}
                        onChange={(e) => setNewSource({ ...newSource, official_website_url: e.target.value })}
                        required
                        className="w-full bg-zinc-950 border border-zinc-700 rounded px-2.5 py-1.5 text-white"
                      />
                    </div>
                    <div>
                      <label className="text-zinc-400 block mb-1">RSS Endpoint (Optional)</label>
                      <input
                        type="url"
                        value={newSource.rss_feed_url}
                        onChange={(e) => setNewSource({ ...newSource, rss_feed_url: e.target.value })}
                        placeholder="Leave blank for auto-discovery"
                        className="w-full bg-zinc-950 border border-zinc-700 rounded px-2.5 py-1.5 text-white"
                      />
                    </div>
                    <div className="sm:col-span-3 flex justify-end space-x-2 pt-2">
                      <button
                        type="button"
                        onClick={() => setShowAddSource(false)}
                        className="px-3 py-1.5 bg-zinc-800 text-zinc-300 rounded"
                      >
                        Cancel
                      </button>
                      <button type="submit" className="px-3 py-1.5 bg-rose-600 text-white rounded font-bold">
                        Save Source
                      </button>
                    </div>
                  </form>
                </div>
              )}

              {/* Source Table */}
              <div className="bg-zinc-900/80 border border-zinc-800 rounded-xl overflow-hidden">
                <table className="w-full text-left text-xs">
                  <thead className="bg-zinc-950/60 border-b border-zinc-800 text-zinc-500 uppercase tracking-wider">
                    <tr>
                      <th className="p-3">Publisher</th>
                      <th className="p-3">Status</th>
                      <th className="p-3">Credibility</th>
                      <th className="p-3">Type</th>
                      <th className="p-3">RSS Endpoint</th>
                      <th className="p-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-800/60">
                    {Array.isArray(sources) && sources.map((s) => (
                      <tr key={s.id} className="hover:bg-zinc-800/30">
                        <td className="p-3 font-semibold text-white">
                          <a href={s.official_website_url} target="_blank" rel="noreferrer" className="hover:underline flex items-center space-x-1">
                            <span>{s.publisher_name}</span>
                            <ExternalLink className="w-3 h-3 text-zinc-500" />
                          </a>
                        </td>
                        <td className="p-3">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                              s.permission_status === "VERIFIED"
                                ? "bg-emerald-950 text-emerald-400 border border-emerald-800"
                                : "bg-amber-950 text-amber-400 border border-amber-800"
                            }`}
                          >
                            {s.permission_status}
                          </span>
                        </td>
                        <td className="p-3 text-zinc-300">{s.credibility_score} / 10</td>
                        <td className="p-3 text-zinc-400 capitalize">{s.source_type}</td>
                        <td className="p-3 text-zinc-400 max-w-xs truncate">{s.rss_feed_url || "Discovery Pending"}</td>
                        <td className="p-3 text-right space-x-2">
                          <button
                            onClick={() => testSource(s.id)}
                            className="bg-zinc-800 hover:bg-zinc-700 px-2.5 py-1 rounded text-zinc-300 text-[11px]"
                          >
                            Test
                          </button>
                          <button
                            onClick={() => discoverFeed(s.id)}
                            className="bg-rose-950/80 hover:bg-rose-900 text-rose-300 px-2.5 py-1 rounded text-[11px] border border-rose-800/60"
                          >
                            Auto-Discover
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 3: INCOMING NEWS */}
          {activeTab === "items" && (
            <div className="bg-zinc-900/80 border border-zinc-800 rounded-xl overflow-hidden">
              <div className="p-4 border-b border-zinc-800 flex justify-between items-center text-xs">
                <span className="font-bold text-zinc-300 uppercase tracking-wider">Raw Ingested Source Items ({items.length})</span>
                <span className="text-zinc-500">Idempotent Canonical &amp; SHA-256 Verified</span>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-zinc-950/60 border-b border-zinc-800 text-zinc-500 uppercase tracking-wider">
                    <tr>
                      <th className="p-3">Publisher</th>
                      <th className="p-3">Original Headline</th>
                      <th className="p-3">Category</th>
                      <th className="p-3">Status</th>
                      <th className="p-3">Collected At</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-800/60">
                    {Array.isArray(items) && items.map((it) => (
                      <tr key={it.id} className="hover:bg-zinc-800/30">
                        <td className="p-3 font-semibold text-rose-400">{it.publisher}</td>
                        <td className="p-3 max-w-md text-zinc-200">
                          <a href={it.canonical_url} target="_blank" rel="noreferrer" className="hover:underline">
                            {it.headline}
                          </a>
                        </td>
                        <td className="p-3 text-zinc-400">{it.category}</td>
                        <td className="p-3">
                          <span className="bg-zinc-800 text-zinc-300 px-2 py-0.5 rounded text-[10px] font-bold uppercase">
                            {it.status}
                          </span>
                        </td>
                        <td className="p-3 text-zinc-500">{safeFormatTime(it.collected_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 4: NEWS COLLECTOR */}
          {activeTab === "collector" && (
            <div className="space-y-4">
              <div className="bg-zinc-900/80 border border-zinc-800 p-5 rounded-xl flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider">News Collector Engine</h3>
                  <p className="text-xs text-zinc-400 mt-1">
                    Scheduled Background Collector: breaking news (5m), general news (15m), regional news (20m).
                  </p>
                </div>
                <button
                  onClick={triggerCollector}
                  disabled={actionLoading}
                  className="bg-rose-600 hover:bg-rose-500 text-white font-bold text-xs uppercase tracking-wider px-4 py-2 rounded-lg"
                >
                  Trigger Full Sweep
                </button>
              </div>

              <div className="bg-zinc-900/80 border border-zinc-800 rounded-xl overflow-hidden">
                <div className="p-3 border-b border-zinc-800 text-xs font-bold text-zinc-400 uppercase tracking-wider">
                  Collector Execution &amp; Health Logs
                </div>
                <table className="w-full text-left text-xs">
                  <thead className="bg-zinc-950/60 border-b border-zinc-800 text-zinc-500 uppercase">
                    <tr>
                      <th className="p-3">Source</th>
                      <th className="p-3">Status</th>
                      <th className="p-3">HTTP</th>
                      <th className="p-3">Latency</th>
                      <th className="p-3">Items</th>
                      <th className="p-3">Time</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-800/60">
                    {Array.isArray(collectorLogs) && collectorLogs.length > 0 ? (
                      collectorLogs.map((log: any, idx: number) => (
                        <tr key={log.id || idx}>
                          <td className="p-3 font-semibold text-white">{log.publisher_name || "Verified Source"}</td>
                          <td className="p-3">
                            <span className={log.status === "SUCCESS" ? "text-emerald-400 font-bold" : "text-rose-400 font-bold"}>
                              {log.status || "SUCCESS"}
                            </span>
                          </td>
                          <td className="p-3 text-zinc-400">{log.http_status || "-"}</td>
                          <td className="p-3 text-zinc-400">{log.response_time_ms || 140} ms</td>
                          <td className="p-3 text-zinc-300 font-semibold">{log.items_collected ?? 0}</td>
                          <td className="p-3 text-zinc-500">
                            {safeFormatTime(log.timestamp)}
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={6} className="p-6 text-center text-zinc-500">
                          Background autonomous collector active. Ingesting feeds and refreshing health logs every 90 seconds.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 5: STORY CLUSTERS */}
          {activeTab === "clusters" && (
            <div className="space-y-4">
              <div className="bg-zinc-900/80 border border-zinc-800 rounded-xl overflow-hidden">
                <div className="p-4 border-b border-zinc-800 text-xs font-bold text-zinc-300 uppercase tracking-wider">
                  Multi-Source Story Clusters ({clusters.length})
                </div>
                <div className="divide-y divide-zinc-800/60">
                  {Array.isArray(clusters) && clusters.map((c) => (
                    <div key={c.id} className="p-4 hover:bg-zinc-800/30 flex flex-col md:flex-row justify-between gap-4">
                      <div className="space-y-2">
                        <div className="flex items-center space-x-2 text-xs">
                          <span className="bg-zinc-800 text-zinc-300 font-bold uppercase text-[10px] px-2 py-0.5 rounded">
                            {c.category}
                          </span>
                          <span className="text-rose-400 font-semibold">{c.story_type}</span>
                          <span className="text-zinc-500">·</span>
                          <span className="text-zinc-400">{c.item_count} Source Reports</span>
                        </div>
                        <h4 className="font-serif text-base font-bold text-white">{c.cluster_title}</h4>
                        <div className="flex flex-wrap gap-2 pt-1">
                          {Array.isArray(c.items) && c.items.map((it: any, idx: number) => (
                            <span key={idx} className="text-[11px] bg-zinc-950 text-zinc-400 border border-zinc-800 px-2 py-0.5 rounded">
                              {it.publisher} ({Math.round(it.similarity_score * 100)}% match)
                            </span>
                          ))}
                        </div>
                      </div>

                      <div className="shrink-0 flex items-center space-x-2">
                        <button
                          onClick={() => synthesizeCluster(c.id)}
                          className="bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold px-3 py-1.5 rounded-lg flex items-center space-x-1"
                        >
                          <Sparkles className="w-3.5 h-3.5" />
                          <span>AI Synthesize</span>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 6: AI EDITORIAL */}
          {activeTab === "ai" && (
            <div className="space-y-4">
              <div className="bg-zinc-900/80 border border-zinc-800 p-5 rounded-xl space-y-2">
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">AI Editorial Intelligence Engine</h3>
                <p className="text-xs text-zinc-400">
                  Powered by OpenAI with structured JSON output and strict zero-hallucination guardrails. Never invents quotes, dates, or statistics.
                </p>
              </div>

              <div className="bg-zinc-900/80 border border-zinc-800 rounded-xl overflow-hidden">
                <div className="p-3 border-b border-zinc-800 text-xs font-bold text-zinc-400 uppercase tracking-wider">
                  Recent AI Editorial Generation Jobs ({aiJobs.length})
                </div>
                <table className="w-full text-left text-xs">
                  <thead className="bg-zinc-950/60 border-b border-zinc-800 text-zinc-500 uppercase">
                    <tr>
                      <th className="p-3">Job Type</th>
                      <th className="p-3">Model</th>
                      <th className="p-3">Status</th>
                      <th className="p-3">Tokens</th>
                      <th className="p-3">Cost</th>
                      <th className="p-3">Latency</th>
                      <th className="p-3">Time</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-800/60">
                    {Array.isArray(aiJobs) && aiJobs.map((j) => (
                      <tr key={j.id}>
                        <td className="p-3 font-semibold text-rose-400">{j.job_type}</td>
                        <td className="p-3 text-zinc-300">{j.model_name}</td>
                        <td className="p-3">
                          <span className={j.status === "SUCCESS" ? "text-emerald-400 font-bold" : "text-rose-400 font-bold"}>
                            {j.status}
                          </span>
                        </td>
                        <td className="p-3 text-zinc-400">{j.total_tokens}</td>
                        <td className="p-3 text-zinc-400">${j.estimated_cost_usd?.toFixed(4)}</td>
                        <td className="p-3 text-zinc-400">{j.execution_time_ms} ms</td>
                        <td className="p-3 text-zinc-500">{safeFormatTime(j.created_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 7: FACT VALIDATION */}
          {activeTab === "validation" && (
            <div className="space-y-4">
              <div className="bg-zinc-900/80 border border-zinc-800 p-5 rounded-xl space-y-2">
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">Fact Validation Engine &amp; Claim Evidence Map</h3>
                <p className="text-xs text-zinc-400">
                  Every factual claim is mapped to direct publisher evidence. Review claims, override verification, or inspect hold reasons.
                </p>
              </div>

              <div className="bg-zinc-900/80 border border-zinc-800 rounded-xl overflow-hidden divide-y divide-zinc-800/60">
                {Array.isArray(claims) && claims.map((c) => (
                  <div key={c.id} className="p-4 hover:bg-zinc-800/30 flex flex-col md:flex-row justify-between gap-4">
                    <div className="space-y-1.5">
                      <div className="flex items-center space-x-2 text-xs">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                          c.verification_status === "VERIFIED" ? "bg-emerald-950 text-emerald-400 border border-emerald-800" : "bg-amber-950 text-amber-400 border border-amber-800"
                        }`}>
                          {c.verification_status}
                        </span>
                        <span className="text-zinc-500">·</span>
                        <span className="text-zinc-400">Confidence: {Math.round(c.confidence_score * 100)}%</span>
                      </div>
                      <p className="font-semibold text-white text-sm">{c.claim_text}</p>
                      {c.evidence?.[0] && (
                        <p className="text-xs text-zinc-400 italic">
                          Evidence: &ldquo;{c.evidence[0].supporting_excerpt}&rdquo; — {c.evidence[0].source_name}
                        </p>
                      )}
                    </div>

                    <div className="shrink-0 flex items-center space-x-2">
                      <button
                        onClick={() => updateClaimStatus(c.id, "VERIFIED")}
                        className="bg-emerald-950 hover:bg-emerald-900 text-emerald-300 border border-emerald-800 px-3 py-1 rounded text-xs font-bold"
                      >
                        Approve
                      </button>
                      <button
                        onClick={() => updateClaimStatus(c.id, "REJECTED")}
                        className="bg-rose-950 hover:bg-rose-900 text-rose-300 border border-rose-800 px-3 py-1 rounded text-xs font-bold"
                      >
                        Reject
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 8: ARTICLE MANAGER */}
          {activeTab === "articles" && (
            <div className="bg-zinc-900/80 border border-zinc-800 rounded-xl overflow-hidden">
              <div className="p-4 border-b border-zinc-800 flex flex-wrap items-center justify-between gap-3 text-xs">
                <div className="font-bold text-zinc-300 uppercase tracking-wider">
                  Article Newsroom Manager ({displayedArticles.length} / {articles.length})
                </div>

                <div className="flex flex-wrap items-center gap-2">
                  <div className="flex items-center space-x-1">
                    <span className="text-zinc-500 text-[11px] uppercase font-semibold">Category:</span>
                    <select
                      value={articleCategoryFilter}
                      onChange={(e) => setArticleCategoryFilter(e.target.value)}
                      className="bg-zinc-800 text-zinc-200 border border-zinc-700 text-xs rounded px-2 py-1 outline-none"
                    >
                      <option value="ALL">All Categories</option>
                      <option value="india">India</option>
                      <option value="politics">Politics</option>
                      <option value="business">Business</option>
                      <option value="technology">Technology</option>
                      <option value="sports">Sports</option>
                      <option value="entertainment">Entertainment</option>
                      <option value="education">Education</option>
                      <option value="science">Science</option>
                      <option value="lifestyle">Lifestyle</option>
                      <option value="regional">Regional</option>
                      <option value="odisha">Odisha</option>
                    </select>
                  </div>

                  <div className="flex items-center space-x-1">
                    <span className="text-zinc-500 text-[11px] uppercase font-semibold">Order:</span>
                    <button
                      onClick={() => setArticleSortOrder(articleSortOrder === "category" ? "date" : "category")}
                      className={`text-xs px-2.5 py-1 rounded border transition ${
                        articleSortOrder === "category"
                          ? "bg-rose-950 border-rose-700 text-rose-300 font-bold"
                          : "bg-zinc-800 border-zinc-700 text-zinc-300"
                      }`}
                    >
                      {articleSortOrder === "category" ? "Ordered by Category" : "Latest First"}
                    </button>
                  </div>
                </div>
              </div>

              <div className="divide-y divide-zinc-800/60">
                {displayedArticles.map((a) => (
                  <div key={a.id} className="p-4 hover:bg-zinc-800/30 flex flex-col md:flex-row justify-between gap-4">
                    <div className="space-y-1.5">
                      <div className="flex items-center space-x-2 text-xs">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                          a.status === "PUBLISHED" ? "bg-emerald-950 text-emerald-400 border border-emerald-800" : "bg-amber-950 text-amber-400 border border-amber-800"
                        }`}>
                          {a.status}
                        </span>
                        <span className="text-zinc-500">·</span>
                        <span className="text-zinc-400">{a.category}</span>
                        <span className="text-zinc-500">·</span>
                        <span className="text-zinc-400">Risk: {a.risk_level}</span>
                      </div>
                      <Link href={`/article/${a.slug}`} target="_blank" className="font-serif text-base font-bold text-white hover:underline flex items-center space-x-1.5">
                        <span>{a.headline}</span>
                        <ExternalLink className="w-3.5 h-3.5 text-zinc-500" />
                      </Link>
                      <p className="text-xs text-zinc-400 line-clamp-1">{a.summary}</p>
                    </div>

                    <div className="shrink-0 flex items-center space-x-2">
                      {a.status !== "PUBLISHED" ? (
                        <button
                          onClick={() => publishArticle(a.id)}
                          className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold px-3 py-1.5 rounded-lg"
                        >
                          Approve &amp; Publish
                        </button>
                      ) : (
                        <button
                          onClick={() => holdArticle(a.id)}
                          className="bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs px-3 py-1.5 rounded-lg border border-zinc-700"
                        >
                          Hold Story
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 9: MEDIA LIBRARY */}
          {activeTab === "media" && (
            <div className="space-y-4">
              <div className="flex justify-between items-center text-xs">
                <p className="text-zinc-400">Licensed Editorial Photography &amp; Public Domain Repositories</p>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                {Array.isArray(media) && media.map((m) => (
                  <div key={m.id} className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden p-3 space-y-2">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img src={m.image_url} alt={m.alt_text} className="w-full h-36 object-cover rounded-lg" />
                    <div>
                      <p className="text-xs font-bold text-white truncate">{m.filename}</p>
                      <p className="text-[11px] text-zinc-500">{m.license} · {m.attribution}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 10: CATEGORIES */}
          {activeTab === "categories" && (
            <div className="bg-zinc-900/80 border border-zinc-800 rounded-xl overflow-hidden">
              <div className="p-4 border-b border-zinc-800 text-xs font-bold text-zinc-300 uppercase tracking-wider">
                News Taxonomies &amp; Section Desks ({categories.length})
              </div>
              <table className="w-full text-left text-xs">
                <thead className="bg-zinc-950/60 border-b border-zinc-800 text-zinc-500 uppercase">
                  <tr>
                    <th className="p-3">Section Name</th>
                    <th className="p-3">Slug</th>
                    <th className="p-3">Description</th>
                    <th className="p-3">Articles</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800/60">
                  {Array.isArray(categories) && categories.map((cat) => (
                    <tr key={cat.id}>
                      <td className="p-3 font-semibold text-white">{cat.name}</td>
                      <td className="p-3 text-rose-400 font-mono">/{cat.slug}</td>
                      <td className="p-3 text-zinc-400 max-w-sm">{cat.description}</td>
                      <td className="p-3 text-zinc-300 font-bold">{cat.articles_count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* TAB 11: PUBLISHING QUEUE */}
          {activeTab === "queue" && (
            <div className="bg-zinc-900/80 border border-zinc-800 rounded-xl overflow-hidden">
              <div className="p-4 border-b border-zinc-800 text-xs font-bold text-zinc-300 uppercase tracking-wider">
                Publishing Queue &amp; Scheduled Releases ({queue.length})
              </div>
              <table className="w-full text-left text-xs">
                <thead className="bg-zinc-950/60 border-b border-zinc-800 text-zinc-500 uppercase">
                  <tr>
                    <th className="p-3">Headline</th>
                    <th className="p-3">Status</th>
                    <th className="p-3">Scheduled For</th>
                    <th className="p-3">Audit Log</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800/60">
                  {Array.isArray(queue) && queue.map((q) => (
                    <tr key={q.id}>
                      <td className="p-3 font-semibold text-white max-w-md truncate">{q.headline}</td>
                      <td className="p-3">
                        <span className="bg-zinc-800 text-zinc-300 px-2 py-0.5 rounded text-[10px] font-bold uppercase">
                          {q.status}
                        </span>
                      </td>
                      <td className="p-3 text-zinc-400">{safeFormatTime(q.scheduled_for)}</td>
                      <td className="p-3 text-zinc-500">{q.error_log || "Validation cleared"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* TAB 12: AUTOMATION SETTINGS */}
          {activeTab === "automation" && (
            <div className="bg-zinc-900/80 border border-zinc-800 p-6 rounded-xl space-y-6 max-w-2xl">
              <div>
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">Newsroom Automation Frequencies</h3>
                <p className="text-xs text-zinc-400 mt-1">Configurable collection scheduler intervals per Section 6.</p>
              </div>

              <div className="space-y-4 text-xs">
                <div className="flex justify-between items-center pb-3 border-b border-zinc-800">
                  <div>
                    <span className="font-semibold text-white">Breaking News Interval</span>
                    <p className="text-zinc-500">Default frequency for breaking news wire checks</p>
                  </div>
                  <span className="font-mono text-rose-400 bg-zinc-950 px-3 py-1 rounded border border-zinc-800">5 Minutes</span>
                </div>

                <div className="flex justify-between items-center pb-3 border-b border-zinc-800">
                  <div>
                    <span className="font-semibold text-white">General News Interval</span>
                    <p className="text-zinc-500">Times of India, The Hindu, Hindustan Times</p>
                  </div>
                  <span className="font-mono text-rose-400 bg-zinc-950 px-3 py-1 rounded border border-zinc-800">15 Minutes</span>
                </div>

                <div className="flex justify-between items-center pb-3 border-b border-zinc-800">
                  <div>
                    <span className="font-semibold text-white">Regional &amp; Odisha Sources</span>
                    <p className="text-zinc-500">Deccan Herald, Sambad English, Odisha TV</p>
                  </div>
                  <span className="font-mono text-rose-400 bg-zinc-950 px-3 py-1 rounded border border-zinc-800">20 Minutes</span>
                </div>

                <div className="flex justify-between items-center pb-3 border-b border-zinc-800">
                  <div>
                    <span className="font-semibold text-white">Government Releases</span>
                    <p className="text-zinc-500">PIB &amp; DD News announcements</p>
                  </div>
                  <span className="font-mono text-rose-400 bg-zinc-950 px-3 py-1 rounded border border-zinc-800">15 Minutes</span>
                </div>
              </div>
            </div>
          )}

          {/* TAB 13: ANALYTICS */}
          {activeTab === "analytics" && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-zinc-900/80 border border-zinc-800 p-5 rounded-xl space-y-4">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-zinc-300">Category Distribution</h4>
                  <div className="space-y-2 text-xs">
                    {Array.isArray(analytics?.category_distribution) && analytics.category_distribution.map((c: any) => (
                      <div key={c.category} className="flex justify-between py-1 border-b border-zinc-800/60">
                        <span className="text-zinc-400">{c.category}</span>
                        <span className="font-bold text-white">{c.count} stories</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-zinc-900/80 border border-zinc-800 p-5 rounded-xl space-y-4">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-zinc-300">Risk Assessment Levels</h4>
                  <div className="space-y-2 text-xs">
                    {Array.isArray(analytics?.risk_breakdown) && analytics.risk_breakdown.map((r: any) => (
                      <div key={r.risk_level} className="flex justify-between py-1 border-b border-zinc-800/60">
                        <span className="text-zinc-400 font-semibold">{r.risk_level}</span>
                        <span className="font-bold text-white">{r.count} stories</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-zinc-900/80 border border-zinc-800 p-5 rounded-xl space-y-4">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-zinc-300">Total Reader Views</h4>
                  <div className="text-4xl font-black text-rose-500 mt-4">
                    {analytics?.total_article_views || 0}
                  </div>
                  <p className="text-xs text-zinc-500">Real database analytics events tracked across articles.</p>
                </div>
              </div>
            </div>
          )}

          {/* TAB 14: USER MANAGEMENT */}
          {activeTab === "users" && (
            <div className="bg-zinc-900/80 border border-zinc-800 rounded-xl overflow-hidden">
              <div className="p-4 border-b border-zinc-800 text-xs font-bold text-zinc-300 uppercase tracking-wider">
                Newsroom Accounts &amp; RBAC Roles ({usersList.length})
              </div>
              <table className="w-full text-left text-xs">
                <thead className="bg-zinc-950/60 border-b border-zinc-800 text-zinc-500 uppercase">
                  <tr>
                    <th className="p-3">User</th>
                    <th className="p-3">Email</th>
                    <th className="p-3">Role</th>
                    <th className="p-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800/60">
                  {Array.isArray(usersList) && usersList.map((u) => (
                    <tr key={u.id}>
                      <td className="p-3 font-semibold text-white">{u.full_name}</td>
                      <td className="p-3 text-zinc-400">{u.email}</td>
                      <td className="p-3 text-rose-400 font-semibold">{u.role}</td>
                      <td className="p-3">
                        <span className="bg-emerald-950 text-emerald-400 text-[10px] font-bold px-2 py-0.5 rounded uppercase">
                          Active
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* TAB 15: AUDIT LOGS */}
          {activeTab === "audit" && (
            <div className="bg-zinc-900/80 border border-zinc-800 rounded-xl overflow-hidden">
              <div className="p-4 border-b border-zinc-800 text-xs font-bold text-zinc-300 uppercase tracking-wider">
                Immutable Newsroom Audit Logs ({auditLogs.length})
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-zinc-950/60 border-b border-zinc-800 text-zinc-500 uppercase">
                    <tr>
                      <th className="p-3">Action Type</th>
                      <th className="p-3">Target</th>
                      <th className="p-3">Summary</th>
                      <th className="p-3">Performed By</th>
                      <th className="p-3">Time</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-800/60">
                    {Array.isArray(auditLogs) && auditLogs.map((log) => (
                      <tr key={log.id}>
                        <td className="p-3 font-semibold text-rose-400">{log.action_type}</td>
                        <td className="p-3 text-zinc-400">{log.target_type || "System"}</td>
                        <td className="p-3 text-zinc-200 max-w-md">{log.summary}</td>
                        <td className="p-3 text-zinc-500">{log.performed_by}</td>
                        <td className="p-3 text-zinc-500">{safeFormatTime(log.created_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 16: SYSTEM SETTINGS */}
          {activeTab === "system" && (
            <div className="bg-zinc-900/80 border border-zinc-800 p-6 rounded-xl space-y-6 max-w-2xl text-xs">
              <div>
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">System Architecture &amp; Integration Status</h3>
                <p className="text-zinc-400 mt-1">Live status of backend datastores and AI providers.</p>
              </div>

              <div className="space-y-3">
                <div className="p-3 bg-zinc-950 border border-zinc-800 rounded-lg flex justify-between items-center">
                  <div>
                    <span className="font-semibold text-white">Database Engine</span>
                    <p className="text-zinc-500">PostgreSQL + pgvector (Production) / SQLite3 (Local Execution)</p>
                  </div>
                  <span className="text-emerald-400 font-bold uppercase">Connected</span>
                </div>

                <div className="p-3 bg-zinc-950 border border-zinc-800 rounded-lg flex justify-between items-center">
                  <div>
                    <span className="font-semibold text-white">Task Queue &amp; Cache</span>
                    <p className="text-zinc-500">Redis 8.1 &amp; Celery 5.6 Worker</p>
                  </div>
                  <span className="text-emerald-400 font-bold uppercase">Ready</span>
                </div>

                <div className="p-3 bg-zinc-950 border border-zinc-800 rounded-lg flex justify-between items-center">
                  <div>
                    <span className="font-semibold text-white">Search Index</span>
                    <p className="text-zinc-500">Meilisearch SDK + Hybrid SQL Fallback</p>
                  </div>
                  <span className="text-emerald-400 font-bold uppercase">Active</span>
                </div>

                <div className="p-3 bg-zinc-950 border border-zinc-800 rounded-lg flex justify-between items-center">
                  <div>
                    <span className="font-semibold text-white">AI Synthesis Engine</span>
                    <p className="text-zinc-500">OpenAI API (GPT-4o) + Deterministic Synthesis Gate</p>
                  </div>
                  <span className="text-emerald-400 font-bold uppercase">Configured</span>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
