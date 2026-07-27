import { useCallback, useEffect, useState } from "react";
import { useAuth } from "./useAuth";
import { parseApiResponse } from "./useApi";

export function useFetch(url) {
  const { authFetch, token } = useAuth();
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

    // url may be absolute (/api/...) from pages; strip /api prefix for authFetch
    const path = url.startsWith("/api") ? url.slice(4) : url;

    authFetch(path, { signal: controller.signal })
      .then(parseApiResponse)
      .then(setData)
      .catch((err) => {
        if (err.name !== "AbortError") {
          setError(err);
          setData(null);
        }
      })
      .finally(() => setLoading(false));

    return () => controller.abort();
  }, [url, token, reloadToken, authFetch]);

  return { data, error, loading, refetch };
}
