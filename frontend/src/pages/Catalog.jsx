import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useFetch } from "../hooks/useFetch";

export default function Catalog() {
  const [page, setPage] = useState(1);
  const [category, setCategory] = useState("");

  const query = useMemo(() => {
    const params = new URLSearchParams({
      page: String(page),
      per_page: "6",
    });
    if (category) params.set("category", category);
    return params.toString();
  }, [page, category]);

  const { data, error, loading } = useFetch(`/api/catalog?${query}`);

  return (
    <main className="page wide">
      <div className="page-head">
        <div>
          <h1>Catalog</h1>
          <p className="lede">Browse service templates, then add one to your list.</p>
        </div>
        <Link className="button-link" to="/subscriptions/new">
          Add subscription
        </Link>
      </div>

      <div className="toolbar panel compact">
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
      </div>

      {loading && <p className="status">Loading catalog…</p>}
      {error && <p className="error">{error.message}</p>}

      {data && (
        <section className="panel">
          {data.items?.length ? (
            <ul className="list">
              {data.items.map((service) => (
                <li key={service.id}>
                  <div>
                    <strong>{service.service_name}</strong>
                    <div className="muted">
                      {service.category} · default $
                      {Number(service.default_cost).toFixed(2)}
                      {service.default_trial_days
                        ? ` · ${service.default_trial_days}-day trial`
                        : ""}
                    </div>
                  </div>
                  <Link
                    to="/subscriptions/new"
                    state={{ catalog_service_id: service.id, cost: service.default_cost }}
                  >
                    Track
                  </Link>
                </li>
              ))}
            </ul>
          ) : (
            <p className="status">No catalog services found.</p>
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
              Page {data.page} of {data.total_pages || 1}
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
