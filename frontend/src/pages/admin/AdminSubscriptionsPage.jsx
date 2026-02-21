import { useEffect, useState } from "react";
import http from "../../api/http";

function Badge({ status }) {
  const colors = {
    active: "bg-green-100 text-green-700",
    trialing: "bg-blue-100 text-blue-700",
    past_due: "bg-yellow-100 text-yellow-700",
    canceled: "bg-red-100 text-red-700",
  };

  return (
    <span
      className={`px-2 py-1 rounded-full text-xs ${colors[status] || "bg-gray-100"}`}
    >
      {status}
    </span>
  );
}

export default function AdminSubscriptionsPage() {
  const [data, setData] = useState(null);

  useEffect(() => {
    http
      .get("/admin/subscriptions/")
      .then((res) => setData(res.data))
      .catch(() => alert("Erreur chargement subscriptions"));
  }, []);

  if (!data) return <div>Chargement...</div>;

  const { stats, subscriptions } = data;

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold">Subscriptions</h1>

      {/* KPI CARDS */}
      <div className="grid grid-cols-5 gap-4">
        <Card title="Total" value={stats.total} />
        <Card title="Active" value={stats.active} />
        <Card title="Trialing" value={stats.trialing} />
        <Card title="Past Due" value={stats.past_due} />
        <Card title="Canceled" value={stats.canceled} />
      </div>

      <div className="rounded-xl bg-white p-4 shadow">
        <div className="mb-4 font-semibold">
          Monthly Recurring Revenue (MRR): {stats.mrr} FCFA
        </div>

        <table className="w-full text-sm">
          <thead>
            <tr className="text-left border-b">
              <th>Pharmacy</th>
              <th>Plan</th>
              <th>Status</th>
              <th>Amount</th>
              <th>Renewal</th>
              <th>Stripe ID</th>
            </tr>
          </thead>

          <tbody>
            {subscriptions.map((sub) => (
              <tr key={sub.id} className="border-b hover:bg-gray-50">
                <td>{sub.name}</td>
                <td>{sub.plan}</td>
                <td>
                  <Badge status={sub.status} />
                </td>
                <td>{sub.monthly_amount} FCFA</td>
                <td>
                  {sub.current_period_end
                    ? new Date(sub.current_period_end).toLocaleDateString()
                    : "-"}
                </td>
                <td className="text-xs text-gray-500">
                  {sub.stripe_customer_id || "-"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function Card({ title, value }) {
  return (
    <div className="bg-white p-4 rounded-xl shadow text-center">
      <div className="text-xs text-gray-500">{title}</div>
      <div className="text-2xl font-bold">{value}</div>
    </div>
  );
}
