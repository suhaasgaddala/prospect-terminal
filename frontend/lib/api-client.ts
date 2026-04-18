import "server-only";

const API_BASE_URL =
  process.env.API_BASE_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api";

export class ApiError extends Error {
  status: number;
  path: string;

  constructor(message: string, status: number, path: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.path = path;
  }
}

export async function apiFetch<T>(path: string): Promise<T> {
  const url = `${API_BASE_URL}${path}`;
  const response = await fetch(url, {
    cache: "no-store"
  });

  if (!response.ok) {
    const responseText = await response.text();
    let detail = responseText.trim();
    try {
      const parsed = JSON.parse(responseText) as { detail?: unknown };
      if (typeof parsed.detail === "string") {
        detail = parsed.detail;
      }
    } catch {
      // response body is plain text; keep the current detail value
    }

    const detailSnippet = detail ? ` - ${detail.slice(0, 180)}` : "";
    throw new ApiError(
      `API request failed (${response.status}) for ${path}${detailSnippet}`,
      response.status,
      url
    );
  }

  return response.json() as Promise<T>;
}
