import React, { useState, useEffect } from 'react';
import { Route, Routes, Navigate } from 'react-router-dom';
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

function App({ navigate }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userRole, setUserRole] = useState('');
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [username, setUsername] = useState('');
  const [userId, setUserId] = useState('');

  // Check if the user is authenticated on initial load
  useEffect(() => {
    const storedUsername = localStorage.getItem('username');
    const role = localStorage.getItem('userRole');
    const userId = localStorage.getItem('userId');
    if (storedUsername && role && userId) {
      setIsAuthenticated(true);
      setUserRole(role);
      setUsername(storedUsername);
      setUserId(userId);
    }

    // Check for saved dark mode preference
    const savedDarkMode = localStorage.getItem('darkMode') === 'true';
    setIsDarkMode(savedDarkMode);
    if (savedDarkMode) {
      document.documentElement.classList.add('dark');
    }
  }, []);

  // Handle login
  const handleLogin = (username, userId, role) => {
    setIsAuthenticated(true);
    setUsername(username);
    setUserId(userId);
    setUserRole(role);
    localStorage.setItem('authToken', 'dummy-token'); // Simulate a token
    localStorage.setItem('userRole', role); // Store user role
    localStorage.setItem('username', username);
    localStorage.setItem('userId', userId);
  };

  // Handle logout
  const handleLogout = () => {
    const role = localStorage.getItem('userRole'); // Get the role before clearing localStorage

    setIsAuthenticated(false);
    setUserRole('');
    setUsername('');
    setUserId('');

    localStorage.removeItem('authToken');
    localStorage.removeItem('userRole');
    localStorage.removeItem('username');
    localStorage.removeItem('userId');

    // Redirect based on role
    if (role === 'admin') {
      navigate('/login-admin'); // Redirect to admin login
    } else {
      navigate('/login-user'); // Redirect to user login
    }
  };

  // Toggle dark mode
  const toggleDarkMode = () => {
    const newDarkMode = !isDarkMode;
    setIsDarkMode(newDarkMode);
    localStorage.setItem('darkMode', newDarkMode);
    document.documentElement.classList.toggle('dark', newDarkMode);
  };

  return (
    <>
      {isAuthenticated &&
        (userRole === 'admin' ? (
          <NavbarAdmin username={username} onLogout={handleLogout} onToggleDarkMode={toggleDarkMode} isDarkMode={isDarkMode} />
        ) : (
          <NavbarUser username={username} onLogout={handleLogout} onToggleDarkMode={toggleDarkMode} isDarkMode={isDarkMode} />
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
              <LoginUser onLogin={(username, userId) => handleLogin(username, userId, 'user')} />
            )
          }
        />
        <Route
          path="/login-admin"
          element={
            isAuthenticated ? (
              <Navigate to="/" />
            ) : (
              <LoginAdmin onLogin={(username, userId) => handleLogin(username, userId, 'admin')} />
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
    </>
  );
}

export default App;