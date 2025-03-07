import React from 'react';
import { BrowserRouter as Router, useNavigate } from 'react-router-dom';
import App from './App';

function AppWrapper() {
  const navigate = useNavigate(); // useNavigate hook

  return <App navigate={navigate} />; // Pass navigate as a prop to App
}

export default function Root() {
  return (
    <Router>
      <AppWrapper />
    </Router>
  );
}