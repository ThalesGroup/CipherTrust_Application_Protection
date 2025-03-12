import React, { useState, useEffect } from 'react';

function UpdatePayment() {
  const [formData, setFormData] = useState({
    cardType: '', // New field for card type
    cardNumber: '',
    expirationDate: '',
    cvv: '',
    id: '',
  });

  // Fetch default values on component mount
  useEffect(() => {
    const fetchDefaultValues = async () => {
      try {
        // Simulate an API call to fetch user data
        const response = await fetch('http://localhost:9090/api/v1/users/'+localStorage.getItem('userId')); // Replace with your API endpoint
        const data = await response.json();

        // Extract payment information from the JSON response
        const { id, cardType, cardNumber, expirationDate, cvv } = data.paymentInfo;

        // Update the form data state
        setFormData({
          id: id,
          cardType: cardType, // Set default card type
          cardNumber: cardNumber,
          expirationDate: expirationDate,
          cvv: cvv
        });
      } catch (error) {
        console.error('Error fetching default values:', error);
      }
    };

    fetchDefaultValues();
  }, []);

  // Handle form field changes
  const handleChange = (e) => {
    const { id, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [id]: value
    }));
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:9090/api/v1/users/'+localStorage.getItem('userId')+'/payment-info', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      const result = await response.json();
      console.log('Update successful:', result);
      // Handle success (e.g., show a success message)
    } catch (error) {
      console.error('Error updating payment:', error);
      // Handle error (e.g., show an error message)
    }
  };

  return (
    <div className="p-6 bg-gray-100 dark:bg-gray-900 min-h-screen">
      <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-6">Update Payment Settings</h1>
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
        <form onSubmit={handleSubmit}>
          {/* Card Type Dropdown */}
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300" htmlFor="cardType">
              Card Type
            </label>
            <select
              id="cardType"
              className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:text-white"
              value={formData.cardType}
              onChange={handleChange}
            >
              <option value="">Select Card Type</option>
              <option value="Visa">Visa</option>
              <option value="Mastercard">Mastercard</option>
            </select>
          </div>

          {/* Card Number */}
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300" htmlFor="cardNumber">
              Card Number
            </label>
            <input
              type="text"
              id="id"
              value={formData.id}
              hidden
            />
            <input
              type="text"
              id="cardNumber"
              className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:text-white"
              placeholder="1234 5678 9012 3456"
              value={formData.cardNumber}
              onChange={handleChange}
            />
          </div>

          {/* Expiry Date */}
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300" htmlFor="expirationDate">
              Expiry Date
            </label>
            <input
              type="text"
              id="expirationDate"
              className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:text-white"
              placeholder="MM/YY"
              value={formData.expirationDate}
              onChange={handleChange}
            />
          </div>

          {/* CVV */}
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300" htmlFor="cvv">
              CVV
            </label>
            <input
              type="text"
              id="cvv"
              className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:text-white"
              placeholder="123"
              value={formData.cvv}
              onChange={handleChange}
            />
          </div>

          {/* Submit Button */}
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