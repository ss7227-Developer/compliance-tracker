import { BarChart2, Table2, Settings, ShieldCheck } from "lucide-react";

const NAV_ITEMS = [
  { label: "Dashboard", icon: BarChart2, href: "#" },
  { label: "Inspections", icon: Table2, href: "#" },
  { label: "Settings", icon: Settings, href: "#" },
];

export default function Sidebar() {
  return (
    <aside className="w-64 bg-gray-900 text-gray-200 flex flex-col min-h-screen flex-shrink-0">
      {/* Logo / Brand */}
      <div className="px-6 py-5 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-6 h-6 text-blue-400" />
          <span className="text-lg font-bold text-white">ComplianceHQ</span>
        </div>
        <p className="text-xs text-gray-400 mt-1">Global Regulatory Dashboard</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {NAV_ITEMS.map(({ label, icon: Icon, href }) => (
          <a
            key={label}
            href={href}
            className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-700 transition-colors text-gray-300 hover:text-white"
          >
            <Icon className="w-5 h-5" />
            <span className="text-sm font-medium">{label}</span>
          </a>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-gray-700">
        <p className="text-xs text-gray-500">Data: OpenFDA Drug Enforcement</p>
        <p className="text-xs text-gray-600 mt-0.5">AWS S3 · SQS · RDS</p>
      </div>
    </aside>
  );
}
