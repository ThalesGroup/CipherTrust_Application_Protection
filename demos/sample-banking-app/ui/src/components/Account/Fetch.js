import { React, useEffect, useState } from 'react';
import { useLocation, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import jwt_decode from "jwt-decode";

export default function Fetch() {
  const [fullName, setFullName] = useState('');
  const [mobileNumber, setMobileNumber] = useState();
  const [dob, setDob] = useState();
  const [ssn, setSsn] = useState();
  const [accounts, setAccounts] = useState("");
  const { state } = useLocation();
  const [searchParams, setSearchParams] = useSearchParams();
  let token = sessionStorage.getItem('token');
  var decodedToken = jwt_decode(token);

  var userQuery = searchParams.get("user");

  useEffect(() => {
    const headers = { Authorization: `Basic ${sessionStorage.getItem('basic')}` };
    axios
      .get('http://'+process.env.REACT_APP_BACKEND_IP_ADDRESS+':8081/api/proxy/account/details/'+userQuery,
      {
        headers: headers
      })
      .then((res) => {
        console.log(res.data.details);
        setFullName(res.data.details.name);
        setMobileNumber(res.data.details.mobile);
        setDob(res.data.details.dob);
        setSsn(res.data.details.ssn);
      })
      .catch((err) => console.log(err));

    axios
      .get('http://'+process.env.REACT_APP_BACKEND_IP_ADDRESS+':8081/api/proxy/accounts/'+
        decodedToken.preferred_username+
        '/'+ 
        userQuery, {
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
        <div className="rounded shadow relative bg-white z-10 -mt-8 mb-8 w-full pb-5">
          <div className="container mx-auto grid sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-2 pt-6 gap-8">
              <div className="rounded border-gray-300  dark:border-gray-700 border-dashed border-2">
                  <div className="w-full bg-white shadow rounded" id="modal">
                      <div className="p-6 border-b border-gray-200 flex items-center justify-between">
                          <div className="flex items-center">
                              <div className="pl-3">
                                  <p className="text-lg font-medium leading-normal text-gray-800">User Details</p>
                              </div>
                          </div>
                      </div>
                      <div className="p-1 border-b border-gray-200">
                          <div className="w-full flex items-center justify-between">
                              <div className="flex items-center">
                                  <div className="pl-3">
                                      <p className="text-sm font-medium leading-normal text-gray-800">Full Name</p>
                                  </div>
                              </div>
                              <div className="flex items-center">
                                  <div className="pr-2 bg-gray-100 rounded flex items-center justify-between">
                                      {fullName}
                                  </div>
                              </div>
                          </div>                            
                      </div>
                      <div className="p-1 border-b border-gray-200">
                          <div className="w-full flex items-center justify-between">
                              <div className="flex items-center">
                                  <div className="pl-3">
                                      <p className="text-sm font-medium leading-normal text-gray-800">SSN</p>
                                  </div>
                              </div>
                              <div className="flex items-center">
                                  <div className="pr-2 bg-gray-100 rounded flex items-center justify-between">
                                      {ssn}
                                  </div>
                              </div>
                          </div>                            
                      </div>
                      <div className="p-1 border-b border-gray-200">
                          <div className="w-full flex items-center justify-between">
                              <div className="flex items-center">
                                  <div className="pl-3">
                                      <p className="text-sm font-medium leading-normal text-gray-800">Date Of Birth</p>
                                  </div>
                              </div>
                              <div className="flex items-center">
                                  <div className="pr-2 bg-gray-100 rounded flex items-center justify-between">
                                      {dob}
                                  </div>
                              </div>
                          </div>                            
                      </div>
                      <div className="p-1 border-b border-gray-200">
                          <div className="w-full flex items-center justify-between">
                              <div className="flex items-center">
                                  <div className="pl-3">
                                      <p className="text-sm font-medium leading-normal text-gray-800">Contact Number</p>
                                  </div>
                              </div>
                              <div className="flex items-center">
                                  <div className="pr-2 bg-gray-100 rounded flex items-center justify-between">
                                      {mobileNumber}
                                  </div>
                              </div>
                          </div>                            
                      </div>                     
                  </div>
              </div>
              <div className="rounded border-gray-300  dark:border-gray-700 border-dashed border-2">
              <div className="w-full bg-white shadow rounded" id="modal">
                      <div className="p-6 border-b border-gray-200 flex items-center justify-between">
                          <div className="flex items-center">
                              <div className="pl-3">
                                  <p className="text-lg font-medium leading-normal text-gray-800">User's Accounts</p>
                              </div>
                          </div>
                      </div>
                      <div className="p-3 border-b border-gray-200">
                          
                              
                              {Object.entries(cards).map((entry) => {
                                  const card = entry[0];
                                  const details = entry[1];
                                  return (
                                  <>
                                  <div className="w-full flex items-center justify-between">
                                  <div className="w-full flex items-center justify-center">
                                      <div className="xl:w-full sm:w-full w-full 2xl:w-full flex flex-col items-center py-16 md:py-12 bg-gradient-to-r from-indigo-700 to-purple-500 rounded-lg">
                                          <div className="w-full flex items-center justify-center">
                                              <div className="flex flex-col items-center">
                                                  <p className="mt-2 text-xs sm:text-sm md:text-base font-semibold text-center text-white">
                                                      Friendly Name: {details[0].friendlyName}
                                                  </p>
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
                                  </div>
                                  <hr />
                                  </>
                                  );
                              })}                        
                      </div>                    
                  </div>
              </div>
          </div>
        </div>
    </div>
  );
}