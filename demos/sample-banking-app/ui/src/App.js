import './App.css';
import {React} from 'react';
import Dashboard from './components/Dashboard/Dashboard';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Account from './components/Account/Account';
import CreateAccount from './components/Account/Create';
import Fetch from './components/Account/Fetch';
import Login from './components/Login/Login';
import UserLayout from './layouts/UserLayout';
import AdminLayout from './layouts/AdminLayout';
import Logout from './components/Login/Logout';
import List from './components/Account/List';
import My from './components/Account/My';
import UserDashboard from './components/Dashboard/UserDashboard';
import CreateFirst from './components/Account/CreateFirst';
import UserCreate from './components/Login/UserCreate';

function App() {
  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route exact path="/" element={<Login />} />
          <Route path='/login' element={<Login />} />
          <Route path='/logout' element={<Logout />} />
          <Route path='/userCreate' element={<UserCreate />} />
          <Route path="/auth/user" element={<UserLayout />}>
            <Route exact path="home" element={<UserDashboard />} />
            <Route path="myAccount" element={<My />} />
            <Route path="accounts" element={<Account />} />
            <Route path="createAccount" element={<CreateAccount />} />
            <Route path="createFirst" element={<CreateFirst />} />
          </Route>
          <Route path="/auth/admin" element={<AdminLayout />}>
            <Route exact path="home" element={<List />} />
            <Route path="fetch" element={<Fetch />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </>
  );
}

export default App;
