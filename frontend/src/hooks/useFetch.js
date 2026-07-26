import { useCallback, useEffect, useState } from "react";
import { useAuth } from "./useAuth";

export function useFetch(url) {
  const { token } = useAuth();
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(Boolean(url));
  const [reloadToken, setReloadToken] = useState(0);

  const refetch = useCallback(() => {
    setReloadToken((value) => value + 1);
  }, []);

  useEffect(() => {
    if (!url) {
      setLoading(false);
      return;
    }

    const controller = new AbortController();
    setLoading(true);
    setError(null);

    const headers = { "Content-Type": "application/json" };
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    fetch(url, {
      headers,
      signal: controller.signal,
    })
      .then(async (response) => {
        if (!response.ok) {
          const body = await response.json().catch(() => ({}));
          throw new Error(body.errors?.[0] || response.statusText);
        }
        if (response.status === 204) return null;
        return response.json();
      })
      .then(setData)
      .catch((err) => {
        if (err.name !== "AbortError") {
          setError(err);
          setData(null);
        }
      })
      .finally(() => setLoading(false));

    return () => controller.abort();
  }, [url, token, reloadToken]);

  return { data, error, loading, refetch };
}
