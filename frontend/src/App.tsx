import { BrowserRouter, Route, Routes } from 'react-router';
import DashboardRoute from './pages/DashboardRoute';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<DashboardRoute />} />
      </Routes>
    </BrowserRouter>
  );
}
