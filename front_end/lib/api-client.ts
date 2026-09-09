import {
  apiDefaults,
  buildUrl,
  DEFAULT_HEADERS,
  DEFAULT_TIMEOUT_MS,
  isSuccess,
  makeRequestId,
  readEnvBoolean,
  RETRY_AFTER_HEADER,
  statusToCode,
  trimBaseUrl,
  type ApiConfig,
  type ApiEnvelope,
  type ApiRequestInit,
  type SupportedErrorCode,
} from "./api-types";

export class ApiClientError extends Error {
  readonly code: SupportedErrorCode;
  readonly status?: number;
  readonly requestId?: string;
  readonly retryAfter?: number;

  constructor(
    message: string,
    code: SupportedErrorCode,
    status?: number,
    requestId?: string,
    retryAfter?: number
  ) {
    super(message);
    this.name = "ApiClientError";
    this.code = code;
    this.status = status;
    this.requestId = requestId;
    this.retryAfter = retryAfter;
  }
}

const config: ApiConfig = {
  baseUrl: trimBaseUrl(process.env.NEXT_PUBLIC_API_BASE_URL || apiDefaults.baseUrl),
  useMocks: readEnvBoolean(process.env.NEXT_PUBLIC_USE_MOCKS, false),
  timeoutMs: Number(process.env.NEXT_PUBLIC_API_TIMEOUT_MS) || DEFAULT_TIMEOUT_MS,
};

export const apiConfig = config;

const errorMessages: Record<SupportedErrorCode, string> = {
  UNAUTHORIZED: "Your session is not authorized for this request.",
  FORBIDDEN: "You do not have permission for this request.",
  NOT_FOUND: "The requested resource was not found.",
  VALIDATION_ERROR: "The API rejected the request parameters.",
  RATE_LIMITED: "Too many requests. Try again shortly.",
  SERVER_ERROR: "The sovereign backend encountered an internal error.",
  SERVICE_UNAVAILABLE: "The local backend service is currently unavailable.",
  NETWORK_ERROR: "Unable to connect to the sovereign backend at " + config.baseUrl,
  TIMEOUT: "The backend request timed out.",
};

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
  options: ApiRequestInit = {}
): Promise<ApiEnvelope<T>> {
  if (config.useMocks) {
    throw new ApiClientError("Mock mode is enabled", "NETWORK_ERROR");
  }

  const controller = new AbortController();
  const timeout = setTimeout(
    () => controller.abort(),
    options.timeoutMs ?? config.timeoutMs
  );
  const requestId = makeRequestId();

  const isFormData = typeof FormData !== "undefined" && body instanceof FormData;
  const url = path.startsWith("http://") || path.startsWith("https://")
    ? path
    : buildUrl(config.baseUrl, path);

  const headers: Record<string, string> = {
    Accept: "application/json",
    "x-request-id": requestId,
    ...(options.headers as Record<string, string> | undefined),
  };

  if (!isFormData) {
    headers["Content-Type"] = "application/json";
  }

  try {
    const response = await fetch(url, {
      ...options,
      method,
      headers,
      body: isFormData ? (body as FormData) : body === undefined ? undefined : JSON.stringify(body),
      signal: options.signal ?? controller.signal,
    });

    const payload = (await response.json().catch(() => undefined)) as any;

    if (!isSuccess(response.status)) {
      const code = (payload?.code as SupportedErrorCode) || statusToCode(response.status);
      let message = errorMessages[code] || "API request failed";

      if (payload && typeof payload === "object") {
        if ("error" in payload && typeof payload.error === "object" && payload.error !== null) {
          message = payload.error.message || message;
        } else if ("detail" in payload) {
          message = typeof payload.detail === "string" ? payload.detail : JSON.stringify(payload.detail);
        } else if ("message" in payload && typeof payload.message === "string") {
          message = payload.message;
        }
      }

      throw new ApiClientError(
        message,
        code,
        response.status,
        response.headers.get("x-request-id") || requestId,
        Number(response.headers.get(RETRY_AFTER_HEADER)) || undefined
      );
    }

    if (payload && typeof payload === "object" && "data" in payload && !("results" in payload) && !("conversation_id" in payload)) {
      return payload as ApiEnvelope<T>;
    }

    return { data: payload as T, requestId, message: "OK" };
  } catch (error) {
    if (error instanceof ApiClientError) throw error;
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiClientError(errorMessages.TIMEOUT, "TIMEOUT", undefined, requestId);
    }
    throw new ApiClientError(
      error instanceof Error ? error.message : errorMessages.NETWORK_ERROR,
      "NETWORK_ERROR",
      undefined,
      requestId
    );
  } finally {
    clearTimeout(timeout);
  }
}

export const apiClient = {
  config,
  get: <T>(path: string, options?: ApiRequestInit) => request<T>("GET", path, undefined, options),
  post: <T>(path: string, body?: unknown, options?: ApiRequestInit) => request<T>("POST", path, body, options),
  put: <T>(path: string, body?: unknown, options?: ApiRequestInit) => request<T>("PUT", path, body, options),
  patch: <T>(path: string, body?: unknown, options?: ApiRequestInit) => request<T>("PATCH", path, body, options),
  delete: <T>(path: string, options?: ApiRequestInit) => request<T>("DELETE", path, undefined, options),
  upload: <T>(path: string, formData: FormData, options?: ApiRequestInit) => request<T>("POST", path, formData, options),
  isMockMode: () => config.useMocks,
  baseUrl: () => config.baseUrl,
};

export const createApiClient = (overrides: Partial<ApiConfig> = {}) => ({
  ...apiClient,
  config: { ...config, ...overrides },
});

export const isApiClientError = (error: unknown): error is ApiClientError =>
  error instanceof ApiClientError;

export const getApiErrorMessage = (error: unknown) =>
  isApiClientError(error) ? error.message : error instanceof Error ? error.message : "Unexpected API error";
