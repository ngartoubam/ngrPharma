import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:8000/api";

export default function AdminDashboardPage() {
  const [stats, setStats] = useState({
    total_pharmacies: 0,
    active_subscriptions: 0,
    monthly_revenue: 0,
    new_pharmacies: 0,
  });

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const token = localStorage.getItem("access");

        if (!token) {
          console.error("No access token found");
          setLoading(false);
          return;
        }

        const response = await fetch(`${API_URL}/admin/overview/`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.status === 401) {
          console.error("Unauthorized - token expired");
          setLoading(false);
          return;
        }

        const data = await response.json();
        console.log("Dashboard API response:", data);

        if (response.ok) {
          setStats({
            // 🔹 Compatible avec les deux formats backend
            total_pharmacies:
              data.total_pharmacies ?? data.pharmacies?.total ?? 0,

            active_subscriptions:
              data.active_subscriptions ?? data.subscriptions?.active ?? 0,

            monthly_revenue:
              data.monthly_revenue ?? data.revenue?.current_month ?? 0,

            new_pharmacies:
              data.new_pharmacies ?? data.pharmacies?.new_last_30_days ?? 0,
          });
        } else {
          console.error("Error fetching stats", data);
        }
      } catch (error) {
        console.error("Server error", error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const formatMoney = (value) => {
    const amount = Number(value || 0);
    return `${amount.toLocaleString()} FCFA`;
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Global Overview</h2>

      <div className="grid grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-xl shadow">
          <p className="text-gray-500 text-sm">Total Pharmacies</p>
          <h3 className="text-3xl font-bold mt-2">
            {loading ? "..." : stats.total_pharmacies}
          </h3>
        </div>

        <div className="bg-white p-6 rounded-xl shadow">
          <p className="text-gray-500 text-sm">Active Subscriptions</p>
          <h3 className="text-3xl font-bold mt-2">
            {loading ? "..." : stats.active_subscriptions}
          </h3>
        </div>

        <div className="bg-white p-6 rounded-xl shadow">
          <p className="text-gray-500 text-sm">Monthly Revenue</p>
          <h3 className="text-3xl font-bold mt-2">
            {loading ? "..." : formatMoney(stats.monthly_revenue)}
          </h3>
        </div>

        <div className="bg-white p-6 rounded-xl shadow">
          <p className="text-gray-500 text-sm">New Pharmacies</p>
          <h3 className="text-3xl font-bold mt-2">
            {loading ? "..." : stats.new_pharmacies}
          </h3>
        </div>
      </div>
    </div>
  );
}
