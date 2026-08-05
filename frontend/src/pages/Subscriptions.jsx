import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useFetch } from "../hooks/useFetch";
import { useApi } from "../hooks/useApi";

export default function Subscriptions() {
  const api = useApi();
  const [page, setPage] = useState(1);
  const [q, setQ] = useState("");
  const [category, setCategory] = useState("");
  const [isTrial, setIsTrial] = useState("");
  const [minCost, setMinCost] = useState("");
  const [maxCost, setMaxCost] = useState("");
  const [actionError, setActionError] = useState(null);
  const [actionStatus, setActionStatus] = useState(null);
  const [deletingId, setDeletingId] = useState(null);

  const query = useMemo(() => {
    const params = new URLSearchParams({
      page: String(page),
      per_page: "5",
    });
    if (q.trim()) params.set("q", q.trim());
    if (category) params.set("category", category);
    if (isTrial !== "") params.set("is_trial", isTrial);
    if (minCost !== "") params.set("min_cost", minCost);
    if (maxCost !== "") params.set("max_cost", maxCost);
    return params.toString();
  }, [page, q, category, isTrial, minCost, maxCost]);

  const { data, error, loading, refetch } = useFetch(
    `/api/subscriptions?${query}`
  );

  async function handleDelete(id) {
    if (!window.confirm("Delete this subscription?")) return;
    setActionError(null);
    setActionStatus(null);
    setDeletingId(id);
    try {
      await api.del(`/subscriptions/${id}`);
      setActionStatus("Subscription deleted.");
      refetch();
    } catch (err) {
      setActionError(err.message);
    } finally {
      setDeletingId(null);
    }
  }

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
          <h1>Subscriptions</h1>
          <p className="lede">
            Your enrollments in catalog services — cost, renewal dates, and
            trial flags live on each subscription (the many-to-many join).
          </p>
        </div>
        <Link className="button-link" to="/subscriptions/new">
          Add subscription
        </Link>
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
            placeholder="Netflix, Music…"
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
            <option value="Streaming">Streaming</option>
            <option value="Music">Music</option>
            <option value="Productivity">Productivity</option>
            <option value="AI">AI</option>
            <option value="Cloud">Cloud</option>
            <option value="Education">Education</option>
            <option value="Fitness">Fitness</option>
            <option value="Gaming">Gaming</option>
            <option value="News">News</option>
            <option value="Shopping">Shopping</option>
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
        <Link to="/catalog">Browse catalog</Link>
      </div>

      {loading && <p className="status">Loading subscriptions…</p>}
      {error && <p className="error">{error.message}</p>}
      {actionError && <p className="error">{actionError}</p>}
      {actionStatus && <p className="success">{actionStatus}</p>}

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
                      {sub.catalog_service?.category} · $
                      {Number(sub.cost).toFixed(2)} · renews {sub.renewal_date}
                      {sub.is_trial ? " · trial" : ""}
                    </div>
                  </div>
                  <div className="row-actions">
                    <Link to={`/subscriptions/${sub.id}/edit`}>Edit</Link>
                    <button
                      type="button"
                      className="danger-link"
                      disabled={deletingId === sub.id}
                      onClick={() => handleDelete(sub.id)}
                    >
                      {deletingId === sub.id ? "Deleting…" : "Delete"}
                    </button>
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
