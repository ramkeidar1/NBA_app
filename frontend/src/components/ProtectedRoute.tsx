import { Navigate } from 'react-router';
import { useAuthStore } from '../store/authStore';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const status = useAuthStore((s) => s.status);

  if (status === 'loading') {
    return (
      <div className="flex h-screen items-center justify-center">
        <span className="text-sm text-gray-400">Authenticating…</span>
      </div>
    );
  }

  if (status === 'guest') {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}
