import React from 'react';
import { FaChartBar, FaCogs, FaUsers, FaFileAlt } from 'react-icons/fa';
import { Link } from 'react-router-dom';

function DashboardAdmin() {
  return (
    <div className="p-6 bg-gray-100 dark:bg-gray-900 min-h-screen">
      <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-6">Admin Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Card 1: Subscribed Users */}
        <Link
          to="/subscribed-users"
          className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow"
        >
          <div className="flex items-center mb-4">
            <FaUsers className="text-blue-500 text-2xl mr-2" />
            <h2 className="text-xl font-semibold text-gray-800 dark:text-white">Subscribed Users</h2>
          </div>
          <p className="text-gray-600 dark:text-gray-400">View and manage subscribed users.</p>
        </Link>

        {/* Card 2: Aggregated Usage */}
        <Link
          to="/aggregators"
          className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow"
        >
          <div className="flex items-center mb-4">
            <FaChartBar className="text-green-500 text-2xl mr-2" />
            <h2 className="text-xl font-semibold text-gray-800 dark:text-white">Aggregators</h2>
          </div>
          <p className="text-gray-600 dark:text-gray-400">View aggregated usage data.</p>
        </Link>

        {/* Card 3: Reports */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow">
          <div className="flex items-center mb-4">
            <FaFileAlt className="text-purple-500 text-2xl mr-2" />
            <h2 className="text-xl font-semibold text-gray-800 dark:text-white">Reports</h2>
          </div>
          <p className="text-gray-600 dark:text-gray-400">Generate and view reports.</p>
        </div>
      </div>
    </div>
  );
}

export default DashboardAdmin;