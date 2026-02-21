import { Routes, Route, Navigate } from "react-router-dom";

import AppLayout from "./layouts/AppLayout";
import AdminLayout from "./layouts/AdminLayout";

import LoginPage from "./pages/auth/LoginPage";
import AdminLoginPage from "./pages/auth/AdminLoginPage";

import DashboardPage from "./pages/app/DashboardPage";
import IntelligencePage from "./pages/app/IntelligencePage";
import ProductsPage from "./pages/app/ProductsPage";
import SalesPage from "./pages/app/SalesPage";

import AdminDashboardPage from "./pages/admin/AdminDashboardPage";
import PharmaciesPage from "./pages/admin/PharmaciesPage";

/* =======================================================
   🔐 ADMIN ROUTE PROTECTION
======================================================= */
function AdminRoute({ children }) {
  const token = localStorage.getItem("access_token");
  const user = JSON.parse(localStorage.getItem("user") || "null");

  if (!token) {
    return <Navigate to="/admin/login" replace />;
  }

  if (!user?.is_saas_admin) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

/* =======================================================
   🔐 PHARMACY ROUTE PROTECTION
======================================================= */
function PharmacyRoute({ children }) {
  const token = localStorage.getItem("access_token");
  const user = JSON.parse(localStorage.getItem("user") || "null");

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  // Empêche admin SaaS d’entrer dans app pharmacie
  if (user?.is_saas_admin) {
    return <Navigate to="/admin/dashboard" replace />;
  }

  return children;
}

/* =======================================================
   🎯 SMART DEFAULT ROUTE
======================================================= */
function SmartRedirect() {
  const token = localStorage.getItem("access_token");
  const user = JSON.parse(localStorage.getItem("user") || "null");

  if (!token) return <Navigate to="/login" replace />;

  if (user?.is_saas_admin) {
    return <Navigate to="/admin/dashboard" replace />;
  }

  return <Navigate to="/app/dashboard" replace />;
}

/* =======================================================
   🚀 APP ROUTING
======================================================= */
export default function App() {
  return (
    <Routes>
      {/* ================= LOGIN ================= */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/admin/login" element={<AdminLoginPage />} />

      {/* ================= ADMIN PANEL ================= */}
      <Route
        path="/admin"
        element={
          <AdminRoute>
            <AdminLayout />
          </AdminRoute>
        }
      >
        <Route path="dashboard" element={<AdminDashboardPage />} />
        <Route path="pharmacies" element={<PharmaciesPage />} />
      </Route>

      {/* ================= PHARMACY APP ================= */}
      <Route
        path="/app"
        element={
          <PharmacyRoute>
            <AppLayout />
          </PharmacyRoute>
        }
      >
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="intelligence" element={<IntelligencePage />} />
        <Route path="products" element={<ProductsPage />} />
        <Route path="sales" element={<SalesPage />} />
      </Route>

      {/* ================= SMART DEFAULT ================= */}
      <Route path="/" element={<SmartRedirect />} />
      <Route path="*" element={<SmartRedirect />} />
    </Routes>
  );
}
