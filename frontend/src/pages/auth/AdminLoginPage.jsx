import { useState } from "react";
import { useNavigate } from "react-router-dom";
import http from "../../api/http";

export default function AdminLoginPage() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await http.post("/auth/admin-login/", {
        email,
        password,
      });

      const data = response.data;

      // 🔎 Vérification sécurité
      if (!data?.access || !data?.user?.is_saas_admin) {
        throw new Error("Invalid admin response");
      }

      // 🔐 Stockage sécurisé
      localStorage.setItem("access_token", data.access);
      localStorage.setItem("refresh_token", data.refresh);
      localStorage.setItem("user", JSON.stringify(data.user));

      // 🚀 Redirection
      navigate("/admin/dashboard", { replace: true });
    } catch (err) {
      console.error("Admin login error:", err);

      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError("Identifiants invalides ou accès refusé.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-100 to-slate-200">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md bg-white p-8 rounded-2xl shadow-xl"
      >
        <h1 className="text-2xl font-bold text-slate-800">SaaS Admin Login</h1>

        <p className="text-sm text-gray-500 mt-2">
          Accès administration globale ngrPharma
        </p>

        <div className="mt-6 space-y-4">
          <input
            className="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-black"
            placeholder="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="username"
            required
          />

          <input
            className="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-black"
            placeholder="Mot de passe"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
          />

          {error && (
            <div className="text-red-600 text-sm bg-red-100 p-2 rounded-lg">
              {error}
            </div>
          )}

          <button
            type="submit"
            className="w-full bg-black text-white rounded-lg py-3 font-semibold hover:bg-slate-900 transition"
            disabled={loading}
          >
            {loading ? "Connexion..." : "Se connecter"}
          </button>
        </div>
      </form>
    </div>
  );
}
