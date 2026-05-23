import { BrowserRouter, Route, Routes } from 'react-router';
import ProtectedRoute from './components/ProtectedRoute';
import DashboardRoute from './pages/DashboardRoute';
import LoginRoute from './pages/LoginRoute';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginRoute />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <DashboardRoute />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
