import Sidebar from "./components/layout/Sidebar";
import Dashboard from "./pages/Dashboard";

export default function App() {
  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />
      <Dashboard />
    </div>
  );
}
