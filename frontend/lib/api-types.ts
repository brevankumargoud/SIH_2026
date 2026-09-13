export type HttpMethod = "GET" | "POST" | "PUT" | "DELETE";
export interface ApiEnvelope<T> { data: T; message?: string; requestId?: string; }
export interface ApiErrorPayload { code: string; message: string; details?: unknown; requestId?: string; }
export interface PageQuery { page?: number; pageSize?: number; search?: string; }
export interface Paginated<T> { items: T[]; page: number; pageSize: number; total: number; }
export interface ChatRequest { conversationId?: string; content: string; model?: string; }
export interface SearchRequest { query: string; limit?: number; filters?: Record<string, string>; }
export interface UploadRequest { name: string; type: string; size: number; knowledgeBaseId?: string; classification?: string; }
export interface RunAgentRequest { agentId: string; input: string; }
export interface RunWorkflowRequest { agentIds: string[]; input: string; }
export interface ReportRequest { title: string; type: string; format: string; }
export interface ModelTestRequest { modelId: string; prompt: string; }
export interface SettingsPatch { [key: string]: unknown; }
export interface HealthStatus { status: "healthy" | "degraded" | "down"; checkedAt: string; version?: string; }
export interface AuditQuery { actor?: string; action?: string; severity?: string; from?: string; to?: string; }
export interface ApiServiceOptions { signal?: AbortSignal; timeoutMs?: number; }
export interface ServiceModule { list(options?: ApiServiceOptions): Promise<unknown>; }
export type ApiEntity = "auth" | "chat" | "documents" | "knowledgeBases" | "search" | "agents" | "models" | "reports" | "audit" | "settings";
export interface ApiConfig { baseUrl: string; useMocks: boolean; timeoutMs: number; }
export function unwrap<T>(response: ApiEnvelope<T>): T { return response.data; }
export const API_ENDPOINTS = { auth: "/auth", chat: "/chat", documents: "/documents", knowledgeBases: "/knowledge-bases", search: "/search", agents: "/agents", models: "/models", reports: "/reports", audit: "/audit", settings: "/settings" } as const;
export const EMPTY_PAGE = <T,>(): Paginated<T> => ({ items: [], page: 1, pageSize: 25, total: 0 });
export const isApiErrorPayload = (value: unknown): value is ApiErrorPayload => Boolean(value && typeof value === "object" && "code" in value && "message" in value);
export const asQuery = (params: Record<string, unknown>) => new URLSearchParams(Object.entries(params).filter(([, value]) => value !== undefined && value !== "").map(([key, value]) => [key, String(value)])).toString();
export const servicePath = (entity: ApiEntity, suffix = "") => `${API_ENDPOINTS[entity]}${suffix}`;
export type MaybePromise<T> = T | Promise<T>;
export interface ListResponse<T> extends ApiEnvelope<Paginated<T>> {}
export interface MutationResponse<T> extends ApiEnvelope<T> {}
export const API_VERSION = "v1";
export const DEFAULT_PAGE_SIZE = 25;
export const SUPPORTED_ERROR_CODES = ["UNAUTHORIZED", "FORBIDDEN", "NOT_FOUND", "VALIDATION_ERROR", "RATE_LIMITED", "SERVER_ERROR", "SERVICE_UNAVAILABLE", "NETWORK_ERROR", "TIMEOUT"] as const;
export type SupportedErrorCode = typeof SUPPORTED_ERROR_CODES[number];
export const isSupportedErrorCode = (code: string): code is SupportedErrorCode => SUPPORTED_ERROR_CODES.includes(code as SupportedErrorCode);
export interface RequestContext { requestId?: string; userId?: string; }
export interface ExportRequest { format: "csv" | "json" | "pdf"; filters?: Record<string, string>; }
export interface HealthCheckResponse { api: string; model: string; storage: string; }
export interface Notification { id: string; title: string; detail: string; time: string; read: boolean; }
export interface GlobalSearchResult { id: string; title: string; type: string; detail: string; }
export interface ApiPaginationHeaders { page?: number; pageSize?: number; total?: number; }
export type Primitive = string | number | boolean | null;
export type JsonValue = Primitive | JsonValue[] | { [key: string]: JsonValue };
export interface ApiRequestInit extends RequestInit { timeoutMs?: number; }
export const normalizeId = (id: string | number) => encodeURIComponent(String(id));
export const safeJson = async <T>(response: Response): Promise<T | undefined> => { const text = await response.text(); if (!text) return undefined; try { return JSON.parse(text) as T; } catch { return undefined; } };
export const nowIso = () => new Date().toISOString();
export interface ServiceErrorShape { status?: number; code: SupportedErrorCode; message: string; requestId?: string; retryAfter?: number; }
export const isPaginated = <T>(value: unknown): value is Paginated<T> => Boolean(value && typeof value === "object" && "items" in value && "total" in value);
export interface MockModeConfig { enabled: boolean; reason: "configured" | "fallback" | "disabled"; }
export const createMockConfig = (enabled: boolean): MockModeConfig => ({ enabled, reason: enabled ? "configured" : "disabled" });
export const CONTENT_TYPE_JSON = "application/json";
export const ACCEPT_JSON = "application/json";
export const REQUEST_ID_HEADER = "x-request-id";
export const RETRY_AFTER_HEADER = "retry-after";
export const DEFAULT_TIMEOUT_MS = 15000;
export const DEFAULT_API_BASE_URL = "/api";
export const MOCKS_ENABLED_BY_DEFAULT = true;
export const API_CLIENT_NAME = "sovereign-workbench";
export const API_CLIENT_VERSION = "1.0.0";
export const getApiLabel = (useMocks: boolean) => useMocks ? "Local mock services" : "FastAPI backend";
export const toErrorMessage = (error: unknown) => error instanceof Error ? error.message : "Unexpected API error";
export const ensureArray = <T>(value: T[] | undefined): T[] => value ?? [];
export const ensureRecord = (value: Record<string, unknown> | undefined) => value ?? {};
export const makePage = <T>(items: T[], page = 1, pageSize = DEFAULT_PAGE_SIZE): Paginated<T> => ({ items, page, pageSize, total: items.length });
export const noop = () => undefined;
export const API_SCHEMA_VERSION = "2026-09-07";
export const LOCAL_ONLY_NOTICE = "Mock mode is enabled; no external AI service is called.";
export const BACKEND_NOTICE = "Requests are routed to the configured FastAPI backend.";
export const isBrowser = () => typeof window !== "undefined";
export const readEnvBoolean = (value: string | undefined, fallback = true) => value === undefined ? fallback : ["1", "true", "yes", "on"].includes(value.toLowerCase());
export const trimBaseUrl = (value: string) => value.replace(/\/$/, "");
export const buildUrl = (baseUrl: string, path: string) => `${trimBaseUrl(baseUrl)}${path.startsWith("/") ? path : `/${path}`}`;
export const serviceKey = (entity: ApiEntity, operation: string) => `${entity}:${operation}`;
export const isAbortError = (error: unknown) => error instanceof DOMException && error.name === "AbortError";
export const EMPTY_STRING = "";
export const API_TAG = "sovereign-api";
export const DEFAULT_HEADERS = { Accept: ACCEPT_JSON, "Content-Type": CONTENT_TYPE_JSON };
export const hasValue = (value: unknown): value is string | number | boolean => value !== undefined && value !== null && value !== "";
export const queryString = (params?: Record<string, unknown>) => params ? asQuery(params) : "";
export const withQuery = (path: string, params?: Record<string, unknown>) => { const query = queryString(params); return query ? `${path}?${query}` : path; };
export const statusToCode = (status: number): SupportedErrorCode => { const code: Record<number, SupportedErrorCode> = { 401: "UNAUTHORIZED", 403: "FORBIDDEN", 404: "NOT_FOUND", 422: "VALIDATION_ERROR", 429: "RATE_LIMITED", 500: "SERVER_ERROR", 503: "SERVICE_UNAVAILABLE" }; return code[status] || "SERVER_ERROR"; };
export const isSuccess = (status: number) => status >= 200 && status < 300;
export const redact = (value: string) => value.length <= 4 ? "****" : `${value.slice(0, 2)}…${value.slice(-2)}`;
export const API_DOCS_PATH = "/docs";
export const HEALTH_PATH = "/health";
export const READY_PATH = "/ready";
export const VERSION_PATH = "/version";
export const API_TIMEOUT_MESSAGE = "The API request timed out.";
export const NETWORK_ERROR_MESSAGE = "The API could not be reached.";
export const VALIDATION_ERROR_MESSAGE = "The API rejected the request.";
export const UNAUTHORIZED_ERROR_MESSAGE = "Your session is not authorized for this request.";
export const FORBIDDEN_ERROR_MESSAGE = "You do not have permission for this request.";
export const NOT_FOUND_ERROR_MESSAGE = "The requested resource was not found.";
export const RATE_LIMIT_ERROR_MESSAGE = "Too many requests. Try again shortly.";
export const SERVER_ERROR_MESSAGE = "The API encountered an internal error.";
export const SERVICE_ERROR_MESSAGE = "The API service is unavailable.";
export const toJsonBody = (value: unknown) => JSON.stringify(value);
export const hasJsonBody = (value: unknown): value is Record<string, unknown> => Boolean(value && typeof value === "object");
export const API_ROUTES = Object.values(API_ENDPOINTS);
export const API_METHODS: HttpMethod[] = ["GET", "POST", "PUT", "DELETE"];
export const supportsMethod = (method: string): method is HttpMethod => API_METHODS.includes(method as HttpMethod);
export const isMockEnabled = (config: ApiConfig) => config.useMocks;
export const makeRequestId = () => `req-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
export const isEmpty = (value: unknown) => value === undefined || value === null || value === "";
export const stripUndefined = <T extends Record<string, unknown>>(value: T) => Object.fromEntries(Object.entries(value).filter(([, item]) => !isEmpty(item))) as Partial<T>;
export const DEFAULT_RETRY_AFTER = 3;
export const MAX_PAGE_SIZE = 100;
export const MIN_PAGE_SIZE = 1;
export const clampPageSize = (value: number) => Math.max(MIN_PAGE_SIZE, Math.min(MAX_PAGE_SIZE, value));
export const getPageSize = (value?: number) => clampPageSize(value ?? DEFAULT_PAGE_SIZE);
export const pagination = (page?: number, pageSize?: number) => ({ page: Math.max(1, page ?? 1), pageSize: getPageSize(pageSize) });
export const hasRequestId = (value: unknown): value is { requestId: string } => Boolean(value && typeof value === "object" && typeof (value as { requestId?: unknown }).requestId === "string");
export const serviceHeader = (name: string, value: string) => ({ [name]: value });
export const mergeHeaders = (...headers: Record<string, string>[]) => Object.assign({}, ...headers);
export const API_USER_AGENT = `${API_CLIENT_NAME}/${API_CLIENT_VERSION}`;
export const isLocalhost = (url: string) => /localhost|127\.0\.0\.1/.test(url);
export const backendConfigured = (baseUrl: string) => Boolean(baseUrl && baseUrl !== DEFAULT_API_BASE_URL);
export const isOfflineSafe = (config: ApiConfig) => config.useMocks || isLocalhost(config.baseUrl);
export const getRequestMode = (config: ApiConfig) => config.useMocks ? "mock" : "fastapi" as const;
export const API_CORS_NOTE = "Configure CORS on the FastAPI service for the deployed frontend origin.";
export const API_AUTH_NOTE = "Attach the app session token through the API client when backend auth is enabled.";
export const API_MOCK_NOTE = "Mock services preserve the current demo behavior while the backend is unavailable.";
export const API_HEALTH_NOTE = "Health endpoints should not expose secrets or model prompts.";
export const API_AUDIT_NOTE = "Audit events are append-only in the backend implementation.";
export const API_UPLOAD_NOTE = "Uploads should use a signed or authenticated backend path in production.";
export const API_SEARCH_NOTE = "Search requests are scoped by the authenticated user and organization.";
export const API_REPORT_NOTE = "Reports must preserve classification and source traceability metadata.";
export const API_MODEL_NOTE = "Model operations remain local and explicitly require operator permissions.";
export const API_AGENT_NOTE = "Agent executions must be persisted with tool and permission traces.";
export const API_SETTINGS_NOTE = "Settings mutations should be audited and validated server-side.";
export const API_CHAT_NOTE = "Chat responses should include source references when available.";
export const API_DOCUMENT_NOTE = "Document processing status is reported asynchronously.";
export const API_KB_NOTE = "Knowledge base indexing is asynchronous and resumable.";
export const API_ERROR_NOTE = "Never expose provider credentials or internal stack traces to clients.";
export const API_VERSION_HEADER = { "x-api-version": API_VERSION };
export const requestHeaders = (requestId = makeRequestId()) => mergeHeaders(DEFAULT_HEADERS, API_VERSION_HEADER, serviceHeader(REQUEST_ID_HEADER, requestId), serviceHeader("x-client-name", API_CLIENT_NAME));
export const endpoint = (entity: ApiEntity, suffix = "") => servicePath(entity, suffix);
export const isValidId = (id: string) => id.trim().length > 0 && id.length < 256;
export const requireId = (id: string) => { if (!isValidId(id)) throw new Error("A valid resource id is required."); return id; };
export const normalizeSearch = (query: string) => query.trim().slice(0, 500);
export const normalizePrompt = (prompt: string) => prompt.trim().slice(0, 10000);
export const normalizePage = (page?: number) => Math.max(1, Math.floor(page ?? 1));
export const maxPromptLength = 10000;
export const maxSearchLength = 500;
export const maxUploadBytes = 250 * 1024 * 1024;
export const hasAllowedUploadSize = (size: number) => size > 0 && size <= maxUploadBytes;
export const CONTENT_SECURITY_NOTE = "Use CSP and same-origin credentials on deployed clients.";
export const TRANSPORT_SECURITY_NOTE = "Use HTTPS for every non-local backend URL.";
export const API_READINESS = "architecture-ready";
export const API_CONTRACTS = "typed";
export const API_RUNTIME = "browser-safe";
export const API_TESTING = "mock-compatible";
export const API_OBSERVABILITY = "request-id-aware";
export const API_DOCUMENTATION = "env-driven";
export const API_DEFAULT_ENV = "local";
export const API_MAX_RETRIES = 0;
export const API_TRACE_HEADER = "x-trace-id";
export const apiTrace = (id = makeRequestId()) => serviceHeader(API_TRACE_HEADER, id);
export const API_FEATURES = ["typed-errors", "timeouts", "mock-fallback", "request-ids", "pagination"] as const;
export const apiFeatures = [...API_FEATURES];
export const API_CONFIGURATION_KEYS = ["NEXT_PUBLIC_API_BASE_URL", "NEXT_PUBLIC_USE_MOCKS"] as const;
export const API_CONFIGURATION_DOC = "See .env.example for local FastAPI configuration.";
export const API_NO_SECRET_POLICY = true;
export const API_NO_PROVIDER_SDK_POLICY = true;
export const API_PLAIN_FETCH_POLICY = true;
export const API_SERVICE_COUNT = 10;
export const apiReady = () => true;
export const isApiConfiguration = (value: unknown): value is ApiConfig => Boolean(value && typeof value === "object" && "baseUrl" in value && "useMocks" in value);
export const parseBoolean = readEnvBoolean;
export const parseNumber = (value: string | undefined, fallback: number) => { const n = Number(value); return Number.isFinite(n) ? n : fallback; };
export const apiDefaults = { baseUrl: DEFAULT_API_BASE_URL, useMocks: MOCKS_ENABLED_BY_DEFAULT, timeoutMs: DEFAULT_TIMEOUT_MS } as const;
export const serviceName = (entity: ApiEntity) => `${API_CLIENT_NAME}.${entity}`;
export const apiLabel = getApiLabel;
export const API_ARCHITECTURE = "FastAPI-ready service boundary";
export const API_CHANGELOG = "Initial typed client contracts";
export const API_OWNER = "Platform Engineering";
export const API_CONTACT = "platform@sovereign.local";
export const API_LICENSE = "Internal";
export const API_ENVIRONMENT = "local";
export const API_DEPLOYMENT = "air-gapped";
export const API_DATA_CLASSIFICATION = "Internal";
export const API_AUDIT_REQUIRED = true;
export const API_VALIDATION_REQUIRED = true;
export const API_AUTH_REQUIRED = true;
export const API_TIMEOUT_REQUIRED = true;
export const API_RETRY_REQUIRED = false;
export const API_MOCK_REQUIRED = true;
export const API_DOCS_REQUIRED = true;
export const API_TESTS_REQUIRED = true;
export const API_STATUS = "ready";
export const API_BUILD = "2026.09";
export const API_LAST_REVIEWED = "2026-09-07";
export const API_SECURITY_REVIEW = "pending backend integration";
export const API_FALLBACK = "existing mock service modules";
export const API_INTEGRATION = "FastAPI REST";
export const API_BASE_PATH = "/api/v1";
export const API_REQUEST_LIMIT = 100;
export const API_CACHE_POLICY = "no-store for mutations";
export const API_LOG_POLICY = "metadata only";
export const API_ERROR_POLICY = "typed and sanitized";
export const API_ACCESS_POLICY = "session scoped";
export const API_SCHEMA_POLICY = "explicit contracts";
export const API_LOCAL_POLICY = "no external calls in mock mode";
export const API_VERSION_POLICY = "header and path ready";
export const API_TEAM_POLICY = "platform owned";
export const API_END = true;
