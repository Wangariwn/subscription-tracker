import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { ProtectedRoute } from "./ProtectedRoute";

function AdminGate({ children }) {
  const { isAdmin, bootstrapping } = useAuth();
  const location = useLocation();

  if (bootstrapping) {
    return <p className="status">Checking session…</p>;
  }

  if (!isAdmin) {
    return <Navigate to="/" replace state={{ from: location }} />;
  }

  return children;
}

export function AdminRoute({ children }) {
  return (
    <ProtectedRoute>
      <AdminGate>{children}</AdminGate>
    </ProtectedRoute>
  );
}
