import { React, useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import axios from 'axios';
import jwt_decode from "jwt-decode";

export default function Fetch() {
    const { state } = useLocation();
    const [accounts, setAccounts] = useState("");
    let token = sessionStorage.getItem('token');
    var decodedToken = jwt_decode(token);

    useEffect(() => {
      const headers = { Authorization: `Basic ${sessionStorage.getItem('basic')}` };
      axios
        .get('http://'+process.env.REACT_APP_BACKEND_IP_ADDRESS+':8081/api/proxy/accounts/all/'+decodedToken.preferred_username, {
          headers: headers
        })
        .then((res) => {
          console.log(res.data.accounts);
          setAccounts(res.data.accounts);
        })
        .catch((err) => console.log(err));
      }, []);  

    return(
      <div className="container px-6 mx-auto">
        {/* Remove class [ h-64 ] when adding a card block */}
        <div className="rounded shadow relative bg-white z-10 -mt-8 mb-8 w-full"> 
          <div className="xl:w-full 2xl:w-full w-full">
            <div className="px-4 md:px-10 py-4 md:py-7">
              <div className="sm:flex items-center justify-between">
                <p className="text-base sm:text-lg md:text-xl lg:text-2xl font-bold leading-normal text-gray-800">Customers</p>
              </div>
            </div>
            <div className="bg-white px-4 md:px-10 pb-5">
              <div className="overflow-x-auto">
                <table className="w-full whitespace-nowrap">
                  <tbody> 
                    <tr className="text-sm leading-none text-gray-600 h-16 border-collapse border-2 border-gray-200">
                      <td className="w-1/2">
                        <div className="flex items-center">
                          <div className="pl-2">
                            <p className="text-md font-medium leading-none text-gray-800">Customer Name</p>
                          </div>
                        </div>
                      </td>
                      <td className="pl-16">
                          <p className="text-md font-medium leading-none text-gray-800">SSN</p>
                      </td>
                      <td className="pl-16">
                          <p className="text-md font-medium leading-none text-gray-800">Date Of Birth</p>
                      </td>
                      <td className="pl-16">
                          <p className="text-md font-medium leading-none text-gray-800">Contact Number</p>
                      </td>
                      <td className="pl-16">
                          <p className="text-md font-medium leading-none text-gray-800">View</p>
                      </td>
                    </tr>       
                    {
                      Object.entries(accounts).map((account, i) => { 
                        console.log(account);
                        const key = account[0];
                        const details = account[1].details;
                        const username = account[1].userName
                        return (
                          <>
                          <tr className="text-sm leading-none text-gray-600 h-16 border-collapse border-2 border-gray-200">
                            <td className="w-1/2">
                              <div className="flex items-center">
                                <div className="pl-2">
                                  <p className="text-md font-medium leading-none text-gray-800">{details.name}</p>
                                </div>
                              </div>
                            </td>
                            <td className="pl-16">
                                <p>{details.ssn}</p>
                            </td>
                            <td className="pl-16">
                                <p>{details.dob}</p>
                            </td>
                            <td className="pl-16">
                                <p>{details.mobile}</p>
                            </td>
                            <td className="pl-16">
                                <p>
                                  <a href={"/auth/admin/fetch?user=" + username + "&meta=" + btoa(details.name)}>View Cards</a>
                                </p>
                            </td>
                          </tr> 
                          </>
                        );
                      }
                    )}                                                 
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
}