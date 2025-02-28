import React from 'react';

function MonthlyBills() {
  const bills = [
    { month: 'January 2025', amount: '$120.50', status: 'Paid' },
    { month: 'February 2025', amount: '$110.00', status: 'Paid' },
    { month: 'March 2025', amount: '$130.75', status: 'Pending' },
  ];

  return (
    <div className="p-6 bg-gray-100 dark:bg-gray-900 min-h-screen">
      <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-6">Monthly Bills</h1>
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
        <table className="w-full">
          <thead>
            <tr>
              <th className="text-left text-gray-700 dark:text-gray-300">Month</th>
              <th className="text-left text-gray-700 dark:text-gray-300">Amount</th>
              <th className="text-left text-gray-700 dark:text-gray-300">Status</th>
            </tr>
          </thead>
          <tbody>
            {bills.map((bill, index) => (
              <tr key={index} className="border-t">
                <td className="py-2 text-gray-800 dark:text-white">{bill.month}</td>
                <td className="py-2 text-gray-800 dark:text-white">{bill.amount}</td>
                <td className="py-2 text-gray-800 dark:text-white">{bill.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default MonthlyBills;