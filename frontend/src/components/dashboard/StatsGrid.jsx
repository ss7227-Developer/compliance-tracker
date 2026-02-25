import { Activity, AlertTriangle, Globe } from "lucide-react";
import StatCard from "./StatCard";

export default function StatsGrid({ stats }) {
  if (!stats) return null;

  const topCountry = stats.top_countries?.[0];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <StatCard
        title="Total Inspections"
        value={stats.total_inspections.toLocaleString()}
        icon={<Activity className="w-6 h-6" />}
        color="blue"
        subtitle="All-time records in database"
      />
      <StatCard
        title="OAI Rate"
        value={`${stats.oai_percentage}%`}
        icon={<AlertTriangle className="w-6 h-6" />}
        color="red"
        subtitle="Official Action Indicated cases"
      />
      <StatCard
        title="Top Country"
        value={topCountry ? topCountry.country || "N/A" : "—"}
        icon={<Globe className="w-6 h-6" />}
        color="green"
        subtitle={
          topCountry ? `${topCountry.count.toLocaleString()} inspections` : undefined
        }
      />
    </div>
  );
}
