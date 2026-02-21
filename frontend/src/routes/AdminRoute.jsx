// frontend/src/routes/AdminRoute.jsx

import { Navigate } from "react-router-dom";

export default function AdminRoute({ children }) {
  const user = JSON.parse(localStorage.getItem("user"));

  if (!localStorage.getItem("access_token")) {
    return <Navigate to="/admin/login" replace />;
  }

  if (!user?.is_saas_admin) {
    return <Navigate to="/" replace />;
  }

  return children;
}
