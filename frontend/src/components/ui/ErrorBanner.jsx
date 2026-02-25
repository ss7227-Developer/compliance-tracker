import { AlertCircle } from "lucide-react";

export default function ErrorBanner({ message }) {
  return (
    <div className="flex items-center gap-3 bg-red-50 border border-red-200 rounded-lg p-4 m-6">
      <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
      <div>
        <p className="font-semibold text-red-700 text-sm">Failed to load data</p>
        <p className="text-red-600 text-xs mt-0.5">{message}</p>
      </div>
    </div>
  );
}
