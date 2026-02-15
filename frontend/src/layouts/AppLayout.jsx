import { Outlet, NavLink } from "react-router-dom";

export default function AppLayout() {
  return (
    <div className="flex h-screen bg-gray-100">
      {/* SIDEBAR */}
      <aside className="w-64 bg-white shadow-lg flex flex-col">
        <div className="p-6 border-b">
          <h1 className="text-xl font-bold text-blue-600">ngrPharma SaaS</h1>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          <SidebarLink to="/app/dashboard" label="Dashboard" />
          <SidebarLink to="/app/intelligence" label="Intelligence BI" />
          <SidebarLink to="/app/products" label="Produits" />
          <SidebarLink to="/app/sales" label="Ventes" />
          <SidebarLink to="/app/finance" label="Finance" />
          <SidebarLink to="/app/stock" label="Stock" />
        </nav>

        <div className="p-4 border-t text-sm text-gray-500">Plan: Pro</div>
      </aside>

      {/* MAIN AREA */}
      <div className="flex-1 flex flex-col">
        {/* TOPBAR */}
        <header className="bg-white shadow px-6 py-4 flex justify-between">
          <h2 className="font-semibold">Dashboard</h2>
          <div className="text-sm text-gray-500">Connecté</div>
        </header>

        {/* CONTENT */}
        <main className="flex-1 p-6 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

function SidebarLink({ to, label }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `block px-4 py-2 rounded-lg transition ${
          isActive
            ? "bg-blue-100 text-blue-600 font-medium"
            : "text-gray-600 hover:bg-gray-100"
        }`
      }
    >
      {label}
    </NavLink>
  );
}
