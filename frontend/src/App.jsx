import { Routes, Route, Navigate } from "react-router-dom";

import AppLayout from "./layouts/AppLayout";
import LoginPage from "./pages/auth/LoginPage";

import DashboardPage from "./pages/app/DashboardPage";
import IntelligencePage from "./pages/app/IntelligencePage";
import ProductsPage from "./pages/app/ProductsPage";
import SalesPage from "./pages/app/SalesPage";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route path="/app" element={<AppLayout />}>
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="intelligence" element={<IntelligencePage />} />
        <Route path="products" element={<ProductsPage />} />
        <Route path="sales" element={<SalesPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/login" />} />
    </Routes>
  );
}
