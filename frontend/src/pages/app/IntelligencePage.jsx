import { useEffect, useState } from "react";
import http from "../../api/http.js";

function Pill({ label }) {
  const map = {
    excellent: "bg-emerald-50 text-emerald-700 border-emerald-200",
    good: "bg-sky-50 text-sky-700 border-sky-200",
    warning: "bg-amber-50 text-amber-700 border-amber-200",
    critical: "bg-red-50 text-red-700 border-red-200",
    healthy: "bg-emerald-50 text-emerald-700 border-emerald-200",
  };
  const cls = map[label] || "bg-slate-50 text-slate-700 border-slate-200";
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs ${cls}`}
    >
      {label}
    </span>
  );
}

export default function IntelligencePage() {
  const [data, setData] = useState(null);
  const [err, setErr] = useState(null);

  useEffect(() => {
    (async () => {
      try {
        setErr(null);
        // adapte si ton endpoint = /bi/intelligence/ ou /intelligence/
        const res = await http.get("/bi/intelligence/");

        setData(res.data);
      } catch (e) {
        setErr("Impossible de charger l’Intelligence.");
      }
    })();
  }, []);

  if (err) return <div className="text-red-600">{err}</div>;
  if (!data) return <div>Chargement...</div>;

  const fh = data.financial_health_score;
  const sh = data.stock_health_index;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold">Intelligence</h1>
        <div className="text-sm text-slate-600">
          Période: {data.period?.current_start} → {data.period?.current_end}
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl bg-white p-4 shadow-sm border">
          <div className="flex items-center justify-between">
            <div className="font-semibold">Financial Health Score</div>
            <Pill label={fh?.label} />
          </div>
          <div className="mt-2 text-3xl font-bold">{fh?.score}/100</div>
          <div className="mt-3 text-sm text-slate-600">
            Revenue: {fh?.kpis?.revenue} | Marge: {fh?.kpis?.gross_margin} | Δ
            Rev: {fh?.kpis?.revenue_change_percent}%
          </div>
        </div>

        <div className="rounded-2xl bg-white p-4 shadow-sm border">
          <div className="flex items-center justify-between">
            <div className="font-semibold">Stock Health Index</div>
            <Pill label={sh?.label} />
          </div>
          <div className="mt-2 text-3xl font-bold">{sh?.index}/100</div>
          <div className="mt-3 text-sm text-slate-600">
            Expirés: {sh?.metrics?.expired_batches} | Expire bientôt:{" "}
            {sh?.metrics?.expiring_soon_batches} | Stock bas:{" "}
            {sh?.metrics?.low_stock_products}
          </div>
        </div>
      </div>

      <div className="rounded-2xl bg-white p-4 shadow-sm border">
        <div className="font-semibold">Alertes</div>
        <div className="mt-3 space-y-2">
          {(data.alert_intelligence || []).length === 0 && (
            <div className="text-sm text-slate-600">Aucune alerte.</div>
          )}
          {(data.alert_intelligence || []).map((a, idx) => (
            <div key={idx} className="rounded-xl border px-3 py-2 text-sm">
              <div className="font-medium">
                {a.type} ({a.severity})
              </div>
              <div className="text-slate-600">
                {a.message} — {String(a.value)}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
