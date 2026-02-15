import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Brain,
  Package,
  Receipt,
  Settings,
} from "lucide-react";

const linkBase =
  "flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium hover:bg-slate-100";
const active = "bg-slate-100 text-slate-900";
const idle = "text-slate-600";

export default function Sidebar() {
  return (
    <aside className="sticky top-0 h-screen w-64 border-r bg-white p-4 hidden md:block">
      <div className="mb-6">
        <div className="text-lg font-bold">ngrPharma</div>
        <div className="text-xs text-slate-500">SaaS Pharmacy BI</div>
      </div>

      <nav className="space-y-1">
        <NavLink
          to="/dashboard"
          className={({ isActive }) =>
            `${linkBase} ${isActive ? active : idle}`
          }
        >
          <LayoutDashboard size={18} /> Dashboard
        </NavLink>

        <NavLink
          to="/intelligence"
          className={({ isActive }) =>
            `${linkBase} ${isActive ? active : idle}`
          }
        >
          <Brain size={18} /> Intelligence
        </NavLink>

        <NavLink
          to="/products"
          className={({ isActive }) =>
            `${linkBase} ${isActive ? active : idle}`
          }
        >
          <Package size={18} /> Produits
        </NavLink>

        <NavLink
          to="/sales"
          className={({ isActive }) =>
            `${linkBase} ${isActive ? active : idle}`
          }
        >
          <Receipt size={18} /> Ventes
        </NavLink>

        <div className="mt-6 border-t pt-4">
          <NavLink
            to="/admin/saas"
            className={({ isActive }) =>
              `${linkBase} ${isActive ? active : idle}`
            }
          >
            <Settings size={18} /> Admin SaaS
          </NavLink>
        </div>
      </nav>
    </aside>
  );
}
