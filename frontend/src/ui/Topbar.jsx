import { useAuth } from "../pages/auth/AuthContext.jsx";

export default function Topbar() {
  const { user, logout } = useAuth();

  return (
    <header className="sticky top-0 z-10 border-b bg-white/80 backdrop-blur">
      <div className="flex items-center justify-between px-4 py-3 md:px-6">
        <div className="text-sm text-slate-600">
          Bienvenue,{" "}
          <span className="font-semibold text-slate-900">
            {user?.name || "Utilisateur"}
          </span>
        </div>

        <button
          onClick={logout}
          className="rounded-xl bg-slate-900 px-3 py-2 text-sm font-medium text-white hover:bg-slate-800"
        >
          Déconnexion
        </button>
      </div>
    </header>
  );
}
