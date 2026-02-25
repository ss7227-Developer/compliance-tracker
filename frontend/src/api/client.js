/**
 * Axios API client.
 *
 * In Docker:  VITE_API_BASE_URL is empty → Vite proxies /api/* to http://api:8000
 * Locally:    Set VITE_API_BASE_URL=http://localhost:8000 in your shell to bypass
 *             the proxy when running Vite outside of Docker.
 */
import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

const apiClient = axios.create({
  baseURL: `${BASE_URL}/api`,
  headers: { "Content-Type": "application/json" },
  timeout: 15000,
});

export const fetchStats = () =>
  apiClient.get("/stats/").then((r) => r.data);

export const fetchInspections = (params = {}) =>
  apiClient.get("/inspections/", { params }).then((r) => r.data);

export const fetchInspectionDetail = (id) =>
  apiClient.get(`/inspections/${id}/`).then((r) => r.data);

export const triggerFetch = (limit = 500) =>
  apiClient.post("/fetch/", { limit }).then((r) => r.data);
