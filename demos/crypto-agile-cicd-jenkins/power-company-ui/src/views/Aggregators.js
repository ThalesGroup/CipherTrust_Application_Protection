import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Aggregators() {
  const [aggregators, setAggregators] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch data from the API
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:9090/api/v1/aggregators/summary?threshold=1000');
        console.log('API Response:', response.data); // Log the response
        setAggregators(response.data);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Handle restart aggregator
  const handleRestart = async (aggregatorId) => {
    try {
      const response = await axios.post(`https://api.example.com/aggregators/${aggregatorId}/restart`);
      console.log('Restart Response:', response.data); // Log the restart response

      // Update the aggregator status in the UI
      setAggregators((prevAggregators) =>
        prevAggregators.map((agg) =>
          agg.aggregatorId === aggregatorId ? { ...agg, status: 'good' } : agg
        )
      );

      alert(`Aggregator ${aggregatorId} restarted successfully!`);
    } catch (err) {
      console.error('Error restarting aggregator:', err);
      alert('Failed to restart aggregator. Please try again.');
    }
  };

  if (loading) {
    return <div className="p-6 text-gray-800 dark:text-white">Loading...</div>;
  }

  if (error) {
    return <div className="p-6 text-red-500">Error: {error}</div>;
  }

  return (
    <div className="p-6 bg-gray-100 dark:bg-gray-900 min-h-screen">
      <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-6">Aggregators</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {aggregators.map((aggregator) => (
          <div
            key={aggregator.aggregatorId}
            className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow"
          >
            <h2 className="text-xl font-bold text-gray-800 dark:text-white mb-2">{aggregator.name}</h2>
            <p className="text-gray-600 dark:text-gray-400 mb-2">
              <span className="font-medium">Location:</span> {aggregator.location}
            </p>
            <p className="text-gray-600 dark:text-gray-400 mb-2">
              <span className="font-medium">Total Energy Consumption:</span> {aggregator.totalEnergyConsumption} kWh
            </p>
            <p className="text-gray-600 dark:text-gray-400 mb-2">
              <span className="font-medium">Status:</span>{' '}
              <span
                className={`px-2 py-1 rounded-full text-sm ${
                  aggregator.status === 'good'
                    ? 'bg-green-100 text-green-800'
                    : aggregator.status === 'warning'
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-red-100 text-red-800'
                }`}
              >
                {aggregator.status}
              </span>
            </p>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              <span className="font-medium">Total Smart Meters:</span> {aggregator.totalSmartMeters}
            </p>
            <button
              onClick={() => handleRestart(aggregator.aggregatorId)}
              className="w-full bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600 transition-all"
            >
              Restart
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Aggregators;