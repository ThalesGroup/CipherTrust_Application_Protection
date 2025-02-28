import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

const data = [
  { day: '1', usage: 20 },
  { day: '2', usage: 25 },
  { day: '3', usage: 30 },
  { day: '4', usage: 22 },
  { day: '5', usage: 28 },
  { day: '6', usage: 35 },
  { day: '7', usage: 40 },
];

function UsageTrend() {
  return (
    <div className="p-6 bg-gray-100 dark:bg-gray-900 min-h-screen">
      <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-6">Current Usage Trend</h1>
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
        <LineChart width={600} height={300} data={data}>
          <XAxis dataKey="day" />
          <YAxis />
          <CartesianGrid stroke="#eee" />
          <Line type="monotone" dataKey="usage" stroke="#8884d8" />
          <Tooltip />
          <Legend />
        </LineChart>
      </div>
    </div>
  );
}

export default UsageTrend;