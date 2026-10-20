export class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request(path, options) {
  let response;
  try {
    response = await fetch(path, options);
  } catch (error) {
    if (error?.name === "AbortError") throw error;
    throw new ApiError(0, "Cannot reach the insult server. Is `insultgen serve` running?");
  }

  let data = null;
  try {
    data = await response.json();
  } catch {
    /* non-JSON body: fall through to the status text */
  }
  if (!response.ok) throw new ApiError(response.status, data?.error ?? response.statusText);
  return data;
}

export const getMeta = () => request("/api/meta");
export const getVocabulary = () => request("/api/vocabulary");

export function generate(params, signal) {
  return request("/api/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
    signal,
  });
}
