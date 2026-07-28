import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function Register() {
  const { registerUser, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    display_name: "",
  });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  function updateField(key) {
    return (event) => {
      setError(null);
      setForm((prev) => ({ ...prev, [key]: event.target.value }));
    };
  }

  function clientValidate() {
    if (form.username.trim().length < 3) {
      return "Username must be at least 3 characters.";
    }
    if (!form.email.includes("@")) {
      return "Enter a valid email address.";
    }
    if (form.password.length < 6) {
      return "Password must be at least 6 characters.";
    }
    return null;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    const localError = clientValidate();
    if (localError) {
      setError(localError);
      return;
    }

    setError(null);
    setLoading(true);
    try {
      await registerUser({
        username: form.username.trim(),
        email: form.email.trim(),
        password: form.password,
        display_name: form.display_name.trim() || form.username.trim(),
      });
      navigate("/", { replace: true });
    } catch (err) {
      setError(err.message || "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <h1>Register</h1>
      <p className="lede">Create a user account and profile, then receive a JWT.</p>

      <form className="auth-form" onSubmit={handleSubmit} noValidate>
        <label>
          Username
          <input
            value={form.username}
            onChange={updateField("username")}
            autoComplete="username"
            required
            minLength={3}
          />
          <span className="field-hint">At least 3 characters</span>
        </label>
        <label>
          Email
          <input
            type="email"
            value={form.email}
            onChange={updateField("email")}
            autoComplete="email"
            required
          />
        </label>
        <label>
          Display name
          <input
            value={form.display_name}
            onChange={updateField("display_name")}
            autoComplete="nickname"
          />
        </label>
        <label>
          Password
          <input
            type="password"
            value={form.password}
            onChange={updateField("password")}
            autoComplete="new-password"
            required
            minLength={6}
          />
          <span className="field-hint">At least 6 characters</span>
        </label>

        {loading && <p className="status">Creating account…</p>}
        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}

        <button type="submit" disabled={loading}>
          Register
        </button>
      </form>

      <p className="auth-switch">
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </main>
  );
}
