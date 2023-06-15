import './App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { React } from 'react';
import Cart from './pages/default/Cart';
import Checkout from './pages/default/Checkout';
import Home from './pages/default/Home';
import ProductDetails from './pages/default/ProductDetails';
import Category from './pages/default/Category';
import MainLayout from './layouts/MainLayout';
import Dashboard from './pages/admin/Dashboard';
import CreateProduct from './pages/admin/Product/CreateProduct';
import Login from './pages/authentication/Login';
import Logout from './pages/authentication/Logout';
import Register from './pages/authentication/Register';
import List from './pages/admin/Order/List';
import AdminLogin from './pages/authentication/AdminLogin';

function App() {
  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route path='/login' element={<Login />} />
          <Route path='/logout' element={<Logout />} />
          <Route path='/register' element={<Register />} />
          <Route exact path="/" element={<MainLayout />}>
            <Route path="" element={<Home />} />
            <Route path="home" element={<Home />} />
            <Route path="cart" element={<Cart />} />
            <Route path="checkout" element={<Checkout />} />
            <Route path="product" element={<ProductDetails />} />
            <Route path="category" element={<Category />} />
          </Route>
          <Route exact path="/admin" element={<Dashboard />} />
          <Route exact path="/admin/addProduct" element={<CreateProduct />} />
          <Route exact path="/admin/listOrders" element={<List />} />
          <Route exact path="/admin/login" element={<AdminLogin />} />
        </Routes>
      </BrowserRouter>
    </>
  );
}

export default App;
