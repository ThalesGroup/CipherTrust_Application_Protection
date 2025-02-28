import React from 'react';

function AggregatedUsage() {
  const usageData = [
    { aggregator: 'Aggregator 1', usage: 500, smartMeters: 100 },
    { aggregator: 'Aggregator 2', usage: 450, smartMeters: 90 },
    { aggregator: 'Aggregator 3', usage: 600, smartMeters: 120 },
  ];

  return (
    <div className="p-6 bg-gray-100 dark:bg-gray-900 min-h-screen">
      <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-6">Aggregated Usage</h1>
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
        <table className="w-full">
          <thead>
            <tr>
              <th className="text-left text-gray-700 dark:text-gray-300">Aggregator</th>
              <th className="text-left text-gray-700 dark:text-gray-300">Usage (kWh)</th>
              <th className="text-left text-gray-700 dark:text-gray-300">Smart Meters</th>
            </tr>
          </thead>
          <tbody>
            {usageData.map((data, index) => (
              <tr key={index} className="border-t">
                <td className="py-2 text-gray-800 dark:text-white">{data.aggregator}</td>
                <td className="py-2 text-gray-800 dark:text-white">{data.usage}</td>
                <td className="py-2 text-gray-800 dark:text-white">{data.smartMeters}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default AggregatedUsage;