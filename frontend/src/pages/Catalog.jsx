import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { useApi } from "../hooks/useApi";
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

const emptyForm = {
  service_name: "",
  category: "Streaming",
  default_cost: "",
  default_trial_days: "0",
};

export default function Catalog() {
  const { isAdmin } = useAuth();
  const api = useApi();
  const [page, setPage] = useState(1);
  const [category, setCategory] = useState("");
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [saving, setSaving] = useState(false);
  const [actionError, setActionError] = useState(null);
  const [actionSuccess, setActionSuccess] = useState(null);

  const query = useMemo(() => {
    const params = new URLSearchParams({
      page: String(page),
      per_page: "6",
    });
    if (category) params.set("category", category);
    return params.toString();
  }, [page, category]);

  const { data, error, loading, refetch } = useFetch(`/api/catalog?${query}`);

  function updateField(key) {
    return (event) => {
      setForm((prev) => ({ ...prev, [key]: event.target.value }));
    };
  }

  function startEdit(service) {
    setEditingId(service.id);
    setForm({
      service_name: service.service_name,
      category: service.category,
      default_cost: String(service.default_cost),
      default_trial_days: String(service.default_trial_days ?? 0),
    });
    setActionError(null);
    setActionSuccess(null);
  }

  function cancelEdit() {
    setEditingId(null);
    setForm(emptyForm);
    setActionError(null);
  }

  async function handleSave(event) {
    event.preventDefault();
    setSaving(true);
    setActionError(null);
    setActionSuccess(null);

    const payload = {
      service_name: form.service_name.trim(),
      category: form.category,
      default_cost: Number(form.default_cost),
      default_trial_days: Number(form.default_trial_days),
    };

    try {
      if (editingId) {
        await api.patch(`/catalog/${editingId}`, payload);
        setActionSuccess("Catalog service updated.");
      } else {
        await api.post("/catalog", payload);
        setActionSuccess("Catalog service created.");
      }
      setEditingId(null);
      setForm(emptyForm);
      refetch();
    } catch (err) {
      setActionError(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(service) {
    if (
      !window.confirm(
        `Delete “${service.service_name}” from the catalog? This cannot be undone.`
      )
    ) {
      return;
    }
    setActionError(null);
    setActionSuccess(null);
    try {
      await api.del(`/catalog/${service.id}`);
      if (editingId === service.id) cancelEdit();
      setActionSuccess("Catalog service deleted.");
      refetch();
    } catch (err) {
      setActionError(err.message);
    }
  }

  return (
    <main className="page wide">
      <div className="page-head">
        <div>
          <h1>Catalog</h1>
          <p className="lede">
            {isAdmin
              ? "Browse templates, or add and edit them as an admin."
              : "Browse service templates, then add one to your list."}
          </p>
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
            {CATEGORIES.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </label>
      </div>

      {isAdmin && (
        <form className="auth-form" onSubmit={handleSave}>
          <h2>{editingId ? "Edit catalog service" : "Add catalog service"}</h2>
          <label>
            Service name
            <input
              value={form.service_name}
              onChange={updateField("service_name")}
              required
            />
          </label>
          <label>
            Category
            <select
              value={form.category}
              onChange={updateField("category")}
              required
            >
              {CATEGORIES.map((name) => (
                <option key={name} value={name}>
                  {name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Default cost
            <input
              type="number"
              min="0"
              step="0.01"
              value={form.default_cost}
              onChange={updateField("default_cost")}
              required
            />
          </label>
          <label>
            Default trial days
            <input
              type="number"
              min="0"
              step="1"
              value={form.default_trial_days}
              onChange={updateField("default_trial_days")}
              required
            />
          </label>
          {actionError && <p className="error">{actionError}</p>}
          {actionSuccess && <p className="success">{actionSuccess}</p>}
          <div className="row-actions">
            <button type="submit" disabled={saving}>
              {saving
                ? "Saving…"
                : editingId
                  ? "Save changes"
                  : "Create service"}
            </button>
            {editingId && (
              <button type="button" className="linkish" onClick={cancelEdit}>
                Cancel
              </button>
            )}
          </div>
        </form>
      )}

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
                  <div className="row-actions">
                    {isAdmin && (
                      <>
                        <button
                          type="button"
                          className="linkish"
                          onClick={() => startEdit(service)}
                        >
                          Edit
                        </button>
                        <button
                          type="button"
                          className="danger-link"
                          onClick={() => handleDelete(service)}
                        >
                          Delete
                        </button>
                      </>
                    )}
                    <Link
                      to="/subscriptions/new"
                      state={{
                        catalog_service_id: service.id,
                        cost: service.default_cost,
                      }}
                    >
                      Track
                    </Link>
                  </div>
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
