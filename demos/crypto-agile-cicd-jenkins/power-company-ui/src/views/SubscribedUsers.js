import React from 'react';

function SubscribedUsers() {
  const users = [
    {
      id: 1,
      name: 'John Doe',
      email: 'john@example.com',
      paymentStatus: 'Active',
      paymentCard: {
        type: 'Visa',
        number: '**** **** **** 1234',
        exp: '12/25',
        cvv: '***',
        cardholder: 'John Doe',
      },
    },
    {
      id: 2,
      name: 'Jane Smith',
      email: 'jane@example.com',
      paymentStatus: 'Inactive',
      paymentCard: {
        type: 'Mastercard',
        number: '**** **** **** 5678',
        exp: '06/24',
        cvv: '***',
        cardholder: 'Jane Smith',
      },
    },
    {
      id: 3,
      name: 'Alice Johnson',
      email: 'alice@example.com',
      paymentStatus: 'Active',
      paymentCard: {
        type: 'Amex',
        number: '**** **** **** 9012',
        exp: '09/23',
        cvv: '***',
        cardholder: 'Alice Johnson',
      },
    },
  ];

  const getCardBackground = (cardType) => {
    switch (cardType) {
      case 'Visa':
        return 'bg-gradient-to-r from-blue-500 to-purple-600';
      case 'Mastercard':
        return 'bg-gradient-to-r from-red-500 to-orange-500';
      case 'Amex':
        return 'bg-gradient-to-r from-green-500 to-teal-500';
      default:
        return 'bg-gradient-to-r from-gray-500 to-gray-700';
    }
  };

  return (
    <div className="p-6 bg-gray-100 dark:bg-gray-900 min-h-screen">
      <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-6">Subscribed Users</h1>
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
        <table className="w-full">
          <thead>
            <tr>
              <th className="text-left text-gray-700 dark:text-gray-300">Name</th>
              <th className="text-left text-gray-700 dark:text-gray-300">Email</th>
              <th className="text-left text-gray-700 dark:text-gray-300">Payment Status</th>
              <th className="text-left text-gray-700 dark:text-gray-300">Payment Card</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id} className="border-t">
                <td className="py-2 text-gray-800 dark:text-white">{user.name}</td>
                <td className="py-2 text-gray-800 dark:text-white">{user.email}</td>
                <td className="py-2 text-gray-800 dark:text-white">{user.paymentStatus}</td>
                <td className="py-2 text-gray-800 dark:text-white">
                  {user.paymentCard ? (
                    <div className={`p-4 rounded-lg shadow-md ${getCardBackground(user.paymentCard.type)}`}>
                      <div className="text-white">
                        <div className="flex justify-between items-center mb-4">
                          <span className="text-lg font-semibold">{user.paymentCard.cardholder}</span>
                          <span className="text-sm">{user.paymentCard.type}</span>
                        </div>
                        <div className="mb-4">
                          <span className="text-xl tracking-widest">{user.paymentCard.number}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <div>
                            <span className="text-sm">Exp:</span>{' '}
                            <span className="text-sm">{user.paymentCard.exp}</span>
                          </div>
                          <div>
                            <span className="text-sm">CVV:</span>{' '}
                            <span className="text-sm">{user.paymentCard.cvv}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <span className="text-sm text-gray-500">No card on file</span>
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

export default SubscribedUsers;