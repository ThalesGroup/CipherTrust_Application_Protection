import React, { useState } from 'react';

function Aggregators() {
  const [aggregators, setAggregators] = useState([
    {
      id: 1,
      name: 'Aggregator 1',
      status: 'online', // Can be 'online', 'warning', or 'offline'
      location: 'New York, NY',
      currentLoad: '200 MW',
      health: 'Good',
    },
    {
      id: 2,
      name: 'Aggregator 2',
      status: 'warning', // Can be 'online', 'warning', or 'offline'
      location: 'Los Angeles, CA',
      currentLoad: '150 MW',
      health: 'Degraded',
    },
    {
      id: 3,
      name: 'Aggregator 3',
      status: 'offline', // Can be 'online', 'warning', or 'offline'
      location: 'Chicago, IL',
      currentLoad: '0 MW',
      health: 'Critical',
    },
  ]);

  const toggleAggregator = (id) => {
    setAggregators((prevAggregators) =>
      prevAggregators.map((agg) =>
        agg.id === id
          ? { ...agg, status: agg.status === 'offline' ? 'online' : 'offline' }
          : agg
      )
    );
  };

  const restartAggregator = (id) => {
    setAggregators((prevAggregators) =>
      prevAggregators.map((agg) =>
        agg.id === id ? { ...agg, status: 'online' } : agg
      )
    );
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'online':
        return 'bg-green-500';
      case 'warning':
        return 'bg-yellow-500';
      case 'offline':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className="p-6 bg-gray-100 dark:bg-gray-900 min-h-screen">
      <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-6">Aggregators</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {aggregators.map((agg) => (
          <div
            key={agg.id}
            className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow"
          >
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-800 dark:text-white">{agg.name}</h2>
              <div className={`w-4 h-4 rounded-full ${getStatusColor(agg.status)}`}></div>
            </div>
            <div className="space-y-2">
              <p className="text-gray-600 dark:text-gray-400">
                <span className="font-medium">Location:</span> {agg.location}
              </p>
              <p className="text-gray-600 dark:text-gray-400">
                <span className="font-medium">Current Load:</span> {agg.currentLoad}
              </p>
              <p className="text-gray-600 dark:text-gray-400">
                <span className="font-medium">Health:</span> {agg.health}
              </p>
            </div>
            <div className="mt-4 flex space-x-2">
              <button
                onClick={() => toggleAggregator(agg.id)}
                className="w-full bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600 transition-all"
              >
                {agg.status === 'offline' ? 'Turn On' : 'Turn Off'}
              </button>
              <button
                onClick={() => restartAggregator(agg.id)}
                className="w-full bg-yellow-500 text-white py-2 rounded-lg hover:bg-yellow-600 transition-all"
              >
                Restart
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Aggregators;