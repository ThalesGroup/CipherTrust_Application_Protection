import React, { useState, useEffect } from 'react';
import axios from 'axios';

function SubscribedUsers() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch data from the API
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('https://api.example.com/subscribed-users');
        console.log('API Response:', response.data); // Log the response
        setUsers(response.data);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <div className="p-6 text-gray-800 dark:text-white">Loading...</div>;
  }

  if (error) {
    return <div className="p-6 text-red-500">Error: {error}</div>;
  }

  return (
    <div className="p-6 bg-gray-100 dark:bg-gray-900 min-h-screen">
      <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-6">Subscribed Users</h1>
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
        <table className="w-full">
          <thead>
            <tr>
              <th className="text-left text-gray-700 dark:text-gray-300">Name</th>
              <th className="text-left text-gray-700 dark:text-gray-300">Email</th>
              <th className="text-left text-gray-700 dark:text-gray-300">Contact Number</th>
              <th className="text-left text-gray-700 dark:text-gray-300">Address</th>
              <th className="text-left text-gray-700 dark:text-gray-300">Payment Info</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id} className="border-t">
                <td className="py-2 text-gray-800 dark:text-white">{user.name}</td>
                <td className="py-2 text-gray-800 dark:text-white">{user.email}</td>
                <td className="py-2 text-gray-800 dark:text-white">{user.contactNum}</td>
                <td className="py-2 text-gray-800 dark:text-white">
                  {user.addressLineOne}, {user.addressLineTwo ? `${user.addressLineTwo}, ` : ''}
                  {user.city}, {user.state}, {user.country}, {user.zip}
                </td>
                <td className="py-2 text-gray-800 dark:text-white">
                  {user.paymentInfo ? (
                    <div className={`p-4 rounded-lg shadow-md ${getCardBackground(user.paymentInfo.cardType)}`}>
                      <div className="text-white">
                        <div className="flex justify-between items-center mb-4">
                          <span className="text-lg font-semibold">{user.name}</span>
                          <span className="text-sm">{user.paymentInfo.cardType}</span>
                        </div>
                        <div className="mb-4">
                          <span className="text-xl tracking-widest">{user.paymentInfo.cardNumber}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <div>
                            <span className="text-sm">Exp:</span>{' '}
                            <span className="text-sm">{user.paymentInfo.expirationDate}</span>
                          </div>
                          <div>
                            <span className="text-sm">CVV:</span>{' '}
                            <span className="text-sm">{user.paymentInfo.cvv}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <span className="text-sm text-gray-500">No payment info on file</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// Helper function to get card background based on type
const getCardBackground = (cardType) => {
  switch (cardType.toLowerCase()) {
    case 'visa':
      return 'bg-gradient-to-r from-blue-500 to-purple-600';
    case 'mastercard':
      return 'bg-gradient-to-r from-red-500 to-orange-500';
    case 'amex':
      return 'bg-gradient-to-r from-green-500 to-teal-500';
    default:
      return 'bg-gradient-to-r from-gray-500 to-gray-700';
  }
};

export default SubscribedUsers;