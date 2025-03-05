import React, { useState, useEffect } from 'react';
import axios from 'axios';

function SubscribedUsers() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAddUserForm, setShowAddUserForm] = useState(false);
  const [newUser, setNewUser] = useState({
    name: '',
    username: '',
    password: '',
    email: '',
    contactNum: '',
    addressLineOne: '',
    addressLineTwo: '',
    city: '',
    state: '',
    country: '',
    zip: '',
    paymentInfo: {
      cardType: '',
      cardNumber: '',
      expirationDate: '',
      cvv: ''
    }
  });

  // Fetch data from the API
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:9090/api/v1/users');
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

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    if (name.startsWith('paymentInfo.')) {
      const paymentInfoField = name.split('.')[1];
      setNewUser((prevUser) => ({
        ...prevUser,
        paymentInfo: {
          ...prevUser.paymentInfo,
          [paymentInfoField]: value
        }
      }));
    } else {
      setNewUser((prevUser) => ({
        ...prevUser,
        [name]: value
      }));
    }
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('https://api.example.com/subscribed-users', newUser);
      console.log('New User Added:', response.data);
      setUsers([...users, response.data]); // Add the new user to the list
      setShowAddUserForm(false); // Close the form
      setNewUser({
        name: '',
        username: '',
        password: '',
        email: '',
        contactNum: '',
        addressLineOne: '',
        addressLineTwo: '',
        city: '',
        state: '',
        country: '',
        zip: '',
        paymentInfo: {
          cardType: '',
          cardNumber: '',
          expirationDate: '',
          cvv: ''
        }
      }); // Reset the form
    } catch (err) {
      console.error('Error adding user:', err);
      setError('Failed to add user. Please try again.');
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
      <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-6">Subscribed Users</h1>
      <button
        onClick={() => setShowAddUserForm(!showAddUserForm)}
        className="mb-6 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-all"
      >
        {showAddUserForm ? 'Cancel' : 'Add New User'}
      </button>

      {showAddUserForm && (
        <div className="mb-6 bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-4">Add New User</h2>
          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Name</label>
                <input
                  type="text"
                  name="name"
                  value={newUser.name}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:text-white"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Username</label>
                <input
                  type="text"
                  name="username"
                  value={newUser.username}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:text-white"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Password</label>
                <input
                  type="password"
                  name="password"
                  value={newUser.password}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:text-white"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Email</label>
                <input
                  type="email"
                  name="email"
                  value={newUser.email}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:text-white"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Contact Number</label>
                <input
                  type="text"
                  name="contactNum"
                  value={newUser.contactNum}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:text-white"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Address Line 1</label>
                <input
                  type="text"
                  name="addressLineOne"
                  value={newUser.addressLineOne}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:text-white"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Address Line 2</label>
                <input
                  type="text"
                  name="addressLineTwo"
                  value={newUser.addressLineTwo}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">City</label>
                <input
                  type="text"
                  name="city"
                  value={newUser.city}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:text-white"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">State</label>
                <input
                  type="text"
                  name="state"
                  value={newUser.state}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:text-white"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Country</label>
                <input
                  type="text"
                  name="country"
                  value={newUser.country}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:text-white"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">ZIP Code</label>
                <input
                  type="text"
                  name="zip"
                  value={newUser.zip}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:text-white"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Card Type</label>
                <input
                  type="text"
                  name="paymentInfo.cardType"
                  value={newUser.paymentInfo.cardType}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:text-white"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Card Number</label>
                <input
                  type="text"
                  name="paymentInfo.cardNumber"
                  value={newUser.paymentInfo.cardNumber}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:text-white"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Expiration Date</label>
                <input
                  type="text"
                  name="paymentInfo.expirationDate"
                  value={newUser.paymentInfo.expirationDate}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:text-white"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">CVV</label>
                <input
                  type="text"
                  name="paymentInfo.cvv"
                  value={newUser.paymentInfo.cvv}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:text-white"
                  required
                />
              </div>
            </div>
            <button
              type="submit"
              className="mt-4 w-full bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600 transition-all"
            >
              Submit
            </button>
          </form>
        </div>
      )}

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