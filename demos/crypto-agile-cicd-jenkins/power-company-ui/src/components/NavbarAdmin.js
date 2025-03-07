import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { FaUser, FaCog, FaSignOutAlt } from 'react-icons/fa';
import { MdDarkMode, MdLightMode } from 'react-icons/md';

function NavbarAdmin({ username, onLogout, onToggleDarkMode, isDarkMode }) {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  return (
    <nav className="bg-white dark:bg-gray-800 p-4 shadow-md">
      <div className="container mx-auto flex justify-between items-center">
        <div className="flex space-x-4">
          <Link to="/" className="text-gray-800 dark:text-white hover:text-blue-500">
            Crestline Power
          </Link>
          {/* <Link to="/data-center" className="text-gray-800 dark:text-white hover:text-blue-500">
            Data Center
          </Link> */}
          <Link to="/aggregators" className="text-gray-800 dark:text-white hover:text-blue-500">
            Aggregators
          </Link>
          <Link to="/subscribed-users" className="text-gray-800 dark:text-white hover:text-blue-500">
            Subscribed Users
          </Link>
        </div>
        <div className="flex items-center space-x-4">
          <button
            onClick={onToggleDarkMode}
            className="text-gray-800 dark:text-white hover:text-blue-500"
          >
            {isDarkMode ? <MdLightMode size={20} /> : <MdDarkMode size={20} />}
          </button>
          <div className="relative">
            <button
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="flex items-center text-gray-800 dark:text-white hover:text-blue-500"
            >
              <FaUser size={20} />&nbsp;Welcome, {username}
            </button>
            {isDropdownOpen && (
              <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-700 rounded-lg shadow-lg">
                <div className="p-2">
                  <button className="w-full flex items-center space-x-2 text-gray-800 dark:text-white hover:bg-gray-100 dark:hover:bg-gray-600 p-2 rounded-lg">
                    <FaCog size={16} />
                    <span>Settings</span>
                  </button>
                  <button
                    onClick={onLogout}
                    className="w-full flex items-center space-x-2 text-gray-800 dark:text-white hover:bg-gray-100 dark:hover:bg-gray-600 p-2 rounded-lg"
                  >
                    <FaSignOutAlt size={16} />
                    <span>Logout</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

export default NavbarAdmin;