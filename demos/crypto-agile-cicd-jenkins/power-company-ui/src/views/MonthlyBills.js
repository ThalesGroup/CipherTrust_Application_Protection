import React, { useState, useEffect } from 'react';

function MonthlyBills() {
  const [bills, setBills] = useState([]);

  // Fetch bills data on component mount
  useEffect(() => {
    const fetchBills = async () => {
      try {
        // Simulate an API call to fetch user data
        const response = await fetch('http://localhost:9090/api/v1/users/'+localStorage.getItem('userId'));
        const data = await response.json();

        // Extract and transform the bills data
        const transformedBills = data.bills.map(bill => ({
          month: new Date(bill.monthYear + '-01').toLocaleString('default', { month: 'long', year: 'numeric' }), // Convert "2025-01" to "January 2025"
          amount: `$${bill.amountPaid.toFixed(2)}`,
          status: bill.status.charAt(0).toUpperCase() + bill.status.slice(1) 
        }));

        // Update the bills state
        setBills(transformedBills);
      } catch (error) {
        console.error('Error fetching bills:', error);
      }
    };

    fetchBills();
  }, []);

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