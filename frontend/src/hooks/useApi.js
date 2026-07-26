import { useAuth } from "./useAuth";

const API = "/api";

export async function apiRequest(path, { method = "GET", token, body } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (response.status === 204) {
    return null;
  }

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = Array.isArray(data.errors)
      ? data.errors[0]
      : data.message || response.statusText;
    throw new Error(typeof message === "string" ? message : "Request failed");
  }
  return data;
}

export function useApi() {
  const { token } = useAuth();

  return {
    get: (path) => apiRequest(path, { token }),
    post: (path, body) => apiRequest(path, { method: "POST", token, body }),
    patch: (path, body) => apiRequest(path, { method: "PATCH", token, body }),
    del: (path) => apiRequest(path, { method: "DELETE", token }),
  };
}
