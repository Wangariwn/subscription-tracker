import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate, useParams } from "react-router-dom";
import { useFetch } from "../hooks/useFetch";
import { useApi } from "../hooks/useApi";

const emptyForm = {
  catalog_service_id: "",
  cost: "",
  renewal_date: "",
  is_trial: false,
  trial_expiration_date: "",
};

export default function SubscriptionForm() {
  const { id } = useParams();
  const isEdit = Boolean(id);
  const navigate = useNavigate();
  const location = useLocation();
  const api = useApi();

  const catalogQuery = useFetch("/api/catalog?page=1&per_page=50");
  const existing = useFetch(isEdit ? `/api/subscriptions/${id}` : null);

  const [form, setForm] = useState(() => {
    const preset = location.state || {};
    return {
      ...emptyForm,
      catalog_service_id: preset.catalog_service_id
        ? String(preset.catalog_service_id)
        : "",
      cost:
        preset.cost !== undefined && preset.cost !== null
          ? String(preset.cost)
          : "",
    };
  });
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!existing.data) return;
    setForm({
      catalog_service_id: String(existing.data.catalog_service_id),
      cost: String(existing.data.cost),
      renewal_date: existing.data.renewal_date || "",
      is_trial: Boolean(existing.data.is_trial),
      trial_expiration_date: existing.data.trial_expiration_date || "",
    });
  }, [existing.data]);

  function updateField(key) {
    return (event) => {
      const value =
        event.target.type === "checkbox"
          ? event.target.checked
          : event.target.value;
      setForm((prev) => ({ ...prev, [key]: value }));
    };
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError(null);
    setSuccess(null);
    setSaving(true);

    const payload = {
      catalog_service_id: Number(form.catalog_service_id),
      cost: Number(form.cost),
      renewal_date: form.renewal_date,
      is_trial: Boolean(form.is_trial),
      trial_expiration_date: form.is_trial
        ? form.trial_expiration_date || null
        : null,
    };

    try {
      if (isEdit) {
        await api.patch(`/subscriptions/${id}`, payload);
        setSuccess("Subscription updated.");
      } else {
        const created = await api.post("/subscriptions", payload);
        setSuccess("Subscription created.");
        navigate(`/subscriptions/${created.id}/edit`, { replace: true });
        return;
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  const loading = catalogQuery.loading || (isEdit && existing.loading);
  const loadError = catalogQuery.error || existing.error;

  return (
    <main className="page">
      <h1>{isEdit ? "Edit subscription" : "Add subscription"}</h1>
      <p className="lede">
        Pick a catalog service and save association details (cost, renewal, trial).
      </p>

      {loading && <p className="status">Loading form…</p>}
      {loadError && <p className="error">{loadError.message}</p>}

      {!loading && !loadError && (
        <form className="auth-form" onSubmit={handleSubmit}>
          <label>
            Catalog service
            <select
              value={form.catalog_service_id}
              onChange={updateField("catalog_service_id")}
              required
              disabled={isEdit}
            >
              <option value="">Select a service</option>
              {(catalogQuery.data?.items || []).map((service) => (
                <option key={service.id} value={service.id}>
                  {service.service_name} ({service.category}) — $
                  {Number(service.default_cost).toFixed(2)}
                </option>
              ))}
            </select>
          </label>

          <label>
            Cost
            <input
              type="number"
              min="0"
              step="0.01"
              value={form.cost}
              onChange={updateField("cost")}
              required
            />
          </label>

          <label>
            Renewal date
            <input
              type="date"
              value={form.renewal_date}
              onChange={updateField("renewal_date")}
              required
            />
          </label>

          <label className="checkbox">
            <input
              type="checkbox"
              checked={form.is_trial}
              onChange={updateField("is_trial")}
            />
            Free trial
          </label>

          {form.is_trial && (
            <label>
              Trial expiration
              <input
                type="date"
                value={form.trial_expiration_date}
                onChange={updateField("trial_expiration_date")}
                required
              />
            </label>
          )}

          {saving && <p className="status">Saving…</p>}
          {error && <p className="error">{error}</p>}
          {success && <p className="success">{success}</p>}

          <div className="row-actions">
            <button type="submit" disabled={saving}>
              {isEdit ? "Save changes" : "Create"}
            </button>
            <Link to="/subscriptions">Back to list</Link>
          </div>
        </form>
      )}
    </main>
  );
}
