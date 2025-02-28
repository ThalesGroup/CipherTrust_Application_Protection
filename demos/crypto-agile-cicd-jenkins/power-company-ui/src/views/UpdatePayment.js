import React from 'react';

function UpdatePayment() {
  return (
    <div className="p-6 bg-gray-100 dark:bg-gray-900 min-h-screen">
      <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-6">Update Payment Settings</h1>
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
        <form>
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300" htmlFor="cardNumber">
              Card Number
            </label>
            <input
              type="text"
              id="cardNumber"
              className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:text-white"
              placeholder="1234 5678 9012 3456"
            />
          </div>
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300" htmlFor="expiryDate">
              Expiry Date
            </label>
            <input
              type="text"
              id="expiryDate"
              className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:text-white"
              placeholder="MM/YY"
            />
          </div>
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300" htmlFor="cvv">
              CVV
            </label>
            <input
              type="text"
              id="cvv"
              className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:text-white"
              placeholder="123"
            />
          </div>
          <button
            type="submit"
            className="w-full bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600 transition-all"
          >
            Save Changes
          </button>
        </form>
      </div>
    </div>
  );
}

export default UpdatePayment;