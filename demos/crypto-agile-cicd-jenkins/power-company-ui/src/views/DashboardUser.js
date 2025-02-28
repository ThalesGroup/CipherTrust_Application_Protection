import React from 'react';
import { FaBolt, FaChartLine, FaUser, FaCreditCard, FaFileInvoice } from 'react-icons/fa';
import { Link } from 'react-router-dom';

function DashboardUser() {
  return (
    <div className="p-6 bg-gray-100 dark:bg-gray-900 min-h-screen">
      <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-6">User Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Card 1: Energy Usage */}
        <Link
          to="/usage-trend"
          className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow"
        >
          <div className="flex items-center mb-4">
            <FaBolt className="text-blue-500 text-2xl mr-2" />
            <h2 className="text-xl font-semibold text-gray-800 dark:text-white">Energy Usage</h2>
          </div>
          <p className="text-gray-600 dark:text-gray-400">View your current usage trends.</p>
        </Link>

        {/* Card 2: Monthly Bills */}
        <Link
          to="/monthly-bills"
          className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow"
        >
          <div className="flex items-center mb-4">
            <FaFileInvoice className="text-green-500 text-2xl mr-2" />
            <h2 className="text-xl font-semibold text-gray-800 dark:text-white">Monthly Bills</h2>
          </div>
          <p className="text-gray-600 dark:text-gray-400">View and manage your monthly bills.</p>
        </Link>

        {/* Card 3: Payment Settings */}
        <Link
          to="/update-payment"
          className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow"
        >
          <div className="flex items-center mb-4">
            <FaCreditCard className="text-purple-500 text-2xl mr-2" />
            <h2 className="text-xl font-semibold text-gray-800 dark:text-white">Payment Settings</h2>
          </div>
          <p className="text-gray-600 dark:text-gray-400">Update your payment details.</p>
        </Link>
      </div>
    </div>
  );
}

export default DashboardUser;