import './App.css';
import {React, useState} from 'react';
import Dashboard from './components/Dashboard/Dashboard';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Statement from './components/Statement/Statement';
import Account from './components/Account/Account';
import CreateAccount from './components/Account/Create';
import Fetch from './components/Account/Fetch';
import Login from './components/Login/Login';
import UserLayout from './layouts/UserLayout';
import AdminLayout from './layouts/AdminLayout';
import Logout from './components/Login/Logout';

function App() {
  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route exact path="/" element={<Login />} />
          <Route path='/login' element={<Login />} />
          <Route path='/logout' element={<Logout />} />
          <Route path="/auth/user" element={<UserLayout />}>
            <Route exact path="home" element={<Dashboard />} />
            <Route path="accounts" element={<Account />} />
            <Route path="createAccount" element={<CreateAccount />} />
          </Route>
          <Route path="/auth/admin" element={<AdminLayout />}>
            <Route exact path="home" element={<Dashboard />} />
            <Route path="listAccounts" element={<Fetch />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </>
  );
}

export default App;
