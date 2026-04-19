import "server-only";

const API_BASE_URL =
  process.env.API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "http://127.0.0.1:8000/api";

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
  let response: Response;
  try {
    response = await fetch(url, {
      cache: "no-store"
    });
  } catch (cause) {
    // Next.js throws this when a route must be dynamic; do not wrap as ApiError or builds break.
    if (cause instanceof Error && cause.message.includes("Dynamic server usage")) {
      throw cause;
    }
    const message = cause instanceof Error ? cause.message : String(cause);
    throw new ApiError(`API unreachable (${url}): ${message}`, 503, url);
  }

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

  const text = await response.text();
  if (!text) {
    throw new ApiError(`Empty response from API for ${path}`, response.status, url);
  }
  try {
    return JSON.parse(text) as T;
  } catch {
    throw new ApiError(`Invalid JSON from API for ${path}`, response.status, url);
  }
}
