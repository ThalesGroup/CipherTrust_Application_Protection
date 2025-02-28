import React from 'react';
import { FaUser, FaLock } from 'react-icons/fa';

function LoginUser({ onLogin }) {
  const handleSubmit = (e) => {
    e.preventDefault();
    onLogin();
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-r from-blue-500 to-purple-600">
      <div className="bg-white p-8 rounded-lg shadow-2xl w-96 transform transition-all hover:scale-105">
        <div className="text-center mb-6">
          <h1 className="text-3xl font-bold text-gray-800">Welcome Back!</h1>
          <p className="text-gray-600">Sign in to your Crestline Power account.</p>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2 text-gray-700" htmlFor="username">
              Username
            </label>
            <div className="relative">
              <input
                type="text"
                id="username"
                className="w-full px-4 py-2 pl-10 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter username"
              />
              <FaUser className="absolute left-3 top-3 text-gray-400" />
            </div>
          </div>
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2 text-gray-700" htmlFor="password">
              Password
            </label>
            <div className="relative">
              <input
                type="password"
                id="password"
                className="w-full px-4 py-2 pl-10 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter password"
              />
              <FaLock className="absolute left-3 top-3 text-gray-400" />
            </div>
          </div>
          <button
            type="submit"
            className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-2 rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all"
          >
            Login
          </button>
        </form>
        <div className="mt-4 text-center">
          <p className="text-gray-600">
            Don't have an account?{' '}
            <a href="#" className="text-blue-500 hover:underline">
              Sign up
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}

export default LoginUser;