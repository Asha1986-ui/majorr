import { useEffect } from "react";
import { Navigate } from "react-router-dom";
import { toast } from "react-toastify";

function ProtectedRoute({ children }) {
  const token = localStorage.getItem("access_token");

  useEffect(() => {
    if (!token) {
      toast.info("🔐 Please sign in to access your DiaSense AI health workspace.");
    }
  }, [token]);

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

export default ProtectedRoute;
