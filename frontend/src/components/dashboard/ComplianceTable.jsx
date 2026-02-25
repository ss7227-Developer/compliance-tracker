import { useState } from "react";
import { Search, ChevronUp, ChevronDown } from "lucide-react";

// Classification badge
const CLASS_STYLES = {
  OAI: "bg-red-100 text-red-700 border border-red-200",
  VAI: "bg-amber-100 text-amber-700 border border-amber-200",
  NAI: "bg-green-100 text-green-700 border border-green-200",
};

function ClassBadge({ value }) {
  return (
    <span
      className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
        CLASS_STYLES[value] ?? "bg-gray-100 text-gray-600"
      }`}
    >
      {value}
    </span>
  );
}

// Risk score badge
function RiskBadge({ score }) {
  if (score === null || score === undefined)
    return <span className="text-gray-300 text-xs">—</span>;
  if (score >= 0.7)
    return (
      <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-red-500 text-white">
        HIGH
      </span>
    );
  if (score >= 0.4)
    return (
      <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-amber-400 text-white">
        MED
      </span>
    );
  return (
    <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-green-500 text-white">
      LOW
    </span>
  );
}

const COLUMNS = [
  { key: "firm_name", label: "Firm Name" },
  { key: "inspection_date", label: "Date" },
  { key: "city", label: "City" },
  { key: "country", label: "Country" },
  { key: "classification", label: "Classification" },
  { key: "predicted_risk_score", label: "Risk" },
];

export default function ComplianceTable({ inspections, onFilterChange }) {
  const [search, setSearch] = useState("");
  const [sortField, setSortField] = useState("inspection_date");
  const [sortDir, setSortDir] = useState("desc");

  const handleSearch = (e) => {
    const val = e.target.value;
    setSearch(val);
    onFilterChange({ search: val });
  };

  const handleSort = (field) => {
    const newDir = sortField === field && sortDir === "asc" ? "desc" : "asc";
    setSortField(field);
    setSortDir(newDir);
    onFilterChange({ ordering: newDir === "desc" ? `-${field}` : field });
  };

  const SortIcon = ({ field }) => {
    if (sortField !== field)
      return <ChevronUp className="w-3 h-3 opacity-20 inline ml-1" />;
    return sortDir === "asc" ? (
      <ChevronUp className="w-3 h-3 inline ml-1 text-blue-500" />
    ) : (
      <ChevronDown className="w-3 h-3 inline ml-1 text-blue-500" />
    );
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div className="flex items-center justify-between mb-5">
        <h2 className="text-lg font-semibold text-gray-800">Inspection Records</h2>
        <div className="flex items-center gap-2 bg-gray-50 border border-gray-200 rounded-lg px-3 py-2">
          <Search className="w-4 h-4 text-gray-400" />
          <input
            type="text"
            className="bg-transparent text-sm outline-none w-52 placeholder-gray-400"
            placeholder="Search firm, city, country..."
            value={search}
            onChange={handleSearch}
          />
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-100">
              {COLUMNS.map(({ key, label }) => (
                <th
                  key={key}
                  onClick={() => handleSort(key)}
                  className="pb-3 pr-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide cursor-pointer hover:text-gray-800 select-none whitespace-nowrap"
                >
                  {label}
                  <SortIcon field={key} />
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {inspections.length === 0 ? (
              <tr>
                <td
                  colSpan={COLUMNS.length}
                  className="py-12 text-center text-gray-400 text-sm"
                >
                  No records found. Try adjusting your search or run data ingestion.
                </td>
              </tr>
            ) : (
              inspections.map((row) => (
                <tr
                  key={row.id}
                  className="border-b border-gray-50 hover:bg-gray-50 transition-colors"
                >
                  <td className="py-3 pr-4 font-medium text-gray-800 max-w-xs truncate">
                    {row.firm_name}
                  </td>
                  <td className="py-3 pr-4 text-gray-600 whitespace-nowrap">
                    {row.inspection_date}
                  </td>
                  <td className="py-3 pr-4 text-gray-600">{row.city || "—"}</td>
                  <td className="py-3 pr-4 text-gray-600">{row.country || "—"}</td>
                  <td className="py-3 pr-4">
                    <ClassBadge value={row.classification} />
                  </td>
                  <td className="py-3 pr-4">
                    <RiskBadge score={row.predicted_risk_score} />
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
