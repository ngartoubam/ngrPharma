import { useEffect, useState } from "react";
import { getFinanceDashboard } from "../api/financeApi";
import KPIcard from "../components/KPIcard";

export default function Dashboard() {
  const [data, setData] = useState(null);

  useEffect(() => {
    getFinanceDashboard().then(setData);
  }, []);

  if (!data) return <p>Chargement...</p>;

  return (
    <div>
      <h1>Dashboard Général</h1>

      <div style={{ display: "flex", gap: "20px", marginTop: "30px" }}>
        <KPIcard title="Chiffre d'affaires" value={data.revenue + " FCFA"} />
        <KPIcard title="Coût des ventes" value={data.cogs + " FCFA"} />
        <KPIcard title="Marge brute" value={data.gross_profit + " FCFA"} />
        <KPIcard title="Valeur du stock" value={data.stock_value + " FCFA"} />
      </div>
    </div>
  );
}
