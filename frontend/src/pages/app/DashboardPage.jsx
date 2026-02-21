import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import http from "../../api/http.js";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

function KpiCard({ title, value, hint }) {
  return (
    <div className="rounded-2xl bg-white p-4 shadow-sm border">
      <div className="text-xs text-slate-500">{title}</div>
      <div className="mt-1 text-2xl font-bold">{value}</div>
      {hint && <div className="mt-1 text-xs text-slate-500">{hint}</div>}
    </div>
  );
}

export default function DashboardPage() {
  const navigate = useNavigate();

  const [data, setData] = useState(null);
  const [err, setErr] = useState(null);
  const [subscription, setSubscription] = useState(null);

  const period = "last_7_days";

  // ================================
  // LOAD BI DATA
  // ================================
  useEffect(() => {
    (async () => {
      try {
        setErr(null);

        const [financeRes, subscriptionRes] = await Promise.all([
          http.get(`/bi/finance/?period=${period}`),
          http.get(`/billing/me/`), // endpoint à créer si pas encore fait
        ]);

        setData(financeRes.data);
        setSubscription(subscriptionRes.data);
      } catch (e) {
        setErr("Impossible de charger le dashboard.");
      }
    })();
  }, []);

  const chartRows = useMemo(() => {
    if (!data?.chart?.labels) return [];
    return data.chart.labels.map((label, i) => ({
      label,
      revenue: data.chart.revenue_series?.[i] ?? 0,
      margin: data.chart.margin_series?.[i] ?? 0,
    }));
  }, [data]);

  if (err) return <div className="text-red-600">{err}</div>;
  if (!data || !subscription) return <div>Chargement...</div>;

  const cur = data.current || {};
  const evo = data.evolution_percent || {};
  const trend = data.trend || {};
  const anomaly = data.anomaly || {};

  const isActive =
    subscription.subscription_status === "active" ||
    subscription.subscription_status === "trialing";

  return (
    <div className="space-y-6">
      {/* ================================
         SUBSCRIPTION HEADER
      ================================= */}
      <div className="rounded-2xl bg-white p-4 shadow-sm border flex justify-between items-center">
        <div>
          <div className="text-sm text-slate-500">Plan actuel</div>
          <div className="text-lg font-bold capitalize">
            {subscription.plan}
          </div>
          <div
            className={`text-sm mt-1 ${isActive ? "text-green-600" : "text-red-600"}`}
          >
            Status: {subscription.subscription_status}
          </div>
        </div>

        <div>
          {!isActive ? (
            <button
              onClick={() => navigate("/app/subscription")}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg"
            >
              Upgrade Plan
            </button>
          ) : (
            <button
              onClick={async () => {
                const res = await http.post("/billing/portal/");
                window.location.href = res.data.url;
              }}
              className="bg-slate-700 text-white px-4 py-2 rounded-lg"
            >
              Manage Billing
            </button>
          )}
        </div>
      </div>

      {/* ================================
         DASHBOARD HEADER
      ================================= */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold">Dashboard BI</h1>
          <div className="text-sm text-slate-600">
            Période: {data.period?.start} → {data.period?.end}
          </div>
        </div>

        {anomaly.is_anomaly && (
          <div className="rounded-xl bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-700">
            ⚠️ Anomalie: baisse revenue ~{anomaly.revenue_drop_percent}%
          </div>
        )}
      </div>

      {/* ================================
         KPI CARDS
      ================================= */}
      <div className="grid gap-4 md:grid-cols-4">
        <KpiCard
          title="Revenue"
          value={Number(cur.revenue || 0).toFixed(2)}
          hint={`Trend: ${trend.revenue} | Δ ${Number(evo.revenue || 0).toFixed(2)}%`}
        />
        <KpiCard title="COGS" value={Number(cur.cogs || 0).toFixed(2)} />
        <KpiCard
          title="Marge brute"
          value={Number(cur.gross_margin || 0).toFixed(2)}
          hint={`Trend: ${trend.gross_margin} | Δ ${Number(evo.gross_margin || 0).toFixed(2)}%`}
        />
        <KpiCard
          title="Valeur stock"
          value={Number(data.stock_value || 0).toFixed(2)}
        />
      </div>

      {/* ================================
         CHART
      ================================= */}
      <div className="rounded-2xl bg-white p-4 shadow-sm border">
        <div className="mb-3 flex items-center justify-between">
          <div className="font-semibold">Revenue & Marge</div>
          <div className="text-xs text-slate-500">Source: /api/bi/finance/</div>
        </div>

        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartRows}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="label" />
              <YAxis />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="revenue"
                strokeWidth={2}
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="margin"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
