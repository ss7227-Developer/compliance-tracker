import { useState, useEffect, useCallback } from "react";
import { fetchStats, fetchInspections } from "../api/client";

/**
 * Custom hook: fetches stats + paginated inspections from the Django API.
 *
 * Both requests fire in parallel via Promise.all to halve perceived load time.
 * Re-fetches automatically whenever `filters` or `page` changes.
 *
 * @param {object} filters  - Query params forwarded to /api/inspections/
 * @returns {{ stats, inspections, loading, error, page, setPage, totalCount }}
 */
export function useInspections(filters = {}) {
  const [stats, setStats] = useState(null);
  const [inspections, setInspections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsData, inspData] = await Promise.all([
        fetchStats(),
        fetchInspections({ ...filters, page }),
      ]);
      setStats(statsData);
      setInspections(inspData.results ?? []);
      setTotalCount(inspData.count ?? 0);
    } catch (err) {
      setError(err.message ?? "Failed to load data from the API");
    } finally {
      setLoading(false);
    }
  }, [JSON.stringify(filters), page]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    load();
  }, [load]);

  return { stats, inspections, loading, error, page, setPage, totalCount };
}
