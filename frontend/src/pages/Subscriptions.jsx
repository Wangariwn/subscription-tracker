import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useFetch } from "../hooks/useFetch";
import { useApi } from "../hooks/useApi";

export default function Subscriptions() {
  const api = useApi();
  const [page, setPage] = useState(1);
  const [category, setCategory] = useState("");
  const [actionError, setActionError] = useState(null);
  const [actionStatus, setActionStatus] = useState(null);
  const [deletingId, setDeletingId] = useState(null);

  const query = useMemo(() => {
    const params = new URLSearchParams({
      page: String(page),
      per_page: "5",
    });
    if (category) params.set("category", category);
    return params.toString();
  }, [page, category]);

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

  return (
    <main className="page wide">
      <div className="page-head">
        <div>
          <h1>Subscriptions</h1>
          <p className="lede">Full CRUD against your personal association rows.</p>
        </div>
        <Link className="button-link" to="/subscriptions/new">
          Add subscription
        </Link>
      </div>

      <div className="toolbar panel compact">
        <label>
          Category filter
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
          </select>
        </label>
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
                      {sub.catalog_service?.category} · ${Number(sub.cost).toFixed(2)} ·
                      renews {sub.renewal_date}
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
            <p className="status">No subscriptions match this filter.</p>
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
