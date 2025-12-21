import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import Login from './components/Login';
import Council from './components/Council';
import DxO from './components/DxO';
import Settings from './components/Settings';
import History from './components/History';
import HistoryDetail from './components/HistoryDetail';
import SuperChat from './components/SuperChat';
import Sidebar from './components/Sidebar';
import ComingSoon from './components/ComingSoon';
import { checkAuth } from './api';

const ProtectedRoute = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(null);

  useEffect(() => {
    checkAuth()
      .then(() => setIsAuthenticated(true))
      .catch(() => setIsAuthenticated(false));
  }, []);

  if (isAuthenticated === null) return <div className="h-screen bg-slate-900 text-white flex items-center justify-center">Loading...</div>;
  if (!isAuthenticated) return <Navigate to="/login" />;

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden">
      <Sidebar />
      <div className="flex-1 overflow-auto p-6">
        {children}
      </div>
    </div>
  );
};

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<ProtectedRoute><Council /></ProtectedRoute>} />
        <Route path="/dxo" element={<ProtectedRoute><DxO /></ProtectedRoute>} />
        <Route path="/history" element={<ProtectedRoute><History /></ProtectedRoute>} />
        <Route path="/history/:id" element={<ProtectedRoute><HistoryDetail /></ProtectedRoute>} />
        <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
        <Route path="/super-chat" element={<ProtectedRoute><SuperChat /></ProtectedRoute>} />
        <Route path="/super-chat/:id" element={<ProtectedRoute><SuperChat /></ProtectedRoute>} />
        <Route path="/frontier" element={<ProtectedRoute><ComingSoon title="Frontier" description="Experimental features and beta models." /></ProtectedRoute>} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
}

export default App;
