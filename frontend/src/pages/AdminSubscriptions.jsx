import { useMemo, useState } from "react";
import { useFetch } from "../hooks/useFetch";

const CATEGORIES = [
  "Streaming",
  "Music",
  "Productivity",
  "AI",
  "Cloud",
  "Education",
  "Fitness",
  "Gaming",
  "News",
  "Shopping",
];

export default function AdminSubscriptions() {
  const [page, setPage] = useState(1);
  const [q, setQ] = useState("");
  const [category, setCategory] = useState("");
  const [isTrial, setIsTrial] = useState("");
  const [minCost, setMinCost] = useState("");
  const [maxCost, setMaxCost] = useState("");

  const query = useMemo(() => {
    const params = new URLSearchParams({
      page: String(page),
      per_page: "8",
    });
    if (q.trim()) params.set("q", q.trim());
    if (category) params.set("category", category);
    if (isTrial !== "") params.set("is_trial", isTrial);
    if (minCost !== "") params.set("min_cost", minCost);
    if (maxCost !== "") params.set("max_cost", maxCost);
    return params.toString();
  }, [page, q, category, isTrial, minCost, maxCost]);

  const { data, error, loading } = useFetch(`/api/admin/subscriptions?${query}`);

  function resetFilters() {
    setPage(1);
    setQ("");
    setCategory("");
    setIsTrial("");
    setMinCost("");
    setMaxCost("");
  }

  return (
    <main className="page wide">
      <div className="page-head">
        <div>
          <h1>All subscriptions</h1>
          <p className="lede">
            Admin view of every subscription on the platform, including the owner.
          </p>
        </div>
      </div>

      <div className="toolbar panel compact filters">
        <label>
          Search
          <input
            value={q}
            onChange={(e) => {
              setPage(1);
              setQ(e.target.value);
            }}
            placeholder="Service, user, email…"
          />
        </label>
        <label>
          Category
          <select
            value={category}
            onChange={(e) => {
              setPage(1);
              setCategory(e.target.value);
            }}
          >
            <option value="">All</option>
            {CATEGORIES.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Trial
          <select
            value={isTrial}
            onChange={(e) => {
              setPage(1);
              setIsTrial(e.target.value);
            }}
          >
            <option value="">Any</option>
            <option value="true">Trials only</option>
            <option value="false">Paid only</option>
          </select>
        </label>
        <label>
          Min cost
          <input
            type="number"
            min="0"
            step="0.01"
            value={minCost}
            onChange={(e) => {
              setPage(1);
              setMinCost(e.target.value);
            }}
          />
        </label>
        <label>
          Max cost
          <input
            type="number"
            min="0"
            step="0.01"
            value={maxCost}
            onChange={(e) => {
              setPage(1);
              setMaxCost(e.target.value);
            }}
          />
        </label>
        <button type="button" className="linkish" onClick={resetFilters}>
          Reset
        </button>
      </div>

      {loading && <p className="status">Loading subscriptions…</p>}
      {error && <p className="error">{error.message}</p>}

      {data && (
        <section className="panel">
          {data.items?.length ? (
            <ul className="list">
              {data.items.map((sub) => (
                <li key={sub.id}>
                  <div>
                    <strong>
                      {sub.catalog_service?.service_name || "Service"}
                    </strong>
                    <div className="muted">
                      {sub.user?.username || "Unknown user"}
                      {sub.user?.email ? ` · ${sub.user.email}` : ""}
                      {" · "}
                      {sub.catalog_service?.category} · $
                      {Number(sub.cost).toFixed(2)} · renews {sub.renewal_date}
                      {sub.is_trial ? " · trial" : ""}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="status">No subscriptions match these filters.</p>
          )}

          <div className="pager">
            <button
              type="button"
              disabled={page <= 1 || loading}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
            >
              Previous
            </button>
            <span className="muted">
              Page {data.page} of {data.total_pages || 1} ({data.total} total)
            </span>
            <button
              type="button"
              disabled={page >= (data.total_pages || 1) || loading}
              onClick={() => setPage((p) => p + 1)}
            >
              Next
            </button>
          </div>
        </section>
      )}
    </main>
  );
}
