const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${path}`;

  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
    ...options,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(
      `Erro na requisição (${response.status}): ${text || response.statusText}`
    );
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

export const apiClient = {
  get:   <T>(path: string)           => request<T>(path),
  post:  <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "POST",  body: body ? JSON.stringify(body) : undefined }),
  put:   <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "PUT",   body: body ? JSON.stringify(body) : undefined }),
  patch: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "PATCH", body: body ? JSON.stringify(body) : undefined }),
};
