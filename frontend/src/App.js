
import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import Upload from './components/Upload';
import Query from './components/Query';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import { getToken, saveToken, removeToken } from './utils/auth';

const App = () => {
  const [token, setToken] = useState(getToken());

  const handleLogin = (newToken) => {
    saveToken(newToken);
    setToken(newToken);
  };

  const handleLogout = () => {
    removeToken();
    setToken(null);
  };

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login onLogin={handleLogin} />} />
        <Route path="/register" element={<Register />} />
        <Route path="/upload" element={token ? <Upload token={token} /> : <Navigate to="/login" />} />
        <Route path="/query" element={token ? <Query /> : <Navigate to="/login" />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
};

export default App;