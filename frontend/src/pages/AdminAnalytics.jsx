import { useFetch } from "../hooks/useFetch";

export default function AdminAnalytics() {
  const { data, error, loading } = useFetch("/api/admin/analytics");

  return (
    <main className="page wide">
      <div className="page-head">
        <div>
          <h1>Platform analytics</h1>
          <p className="lede">
            Admin-only view of users, spend, categories, and popular services.
          </p>
        </div>
      </div>

      {loading && <p className="status">Loading analytics…</p>}
      {error && <p className="error">{error.message}</p>}

      {data && (
        <>
          <section className="stats">
            <article className="panel compact">
              <h2>Users</h2>
              <p className="stat">{data.total_users}</p>
            </article>
            <article className="panel compact">
              <h2>Admins</h2>
              <p className="stat">{data.total_admins}</p>
            </article>
            <article className="panel compact">
              <h2>Subscriptions</h2>
              <p className="stat">{data.total_subscriptions}</p>
            </article>
            <article className="panel compact">
              <h2>Platform spend</h2>
              <p className="stat">
                ${Number(data.platform_monthly_spend).toFixed(2)}
              </p>
            </article>
            <article className="panel compact">
              <h2>Active trials</h2>
              <p className="stat">{data.active_trials}</p>
            </article>
            <article className="panel compact">
              <h2>Catalog services</h2>
              <p className="stat">{data.catalog_services}</p>
            </article>
          </section>

          <section className="panel">
            <h2>Subscriptions by category</h2>
            {data.subscriptions_by_category?.length ? (
              <ul className="list">
                {data.subscriptions_by_category.map((row) => (
                  <li key={row.category}>
                    <div>
                      <strong>{row.category}</strong>
                      <div className="muted">
                        {row.subscription_count} subscription
                        {row.subscription_count === 1 ? "" : "s"}
                      </div>
                    </div>
                    <span>${Number(row.total_cost).toFixed(2)}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="status">No category data yet.</p>
            )}
          </section>

          <section className="panel">
            <h2>Popular services</h2>
            {data.popular_services?.length ? (
              <ul className="list">
                {data.popular_services.map((row) => (
                  <li key={row.service_name}>
                    <div>
                      <strong>{row.service_name}</strong>
                      <div className="muted">
                        {row.category} · {row.subscribers} subscriber
                        {row.subscribers === 1 ? "" : "s"}
                      </div>
                    </div>
                    <span>${Number(row.revenue).toFixed(2)}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="status">No popular services yet.</p>
            )}
          </section>
        </>
      )}
    </main>
  );
}
