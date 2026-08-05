import { Link } from "react-router-dom";
import { useFetch } from "../hooks/useFetch";
import { useAuth } from "../hooks/useAuth";

export default function Home() {
  const { user } = useAuth();
  const { data, error, loading } = useFetch("/api/dashboard");

  return (
    <main className="page wide">
      <div className="page-head">
        <div>
          <h1>Dashboard</h1>
          <p className="lede">
            Aggregates from your subscriptions — spend, renewals, and trials
            ending soon.
          </p>
        </div>
        <Link className="button-link" to="/subscriptions/new">
          Add subscription
        </Link>
      </div>

      {loading && <p className="status">Loading dashboard…</p>}
      {error && <p className="error">{error.message}</p>}

      {data && (
        <>
          <section className="stats">
            <article className="panel compact">
              <h2>Active</h2>
              <p className="stat">{data.total_subscriptions}</p>
            </article>
            <article className="panel compact">
              <h2>Monthly spend</h2>
              <p className="stat">${Number(data.monthly_spend).toFixed(2)}</p>
            </article>
            <article className="panel compact">
              <h2>Trial alerts</h2>
              <p className="stat">{data.trial_alerts?.length ?? 0}</p>
            </article>
          </section>

          <section className="panel">
            <div className="section-head">
              <h2>Upcoming renewals</h2>
              <Link to="/subscriptions">View all</Link>
            </div>
            {data.upcoming_renewals?.length ? (
              <ul className="list">
                {data.upcoming_renewals.map((sub) => (
                  <li key={sub.id}>
                    <div>
                      <strong>
                        {sub.catalog_service?.service_name || "Service"}
                      </strong>
                      <span className="muted">
                        {" "}
                        · renews {sub.renewal_date}
                        {sub.is_trial ? " · trial" : ""}
                      </span>
                    </div>
                    <span>${Number(sub.cost).toFixed(2)}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="status">No subscriptions yet.</p>
            )}
          </section>

          <section className="panel">
            <h2>Trial alerts (next 7 days)</h2>
            {data.trial_alerts?.length ? (
              <ul className="list">
                {data.trial_alerts.map((sub) => (
                  <li key={sub.id}>
                    <div>
                      <strong>
                        {sub.catalog_service?.service_name || "Service"}
                      </strong>
                      <span className="muted">
                        {" "}
                        · expires {sub.trial_expiration_date}
                      </span>
                    </div>
                    <Link to={`/subscriptions/${sub.id}/edit`}>Edit</Link>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="status">No trials expiring soon.</p>
            )}
          </section>
        </>
      )}
    </main>
  );
}
