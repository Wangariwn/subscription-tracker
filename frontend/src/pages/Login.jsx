import { useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function Login() {
  const { loginWithCredentials, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || "/";

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  if (isAuthenticated) {
    return <Navigate to={from} replace />;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await loginWithCredentials(username.trim(), password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(err.message || "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <p className="eyebrow">Renewly</p>
      <h1>Log in</h1>
      <p className="lede">
        Sign in to track subscriptions, renewals, and free trials. The API
        returns a JWT used on every protected request.
      </p>

      <form className="auth-form" onSubmit={handleSubmit}>
        <label>
          Username
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
            required
          />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
          />
        </label>

        {loading && <p className="status">Signing in…</p>}
        {error && <p className="error">{error}</p>}

        <button type="submit" disabled={loading}>
          Log in
        </button>
      </form>

      <p className="demo-hint muted">
        Demo: <code>demo</code> / <code>demo123</code> · Admin:{" "}
        <code>admin</code> / <code>admin123</code>
      </p>

      <p className="auth-switch">
        No account? <Link to="/register">Register</Link>
      </p>
    </main>
  );
}
