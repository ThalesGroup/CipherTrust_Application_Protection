import {React, useEffect, useState} from 'react';
import jwt_decode from "jwt-decode";
import axios from 'axios';
import { data } from 'autoprefixer';

function Account() {
  let token = sessionStorage.getItem('token');
  const [accounts, setAccounts] = useState("");
  var decodedToken = jwt_decode(token);

  useEffect(() => {
    const headers = { Authorization: `Basic ${sessionStorage.getItem('basic')}` };
    axios
      .get(
        'http://'+process.env.REACT_APP_BACKEND_IP_ADDRESS+':8081/api/proxy/accounts/'+decodedToken.preferred_username+'/'+ decodedToken.preferred_username,
        {
          headers: headers
        })
      .then((res) => {
        setAccounts(res.data.accounts);
      })
      .catch((err) => console.log(err));
    }, []);
  
  const cards = {};
  for (const account of accounts) {
    if (account.friendlyName in cards) {
      cards[account.friendlyName].push(account);
    } else {
      cards[account.friendlyName] = [account];
    }
  }
  
  return(   
    <div className="container px-6 mx-auto">
      {/* Remove class [ h-64 ] when adding a card block */}
      <div className="rounded shadow relative bg-white z-10 -mt-8 mb-8 w-full">
      <div className="w-full flex items-center justify-center">
        <h3 className="bg-blue-100 text-black justify-center items-center">My Credit Cards</h3>
      </div>
      {Object.entries(cards).map((entry) => {
        const card = entry[0];
        const details = entry[1];
        return (
          <>
          <div className="w-full flex items-center justify-center">
            <div className="xl:w-1/3 sm:w-1/3 w-full 2xl:w-1/3 flex flex-col items-center py-16 md:py-12 bg-gradient-to-r from-indigo-700 to-purple-500 rounded-lg">
                <div className="w-full flex items-center justify-center">
                    <div className="flex flex-col items-center">
                        <img src="https://cdn.tuk.dev/assets/webapp/master_layouts/boxed_layout/boxed_layout2.jpg" alt="profile" />
                        <p className="mt-2 text-xs sm:text-sm md:text-base font-semibold text-center text-white">{decodedToken.preferred_username}</p>
                    </div>
                </div>
                <div className="flex items-center mt-7">
                    <div className>
                        <p className="text-xs text-gray-300">Card Number</p>
                        <p className="mt-2 text-base sm:text-xs md:text-xs 2xl:text-xs text-gray-50">{details[0].ccNumber}</p>
                    </div>
                    <div className="ml-12">
                        <p className="text-xs text-gray-300">CVV</p>
                        <p className="mt-2 text-base sm:text-xs md:text-xs 2xl:text-xs text-gray-50">{details[0].cvv}</p>
                    </div>
                    <div className="ml-12">
                        <p className="text-xs text-gray-300">Expiry Date</p>
                        <p className="mt-2 text-base sm:text-xs md:text-xs 2xl:text-xs text-gray-50">{details[0].expDate}</p>
                    </div>
                </div>
            </div>
          </div>
          <hr />
          </>
        );
    })}
    </div></div>
  )
}

export default Account;