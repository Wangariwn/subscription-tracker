import { useFetch } from "../hooks/useFetch";

export default function AdminUsers() {
  const { data, error, loading } = useFetch("/api/admin/users");

  return (
    <main className="page wide">
      <div className="page-head">
        <div>
          <h1>Users</h1>
          <p className="lede">Admin-only directory of every account on the platform.</p>
        </div>
        {data && (
          <span className="muted">
            {data.total} user{data.total === 1 ? "" : "s"}
          </span>
        )}
      </div>

      {loading && <p className="status">Loading users…</p>}
      {error && <p className="error">{error.message}</p>}

      {data && (
        <section className="panel">
          {data.users?.length ? (
            <ul className="list">
              {data.users.map((account) => (
                <li key={account.id}>
                  <div>
                    <strong>{account.username}</strong>
                    <div className="muted">{account.email}</div>
                  </div>
                  <span className={`role-badge role-${account.role}`}>
                    {account.role}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="status">No users found.</p>
          )}
        </section>
      )}
    </main>
  );
}
