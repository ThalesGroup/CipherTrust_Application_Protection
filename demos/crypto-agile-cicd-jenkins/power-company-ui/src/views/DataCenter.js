import React from 'react';

function DataCenter() {
  return (
    <div className="p-6 bg-gray-100 dark:bg-gray-900 min-h-screen">
      <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-6">Data Center</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white">Power Generation</h2>
          <p className="text-gray-600 dark:text-gray-400">Current output: 500 MW</p>
        </div>
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white">Storage Capacity</h2>
          <p className="text-gray-600 dark:text-gray-400">Available: 1000 MWh</p>
        </div>
      </div>
    </div>
  );
}

export default DataCenter;