import { createContext, useContext, useEffect, useState } from "react";

const AuthContext = createContext(null);
const API = "/api";

export function AuthProvider({ children }) {
  const [token, setToken] = useState(
    () => localStorage.getItem("token") || null
  );
  const [user, setUser] = useState(null);
  const [bootstrapping, setBootstrapping] = useState(Boolean(token));

  useEffect(() => {
    if (!token) {
      setUser(null);
      setBootstrapping(false);
      return;
    }

    let cancelled = false;
    setBootstrapping(true);

    fetch(`${API}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(async (response) => {
        if (!response.ok) {
          throw new Error("Session expired");
        }
        return response.json();
      })
      .then((data) => {
        if (!cancelled) setUser(data);
      })
      .catch(() => {
        if (!cancelled) {
          localStorage.removeItem("token");
          setToken(null);
          setUser(null);
        }
      })
      .finally(() => {
        if (!cancelled) setBootstrapping(false);
      });

    return () => {
      cancelled = true;
    };
  }, [token]);

  function login(accessToken, userData) {
    localStorage.setItem("token", accessToken);
    setToken(accessToken);
    setUser(userData ?? null);
  }

  function logout() {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
  }

  async function loginWithCredentials(username, password) {
    const response = await fetch(`${API}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(body.errors?.[0] || "Login failed");
    }
    login(body.access_token, body.user);
    return body;
  }

  async function registerUser(payload) {
    const response = await fetch(`${API}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(body.errors?.[0] || "Registration failed");
    }
    // Auto-login after register
    return loginWithCredentials(payload.username, payload.password);
  }

  const value = {
    token,
    user,
    bootstrapping,
    isAuthenticated: Boolean(token),
    login,
    logout,
    loginWithCredentials,
    registerUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuthContext() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuthContext must be used within AuthProvider");
  }
  return context;
}
