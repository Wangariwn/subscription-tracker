import { createContext, useCallback, useContext, useEffect, useState } from "react";

const AuthContext = createContext(null);
export const API_BASE = import.meta.env.VITE_API_URL || "/api";

let refreshPromise = null;

async function refreshAccessToken(refreshToken) {
  const response = await fetch(`${API_BASE}/auth/refresh`, {
    method: "POST",
    headers: { Authorization: `Bearer ${refreshToken}` },
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(body.errors?.[0] || "Session expired");
  }
  return body.access_token;
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(
    () => localStorage.getItem("token") || null
  );
  const [refreshToken, setRefreshToken] = useState(
    () => localStorage.getItem("refresh_token") || null
  );
  const [user, setUser] = useState(null);
  const [bootstrapping, setBootstrapping] = useState(Boolean(token));

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    localStorage.removeItem("refresh_token");
    setToken(null);
    setRefreshToken(null);
    setUser(null);
  }, []);

  const login = useCallback((accessToken, userData, nextRefreshToken) => {
    localStorage.setItem("token", accessToken);
    setToken(accessToken);
    if (nextRefreshToken) {
      localStorage.setItem("refresh_token", nextRefreshToken);
      setRefreshToken(nextRefreshToken);
    }
    setUser(userData ?? null);
  }, []);

  const ensureFreshToken = useCallback(async () => {
    if (!refreshToken) {
      throw new Error("Session expired");
    }
    if (!refreshPromise) {
      refreshPromise = refreshAccessToken(refreshToken)
        .then((accessToken) => {
          localStorage.setItem("token", accessToken);
          setToken(accessToken);
          return accessToken;
        })
        .catch((err) => {
          logout();
          throw err;
        })
        .finally(() => {
          refreshPromise = null;
        });
    }
    return refreshPromise;
  }, [refreshToken, logout]);

  const authFetch = useCallback(
    async (path, options = {}, retry = true) => {
      const headers = {
        ...(options.headers || {}),
      };
      if (!(options.body instanceof FormData)) {
        headers["Content-Type"] = headers["Content-Type"] || "application/json";
      }
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      }

      const response = await fetch(`${API_BASE}${path}`, {
        ...options,
        headers,
      });

      if (response.status === 401 && retry && refreshToken) {
        const nextToken = await ensureFreshToken();
        const retryHeaders = {
          ...headers,
          Authorization: `Bearer ${nextToken}`,
        };
        return fetch(`${API_BASE}${path}`, {
          ...options,
          headers: retryHeaders,
        });
      }

      return response;
    },
    [token, refreshToken, ensureFreshToken]
  );

  useEffect(() => {
    if (!token) {
      setUser(null);
      setBootstrapping(false);
      return;
    }

    let cancelled = false;
    setBootstrapping(true);

    authFetch("/auth/me", {}, true)
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
        if (!cancelled) logout();
      })
      .finally(() => {
        if (!cancelled) setBootstrapping(false);
      });

    return () => {
      cancelled = true;
    };
  }, [token]); // eslint-disable-line react-hooks/exhaustive-deps

  async function loginWithCredentials(username, password) {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(body.errors?.[0] || "Login failed");
    }
    login(body.access_token, body.user, body.refresh_token);
    return body;
  }

  async function registerUser(payload) {
    const response = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(body.errors?.[0] || "Registration failed");
    }
    return loginWithCredentials(payload.username, payload.password);
  }

  const value = {
    token,
    refreshToken,
    user,
    setUser,
    bootstrapping,
    isAuthenticated: Boolean(token),
    login,
    logout,
    loginWithCredentials,
    registerUser,
    authFetch,
    ensureFreshToken,
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
