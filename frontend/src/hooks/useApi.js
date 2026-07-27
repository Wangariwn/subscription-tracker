import { useAuth } from "./useAuth";

export async function parseApiResponse(response) {
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
  const { authFetch } = useAuth();

  return {
    get: async (path) => parseApiResponse(await authFetch(path)),
    post: async (path, body) =>
      parseApiResponse(
        await authFetch(path, {
          method: "POST",
          body: JSON.stringify(body),
        })
      ),
    patch: async (path, body) =>
      parseApiResponse(
        await authFetch(path, {
          method: "PATCH",
          body: JSON.stringify(body),
        })
      ),
    del: async (path) =>
      parseApiResponse(await authFetch(path, { method: "DELETE" })),
    upload: async (path, formData) =>
      parseApiResponse(
        await authFetch(path, {
          method: "POST",
          body: formData,
        })
      ),
  };
}
