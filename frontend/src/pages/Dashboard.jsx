import { useState } from "react";
import { RefreshCw } from "lucide-react";
import { useInspections } from "../hooks/useInspections";
import { triggerFetch } from "../api/client";
import StatsGrid from "../components/dashboard/StatsGrid";
import TrendChart from "../components/dashboard/TrendChart";
import ComplianceTable from "../components/dashboard/ComplianceTable";
import LoadingSpinner from "../components/ui/LoadingSpinner";
import ErrorBanner from "../components/ui/ErrorBanner";

export default function Dashboard() {
  const [filters, setFilters] = useState({});
  const [fetchTriggered, setFetchTriggered] = useState(null);

  const { stats, inspections, loading, error, page, setPage, totalCount } =
    useInspections(filters);

  const handleFilterChange = (newFilters) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
    setPage(1);
  };

  const handleTriggerFetch = async () => {
    try {
      const result = await triggerFetch(500);
      setFetchTriggered(result.task_id);
    } catch {
      // ignore — UI feedback is cosmetic here
    }
  };

  const PAGE_SIZE = 50;
  const totalPages = Math.ceil(totalCount / PAGE_SIZE);

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorBanner message={error} />;

  return (
    <main className="flex-1 p-8 bg-gray-50 overflow-auto">
      {/* Page header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Regulatory Compliance Overview
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            OpenFDA Drug Enforcement Records · Powered by AWS S3 + SQS + RDS
          </p>
        </div>
        <button
          onClick={handleTriggerFetch}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
          title="Enqueue a background FDA data fetch via Celery"
        >
          <RefreshCw className="w-4 h-4" />
          Fetch Latest Data
        </button>
      </div>

      {fetchTriggered && (
        <div className="mb-6 text-xs text-green-700 bg-green-50 border border-green-200 rounded-lg px-4 py-2">
          Background fetch enqueued (task ID: {fetchTriggered}). Check Celery
          worker logs for progress.
        </div>
      )}

      {/* Stats */}
      <StatsGrid stats={stats} />

      {/* 12-month trend chart */}
      <TrendChart data={stats?.monthly_trend ?? []} />

      {/* Searchable / sortable inspection table */}
      <ComplianceTable
        inspections={inspections}
        onFilterChange={handleFilterChange}
      />

      {/* Pagination */}
      <div className="flex items-center justify-center gap-4 mt-6">
        <button
          onClick={() => setPage((p) => Math.max(1, p - 1))}
          disabled={page === 1}
          className="px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm disabled:opacity-40 hover:bg-gray-50 transition-colors"
        >
          Previous
        </button>
        <span className="text-sm text-gray-500">
          Page {page} of {totalPages || 1} &nbsp;·&nbsp;{" "}
          {totalCount.toLocaleString()} total records
        </span>
        <button
          onClick={() => setPage((p) => p + 1)}
          disabled={page >= totalPages}
          className="px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm disabled:opacity-40 hover:bg-gray-50 transition-colors"
        >
          Next
        </button>
      </div>
    </main>
  );
}
