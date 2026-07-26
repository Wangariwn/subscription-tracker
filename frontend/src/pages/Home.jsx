import { useFetch } from "../hooks/useFetch";
import { useAuth } from "../hooks/useAuth";

export default function Home() {
  const { user, logout } = useAuth();
  const { data, error, loading } = useFetch("/api/auth/me");

  return (
    <main className="page">
      <h1>Welcome{user?.username ? `, ${user.username}` : ""}</h1>
      <p className="lede">
        You are signed in. Protected API calls attach your JWT automatically.
      </p>

      {loading && <p className="status">Loading profile…</p>}
      {error && <p className="error">{error.message}</p>}
      {data && (
        <section className="panel">
          <h2>Session</h2>
          <dl className="meta">
            <div>
              <dt>Username</dt>
              <dd>{data.username}</dd>
            </div>
            <div>
              <dt>Email</dt>
              <dd>{data.email}</dd>
            </div>
            <div>
              <dt>Role</dt>
              <dd>{data.role}</dd>
            </div>
            {data.profile && (
              <div>
                <dt>Display name</dt>
                <dd>{data.profile.display_name}</dd>
              </div>
            )}
          </dl>
          <button type="button" onClick={logout}>
            Log out
          </button>
        </section>
      )}
    </main>
  );
}
