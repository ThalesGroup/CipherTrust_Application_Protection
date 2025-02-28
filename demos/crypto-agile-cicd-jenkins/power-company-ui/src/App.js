import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import NavbarUser from './components/NavbarUser';
import NavbarAdmin from './components/NavbarAdmin';
import DashboardUser from './views/DashboardUser';
import DashboardAdmin from './views/DashboardAdmin';
import DataCenter from './views/DataCenter';
import Aggregators from './views/Aggregators';
import SmartMeters from './views/SmartMeters';
import LoginUser from './views/LoginUser';
import LoginAdmin from './views/LoginAdmin';
import UpdatePayment from './views/UpdatePayment';
import UpdateProfile from './views/UpdateProfile';
import MonthlyBills from './views/MonthlyBills';
import UsageTrend from './views/UsageTrend';
import SubscribedUsers from './views/SubscribedUsers';
import AggregatedUsage from './views/AggregatedUsage';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userRole, setUserRole] = useState('');
  const [isDarkMode, setIsDarkMode] = useState(false);

  // Check if the user is authenticated on initial load
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    const role = localStorage.getItem('userRole');
    if (token && role) {
      setIsAuthenticated(true);
      setUserRole(role);
    }

    // Check for saved dark mode preference
    const savedDarkMode = localStorage.getItem('darkMode') === 'true';
    setIsDarkMode(savedDarkMode);
    if (savedDarkMode) {
      document.documentElement.classList.add('dark');
    }
  }, []);

  // Handle login
  const handleLogin = (role) => {
    localStorage.setItem('authToken', 'dummy-token'); // Simulate a token
    localStorage.setItem('userRole', role); // Store user role
    setIsAuthenticated(true);
    setUserRole(role);
  };

  // Handle logout
  const handleLogout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userRole');
    setIsAuthenticated(false);
    setUserRole('');
  };

  // Toggle dark mode
  const toggleDarkMode = () => {
    const newDarkMode = !isDarkMode;
    setIsDarkMode(newDarkMode);
    localStorage.setItem('darkMode', newDarkMode);
    document.documentElement.classList.toggle('dark', newDarkMode);
  };

  return (
    <Router>
      {isAuthenticated &&
        (userRole === 'admin' ? (
          <NavbarAdmin onLogout={handleLogout} onToggleDarkMode={toggleDarkMode} isDarkMode={isDarkMode} />
        ) : (
          <NavbarUser onLogout={handleLogout} onToggleDarkMode={toggleDarkMode} isDarkMode={isDarkMode} />
        ))}
      <Routes>
        <Route
          path="/"
          element={
            isAuthenticated ? (
              userRole === 'admin' ? (
                <DashboardAdmin />
              ) : (
                <DashboardUser />
              )
            ) : (
              <Navigate to="/login-user" />
            )
          }
        />
        <Route
          path="/data-center"
          element={
            isAuthenticated && userRole === 'admin' ? (
              <DataCenter />
            ) : (
              <Navigate to="/login-admin" />
            )
          }
        />
        <Route
          path="/aggregators"
          element={
            isAuthenticated && userRole === 'admin' ? (
              <Aggregators />
            ) : (
              <Navigate to="/login-admin" />
            )
          }
        />
        <Route
          path="/smart-meters"
          element={
            isAuthenticated && userRole === 'user' ? (
              <SmartMeters />
            ) : (
              <Navigate to="/login-user" />
            )
          }
        />
        <Route
          path="/login-user"
          element={
            isAuthenticated ? (
              <Navigate to="/" />
            ) : (
              <LoginUser onLogin={() => handleLogin('user')} />
            )
          }
        />
        <Route
          path="/login-admin"
          element={
            isAuthenticated ? (
              <Navigate to="/" />
            ) : (
              <LoginAdmin onLogin={() => handleLogin('admin')} />
            )
          }
        />
        <Route
          path="/update-payment"
          element={
            isAuthenticated && userRole === 'user' ? (
              <UpdatePayment />
            ) : (
              <Navigate to="/login-user" />
            )
          }
        />
        <Route
          path="/update-profile"
          element={
            isAuthenticated && userRole === 'user' ? (
              <UpdateProfile />
            ) : (
              <Navigate to="/login-user" />
            )
          }
        />
        <Route
          path="/monthly-bills"
          element={
            isAuthenticated && userRole === 'user' ? (
              <MonthlyBills />
            ) : (
              <Navigate to="/login-user" />
            )
          }
        />
        <Route
          path="/usage-trend"
          element={
            isAuthenticated && userRole === 'user' ? (
              <UsageTrend />
            ) : (
              <Navigate to="/login-user" />
            )
          }
        />
        <Route
          path="/subscribed-users"
          element={
            isAuthenticated && userRole === 'admin' ? (
              <SubscribedUsers />
            ) : (
              <Navigate to="/login-admin" />
            )
          }
        />
        <Route
          path="/aggregated-usage"
          element={
            isAuthenticated && userRole === 'admin' ? (
              <AggregatedUsage />
            ) : (
              <Navigate to="/login-admin" />
            )
          }
        />
      </Routes>
    </Router>
  );
}

export default App;