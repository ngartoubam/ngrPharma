import { Outlet, NavLink, useNavigate } from "react-router-dom";

export default function AdminLayout() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user") || "null");

  const logout = () => {
    localStorage.clear();
    navigate("/admin/login");
  };

  return (
    <div className="flex min-h-screen bg-slate-100">
      {/* SIDEBAR */}
      <aside className="w-64 bg-slate-900 text-white flex flex-col">
        <div className="p-6 border-b border-slate-700">
          <h2 className="text-xl font-bold">ngrPharma SaaS</h2>
          <p className="text-xs text-slate-400 mt-1">Admin Panel</p>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          <NavLink
            to="/admin/dashboard"
            className={({ isActive }) =>
              `block px-4 py-2 rounded-lg ${
                isActive ? "bg-slate-700" : "hover:bg-slate-800"
              }`
            }
          >
            Dashboard
          </NavLink>

          <NavLink
            to="/admin/pharmacies"
            className={({ isActive }) =>
              `block px-4 py-2 rounded-lg ${
                isActive ? "bg-slate-700" : "hover:bg-slate-800"
              }`
            }
          >
            Pharmacies
          </NavLink>

          <NavLink
            to="/admin/subscriptions"
            className={({ isActive }) =>
              `block px-4 py-2 rounded-lg ${
                isActive ? "bg-slate-700" : "hover:bg-slate-800"
              }`
            }
          >
            Subscriptions
          </NavLink>

          <NavLink
            to="/admin/analytics"
            className={({ isActive }) =>
              `block px-4 py-2 rounded-lg ${
                isActive ? "bg-slate-700" : "hover:bg-slate-800"
              }`
            }
          >
            Global Analytics
          </NavLink>
        </nav>

        <div className="p-4 border-t border-slate-700">
          <p className="text-sm text-slate-400">{user?.name}</p>
          <button
            onClick={logout}
            className="mt-2 w-full bg-red-600 hover:bg-red-700 py-2 rounded-lg text-sm"
          >
            Logout
          </button>
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <div className="flex-1 flex flex-col">
        {/* TOPBAR */}
        <header className="bg-white shadow px-8 py-4 flex justify-between items-center">
          <h1 className="text-xl font-semibold">SaaS Administration</h1>
        </header>

        {/* CONTENT */}
        <main className="p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
